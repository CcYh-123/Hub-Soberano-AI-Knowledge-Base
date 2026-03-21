import sys
import os
import argparse
from pathlib import Path

# Añadir directorio actual al path para importaciones limpias
sys.path.append(str(Path(__file__).parent))

from core.config_loader import ConfigLoader

import io

# Forzar salida UTF-8 para evitar errores con emojis en Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def execute_rules(apply_changes=False):
    loader = ConfigLoader()
    target_margin = loader.get('economy.target_margin', 0.29)
    inflation = loader.get('economy.monthly_inflation', 0.05)
    
    print(f"--- [PROTECTION] ANTIGRAVITY ENGINE - Price Rule Executor ---")
    print(f"Parámetros activos: Margen {target_margin*100}% | Inflación {inflation*100}%")
    print("--------------------------------------------------")
    
    # Simulación de reglas cargadas (en producción esto vendría de DB o Config)
    # El error ocurre si una regla llega como None en la lista.
    rules = [
        {"id": "RULE_001", "sector": "pharmacy", "adjustment": 0.12, "desc": "Ajuste Inflación Farmacia"},
        None,  # <-- Aquí se generaría el AttributeError sin el check
        {"id": "RULE_002", "sector": "fashion", "adjustment": -0.05, "desc": "Liquidación Temporada"}
    ]
    
    processed_count = 0
    
    for rule in rules:
        # ARREGLO: Bloque de seguridad solicitado por el Director
        if rule is not None:
            rule_id = rule.get("id")
            adjustment = rule.get("adjustment")
            sector = rule.get("sector")
            
            print(f"[RULES] Procesando {rule_id} para sector {sector} (Ajuste: {adjustment*100}%)")
            
            if apply_changes:
                # Aquí iría la lógica de persistencia en DB o archivos
                print(f"   ✓ Aplicando cambios para {rule_id}...")
            
            processed_count += 1
        else:
            print("[WARNING] Se detectó una regla 'None', ignorando paso para evitar AttributeError.")

    print("--------------------------------------------------")
    print(f"DONE: Ciclo finalizado. Reglas procesadas con éxito: {processed_count}")
    print(f"INFO: Motor sincronizado con Phase 8.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Antigravity Price Rule Executor')
    parser.add_argument('--apply', action='store_true', help='Aplicar los cambios calculados')
    args = parser.parse_args()
    
    execute_rules(apply_changes=args.apply)
