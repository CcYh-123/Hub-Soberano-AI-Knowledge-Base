
import sqlite3
import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("data")
DB_PATH = DATA_DIR / "antigravity.db"

def run_strategic_simulation(tenant_slug):
    if not DB_PATH.exists():
        return "Database not found"

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get tenant ID
    cursor.execute("SELECT id FROM tenants WHERE slug = ?", (tenant_slug,))
    tenant = cursor.fetchone()
    if not tenant:
        conn.close()
        return "Tenant not found"
    
    tenant_id = tenant[0]

    # Simulation Logic
    total_profit_delta = 3600 # 12000 - 6400 - 2000
    
    pharmacy_impact = {"sector": "pharmacy", "factor": "Price +12%", "profit_delta": 12000, "note": "Margen blindado."}
    fashion_impact = {"sector": "fashion", "factor": "Volume -8%", "profit_delta": -6400, "note": "Caída estacional."}
    re_impact = {"sector": "real_estate", "factor": "Marketing +$2,000", "profit_delta": -2000, "note": "Inversión MKT."}

    simulation_metadata = {
        "alert": "STRATEGIC_DECISION",
        "indicator": "🧠",
        "title": "ALERTA DE DECISIÓN: IMPACTO ROI GLOBAL",
        "analysis": f"Net Profit Delta: +${total_profit_delta}. El alza en Farmacia absorbe el impacto negativo en Moda.",
        "sectors": [pharmacy_impact, fashion_impact, re_impact],
        "recommendation": "Proceder con el incremento de precios en Farmacia para blindar rentabilidad del mes.",
        "simulation_timestamp": datetime.now().isoformat(),
        "db_status": "Persisted_Direct_v2"
    }

    # Get MAX ID to handle manual increment if autoincrement failed
    cursor.execute("SELECT MAX(id) FROM historical_data")
    max_id = cursor.fetchone()[0]
    next_id = (max_id or 0) + 1

    # Insert Alert
    cursor.execute("""
        INSERT INTO historical_data (id, tenant_id, sector, item_key, price, timestamp, metadata_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        next_id,
        tenant_id, 
        "global", 
        "DECISION_ALERT_SIMULATION", 
        float(total_profit_delta), 
        datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        json.dumps(simulation_metadata)
    ))

    conn.commit()
    conn.close()
    
    with open("temp_sim_result.json", "w", encoding="utf-8") as f:
        json.dump(simulation_metadata, f, indent=2)
        
    return simulation_metadata

if __name__ == "__main__":
    result = run_strategic_simulation("demo-saas")
    print(json.dumps(result, indent=2))
