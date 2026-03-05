
import sqlite3
from pathlib import Path
import os
import sys

# Añadir scripts al path
sys.path.append(os.path.join(os.getcwd(), "scripts"))

from core.database import init_db

DB_PATH = Path("data/antigravity.db")

def reset_table():
    print(f"🔄 Reseteando tabla historical_data en {DB_PATH}...")
    
    if not DB_PATH.exists():
        print("ℹ️ La DB no existe aún. Ejecutando init_db normal.")
        init_db()
        return

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # Drop table to force recreation with new schema (Integer ID)
        cursor.execute("DROP TABLE IF EXISTS historical_data")
        conn.commit()
        print("✅ Tabla historical_data eliminada.")
    finally:
        conn.close()
    
    # Re-initialize
    init_db()
    print("✨ Tabla recreateda con el nuevo esquema de autoincremento.")

if __name__ == "__main__":
    reset_table()
