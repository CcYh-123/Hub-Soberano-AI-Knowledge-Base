import os
from dotenv import load_dotenv
from supabase import create_client

# 1. Conectamos con las llaves del archivo .env
load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def agregar_producto(nombre, precio, stock):
    """Función para subir un producto a la nube"""
    try:
        item = {
            "name": nombre, 
            "price": precio, 
            "stock": stock
        }
        # Enviamos a la tabla 'products'
        resultado = supabase.table("products").insert(item).execute()
        print(f"✅ ¡Subido con éxito!: {nombre} (${precio})")
        return resultado
    except Exception as e:
        print(f"❌ Error al subir {nombre}: {e}")

# --- SECCIÓN DE CARGA ---
# Aquí podés agregar todos los que quieras:
agregar_producto("Amoxicilina 500mg", 3450.00, 25)
agregar_producto("Buscapina Fem", 1890.50, 15)
agregar_producto("Sertal Compuesto", 2200.00, 40)