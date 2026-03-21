import sqlite3

def search_db(db_path, word):
    print(f"Buscando en {db_path}...")
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cur.fetchall()
        for table in tables:
            try:
                cur.execute(f"SELECT * FROM {table[0]}")
                rows = cur.fetchall()
                for row in rows:
                    if word.lower() in str(row).lower() or '06/03' in str(row) or '03-06' in str(row) or '06-03' in str(row):
                        print(f"Table: {table[0]} - Row: {row}")
            except Exception as e:
                print(f"Skip table {table[0]}: {e}")
    except Exception as e:
        print(f"No se pudo leer {db_path}: {e}")

search_db('C:/Users/Lenovo/Antigravity_Home/Proyecto_Antigravity/data/antigravity.db', 'glifosato')
search_db('C:/Users/Lenovo/Documents/CURSO/database.db', 'glifosato')
search_db('C:/Users/Lenovo/Documents/CURSO/database.db', '06')
