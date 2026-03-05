"""
-----------------------------------------------------------------------
SCRIPT: seed_pharmacy_data.py (v3 - Raw SQL, bypasses ORM autoincrement bug)
-----------------------------------------------------------------------
"""
import sqlite3
import json
import random
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path(__file__).parent.parent / "data" / "antigravity.db"

def seed():
    print(f"📦 Conectando a: {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # 1. Buscar tenant demo-saas
    cursor.execute("SELECT id, slug, subscription_tier FROM tenants WHERE slug = 'demo-saas'")
    tenant = cursor.fetchone()
    if not tenant:
        print("❌ Tenant 'demo-saas' no existe. Crealo primero.")
        conn.close()
        return

    tenant_id = tenant[0]
    print(f"✅ Tenant: {tenant[1]} (ID: {tenant_id}, Tier: {tenant[2]})")

    # 2. Limpiar datos anteriores
    cursor.execute("DELETE FROM historical_data WHERE tenant_id = ? AND sector = 'pharmacy'", (tenant_id,))
    deleted = cursor.rowcount
    conn.commit()
    print(f"🧹 Limpiados {deleted} registros anteriores")

    # 3. Productos de Farmacia
    products = [
        ("Ibuprofeno 400mg x 20",   1850.00),
        ("Paracetamol 500mg x 16",  1200.00),
        ("Amoxicilina 500mg x 12",  3500.00),
        ("Losartan 50mg x 30",      2800.00),
        ("Omeprazol 20mg x 14",     1650.00),
        ("Diclofenac 75mg x 10",    950.00),
        ("Enalapril 10mg x 30",     1400.00),
        ("Metformina 850mg x 30",   2100.00),
        ("Atorvastatina 20mg x 30", 3200.00),
        ("Cetirizina 10mg x 10",    780.00),
    ]

    # 4. Obtener el max ID actual para evitar conflictos
    cursor.execute("SELECT COALESCE(MAX(id), 0) FROM historical_data")
    max_id = cursor.fetchone()[0]
    next_id = max_id + 1

    now = datetime.utcnow()
    records = []

    for item_name, base_price in products:
        for day_offset in range(7, -1, -1):
            ts = now - timedelta(days=day_offset, hours=random.randint(0, 8))

            random.seed(hash(item_name) + day_offset)
            variation = random.uniform(-0.02, 0.03)
            price = round(base_price * (1 + variation * (7 - day_offset) / 7), 2)

            if day_offset == 0:
                competitor_price = round(base_price * 1.15, 2)
                meta = json.dumps({
                    "trend": "up",
                    "alert": True,
                    "intelligence_note": f"CRITICA: Competencia subio {item_name} a ${competitor_price} (+15%). Precio nuestro: ${price}.",
                    "competitor_price": competitor_price,
                    "our_price": price
                })
            elif day_offset <= 2:
                meta = json.dumps({
                    "trend": "opportunity",
                    "intelligence_note": f"ADVERTENCIA: Movimiento detectado en {item_name}."
                })
            else:
                meta = json.dumps({"trend": "stable"})

            records.append((next_id, tenant_id, "pharmacy", item_name, price, ts.strftime("%Y-%m-%d %H:%M:%S"), meta))
            next_id += 1

    # 5. Insertar todo de una
    cursor.executemany(
        "INSERT INTO historical_data (id, tenant_id, sector, item_key, price, timestamp, metadata_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
        records
    )
    conn.commit()
    print(f"✅ {len(records)} registros de Farmacia inyectados")
    print(f"💊 Productos: {len(products)}")
    print(f"📅 Período: últimos 7 días")

    # 6. Verificación
    cursor.execute("SELECT COUNT(*) FROM historical_data WHERE tenant_id = ? AND sector = 'pharmacy'", (tenant_id,))
    total = cursor.fetchone()[0]
    print(f"📊 Total registros pharmacy en DB: {total}")

    cursor.execute(
        "SELECT item_key, price, timestamp FROM historical_data WHERE tenant_id = ? AND sector = 'pharmacy' ORDER BY timestamp DESC LIMIT 3",
        (tenant_id,)
    )
    print(f"\n🔍 Últimos 3 registros:")
    for row in cursor.fetchall():
        print(f"   💊 {row[0]}: ${row[1]} @ {row[2]}")

    conn.close()
    print("\n✅ Seed completado exitosamente.")

if __name__ == "__main__":
    seed()
