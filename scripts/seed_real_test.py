import sqlite3
from pathlib import Path



def main():
    """
    Inyecta un producto de prueba en la base SQLite local
    para el sector agro.
    """
    base_dir = Path(__file__).resolve().parent.parent
    db_path = base_dir / "data" / "antigravity.db"

    print(f"[seed_real_test] Conectando a SQLite en: {db_path}")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Asegurarnos de que exista la tabla usada por MarginGuardian: `historical_data`
    # (es la que consulta scripts/margin_guardian.py)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS historical_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_key TEXT,
            price REAL,
            sector TEXT,
            tenant_id TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # Insertar registro de prueba en la tabla `historical_data`
    payload = {
        "item_key": "PRODUCTO_TEST_AGRO",
        "price": 1000,
        "sector": "agro",
        "tenant_id": "3947b9dc-7e89-4a05-a659-46e8ccdde558",
    }

    cur.execute(
        """
        INSERT INTO historical_data (item_key, price, sector, tenant_id)
        VALUES (:item_key, :price, :sector, :tenant_id)
        """,
        payload,
    )

    conn.commit()
    conn.close()

    print("✅ Producto de prueba inyectado")


if __name__ == "__main__":
    main()

