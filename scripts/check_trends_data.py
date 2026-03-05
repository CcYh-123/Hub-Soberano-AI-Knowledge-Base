import sqlite3
import os

db_path = "data/antigravity.db"
if not os.path.exists(db_path):
    # Try looking for it from the root
    db_path = "c:/Users/Lenovo/Antigravity_Home/Proyecto_Antigravity/data/antigravity.db"

if not os.path.exists(db_path):
    print(f"Error: {db_path} not found")
    exit(1)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

print("--- Tenants ---")
try:
    cur.execute("SELECT id, slug FROM tenants")
    for row in cur.fetchall():
        print(row)
except Exception as e:
    print(f"Error querying tenants: {e}")

print("\n--- Summary by Tenant and Sector ---")
try:
    cur.execute("SELECT tenant_id, sector, COUNT(*) FROM historical_data GROUP BY tenant_id, sector")
    for row in cur.fetchall():
        print(row)
except Exception as e:
    print(f"Error querying historical_data summary: {e}")

print("\n--- Last 5 pharmacy records ---")
try:
    cur.execute("SELECT * FROM historical_data WHERE sector='pharmacy' ORDER BY timestamp DESC LIMIT 5")
    for row in cur.fetchall():
        print(row)
except Exception as e:
    print(f"Error querying historical_data details: {e}")

conn.close()
