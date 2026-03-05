# scripts/debug_schema.py
import sqlite3
from pathlib import Path

conn = sqlite3.connect(Path('data/antigravity.db'))

tablas = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
for t in tablas:
    print(f'\nTABLA: {t[0]}')
    cols = conn.execute(f"PRAGMA table_info({t[0]})").fetchall()
    for c in cols:
        print(f'  col {c[0]}: {c[1]} ({c[2]})')
    muestra = conn.execute(f'SELECT * FROM {t[0]} LIMIT 2').fetchall()
    print(f'  MUESTRA: {muestra}')

conn.close()
