import random
import requests
import json

# Configuración de Conexión
SUPABASE_URL = "https://ijzazdwdgtxsosiibjoj.supabase.co"
SUPABASE_KEY = "sb_publishable_8PjB5UfXcJAf5MbtvDizlQ_xcH4mEQO"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

def seed_agro_data():
    print(f"--- INICIANDO CARGA DE 1200 MÁRTIRES ---")
    
    products_list = []
    names = ["Herbicida Glifosato", "Fertilizante Premium X", "Insecticida Control Total", "Fungicida Power", "Acondicionador de Suelo", "Nutriente Foliar Z"]
    units = ["20L", "50kg", "10L", "5L", "100kg"]
    types = ["Litros", "Bidones"]

    for i in range(1200):
        name = f"{random.choice(names)} {random.choice(units)} #{i+1}"
        cost = round(random.uniform(30.0, 60.0), 2)
        # Algunos con margen bajo para activar alertas
        price = round(cost * random.uniform(1.10, 1.50), 2) 
        stock = random.randint(10, 500)
        unit_type = random.choice(types)

        products_list.append({
            "name": name,
            "price": price,
            "cost_price": cost,
            "stock": stock,
            "unit_type": unit_type
        })

    # Inserción por lotes de 100 para evitar timeouts
    batch_size = 100
    for i in range(0, len(products_list), batch_size):
        batch = products_list[i:i + batch_size]
        response = requests.post(f"{SUPABASE_URL}/rest/v1/products", headers=HEADERS, data=json.dumps(batch))
        if response.status_code in [200, 201]:
            print(f"Lote {i//batch_size + 1} insertado correctamente.")
        else:
            print(f"Error en lote {i//batch_size + 1}: {response.text}")

if __name__ == "__main__":
    seed_agro_data()

