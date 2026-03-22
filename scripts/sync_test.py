import csv
import os
import requests
from dotenv import load_dotenv

# Cargamos entorno
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

CSV_PATH = "scripts/external_prices.csv"

def sync_data():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Error: Faltan credenciales en .env")
        return

    print("Iniciando Sincronizacion Tactica de Fase 5...")
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }

    try:
        with open(CSV_PATH, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                sku = row.get('sku')
                cost = float(row.get('cost', 0))
                price = float(row.get('price', 0))
                stock = float(row.get('stock', 0))
                
                print(f"Sincronizando: {sku} | Cost: {cost} | Stock: {stock}")
                
                headers["Prefer"] = "return=representation,resolution=merge-duplicates"
                
                # Actualización directa via Postgrest API Upsert
                # La tabla es 'products', la PK es 'name' (o similar)
                payload = {
                    "name": sku,
                    "cost_price": cost,
                    "price": price,
                    "stock": stock,
                    "user_id": "d0636a5b-d53a-4316-ba8a-5737c61c66a0"
                }
                
                url = f"{SUPABASE_URL}/rest/v1/products"
                resp = requests.post(url, headers=headers, json=payload)
                
                if resp.status_code in [200, 201, 204]:
                    print(f"Status: {sku} sincronizado con exito (Upsert).")
                else:
                    print(f"Error sincronizando {sku}: {resp.status_code} - {resp.text}")
                    
    except Exception as e:
        print(f"Error en sincronizacion: {e}")

if __name__ == "__main__":
    sync_data()
