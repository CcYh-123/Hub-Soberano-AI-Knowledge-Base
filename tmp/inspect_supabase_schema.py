"""
inspect_supabase_schema.py
==========================
Inspecciona las tablas disponibles en Supabase via REST API para
detectar el schema real de products y historical_data.
"""
import os, sys, json
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

import requests

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

tables = ["products", "historical_data", "profiles", "price_logs"]

for table in tables:
    url = f"{SUPABASE_URL}/rest/v1/{table}?limit=1"
    r = requests.get(url, headers=HEADERS)
    print(f"\n=== {table} (status {r.status_code}) ===")
    if r.status_code == 200:
        data = r.json()
        if data:
            print(f"  Columnas detectadas: {list(data[0].keys())}")
            print(f"  Ejemplo: {json.dumps(data[0], ensure_ascii=False)[:200]}")
        else:
            print("  Tabla vacía — sin columnas detectables via REST.")
    else:
        print(f"  ERROR: {r.text[:200]}")
