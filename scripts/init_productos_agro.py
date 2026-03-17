import sqlite3



from pathlib import Path



DB_PATH = Path(r"C:/Users/Lenovo/Documents/CURSO/database.db")


def ensure_productos_agro_table(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS productos_agro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            costo_reposicion REAL NOT NULL DEFAULT 0,
            precio_venta REAL NOT NULL DEFAULT 0,
            tenant_id TEXT NOT NULL
        )
        """
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_productos_agro_tenant "
        "ON productos_agro (tenant_id)"
    )
    conn.commit()


def migrate_from_todos_if_possible(conn: sqlite3.Connection) -> None:
    """
    Si existe una tabla 'todos' con alguna columna de texto tipo 'title' o 'text',
    crear filas iniciales en productos_agro usando esos nombres. Es opcional y
    no rompe si 'todos' no existe o tiene otra forma.
    """
    cur = conn.cursor()
    try:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='todos'")
        row = cur.fetchone()
        if not row:
            return
    except Exception:
        return

    cur.execute("PRAGMA table_info('todos')")
    cols = [c[1] for c in cur.fetchall()]
    text_col = None
    for candidate in ("title", "text", "nombre", "name"):
        if candidate in cols:
            text_col = candidate
            break

    if not text_col:
        return

    # Insertar solo si productos_agro está vacío, para no duplicar
    cur.execute("SELECT COUNT(1) FROM productos_agro")
    count = cur.fetchone()[0]
    if count:
        return

    tenant_id_default = "demo-local"
    cur.execute(f"SELECT {text_col} FROM todos")
    rows = cur.fetchall()
    for (nombre,) in rows:
        if not nombre:
            continue
        cur.execute(
            """
            INSERT INTO productos_agro (nombre, costo_reposicion, precio_venta, tenant_id)
            VALUES (?, 0, 0, ?)
            """,
            (str(nombre), tenant_id_default),
        )
    conn.commit()


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit(f"DB not found: {DB_PATH}")

    conn = sqlite3.connect(str(DB_PATH))
    try:
        ensure_productos_agro_table(conn)
        migrate_from_todos_if_possible(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()

