
import sqlite3
from pathlib import Path

DB_PATH = Path("data/antigravity.db")

def inspect_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(historical_data)")
    columns = cursor.fetchall()
    for col in columns:
        print(col)
    conn.close()

if __name__ == "__main__":
    inspect_schema()
