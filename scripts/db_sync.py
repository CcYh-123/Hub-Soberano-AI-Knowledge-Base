import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TENANT_ID = "fa60ff74-574a-48a4-8ec9-074dde3746aa"
ORGANIZATION_ID = os.getenv("ORGANIZATION_ID", "kixnlqjuiqtodzdubydb") # Default org found in the remote Supabase project

def sync_high_impact_event():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Faltan credenciales de Supabase en .env")
        return

    print("🔄 Sincronizando evento de alto impacto (Farmacia) con Supabase...")
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    endpoint = f"{SUPABASE_URL}/rest/v1/historical_data"
    
    payload = {
        "tenant_id": TENANT_ID,
        "organization_id": ORGANIZATION_ID,
        "sector": "pharmacy",
        "item_key": "FARMACIA CENTRAL",
        "price": 12500.0,
        "timestamp": datetime.now().isoformat(),
        "metadata_json": {
            "trend": "critical",
            "intelligence_note": "CRÍTICA: OPORTUNIDAD FARMACIA SUPABASE - ALZA DE PRECIOS DETECTADA",
            "source": "db_sync"
        }
    }
    
    try:
        response = requests.post(endpoint, json=payload, headers=headers)
        if response.status_code in [201, 204]:
            print("✅ Evento subido a Supabase exitosamente.")
        else:
            print(f"❌ Error al subir a Supabase: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Excepción durante la sincronización: {e}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    sync_high_impact_event()
