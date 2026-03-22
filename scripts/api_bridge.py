import os
import csv
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from supabase import create_client
import uvicorn

load_dotenv()

app = FastAPI(
    title="Antigravity API Bridge - Phase 5 Fuel",
    description="Sincronizador Maestro — Motor Martir de Volumen",
    version="0.7.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── SUPABASE CLIENT ──────────────────────────────────────────────────────────
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key) if url and key else None

# ── ENDPOINTS ────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"status": "OK - Phase 5 Sync Active", "version": "0.7.0"}

@app.post("/sync")
async def sync_external_prices():
    """
    Lee external_prices.csv y actualiza Supabase: cost_price y market_price.
    Fase 5: Combustible de Datos.
    """
    if not supabase:
        return {"error": "Supabase no configurado"}
    
    csv_path = os.path.join(os.path.dirname(__file__), "external_prices.csv")
    sync_results = []
    
    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                sku = row['sku']
                new_cost = float(row['cost_price'])
                new_market = float(row['market_price'])
                
                # Sincronizar campo cost_price en la tabla products
                res = supabase.table("products").update({
                    "cost_price": new_cost,
                    "price": new_market  # Actualizamos el precio sugerido/venta
                }).eq("name", sku).execute()
                
                sync_results.append({"sku": sku, "status": "updated", "data": res.data})
        
        return {"status": "success", "synced": sync_results}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/get-martires")
async def get_martires_live():
    """
    Devuelve los martires directamente desde Supabase con calculo de Volumen.
    Gap Total = (Market_Price - Sale_Price) * Stock
    """
    if not supabase:
        return {"error": "No Supabase connection"}
    
    products = supabase.table("products").select("*").execute()
    martires = []
    for p in products.data:
        cost = float(p.get('cost_price') or 0)
        price = float(p.get('price') or 0)
        stock = float(p.get('stock') or 0)
        
        # Calculo de margen real
        margin = ((price - cost) / price * 100) if price > 0 else 0
        
        # En la Fase 5, el GAP es por volumen
        # Si el sugerido fuera un 30% arriba del costo...
        suggested = cost * 1.30
        gap_unit = suggested - price
        gap_total = gap_unit * stock
        
        if margin < 25: # Umbral de alerta
            martires.append({
                "sku": p['name'],
                "cost_supa": cost,
                "price": price,
                "stock": stock,
                "margin": round(margin, 2),
                "gap": round(gap_total, 2),
                "suggested_price": round(suggested, 2)
            })
            
    return {"status": "ok", "fuente": "supabase_live", "productos": martires}

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    print(f"Antigravity Bridge (Phase 5) en el puerto: {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
