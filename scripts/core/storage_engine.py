"""
-----------------------------------------------------------------------
SCRIPT: storage_engine.py
DIRECTIVA: D018_StorageEngine
ROL: Motor de Persistencia Histórica y Análisis de Tendencias
-----------------------------------------------------------------------
"""
import json
import os
from datetime import datetime
from pathlib import Path

# CONFIGURACIÓN
ROOT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / "data"
HISTORY_FILE = DATA_DIR / "history.json"

def load_history():
    """Carga el historial desde data/history.json."""
    if not HISTORY_FILE.exists():
        return {}
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Error cargando historial: {e}")
        return {}

def save_history(history_data):
    """Guarda el historial en data/history.json."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Error guardando historial: {e}")
        return False

def get_item_key(item, sector):
    """Genera una llave única para un ítem basada en su nombre o ID y sector."""
    # Intentamos buscar un identificador único
    item_id = item.get('id') or item.get('nombre') or item.get('nombre_producto') or item.get('zona')
    if not item_id:
        return None
    return f"{sector}:{item_id}"

def process_trends(current_data_files):
    """
    Procesa los datos actuales comparándolos con el historial.
    Actualiza los ítems con tendencias y guarda el nuevo historial.
    """
    history = load_history()
    new_history = history.copy()
    
    for file_entry in current_data_files:
        data = file_entry.get('data', {})
        sector = data.get('sector', 'unknown')
        items = data.get('properties', data.get('products', []))
        
        for item in items:
            key = get_item_key(item, sector)
            if not key:
                continue
                
            current_price = item.get('precio')
            previous_entry = history.get(key)
            
            if previous_entry and isinstance(current_price, (int, float)) and isinstance(previous_entry.get('price'), (int, float)):
                previous_price = previous_entry.get('price')
                
                if previous_price > 0:
                    delta_percent = ((previous_price - current_price) / previous_price) * 100
                    
                    if delta_percent >= 20:
                        item['trend'] = 'critical'
                        item['indicator'] = '🚨'
                    elif delta_percent >= 5:
                        item['trend'] = 'opportunity'
                        item['indicator'] = '🟢'
                    elif current_price < previous_price:
                        item['trend'] = 'down'
                        item['indicator'] = '📉'
                    elif current_price > previous_price:
                        item['trend'] = 'up'
                        item['indicator'] = '🔴'
                    else:
                        item['trend'] = 'stable'
                        item['indicator'] = '⚪'
                else:
                    item['trend'] = 'new'
                    item['indicator'] = '🆕'
            else:
                item['trend'] = 'new'
                item['indicator'] = '🆕'
            
            # Actualizar historial DESPUÉS de comparar
            new_history[key] = {
                'price': current_price,
                'last_updated': datetime.now().isoformat(),
                'sector': sector
            }
            
    save_history(new_history)
    
    # Check System Health (D019)
    try:
        if HISTORY_FILE.exists() and HISTORY_FILE.stat().st_size > 2 * 1024 * 1024: # 2MB
            # Injecting system overload flag into the first file metadata
            if current_data_files:
                current_data_files[0]['system_overload'] = True
    except Exception as e:
        print(f"⚠️ Error checking health: {e}")
        
    return current_data_files

if __name__ == "__main__":
    # Test simple
    test_item = {'nombre': 'Test Item', 'precio': 100}
    history = {'real_estate:Test Item': {'price': 150}}
    
    # Mock de carga para test local
    def load_history_mock(): return history
    
    # Guardar original
    _load = load_history
    load_history = load_history_mock
    
    mock_files = [{'data': {'sector': 'real_estate', 'products': [test_item]}}]
    processed = process_trends(mock_files)
    
    print(f"Trend: {test_item.get('trend')} {test_item.get('indicator')}")
    
    # Restaurar
    load_history = _load
