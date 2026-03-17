import re



import sqlite3
from pathlib import Path




KEYWORDS_RE = re.compile(
    r"(producto|product|sku|item|articulo|costo|cost|precio|price|venta|pvp|unit|internal)",
    re.IGNORECASE,
)


def main() -> None:
    db_path = Path(r"C:/Users/Lenovo/Documents/CURSO/database.db")
    if not db_path.exists():
        raise SystemExit(f"DB not found: {db_path}")

    con = sqlite3.connect(str(db_path))
    cur = con.cursor()

    cur.execute(
        "select name, type from sqlite_master "
        "where type in ('table','view') and name not like 'sqlite_%' "
        "order by type, name"
    )
    objs = cur.fetchall()
    print(f"OBJECTS ({len(objs)})")
    for name, typ in objs:
        print(f"{typ}\t{name}")

    cur.execute(
        "select name from sqlite_master where type='table' and name not like 'sqlite_%' order by name"
    )
    tbls = [r[0] for r in cur.fetchall()]

    print("\nTABLE_COLUMNS")
    for t in tbls:
        cur.execute(f"pragma table_info('{t}')")
        cols = [c[1] for c in cur.fetchall()]
        hits = [c for c in cols if KEYWORDS_RE.search(c or "")]
        if hits:
            print(f"{t}: {', '.join(cols)}")
            print(f"  HIT => {', '.join(hits)}")

    print("\nDDL_KEYWORD_MATCHES")
    cur.execute(
        "select name, sql from sqlite_master "
        "where type in ('table','view') and name not like 'sqlite_%' "
        "order by type, name"
    )
    for name, sql in cur.fetchall():
        if not sql:
            continue
        sql_l = sql.lower()
        if any(k in sql_l for k in ["precio", "price", "costo", "cost", "sku", "product", "producto", "item"]):
            print(f"--- {name} ---")
            print(sql)

    con.close()


if __name__ == "__main__":
    main()

