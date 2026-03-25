import requests
import time
import os
from datetime import datetime
from dotenv import load_dotenv

# Cargar configuración
load_dotenv()

# URLs de monitoreo
RENDER_URL = "https://antigravity-backend-e770.onrender.com/api/health"
SUPABASE_URL = "https://ijzazwdgtxsosiibjoj.supabase.co"

def check_endpoint(name, url):
    try:
        # Timeout de 10 segundos para no bloquear el script
        response = requests.get(url, timeout=10)
        
        # Para Supabase, un 404 suele ser normal si no se especifica endpoint REST, 
        # pero indica que el host está vivo. Para Render esperamos 200.
        if response.status_code < 500:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ {name}: Conexión exitosa ({response.status_code})")
            return True
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ {name}: Error de servidor ({response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ {name}: Caído o inaccesible - Error: {type(e).__name__}")
        return False

def monitor():
    print("🚀 Iniciando Monitor de Red Antigravity (Intervalo: 30s)")
    print(f"📡 Monitoreando Render: {RENDER_URL}")
    print(f"📡 Monitoreando Supabase: {SUPABASE_URL}")
    print("-" * 60)
    
    try:
        while True:
            check_endpoint("RENDER  ", RENDER_URL)
            check_endpoint("SUPABASE", SUPABASE_URL)
            print("-" * 60)
            time.sleep(30)
    except KeyboardInterrupt:
        print("\n🛑 Monitoreo detenido por el usuario.")

if __name__ == "__main__":
    monitor()
