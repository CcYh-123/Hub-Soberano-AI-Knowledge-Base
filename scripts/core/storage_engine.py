"""
-----------------------------------------------------------------------
SCRIPT: storage_engine.py
DIRECTIVA: D018_StorageEngine / D011_MultiTenancy
ROL: Motor de Persistencia Relacional con Aislamiento (Multi-Tenant)
-----------------------------------------------------------------------
"""
import os
import json
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from .database import SessionLocal, Tenant, HistoricalData

# CONFIGURACIÓN
ROOT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / "data"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def load_history_for_tenant(tenant_id: str, sector: str = None):
    """
    Carga el historial filtrado por tenant_id y opcionalmente por sector.
    """
    db = next(get_db()) # Use next() to get the session from the generator
    try:
        query = db.query(HistoricalData).filter(HistoricalData.tenant_id == tenant_id)
        if sector:
            query = query.filter(HistoricalData.sector == sector)
        
        # Convertir a formato compatible con el código anterior para evitar rupturas masivas
        results = {}
        for entry in query.all():
            results[f"{entry.sector}:{entry.item_key}"] = {
                'price': entry.price,
                'last_updated': entry.timestamp.isoformat(),
                'sector': entry.sector,
                'metadata': json.loads(entry.metadata_json) if entry.metadata_json else None
            }
        return results
    except Exception as e:
        print(f"⚠️ Error cargando historial DB para tenant {tenant_id}: {e}")
        return {}
    finally:
        db.close()

def save_item_history(tenant_id: str, sector: str, item_key: str, price: float, metadata: dict = None):
    """
    Guarda o actualiza un registro individual en la base de datos vinculado a un tenant.
    """
    db = next(get_db()) # Use next() to get the session from the generator
    try:
        # Buscar entrada existente para actualizar
        entry = db.query(HistoricalData).filter(
            HistoricalData.tenant_id == tenant_id,
            HistoricalData.sector == sector,
            HistoricalData.item_key == item_key
        ).first()
        
        metadata_json_str = json.dumps(metadata) if metadata else None

        if entry:
            entry.price = price
            entry.timestamp = datetime.utcnow()
            entry.metadata_json = metadata_json_str
        else:
            entry = HistoricalData(
                tenant_id=tenant_id,
                sector=sector,
                item_key=item_key,
                price=price,
                timestamp=datetime.utcnow(),
                metadata_json=metadata_json_str
            )
            db.add(entry)
        
        db.commit()
        return True
    except Exception as e:
        print(f"❌ Error guardando en DB: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def get_item_key(item, sector):
    """Genera una llave única para un ítem basada en su nombre o ID y sector."""
    item_id = item.get('id') or item.get('nombre') or item.get('nombre_producto') or item.get('zona')
    if not item_id:
        return None
    return item_id # Retornamos solo el ID, el sector se maneja en columnas separadas en DB

def process_trends(current_data_files, tenant_id: str = "default-client"):
    """
    Procesa las tendencias filtrando estrictamente por tenant_id.
    """
    # Cargar historial del tenant
    history = load_history_for_tenant(tenant_id)
    
    for file_entry in current_data_files:
        data = file_entry.get('data', {})
        sector = data.get('sector', 'unknown')
        items = data.get('properties', data.get('products', []))
        
        for item in items:
            item_id = get_item_key(item, sector)
            if not item_id:
                continue
            
            key = f"{sector}:{item_id}"
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
            
            # Guardar en DB vinculado al tenant
            save_item_history(
                tenant_id=tenant_id,
                sector=sector,
                item_key=item_id,
                price=current_price,
                metadata={'trend': item.get('trend')}
            )
            
    # The original JSON file-based health check is removed as the persistence mechanism has changed.
    # A new database-centric health check would be needed if this functionality is still desired.
        
    return current_data_files

# Mantener firmas originales para compatibilidad temporal si es necesario
def load_history(): return load_history_for_tenant("default-client")
def save_history(data): print("⚠️ save_history(JSON) obsoleto. Use save_item_history(DB)."); return False

if __name__ == "__main__":
    # This block needs to be updated to use the new DB functions for testing
    print("Running a simplified test for the new DB-based storage engine.")

    # Mock DB setup (assuming database.py and models are set up)
    # For a real test, you'd need to initialize the DB and potentially mock SessionLocal
    
    # Example tenant and item
    test_tenant_id = "test-client-123"
    test_sector = "real_estate"
    test_item_id = "Test Item 001"
    test_price_initial = 150.0
    test_price_current = 100.0

    # Clean up any previous test data for this item
    db = next(get_db())
    try:
        db.query(HistoricalData).filter(
            HistoricalData.tenant_id == test_tenant_id,
            HistoricalData.sector == test_sector,
            HistoricalData.item_key == test_item_id
        ).delete()
        db.commit()
    except Exception as e:
        print(f"Error cleaning up test data: {e}")
        db.rollback()
    finally:
        db.close()

    # 1. Save an initial history entry
    print(f"Saving initial history for {test_item_id} at {test_price_initial}...")
    save_item_history(test_tenant_id, test_sector, test_item_id, test_price_initial, {'initial_state': True})

    # 2. Prepare current data for processing
    test_item = {'nombre': test_item_id, 'precio': test_price_current}
    mock_files = [{'data': {'sector': test_sector, 'products': [test_item]}}]

    # 3. Process trends
    print(f"Processing trends for {test_item_id} with current price {test_price_current}...")
    processed = process_trends(mock_files, tenant_id=test_tenant_id)
    
    print(f"Trend: {test_item.get('trend')} {test_item.get('indicator')}")

    # 4. Verify the updated history in the DB
    print("Verifying updated history in DB...")
    history_after_processing = load_history_for_tenant(test_tenant_id, test_sector)
    key_to_check = f"{test_sector}:{test_item_id}"
    if key_to_check in history_after_processing:
        entry = history_after_processing[key_to_check]
        print(f"DB entry for {key_to_check}: Price={entry['price']}, Last Updated={entry['last_updated']}, Metadata={entry['metadata']}")
        assert entry['price'] == test_price_current
        assert entry['metadata']['trend'] == test_item.get('trend')
        print("Verification successful!")
    else:
        print("Error: Item not found in history after processing.")

    # Test with a new item (should be 'new')
    new_item_id = "New Item 002"
    new_item_price = 50.0
    new_test_item = {'nombre': new_item_id, 'precio': new_item_price}
    new_mock_files = [{'data': {'sector': test_sector, 'products': [new_test_item]}}]
    print(f"\nProcessing trends for new item {new_item_id} with price {new_item_price}...")
    processed_new = process_trends(new_mock_files, tenant_id=test_tenant_id)
    print(f"Trend for new item: {new_test_item.get('trend')} {new_test_item.get('indicator')}")
    assert new_test_item.get('trend') == 'new'
    print("New item trend verification successful!")

    print("\nStorage engine tests completed.")
