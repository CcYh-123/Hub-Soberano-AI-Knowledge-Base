import os
from dotenv import load_dotenv
from supabase import create_client
from tabulate import tabulate

# Configuración de colores para terminal
GREEN = "\033[92m"
BLUE = "\033[94m"
RESET = "\033[0m"

def buscar_remedio():
    # 1. Cargamos entorno y cliente Supabase
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Error: No se encontraron las credenciales en el archivo .env")
        return

    supabase = create_client(url, key)

    print(f"\n{BLUE}--- BUSCADOR DE SOBERANÍA ---{RESET}")
    nombre_buscado = input("🔍 Ingresá el nombre del remedio a buscar: ").strip()

    if not nombre_buscado:
        print("💡 Por favor, ingresá un nombre válido.")
        return

    try:
        # 2. Consultamos la base de datos con un filtro de similitud
        # Usamos ilike para que no importe mayúsculas/minúsculas
        response = supabase.table("products").select("*").ilike("name", f"%{nombre_buscado}%").execute()
        
        datos = response.data

        if not datos:
            print(f"\n❌ No se encontró ningún remedio que contenga '{nombre_buscado}'.")
        else:
            # 3. Formateamos para tabulate
            tabla = []
            for item in datos:
                tabla.append([
                    item.get("id", "N/A"),
                    item.get("name", "Sin nombre"),
                    f"${item.get('price', 0):,.2f}",
                    f"{item.get('stock', 0)} unidades"
                ])
            
            headers = ["ID", "Producto", "Precio", "Stock"]
            
            print(f"\n{GREEN}Resultados encontrados:{RESET}")
            print(tabulate(tabla, headers=headers, tablefmt="fancy_grid"))
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    buscar_remedio()
