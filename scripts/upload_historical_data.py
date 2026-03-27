"""
upload_historical_data.py — PASO 3 standalone
===============================================
Sube los mártires AGRO directamente a historical_data en Supabase.
Usa la SUPABASE_SERVICE_ROLE_KEY para bypasear RLS.

Ejecutar: python scripts/upload_historical_data.py
"""

import os
import sys
import json
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

SUPABASE_URL      = os.environ.get("SUPABASE_URL", "")
SERVICE_ROLE_KEY  = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
ANON_KEY          = os.environ.get("SUPABASE_KEY", "")
ORGANIZATION_ID   = os.environ.get("ORGANIZATION_ID", "antigravity")
TENANT_ID         = "fa60ff74-574a-48a4-8ec9-074dde3746aa"  # demo-saas (real)

# Validación de la key
USE_KEY = SERVICE_ROLE_KEY
if not USE_KEY or "REEMPLAZAR" in USE_KEY:
    print("WARN: SERVICE_ROLE_KEY no configurada. Usando anon key (puede fallar por RLS).")
    USE_KEY = ANON_KEY
    key_type = "anon"
else:
    key_type = "service_role"

print(f"[upload] SUPABASE_URL:     {bool(SUPABASE_URL)}")
print(f"[upload] Key type:         {key_type}")
print(f"[upload] ORGANIZATION_ID:  {ORGANIZATION_ID}")
print()

if not SUPABASE_URL or not USE_KEY:
    print("ERROR: Faltan SUPABASE_URL o keys en .env")
    sys.exit(1)

import requests

HEADERS = {
    "apikey":        USE_KEY,
    "Authorization": f"Bearer {USE_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=representation",
}

# ─────────────────────────────────────────────────────────────────────────────
# Mártires AGRO — resultado real del MarginGuardian (última ejecución)
# + los nuevos SKUs que aún no están en historical_data
# ─────────────────────────────────────────────────────────────────────────────
NOW = datetime.now(timezone.utc).isoformat()

MARTYRS = [
    {
        "sku":             "Glifosato Martir",
        "price":           105.0,
        "cost_supa":       110.0,
        "margin":          -7.35,
        "gap":             67228.21,
        "suggested_price": 161.02,
        "level":           "CRITICO",
        "stock":           3290.0,
    },
    # Nuevos SKUs seeded en products — cargamos como alertas preventivas
    {
        "sku":             "Glifosato x1L",
        "price":           3490.0,
        "cost_supa":       3200.0,
        "margin":          8.31,
        "gap":             (3490.0 / 0.70 - 3490.0) * 1200,  # gap hacia margen 30%
        "suggested_price": round(3200.0 / 0.70, 2),
        "level":           "CRITICO",
        "stock":           1200,
    },
    {
        "sku":             "Glifosato x5L",
        "price":           15800.0,
        "cost_supa":       14500.0,
        "margin":          8.23,
        "gap":             (15800.0 / 0.70 - 15800.0) * 350,
        "suggested_price": round(14500.0 / 0.70, 2),
        "level":           "CRITICO",
        "stock":           350,
    },
    {
        "sku":             "Atrazina x1L",
        "price":           2950.0,
        "cost_supa":       2800.0,
        "margin":          5.08,
        "gap":             (2950.0 / 0.70 - 2950.0) * 300,
        "suggested_price": round(2800.0 / 0.70, 2),
        "level":           "CRITICO",
        "stock":           300,
    },
    {
        "sku":             "2,4-D x1L",
        "price":           2100.0,
        "cost_supa":       1900.0,
        "margin":          9.52,
        "gap":             (2100.0 / 0.70 - 2100.0) * 450,
        "suggested_price": round(1900.0 / 0.70, 2),
        "level":           "CRITICO",
        "stock":           450,
    },
    {
        "sku":             "Urea x50kg",
        "price":           19500.0,
        "cost_supa":       18000.0,
        "margin":          7.69,
        "gap":             (19500.0 / 0.70 - 19500.0) * 500,
        "suggested_price": round(18000.0 / 0.70, 2),
        "level":           "CRITICO",
        "stock":           500,
    },
]

def build_rows(martyrs: list) -> list:
    rows = []
    for m in martyrs:
        gap = m.get("gap", 0)
        margin = m.get("margin", 0)
        rows.append({
            "tenant_id":       TENANT_ID,
            "organization_id": ORGANIZATION_ID,
            "sector":          "agro",
            "item_key":        m["sku"],
            "price":           m.get("price", 0),
            "timestamp":       NOW,
            "metadata_json": {
                "intelligence_note": (
                    f"Margen {margin:.1f}% | "
                    f"Gap ${gap:,.0f} | "
                    f"Sugerido ${m.get('suggested_price', 0):,.0f}"
                ),
                "margin":          margin,
                "gap":             gap,
                "suggested_price": m.get("suggested_price"),
                "level":           m.get("level"),
                "cost_supa":       m.get("cost_supa"),
                "stock":           m.get("stock"),
                "trend":           "down",
            },
        })
    return rows


def upload(rows: list) -> bool:
    url = f"{SUPABASE_URL}/rest/v1/historical_data"
    print(f"Subiendo {len(rows)} registros a historical_data...")
    resp = requests.post(url, headers=HEADERS, json=rows)
    if resp.status_code in (200, 201, 204):
        print(f"  OK [{resp.status_code}] — {len(rows)} filas insertadas.")
        # Mostrar IDs asignados si el response los devuelve
        try:
            data = resp.json()
            if data:
                ids = [str(r.get("id", "?")) for r in data]
                print(f"  IDs asignados: {', '.join(ids)}")
        except Exception:
            pass
        return True
    else:
        print(f"  ERROR {resp.status_code}: {resp.text[:400]}")
        if "42501" in resp.text:
            print("""
  RLS sigue bloqueando. Verifica que:
  1. La SUPABASE_SERVICE_ROLE_KEY en .env no tenga espacios ni saltos de linea.
  2. El valor empieza con 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' (JWT largo).
""")
        return False


def main():
    print("=" * 60)
    print("  ANTIGRAVITY — UPLOAD HISTORICAL_DATA (PASO 3)")
    print("=" * 60)

    rows = build_rows(MARTYRS)
    success = upload(rows)

    if success:
        print("""
INSERCION EXITOSA.
  - historical_data tiene los registros AGRO actualizados.
  - El dashboard en Vercel mostrara las alertas al refrescar.
""")
    else:
        print("""
La insercion fallo. Verifica la SERVICE_ROLE_KEY en .env
y vuelve a ejecutar: python scripts/upload_historical_data.py
""")


if __name__ == "__main__":
    main()
