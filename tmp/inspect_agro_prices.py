import sqlite3
import os

db_path = r"c:\Users\Lenovo\Antigravity_Home\Proyecto_Antigravity\data\antigravity.db"

def inspect():
    if not os.path.exists(db_path):
        print(f"DB not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # List tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cur.fetchall()]
    print(f"Tables: {tables}")

    for table in tables:
        print(f"\n--- Table: {table} ---")
        try:
            cur.execute(f"PRAGMA table_info({table});")
            cols = [c[1] for c in cur.fetchall()]
            query = f"SELECT * FROM {table} WHERE " + " OR ".join([f"CAST({c} AS TEXT) LIKE '%Glifosato%'" for c in cols])
            cur.execute(query)
            rows = cur.fetchall()
            for row in rows:
                print(row)
        except Exception as e:
            print(f"Error searching in {table}: {e}")

    conn.close()

if __name__ == "__main__":
    inspect()
