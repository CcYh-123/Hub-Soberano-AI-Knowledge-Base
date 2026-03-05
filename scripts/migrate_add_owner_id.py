"""
Migración: Agrega la columna owner_id a la tabla tenants.
La tabla fue creada antes de que el modelo incluyera este campo.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "antigravity.db"

def migrate():
    print(f"📦 Conectando a: {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Verificar si la columna ya existe
    cursor.execute("PRAGMA table_info(tenants)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"   Columnas actuales: {columns}")

    if "owner_id" not in columns:
        print("   ➕ Agregando columna 'owner_id'...")
        cursor.execute("ALTER TABLE tenants ADD COLUMN owner_id TEXT")
        conn.commit()
        print("   ✅ Columna 'owner_id' agregada exitosamente.")
    else:
        print("   ✅ Columna 'owner_id' ya existe.")

    # Verificar estado final
    cursor.execute("PRAGMA table_info(tenants)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"   Columnas finales: {columns}")

    # Mostrar tenants existentes
    cursor.execute("SELECT id, slug, subscription_tier FROM tenants")
    tenants = cursor.fetchall()
    print(f"\n   📋 Tenants existentes ({len(tenants)}):")
    for t in tenants:
        print(f"      {t[1]} (tier: {t[2]}, id: {t[0][:8]}...)")

    conn.close()
    print("\n✅ Migración completada.")

if __name__ == "__main__":
    migrate()
