import sys
import os
from scripts.core.config_loader import ConfigLoader

def execute_rules():
    loader = ConfigLoader()
    target_margin = loader.get('economy.target_margin', 0.29)
    inflation = loader.get('economy.monthly_inflation', 0.05)
    
    print(f"--- ??? ANTIGRAVITY ENGINE ---")
    print(f"Parámetros activos: Margen {target_margin*100}% | Inflación {inflation*100}%")
    print("--------------------------------")
    
    # Aquí el motor ya puede usar target_margin en sus cálculos
    # Por ahora, simulamos la salida para confirmar la conexión
    print(f"? Motor sincronizado con Phase 8.")

if __name__ == '__main__':
    execute_rules()
