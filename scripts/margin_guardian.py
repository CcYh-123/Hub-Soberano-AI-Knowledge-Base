# scripts/margin_guardian.py




# ANTIGRAVITY SYSTEM — Margin Guardian


# Corre automático al final de cada ciclo de main.py



import os

import sqlite3

import logging
from datetime import datetime, timezone
from pathlib import Path


from dotenv import load_dotenv
try:
    
    from supabase import create_client  # type: ignore
except Exception:
    create_client = None

try:
    from core.config_loader import config  # type: ignore
except Exception:
    class _FallbackConfig:
        def get(self, key: str, default=None):
            return default

    config = _FallbackConfig()

BASE_DIR   = Path(__file__).resolve().parent.parent
DB_PATH    = BASE_DIR / "data" / "antigravity.db"
EXTERNAL_DB_PATH = Path("C:/Users/Lenovo/Documents/CURSO/database.db")
KB_PATH    = BASE_DIR / "KNOWLEDGE_BASE.md"
REPORTS_DIR = BASE_DIR / "reports"

TENANT_ID             = config.get("tenants.demo_saas_id", "3947b9dc-7e89-4a05-a659-46e8ccdde558")
CRITICAL_THRESHOLD    = 0.15
PREVENTIVE_THRESHOLD  = 0.25
SUGGESTED_MARGIN_GOAL = 0.30  # margen objetivo para "Precio Sugerido"

log = logging.getLogger("MarginGuardian")

print('--- ARRANCANDO MOTOR DEL GUARDIÁN ---')
load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
print(f"[MarginGuardian] SUPABASE_URL presente: {bool(SUPABASE_URL)}, SUPABASE_KEY presente: {bool(SUPABASE_KEY)}")
supabase = (
    create_client(SUPABASE_URL, SUPABASE_KEY)
    if (create_client and SUPABASE_URL and SUPABASE_KEY)
    else None
)


class MarginGuardian:

    def __init__(self, db_path=None, tenant_id=TENANT_ID):
        if db_path is None:
            self.db_path = EXTERNAL_DB_PATH if EXTERNAL_DB_PATH.exists() else DB_PATH
        else:
            self.db_path = Path(db_path)
        self.tenant_id = tenant_id

    def run(self) -> dict:
        """
        Punto de entrada principal.
        Retorna resumen para que main.py decida si continuar o alertar.
        """
        log.info("🛡️  MarginGuardian activado...")
        print(f"[MarginGuardian] Ejecutando run() para tenant {self.tenant_id}")
        print(f"[MarginGuardian] Usando base local en: {DB_PATH}")
        result = {
            "martyrs":       [],
            "total_gap":     0.0,
            "critical_count": 0,
            "status":        "OK"
        }

        try:
            print(f"[MarginGuardian] Conectando a SQLite en {self.db_path} ...")
            conn    = sqlite3.connect(self.db_path)
            martyrs = self._detect_martyrs(conn)
            conn.close()

            critical = [m for m in martyrs if m["level"] == "CRITICO"]
            result["martyrs"]        = martyrs
            result["total_gap"]      = round(sum(m["gap"] for m in martyrs), 2)
            result["critical_count"] = len(critical)
            result["status"]         = "ALERT" if len(critical) > 0 else "WARNING"

            self._log_to_console(martyrs, result)
            self._print_martyrs_table(martyrs)

            # Escribimos siempre en la KB, incluso sin alertas
            self._write_knowledge_base(martyrs, result)

        except Exception as e:
            log.error(f"❌ Guardian falló: {e} — continuando ciclo.")
            result["status"] = "ERROR"

        return result

    def _load_costs_and_stock_from_supabase(self) -> dict:
        """
        Carga los costos y el stock actual desde la tabla products en Supabase usando requests.
        Fase 5: Combustible de Volumen.
        """
        print("[MarginGuardian] Iniciando carga de costos y stock desde Supabase (Via REST API)...")
        import requests
        
        url = f"{SUPABASE_URL}/rest/v1/products?select=name,cost_price,stock"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }

        try:
            resp = requests.get(url, headers=headers)
            if resp.status_code != 200:
                print(f"[MarginGuardian] Error API Supabase: {resp.status_code}")
                return {}
            rows = resp.json() or []
        except Exception as e:
            print(f"[MarginGuardian] Fallo de conexion a Supabase: {e}")
            return {}

        data_by_sku: dict = {}
        for row in rows:
            sku = row.get("name")
            if not sku:
                continue
            
            try:
                data_by_sku[str(sku)] = {
                    "cost": float(row.get("cost_price") or 0),
                    "stock": float(row.get("stock") or 0)
                }
            except (TypeError, ValueError):
                continue

        print(f"[MarginGuardian] {len(data_by_sku)} productos cargados desde Supabase.")
        return data_by_sku

    def _detect_martyrs(self, conn) -> list[dict]:
        import math
        monthly = config.get("economy.monthly_inflation", 0.05)
        days    = config.get("thresholds.days_inventory", 15)
        target  = config.get("economy.target_margin", 0.25)

        # Fase 5: Cargamos Costos y Volumen desde Supabase (Carga combinada)
        print(f"[MarginGuardian] Cargando Costos y Volumen desde Supabase para Fase 5...")
        data_by_sku = self._load_costs_and_stock_from_supabase()
        
        # ... (lógica de resolución de fuente local omitida por brevedad para el patch)
        source = self._resolve_price_source(conn)
        if source is None: 
            print("[MarginGuardian] ERROR: No se detecto ninguna tabla compatible en SQLite.")
            return []
            
        table, item_col, price_col, tenant_col, sector_col = source
        print(f"[MarginGuardian] Fuente detectada: tabla={table}, item={item_col}, price={price_col}, tenant={tenant_col}")

        sql = f"SELECT {item_col} AS item_key, MAX({price_col}) as last_price FROM {table} WHERE {tenant_col} = ? GROUP BY {item_col}"
        rows = conn.execute(sql, (self.tenant_id,)).fetchall()
        print(f"[MarginGuardian] Filas SQLite encontradas para el tenant {self.tenant_id}: {len(rows)}")
        
        martyrs = []
        for row in rows:
            sku    = str(row[0])
            price  = float(row[1])
            
            # Busqueda de datos en el dict de Supabase
            print(f"[DEBUG] Buscando SKU en Supabase: '{sku}'")
            product_data = data_by_sku.get(sku)
            if not product_data: 
                print(f"[DEBUG] SKU '{sku}' no encontrado en Supabase. Llaves disponibles: {list(data_by_sku.keys())}")
                continue
            
            cost = product_data['cost']
            stock = product_data['stock']
            
            if cost <= 0: continue

            r      = math.log(1 + monthly)
            real   = cost * math.exp(r * days / 30)
            margin = (price - real) / price

            if margin < PREVENTIVE_THRESHOLD:
                level = "CRITICO" if margin < CRITICAL_THRESHOLD else "PREVENTIVO"
                
                # Fase 5: GAP TOTAL = (Sugerido - Actual) * Stock
                suggested_price = real / (1 - SUGGESTED_MARGIN_GOAL)
                gap_unit = suggested_price - price
                gap_total = gap_unit * stock

                martyrs.append({
                    "sku":             sku,
                    "cost_supa":       round(cost, 2),
                    "price":           round(price, 2),
                    "stock":           round(stock, 2),
                    "margin":          round(margin * 100, 2),
                    "gap":             round(gap_total, 2),
                    "level":           level,
                    "suggested_price": round(suggested_price, 2),
                })

        return martyrs

        print(f"[MarginGuardian] Mártires detectados para tenant {self.tenant_id}: {len(martyrs)}")
        return martyrs

    def _detect_martyrs_from_productos_agro_v2(self, conn, monthly: float, days: int) -> list[dict]:
        """
        Lee directamente de productos_agro_v2 (id, nombre, costo_reposicion, precio_venta, tenant_id)
        y marca como 'MÁRTIR' todo producto con margen bruto < 15%.
        """
        import math

        rows = conn.execute(
            """
            SELECT nombre, costo_reposicion, precio_venta
            FROM productos_agro_v2
            WHERE tenant_id = ?
              AND precio_venta > 0
            """,
            (self.tenant_id,),
        ).fetchall()
        print(f"[MarginGuardian] Filas leídas desde productos_agro_v2 para tenant {self.tenant_id}: {len(rows)}")

        martyrs: list[dict] = []
        for nombre, costo_reposicion, precio_venta in rows:
            sku = str(nombre)
            cost = float(costo_reposicion or 0)
            price = float(precio_venta or 0)
            if price <= 0:
                continue

            # Margen bruto simple usando costo de reposición local
            margin = (price - cost) / price if price else 0

            # Ajuste inflacionario opcional (mismo criterio que el modo histórico)
            r = math.log(1 + monthly)
            real = cost * math.exp(r * days / 30)

            # Precio sugerido para alcanzar el margen objetivo del 30%
            suggested_price = real / (1 - SUGGESTED_MARGIN_GOAL) if (1 - SUGGESTED_MARGIN_GOAL) != 0 else price
            gap = suggested_price - price

            if margin < CRITICAL_THRESHOLD:
                level = "MÁRTIR"
            elif margin < PREVENTIVE_THRESHOLD:
                level = "PREVENTIVO"
            else:
                level = "SANO"

            if level == "SANO":
                continue

            martyrs.append(
                {
                    "sku": sku,
                    "cost_supa": round(cost, 2),
                    "price": round(price, 2),
                    "margin": round(margin * 100, 2),
                    "gap": round(gap, 2),
                    "level": level,
                    "suggested_price": round(suggested_price, 2),
                }
            )

        print(f"[MarginGuardian] Mártires detectados en productos_agro para tenant {self.tenant_id}: {len(martyrs)}")
        return martyrs

    def _resolve_price_source(self, conn):
        """
        Intenta detectar automáticamente una tabla fuente con precios por item/SKU.
        Esto permite que el script no falle si el esquema cambió desde ayer.
        """
        try:
            objs = conn.execute(
                "select name, type from sqlite_master "
                "where type in ('table','view') and name not like 'sqlite_%'"
            ).fetchall()
        except Exception:
            return None

        candidates = [name for name, typ in objs]
        if not candidates:
            return None

        def cols_for(table_name: str) -> set[str]:
            try:
                rows = conn.execute(f"pragma table_info('{table_name}')").fetchall()
            except Exception:
                return set()
            return {str(r[1]).lower() for r in rows if r and r[1]}

        item_syn = ["item_key", "sku", "producto_sku", "product_sku", "item", "producto", "product", "nombre"]
        price_syn = ["price", "precio", "precio_venta", "pvp", "venta", "unit_price"]
        tenant_syn = ["tenant_id", "tenant", "company_id", "org_id"]
        sector_syn = ["sector", "category", "rubro"]

        scored = []
        for t in candidates:
            cols = cols_for(t)
            if not cols:
                continue
            item = next((c for c in item_syn if c in cols), None)
            price = next((c for c in price_syn if c in cols), None)
            tenant = next((c for c in tenant_syn if c in cols), None)
            sector = next((c for c in sector_syn if c in cols), None)
            score = int(item is not None) + int(price is not None) + int(tenant is not None) + int(sector is not None)
            if score >= 3:
                scored.append((score, t, item, price, tenant, sector))

        if not scored:
            return None

        scored.sort(reverse=True)
        _, table, item, price, tenant, sector = scored[0]
        return table, item, price, tenant, sector

    def _log_to_console(self, martyrs, result):
        """
        Imprime mártires en la terminal usando colores ANSI:
        - Verde: productos sin problema grave (no se muestra aquí).
        - Amarillo: nivel PREVENTIVO.
        - Rojo: nivel CRITICO.
        """
        log.warning(
            f"🚨 Guardian detectó {len(martyrs)} mártires | "
            f"Gap total: ${result['total_gap']:,.2f} | "
            f"Status: {result['status']}"
        )

        COLOR_RESET = "\033[0m"
        COLOR_RED   = "\033[91m"
        COLOR_YEL   = "\033[93m"
        COLOR_GRN   = "\033[92m"

        for m in martyrs:
            level = m.get("level", "")
            if level == "CRITICO":
                color = COLOR_RED
                icon  = "[CRITICO]"
            elif level == "PREVENTIVO":
                color = COLOR_YEL
                icon  = "[AVISO]"
            else:
                color = COLOR_GRN
                icon  = "[OK]"

            suggested = m.get("suggested_price")
            suggested_str = f" | sugerido=${suggested}" if (suggested is not None and level == "CRITICO") else ""

            line = (
                f"{icon} {m['sku']:<35} "
                f"margen={m['margin']}%  gap=${m['gap']}  nivel={level}"
                f"{suggested_str}"
            )
            print(color + "[MarginGuardian] " + line + COLOR_RESET)

    def _print_martyrs_table(self, martyrs):
        """
        Imprime al final una tabla ASCII con los mártires.
        Columnas: SKU | COSTO (SUPA) | VENTA (SQLITE) | MARGEN % | GAP $ | PRECIO SUGERIDO.
        Si margen < 15%, la fila se resalta con !! al inicio.
        """
        if not martyrs:
            return

        # Anchuras para alinear (ajustables)
        w_sku = max(28, max(len(str(m.get("sku", ""))) for m in martyrs))
        w_sku = min(w_sku, 40)
        w_cost = 12
        w_venta = 14
        w_margen = 8
        w_gap = 8
        w_sug = 14

        header = (
            f"| {'SKU':<{w_sku}} | {'COSTO (SUPA)':>{w_cost}} | {'VENTA (SQLITE)':>{w_venta}} | {'MARGEN %':>{w_margen}} | {'GAP $':>{w_gap}} | {'PRECIO SUGERIDO':>{w_sug}} |"
        )
        sep = (
            f"|{'-' * (w_sku + 2)}|{'-' * (w_cost + 2)}|{'-' * (w_venta + 2)}|{'-' * (w_margen + 2)}|{'-' * (w_gap + 2)}|{'-' * (w_sug + 2)}|"
        )

        print("")
        print("[MarginGuardian] === TABLA DE MÁRTIRES (SECTOR AGRO) ===")
        print(sep)
        print(header)
        print(sep)

        alert_prefix = "!! "
        for m in martyrs:
            margin = m.get("margin", 0)
            alert = alert_prefix if margin < 15 else "   "
            sku_raw = str(m.get("sku", ""))
            sku = (alert + sku_raw)[:w_sku] if len(alert + sku_raw) > w_sku else (alert + sku_raw).ljust(w_sku)
            cost_supa = m.get("cost_supa")
            cost_str = f"{cost_supa:,.2f}" if cost_supa is not None else "-"
            price = m.get("price", 0)
            venta_str = f"{price:,.2f}"
            gap = m.get("gap", 0)
            sug = m.get("suggested_price")
            sug_str = f"{sug:,.2f}" if sug is not None else "-"

            row = (
                f"| {sku:<{w_sku}} | {cost_str:>{w_cost}} | {venta_str:>{w_venta}} | {margin:>{w_margen}.2f} | {gap:>{w_gap}.2f} | {sug_str:>{w_sug}} |"
            )
            print(row)

        print(sep)
        print("")

    def _write_knowledge_base(self, martyrs, result):
        now   = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        lines = [f"\n---\n"]

        if martyrs:
            # Caso con alertas/mártires
            lines.extend([
                f"## 🚨 REPORTE DE PROTECCIÓN DE MARGEN - SECTOR AGRO — {now}\n",
                f"**Status**: {result['status']}  \n",
                f"**Críticos**: {result['critical_count']}  \n",
                f"**Gap de Ganancia total**: ${result['total_gap']:,.2f}/unidad  \n\n",
                f"> Nota: Valores sujetos a variabilidad logística y tipo de cambio.\n\n",
                f"| Producto | Margen% | Gap de Ganancia/U | Nivel | Precio Sugerido |\n",
                f"|---|---|---|---|---|\n",
            ])
            for m in martyrs:
                suggested = m.get("suggested_price")
                suggested_str = f"${suggested}" if (suggested is not None and m.get("level") == "CRITICO") else "-"
                lines.append(
                    f"| {m['sku']} | {m['margin']}% | ${m['gap']} | {m['level']} | {suggested_str} |\n"
                )
            lines.append(f"\n**Acción sugerida**: Ejecutar `price_rule_executor.py --apply`\n")
        else:
            # Caso sin novedades: registrar latido del sistema
            lines.extend([
                f"## ✅ SISTEMA ACTIVO SIN NOVEDADES — {now}\n",
                f"**Status**: {result.get('status', 'OK')}  \n",
                f"**Detalle**: No se detectaron productos con margen bajo para el tenant {self.tenant_id}.  \n",
            ])

        with open(KB_PATH, "a", encoding="utf-8") as f:
            f.writelines(lines)

        log.info(f"📝 Alerta registrada en KNOWLEDGE_BASE.md")
        self._write_margin_csv(martyrs)

    def _write_margin_csv(self, martyrs):
        """Escribe el reporte de mártires en CSV para el dashboard (reports/reporte_margen_YYYYMMDD_HHMMSS.csv)."""
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        csv_path = REPORTS_DIR / f"reporte_margen_{ts}.csv"
        import csv
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["sku", "cost_supa", "price", "stock", "margin", "gap", "suggested_price", "level"])
            for m in martyrs:
                w.writerow([
                    m.get("sku", ""),
                    m.get("cost_supa"),
                    m.get("price"),
                    m.get("stock"),
                    m.get("margin"),
                    m.get("gap"),
                    m.get("suggested_price"),
                    m.get("level", ""),
                ])
        log.info(f"📄 Reporte CSV guardado: {csv_path}")


def main():
    """
    Punto de entrada CLI para ejecutar el MarginGuardian de forma standalone.
    """
    guardian = MarginGuardian()
    result = guardian.run()
    if not result.get("martyrs"):
        print("[DEBUG] No se encontró nada, pero el script llegó al final.")
    else:
        print(f"[DEBUG] Ejecución completa. Mártires detectados: {len(result['martyrs'])}")


if __name__ == "__main__":
    main()
