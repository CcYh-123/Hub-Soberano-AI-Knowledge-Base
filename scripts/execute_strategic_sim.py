
import sys
import os
from pathlib import Path
import json
from datetime import datetime

# Añadir directorio actual al path
sys.path.append(str(Path(__file__).parent))

from core.database import SessionLocal, HistoricalData, Tenant

def run_strategic_simulation(tenant_slug):
    db = SessionLocal()
    try:
        tenant = db.query(Tenant).filter(Tenant.slug == tenant_slug).first()
        if not tenant:
            return "Tenant not found"

        # 1. Pharmacy (+12% Price)
        pharmacy_impact = {
            "sector": "pharmacy",
            "factor": "Price +12%",
            "profit_delta": 12000,
            "note": "Aumento proyectado en margen bruto."
        }

        # 2. Fashion (-8% Volume)
        fashion_impact = {
            "sector": "fashion",
            "factor": "Volume -8%",
            "profit_delta": -6400,
            "note": "Caída estacional proyectada."
        }

        # 3. Real Estate (+$2,000 Marketing)
        re_impact = {
            "sector": "real_estate",
            "factor": "Marketing +$2,000",
            "profit_delta": -2000,
            "note": "Inversión necesaria para visibilidad."
        }

        total_profit_delta = pharmacy_impact["profit_delta"] + fashion_impact["profit_delta"] + re_impact["profit_delta"]
        
        # Generate DECISION ALERT
        simulation_metadata = {
            "alert": "STRATEGIC_DECISION",
            "indicator": "🧠",
            "title": "ALERTA DE DECISIÓN: IMPACTO ROI GLOBAL",
            "analysis": f"Net Profit Delta: +${total_profit_delta}. El alza en Farmacia absorbe el impacto negativo en Moda.",
            "sectors": [pharmacy_impact, fashion_impact, re_impact],
            "recommendation": "Proceder con el incremento de precios en Farmacia para blindar rentabilidad del mes.",
            "simulation_timestamp": datetime.now().isoformat(),
            "db_status": "Persisted"
        }

        # Insert into Database as an Alert
        alert_entry = HistoricalData(
            tenant_id=tenant.id,
            sector="global",
            item_key="DECISION_ALERT_SIMULATION",
            price=total_profit_delta,
            metadata_json=simulation_metadata,
            timestamp=datetime.utcnow()
        )
        
        db.add(alert_entry)
        db.commit()
        
        with open("temp_sim_result.json", "w", encoding="utf-8") as f:
            json.dump(simulation_metadata, f, indent=2)
            
        return simulation_metadata
    except Exception as e:
        print(f"Error in simulation: {e}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    result = run_strategic_simulation("demo-saas")
    if result:
        print(json.dumps(result, indent=2))
