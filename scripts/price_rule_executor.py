import sqlite3
import argparse
import math
import logging
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR   = Path(__file__).resolve().parent.parent
DB_PATH    = BASE_DIR / "data" / "antigravity.db"
REPORT_DIR = BASE_DIR / "reports"
LOG_FILE   = REPORT_DIR / "price_execution_log.txt"
REPORT_DIR.mkdir(exist_ok=True)

TENANT_ID         = "3947b9dc-7e89-4a05-a659-46e8ccdde558"
MONTHLY_INFLATION = 0.05
TARGET_MARGIN     = 0.25
MARTYR_THRESHOLD  = 0.29
MAX_PRICE_UP      = 0.40
DAYS_INVENTORY    = 15

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("PriceRuleExecutor")


class WealthModel:
    def adjusted_cost(self, cost, days):
        r = math.log(1 + MONTHLY_INFLATION)
        return cost * math.exp(r * days / 30)

    def forward_cost(self, cost, days):
        return self.adjusted_cost(cost, days) * (1 + MONTHLY_INFLATION)

    def protected_price(self, cost, days):
        return self.forward_cost(cost, days) / (1 - TARGET_MARGIN)

    def urgency(self, gap):
        if gap > 50:
            return "CRITICO"
        elif gap > 20:
            return "URGENTE"
        return "MONITOREAR"


def setup_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS price_rules (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id           TEXT NOT NULL,
            sku                 TEXT NOT NULL,
            old_price           REAL NOT NULL,
            new_price           REAL NOT NULL,
            margin_gap          REAL NOT NULL,
            profit_gap_per_unit REAL NOT NULL,
            status              TEXT DEFAULT 'PENDING',
            applied_at          TIMESTAMP,
            created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()


def get_martyrs(conn):
    rows = conn.execute("""
        SELECT item_key, MAX(price) as last_price
        FROM historical_data
        WHERE tenant_id = ? AND sector = 'pharmacy'
        GROUP BY item_key
        ORDER BY last_price ASC
    """, (TENANT_ID,)).fetchall()

    model   = WealthModel()
    martyrs = []

    for row in rows:
        sku   = row[0]
        price = row[1]
        cost  = price * 0.72
        real  = model.adjusted_cost(cost, DAYS_INVENTORY)
        margin = (price - real) / price

        if margin < MARTYR_THRESHOLD:
            prot   = model.protected_price(cost, DAYS_INVENTORY)
            gap    = prot - price
            capped = min(prot, price * (1 + MAX_PRICE_UP))
            martyrs.append({
                "sku":       sku,
                "old_price": round(price,  2),
                "new_price": round(capped, 2),
                "prot":      round(prot,   2),
                "margin":    round(margin * 100, 2),
                "mgap":      round((TARGET_MARGIN - margin) * 100, 2),
                "gap":       round(gap, 2),
                "urgency":   model.urgency(gap),
                "capped":    capped < prot
            })

    return martyrs


def dry_run(martyrs):
    total = sum(p["gap"] for p in martyrs)
    print("\n" + "=" * 80)
    print(f"  DRY-RUN | {len(martyrs)} martires | Recuperacion potencial: ${total:,.2f}/unidad")
    print("=" * 80)
    print(f"{'PRODUCTO':<35} {'ACTUAL':>10} {'SUGERIDO':>10} {'GAP':>10} {'MARGEN%':>8}  ESTADO")

    for p in martyrs:
        cap = "(CAP)" if p["capped"] else ""
        print(f"{p['sku']:<35} ${p['old_price']:>9.2f} ${p['new_price']:>9.2f}{cap:<6} ${p['gap']:>9.2f} {p['margin']:>7.1f}%  {p['urgency']}")

    print("-" * 80)


def apply_rules(conn, martyrs):
    log.info(f"🚀 EJECUCIÓN REAL — Escribiendo {len(martyrs)} reglas en DB")
    for p in martyrs:
        conn.execute("""
            INSERT INTO price_rules (tenant_id, sku, old_price, new_price, margin_gap, profit_gap_per_unit, status)
            VALUES (?, ?, ?, ?, ?, ?, 'PENDING')
        """, (TENANT_ID, p['sku'], p['old_price'], p['new_price'], p['mgap'], p['gap']))
    conn.commit()
    log.info("✅ Reglas persistidas exitosamente.")


def main():
    parser = argparse.ArgumentParser(description="Antigravity Phase 6")
    group  = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="Simular sin escribir en DB")
    group.add_argument("--apply",   action="store_true", help="Aplicar precios en DB")
    args = parser.parse_args()

    log.info(f"Executor iniciado | DB: {DB_PATH}")

    try:
        conn = sqlite3.connect(DB_PATH)
        setup_table(conn)
        martyrs = get_martyrs(conn)

        if not martyrs:
            print("\nSin martires. Todos los margenes son saludables.\n")
            return

        if args.dry_run:
            dry_run(martyrs)
        elif args.apply:
            apply_rules(conn, martyrs)

    except Exception as e:
        log.error(f"Error critico: {e}")
        raise
    finally:
        if "conn" in locals():
            conn.close()


if __name__ == "__main__":
    main()
