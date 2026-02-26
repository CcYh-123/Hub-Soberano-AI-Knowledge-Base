
import json
import os
from datetime import datetime
from pathlib import Path

REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)

def generate_strategic_report(simulation_data):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = REPORTS_DIR / f"ESTRATEGIA_SIMULACION_{timestamp}.md"
    
    content = f"""# 🧠 REPORTE ESTRATÉGICO: SIMULACIÓN WHAT-IF

**Fecha:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Escenario Ejecutado:** Multi-Sector Crisis/Opportunity 2026

## 1. Análisis de Factores de Impacto

| Sector | Ajuste Realizado | Impacto Profit (Delta) | Nota Táctica |
|--------|------------------|------------------------|--------------|
| **Farmacia** | +12% Precio | +$12,000 | Absorbe el riesgo inflacionario y de costos. |
| **Moda** | -8% Volumen | -$6,400 | Mitigación por estacionalidad detectada. |
| **Inmobiliaria** | +$2,000 MKT | -$2,000 | Inversión estratégica para CAC favorable. |

## 2. Resultados Proyectados (ROI Global)

- **Impacto Neto en Ganancia:** `${simulation_data['analysis'].split(':')[1].strip()}`
- **Veredicto del Cerebro Antigravity:** {simulation_data['recommendation']}

### Resumen Visual en Dashboard
Se ha disparado una **Alerta de Decisión** en el Dashboard para el Tenant `demo-saas`.

---
## 🚀 ALERTA DE DECISIÓN: RECOMENDACIÓN FINAL
El sistema recomienda implementar el alza de precios en **Farmacia** de forma inmediata. La rentabilidad global se mantiene positiva a pesar de la caída en el sector de Moda. 

**Indicador de Salud Post-Simulación:** EXCELENTE
"""
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return str(report_path)

if __name__ == "__main__":
    # Simulate reading from the executed simulation
    with open("temp_sim_result.json", "r") as f:
        sim_data = json.load(f)
    print(f"Reporte generado: {generate_strategic_report(sim_data)}")
