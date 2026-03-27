"""
seed_agro_supabase.py  (v2 — schema-aware)
==========================================
1. Inserta/actualiza SKUs AGRO en la tabla `products` (schema real: name, cost_price, price, stock, unit_type).
2. Corre MarginGuardian para calcular gaps de ganancia.
3. Sube los mártires a `historical_data` con organization_id y tenant_id correctos.

Requiere: SUPABASE_URL, SUPABASE_KEY (anon o service_role) en .env
"""

import os
import sys
import json
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

SUPABASE_URL  = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY  = os.environ.get("SUPABASE_KEY", "")  # anon key (lectura/escritura con RLS)
SERVICE_KEY   = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
ORGANIZATION_ID = os.environ.get("ORGANIZATION_ID", "antigravity")

# Para writes, prioriza service_role si está disponible y válida
WRITE_KEY = SERVICE_KEY if (SERVICE_KEY and "REEMPLAZAR" not in SERVICE_KEY) else SUPABASE_KEY
WRITE_MODE = "service_role" if WRITE_KEY == SERVICE_KEY else "anon"

print(f"[seed_agro] SUPABASE_URL:      {bool(SUPABASE_URL)}")
print(f"[seed_agro] WRITE_KEY mode:    {WRITE_MODE}")
print(f"[seed_agro] ORGANIZATION_ID:   {ORGANIZATION_ID}")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Faltan SUPABASE_URL o SUPABASE_KEY en .env")
    sys.exit(1)

import requests

# Headers base (lectura - anon)
READ_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# Headers escritura (service_role si disponible)
WRITE_HEADERS = {
    "apikey": WRITE_KEY,
    "Authorization": f"Bearer {WRITE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates",
}

# ─────────────────────────────────────────────────────────────────────────────
# CATÁLOGO AGRO realista (schema products: name, cost_price, price, stock, unit_type)
# Los precios de venta son los actuales (mercado); cost_price = costo de reposición
# ─────────────────────────────────────────────────────────────────────────────
AGRO_SKUS = [
    # name                        cost_price   price    stock   unit_type
    ("Glifosato x1L",              3200.0,     3490.0,  1200,   "Litros"),
    ("Glifosato x5L",             14500.0,    15800.0,   350,   "Litros"),
    ("Glifosato x20L",            54000.0,    56000.0,    80,   "Litros"),
    ("Atrazina x1L",               2800.0,     2950.0,   300,   "Litros"),
    ("Atrazina x5L",              12500.0,    13200.0,   120,   "Litros"),
    ("2,4-D x1L",                  1900.0,     2100.0,   450,   "Litros"),
    ("2,4-D x5L",                  8500.0,     8800.0,   200,   "Litros"),
    ("Clorpirifos x1L",            4100.0,     4300.0,   180,   "Litros"),
    ("Lambdacialotrina x1L",       5600.0,     5750.0,    90,   "Litros"),
    ("Urea x50kg",                18000.0,    19500.0,   500,   "Bolsas"),
    ("Fertilizante NPK",          22000.0,    23000.0,   200,   "Bolsas"),
]

# TENANT_ID del demo-saas (corresponde al perfil en Supabase)
TENANT_ID = "3947b9dc-7e89-4a05-a659-46e8ccdde558"


def upsert_products():
    """Inserta/actualiza los productos AGRO en Supabase con el schema real."""
    url = f"{SUPABASE_URL}/rest/v1/products"
    rows = [
        {
            "name":       name,
            "cost_price": cost,
            "price":      price,
            "stock":      stock,
            "unit_type":  unit,
        }
        for name, cost, price, stock, unit in AGRO_SKUS
    ]

    print(f"\n[PASO 1] Upserting {len(rows)} SKUs AGRO en Supabase (tabla: products)...")
    resp = requests.post(url, headers=WRITE_HEADERS, json=rows)

    if resp.status_code in (200, 201, 204):
        print(f"  OK: {len(rows)} productos insertados/actualizados.")
        return True
    else:
        print(f"  WARN: Upsert respondio {resp.status_code}: {resp.text[:250]}")
        # Intentar sin merge-duplicates (insert simple de los que falten)
        ok = 0
        for row in rows:
            # Intentar update primero
            upd_url = f"{SUPABASE_URL}/rest/v1/products?name=eq.{requests.utils.quote(row['name'])}"
            r = requests.patch(upd_url, headers={**WRITE_HEADERS, "Prefer": "return=minimal"}, json=row)
            if r.status_code in (200, 204):
                ok += 1
            else:
                # Intentar insert
                r2 = requests.post(url, headers={**WRITE_HEADERS, "Prefer": "return=minimal"}, json=row)
                if r2.status_code in (200, 201, 204):
                    ok += 1
                else:
                    print(f"  SKIP {row['name']}: {r2.status_code}")
        print(f"  Insertados/actualizados: {ok}/{len(rows)}")
        return ok > 0


def run_margin_guardian():
    """Ejecuta el MarginGuardian y retorna el resultado."""
    print(f"\n[PASO 2] Ejecutando MarginGuardian...")
    sys.path.insert(0, str(ROOT / "scripts"))

    try:
        from margin_guardian import MarginGuardian
        guardian = MarginGuardian()
        result = guardian.run()
        return result
    except Exception as e:
        print(f"  ERROR ejecutando MarginGuardian: {e}")
        import traceback
        traceback.print_exc()
        return None


def upload_to_historical_data(martyrs: list):
    """
    Sube los martires a historical_data con el schema correcto:
    tenant_id, organization_id, sector, item_key, price, timestamp, metadata_json
    """
    if not martyrs:
        print("\n[PASO 3] Sin martires para subir.")
        return

    url = f"{SUPABASE_URL}/rest/v1/historical_data"
    now = datetime.now(timezone.utc).isoformat()

    rows = []
    for m in martyrs:
        rows.append({
            "tenant_id":       TENANT_ID,
            "organization_id": ORGANIZATION_ID,
            "sector":          "agro",
            "item_key":        m.get("sku", ""),
            "price":           m.get("price", 0),
            "timestamp":       now,
            "metadata_json": {
                "intelligence_note": (
                    f"Margen {m.get('margin', 0):.1f}% | "
                    f"Gap ${m.get('gap', 0):,.0f} | "
                    f"Sugerido ${m.get('suggested_price', 0):,.0f}"
                ),
                "margin":          m.get("margin"),
                "gap":             m.get("gap"),
                "suggested_price": m.get("suggested_price"),
                "level":           m.get("level"),
                "trend":           "down" if (m.get("margin", 0) or 0) < 15 else "neutral",
                "cost_supa":       m.get("cost_supa"),
                "stock":           m.get("stock"),
            }
        })

    print(f"\n[PASO 3] Subiendo {len(rows)} registros a historical_data...")
    resp = requests.post(url, headers=WRITE_HEADERS, json=rows)

    if resp.status_code in (200, 201, 204):
        print(f"  OK: {len(rows)} registros subidos correctamente.")
    else:
        print(f"  ERROR {resp.status_code}: {resp.text[:400]}")
        if "42501" in resp.text:
            print("""
  TIP: RLS bloqueando escritura con anon key.
  Para resolver:
    1. Ve a Supabase > Table Editor > historical_data > RLS Policies
    2. Agrega una policy: "Allow inserts from service role"
    O bien agrega tu SUPABASE_SERVICE_ROLE_KEY al .env
""")


def main():
    print("=" * 60)
    print("  ANTIGRAVITY — AGRO SEEDER + MARGIN GUARDIAN v2")
    print("=" * 60)

    upsert_products()
    result = run_margin_guardian()

    if not result:
        print("\nERROR: Guardian no pudo ejecutarse.")
        sys.exit(1)

    martyrs = result.get("martyrs", [])

    print(f"\n{'=' * 60}")
    print(f"  RESUMEN FINAL")
    print(f"{'=' * 60}")
    print(f"  Martires detectados:  {len(martyrs)}")
    print(f"  Gap total:            ${result.get('total_gap', 0):,.2f}")
    print(f"  Status:               {result.get('status', 'N/A')}")
    print(f"{'=' * 60}")

    upload_to_historical_data(martyrs)

    print("\n LISTO. Si la subida fue OK, refresca el Dashboard en Vercel.")


if __name__ == "__main__":
    main()
