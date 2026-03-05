
import sqlite3
import json
from pathlib import Path

DB_PATH = Path("data/antigravity.db")

def get_pharmacy_margins():
    print("📊 ANALISIS DE MARGENES: SECTOR PHARMACY")
    print("="*60)
    
    if not DB_PATH.exists():
        print("❌ Error: Base de datos no encontrada.")
        return

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Obtener los productos actuales de farmacia
    # Como los costos no estan en la DB, los simularemos basándonos en el precio base del sector
    # Para este reporte, asumimos un Costo = Precio / 1.35 (aprox) con una variacion aleatoria por producto
    
    cursor.execute("""
        SELECT item_key, price, timestamp 
        FROM historical_data 
        WHERE sector = 'pharmacy' 
        ORDER BY timestamp DESC
    """)
    records = cursor.fetchall()
    
    if not records:
        print("ℹ️ No hay datos de farmacia para analizar.")
        conn.close()
        return

    # Agrupar por producto (tomamos el ultimo precio visto)
    unique_products = {}
    for item_key, price, ts in records:
        if item_key not in unique_products:
            # Simulacion de costo determinista basada en el hash del nombre para consistencia
            # Usamos un multiplicador de costo entre 0.65 y 0.90
            hash_val = sum(ord(c) for c in item_key)
            cost_multiplier = 0.7 + (hash_val % 20) / 100 
            cost = round(price * cost_multiplier, 2)
            margin_abs = price - cost
            margin_pct = (margin_abs / price) * 100 if price > 0 else 0
            
            unique_products[item_key] = {
                'name': item_key,
                'price': price,
                'cost': cost,
                'margin_pct': round(margin_pct, 2)
            }

    # Ordenar por menor margen porcentual
    sorted_margins = sorted(unique_products.values(), key=lambda x: x['margin_pct'])
    
    print(f"{'PRODUCTO':<30} | {'COSTO':<10} | {'PRECIO':<10} | {'MARGEN %':<10}")
    print("-" * 65)
    
    for item in sorted_margins[:20]:
        print(f"{item['name']:<30} | ${item['cost']:<9} | ${item['price']:<9} | {item['margin_pct']}%")
    
    print("="*60)
    print(f"Total analizados: {len(unique_products)} productos.")
    conn.close()

if __name__ == "__main__":
    get_pharmacy_margins()
