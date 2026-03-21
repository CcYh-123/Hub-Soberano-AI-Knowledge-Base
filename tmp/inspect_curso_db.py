import sqlite3
import os

db_path = r"C:/Users/Lenovo/Documents/CURSO/database.db"

def inspect():
    if not os.path.exists(db_path):
        print(f"DB not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # List tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cur.fetchall()]
    print(f"Tables in CURSO database: {tables}")

    for table in tables:
        print(f"\n--- Table: {table} ---")
        try:
            cur.execute(f"PRAGMA table_info('{table}');")
            cols = [c[1] for c in cur.fetchall()]
            query = f"SELECT * FROM '{table}'"
            cur.execute(query)
            rows = cur.fetchall()
            for row in rows:
                if any("Glifosato" in str(val) for val in row):
                    print(row)
        except Exception as e:
            print(f"Error searching in {table}: {e}")

    conn.close()

if __name__ == "__main__":
    inspect()
