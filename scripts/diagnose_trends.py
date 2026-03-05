import sqlite3
import os

db_path = "data/antigravity.db"
if not os.path.exists(db_path):
    db_path = "c:/Users/Lenovo/Antigravity_Home/Proyecto_Antigravity/data/antigravity.db"

if not os.path.exists(db_path):
    print(f"Error: {db_path} not found")
    exit(1)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

print("--- TENANTS (slug, id) ---")
try:
    cur.execute("SELECT slug, id FROM tenants")
    for row in cur.fetchall():
        print(row)
except Exception as e:
    print(f"Error querying tenants: {e}")

print("\n--- DATA (count, sector, tenant_id) ---")
try:
    cur.execute("SELECT COUNT(*), sector, tenant_id FROM historical_data GROUP BY sector, tenant_id")
    for row in cur.fetchall():
        print(row)
except Exception as e:
    print(f"Error querying historical_data: {e}")

print("\n--- SCHEMA (historical_data) ---")
try:
    cur.execute("PRAGMA table_info(historical_data)")
    for row in cur.fetchall():
        print(row)
except Exception as e:
    print(f"Error checking schema: {e}")

conn.close()
