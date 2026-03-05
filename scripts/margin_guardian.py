# scripts/margin_guardian.py
# ANTIGRAVITY SYSTEM — Margin Guardian
# Corre automático al final de cada ciclo de main.py

import sqlite3
import logging
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR  = Path(__file__).resolve().parent.parent
DB_PATH   = BASE_DIR / "data" / "antigravity.db"
KB_PATH   = BASE_DIR / "KNOWLEDGE_BASE.md"

TENANT_ID        = "3947b9dc-7e89-4a05-a659-46e8ccdde558"
MARTYR_THRESHOLD = 0.29
CRITICAL_COUNT   = 3   # si hay mas de 3 criticos → alerta

log = logging.getLogger("MarginGuardian")


class MarginGuardian:

    def __init__(self, db_path=DB_PATH, tenant_id=TENANT_ID):
        self.db_path   = db_path
        self.tenant_id = tenant_id

    def run(self) -> dict:
        """
        Punto de entrada principal.
        Retorna resumen para que main.py decida si continuar o alertar.
        """
        log.info("🛡️  MarginGuardian activado...")
        result = {
            "martyrs":       [],
            "total_gap":     0.0,
            "critical_count": 0,
            "status":        "OK"
        }

        try:
            conn    = sqlite3.connect(self.db_path)
            martyrs = self._detect_martyrs(conn)
            conn.close()

            if not martyrs:
                log.info("✅ Guardian: sin mártires detectados.")
                return result

            critical = [m for m in martyrs if m["gap"] > 50]
            result["martyrs"]        = martyrs
            result["total_gap"]      = round(sum(m["gap"] for m in martyrs), 2)
            result["critical_count"] = len(critical)
            result["status"]         = "ALERT" if len(critical) >= CRITICAL_COUNT else "WARNING"

            self._log_to_console(martyrs, result)

            if result["status"] == "ALERT":
                self._write_knowledge_base(martyrs, result)

        except Exception as e:
            log.error(f"❌ Guardian falló: {e} — continuando ciclo.")
            result["status"] = "ERROR"

        return result

    def _detect_martyrs(self, conn) -> list[dict]:
        import math
        monthly = 0.05
        days    = 15

        rows = conn.execute("""
            SELECT item_key, MAX(price) as last_price
            FROM historical_data
            WHERE tenant_id = ? AND sector = 'pharmacy'
            GROUP BY item_key
            ORDER BY last_price ASC
        """, (self.tenant_id,)).fetchall()

        martyrs = []
        for row in rows:
            sku   = row[0]
            price = row[1]
            cost  = price * 0.72
            r     = math.log(1 + monthly)
            real  = cost * math.exp(r * days / 30)
            margin = (price - real) / price

            if margin < MARTYR_THRESHOLD:
                fc        = real * (1 + monthly)
                prot      = fc / (1 - 0.25)
                gap       = prot - price
                martyrs.append({
                    "sku":    sku,
                    "price":  round(price,  2),
                    "margin": round(margin * 100, 2),
                    "gap":    round(gap,    2),
                    "level":  "CRITICO" if gap > 50 else "URGENTE"
                })

        return martyrs

    def _log_to_console(self, martyrs, result):
        log.warning(f"🚨 Guardian detectó {len(martyrs)} mártires | "
                    f"Gap total: ${result['total_gap']:,.2f} | "
                    f"Status: {result['status']}")
        for m in martyrs:
            log.warning(f"   {'🔴' if m['level']=='CRITICO' else '🟡'} "
                        f"{m['sku']:<35} margen={m['margin']}%  gap=${m['gap']}")

    def _write_knowledge_base(self, martyrs, result):
        now   = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        lines = [
            f"\n---\n",
            f"## 🚨 MARGIN ALERT — {now}\n",
            f"**Status**: {result['status']}  \n",
            f"**Críticos**: {result['critical_count']}  \n",
            f"**Gap total**: ${result['total_gap']:,.2f}/unidad  \n\n",
            f"| Producto | Margen% | Gap/U | Nivel |\n",
            f"|---|---|---|---|\n",
        ]
        for m in martyrs:
            lines.append(
                f"| {m['sku']} | {m['margin']}% | ${m['gap']} | {m['level']} |\n"
            )
        lines.append(f"\n**Acción sugerida**: Ejecutar `price_rule_executor.py --apply`\n")

        with open(KB_PATH, "a", encoding="utf-8") as f:
            f.writelines(lines)

        log.info(f"📝 Alerta registrada en KNOWLEDGE_BASE.md")
