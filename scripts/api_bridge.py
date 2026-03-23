"""
Antigravity API Bridge — sin supabase-py (evita storage3, pyiceberg, deps C++).
Usa requests + PostgREST (REST API nativa de Supabase).
Ejecutar: py scripts/api_bridge.py  →  uvicorn en puerto 8000 por defecto.
"""
from __future__ import annotations

import csv
import os
from typing import Any

import requests
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

SUPABASE_URL = (os.environ.get("SUPABASE_URL") or "").rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY") or ""

app = FastAPI(
    title="Antigravity API Bridge - Phase 5 Fuel",
    description="Sincronizador Maestro — Motor Martir de Volumen (REST puro)",
    version="0.8.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _headers() -> dict[str, str]:
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Prefer": "return=representation",
    }


def rest_get_products() -> list[dict[str, Any]]:
    """GET /rest/v1/products?select=*"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return []
    url = f"{SUPABASE_URL}/rest/v1/products"
    r = requests.get(url, params={"select": "*"}, headers=_headers(), timeout=60)
    r.raise_for_status()
    data = r.json()
    return data if isinstance(data, list) else []


def rest_patch_product_by_name(name: str, fields: dict[str, Any]) -> list[dict[str, Any]]:
    """PATCH .../products?name=eq.<name>"""
    url = f"{SUPABASE_URL}/rest/v1/products"
    r = requests.patch(
        url,
        params={"name": f"eq.{name}"},
        headers=_headers(),
        json=fields,
        timeout=60,
    )
    r.raise_for_status()
    if r.status_code == 204 or not (r.content and r.content.strip()):
        return []
    try:
        out = r.json()
    except ValueError:
        return []
    return out if isinstance(out, list) else []


def compute_martires(products_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Gap total = (sugerido - precio) * stock; umbral margen < 25%.
    """
    martires: list[dict[str, Any]] = []
    for p in products_rows:
        cost = float(p.get("cost_price") or 0)
        price = float(p.get("price") or 0)
        stock = float(p.get("stock") or 0)
        margin = ((price - cost) / price * 100) if price > 0 else 0.0
        suggested = cost * 1.30
        gap_unit = suggested - price
        gap_total = gap_unit * stock
        if margin < 25:
            martires.append(
                {
                    "sku": p.get("name") or "",
                    "cost_supa": cost,
                    "price": price,
                    "stock": stock,
                    "margin": round(margin, 2),
                    "gap": round(gap_total, 2),
                    "suggested_price": round(suggested, 2),
                }
            )
    return martires


def run_csv_sync() -> dict[str, Any]:
    """Lee external_prices.csv y actualiza filas en Supabase (POST /sync y startup)."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return {"error": "Supabase no configurado (SUPABASE_URL / SUPABASE_KEY)"}

    csv_path = os.path.join(os.path.dirname(__file__), "external_prices.csv")
    sync_results: list[dict[str, Any]] = []

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sku = row["sku"]
            new_cost = float(row["cost"])
            new_market = float(row["price"])
            new_stock = float(row["stock"])
            data = rest_patch_product_by_name(
                sku,
                {
                    "cost_price": new_cost,
                    "price": new_market,
                    "stock": new_stock,
                },
            )
            sync_results.append({"sku": sku, "status": "updated", "rows": data})
    return {"status": "success", "synced": sync_results}


@app.on_event("startup")
async def startup_event() -> None:
    print("[Fase 5] Iniciando sincronizacion de volumen automatica (REST)...")
    try:
        run_csv_sync()
        print("[Fase 5] Sincronizacion CSV completada.")
    except Exception as e:
        print(f"[Fase 5] Aviso startup sync: {e}")


@app.get("/")
async def root() -> dict[str, Any]:
    return {"status": "OK - Phase 5 Sync Active", "version": "0.8.0", "backend": "requests+PostgREST"}


@app.post("/sync")
async def sync_external_prices() -> dict[str, Any]:
    """Lee external_prices.csv y actualiza Supabase vía PATCH por nombre de producto."""
    try:
        return run_csv_sync()
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/get-martires")
async def get_martires_live() -> dict[str, Any]:
    """Mismos martires que antes; fuente REST."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return {"error": "No Supabase connection", "productos": []}
    try:
        rows = rest_get_products()
        martires = compute_martires(rows)
        return {"status": "ok", "fuente": "supabase_rest", "productos": martires}
    except Exception as e:
        return {"status": "error", "message": str(e), "productos": []}


@app.get("/get-agro-data")
async def get_agro_data() -> dict[str, Any]:
    """
    Datos AGRO desde la DB (misma lógica que /get-martires).
    total_bidones = suma de stock en productos críticos (ej. 1200 bidones Glifosato).
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        return {
            "status": "error",
            "message": "No Supabase connection",
            "productos": [],
            "total_bidones": 0,
        }
    try:
        rows = rest_get_products()
        martires = compute_martires(rows)
        total_bidones = int(sum(float(p.get("stock") or 0) for p in martires))
        return {
            "status": "ok",
            "fuente": "supabase_rest",
            "productos": martires,
            "total_bidones": total_bidones,
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "productos": [], "total_bidones": 0}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    print(f"Antigravity Bridge (Phase 5) en http://0.0.0.0:{port} — sin supabase-py")
    uvicorn.run(app, host="0.0.0.0", port=port)
