"""
api_bridge.py — Antigravity Bridge v0.6.0
Fase 5: Puente de Datos Local para el Motor Martir.
El celu le pide los precios a la Lenovo por Wi-Fi.
"""
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

load_dotenv()

app = FastAPI(
    title="Antigravity API Bridge",
    description="Puente de datos local — Motor Martir Fase 5",
    version="0.6.0",
)

# CORS: acepta peticiones del celu en la red local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware verbose: imprime cada peticion que llega al servidor
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest

class VerboseLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        client_ip = request.client.host if request.client else "desconocido"
        print(f"[PETICION] {request.method} {request.url.path} — desde {client_ip}")
        response = await call_next(request)
        print(f"[RESPUESTA] {response.status_code} para {request.url.path}")
        return response

app.add_middleware(VerboseLogMiddleware)

# ── PRODUCTOS MARTIRES (Fuente de Verdad Local - Calibracion Fase 3) ────────
# Margen = (Venta - Costo) / Venta * 100
MARTIRES = [
    {
        "id": 1,
        "nombre": "Glifosato Martir",
        "costo_reposicion": 105.00,
        "precio_venta": 135.00,
        "ganancia": 30.00,
        "margen_pct": round((135 - 105) / 135 * 100, 2),   # 22.22%
        "tenant_id": "tenant_agro_test",
    },
    {
        "id": 2,
        "nombre": "Fertilizante Urea",
        "costo_reposicion": 450.00,
        "precio_venta": 580.00,
        "ganancia": 130.00,
        "margen_pct": round((580 - 450) / 580 * 100, 2),   # 22.41%
        "tenant_id": "tenant_agro_test",
    },
]


# ── ENDPOINTS ────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    """Heartbeat — verifica que el bridge esta online."""
    return {"status": "OK - Antigravity Bridge Online", "version": "0.6.0"}


@app.get("/get-martires")
async def get_martires():
    """
    Fase 5 - Fuel: Devuelve los precios de los Martires al celular por Wi-Fi.
    El celu le pide los precios a la Lenovo — Handshake activado.
    """
    return JSONResponse(content={
        "status": "ok",
        "fuente": "local_calibrado",
        "total": len(MARTIRES),
        "productos": MARTIRES,
    })


@app.get("/data")
async def get_data():
    """Endpoint legacy — consulta Supabase si las credenciales estan disponibles."""
    try:
        from supabase import create_client  # import lazy para aislar el fallo
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if not url or not key:
            return {"error": "SUPABASE_URL o SUPABASE_KEY no configurados en .env"}
        client = create_client(url, key)
        response = client.table("dashboard_agro").select("*").execute()
        return response.data
    except ImportError:
        return {"error": "supabase-py no disponible en este entorno"}
    except Exception as e:
        return {"error": str(e)}


# ── ARRANQUE DINÁMICO (Cloud Run Compatible) ────────────────────────────────
if __name__ == "__main__":
    # Google Cloud Run inyecta la variable "PORT", localmente usamos 8000 si preferís
    port = int(os.environ.get('PORT', 8080))
    print(f"Antigravity Bridge arrancando en http://0.0.0.0:{port}")
    print(f"Para el Handshake local usá: http://<TU_IP_LOCAL>:{port}/get-martires")
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
