import os
import csv
from dotenv import load_dotenv
from supabase import create_client

# Colores para terminal
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def cargar_desde_csv(archivo_csv="stock_farmacia.csv"):
    # 1. Configuración de Supabase
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Error: Faltan credenciales en el archivo .env")
        return

    supabase = create_client(url, key)

    print(f"\n{BLUE}--- PROCESADOR DE CARGA MASIVA ---{RESET}")
    
    if not os.path.exists(archivo_csv):
        print(f"❌ Error: No se encuentra el archivo {archivo_csv}")
        return

    productos_a_subir = []
    
    # 2. Lectura del CSV
    try:
        with open(archivo_csv, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    producto = {
                        "name": row['name'],
                        "price": float(row['price']),
                        "stock": int(row['stock'])
                    }
                    productos_a_subir.append(producto)
                except ValueError as ve:
                    print(f"⚠️ Saltando fila inválida ({row.get('name')}): {ve}")

        if not productos_a_subir:
            print("💡 No se encontraron productos válidos para subir.")
            return

        # 3. Subida masiva (Bulk Insert)
        print(f"📦 Subiendo {len(productos_a_subir)} productos a Supabase...")
        
        # Insertamos toda la lista de una sola vez
        resultado = supabase.table("products").insert(productos_a_subir).execute()
        
        print(f"✅ {GREEN}¡Éxito!{RESET} Se cargaron {len(productos_a_subir)} productos correctamente.")
        
    except Exception as e:
        print(f"❌ Error inesperado durante la carga: {e}")

if __name__ == "__main__":
    cargar_desde_csv()
