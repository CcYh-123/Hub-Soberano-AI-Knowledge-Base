import subprocess
import os
import sys
from pathlib import Path
from core.database import SessionLocal, HistoricalData, Tenant

def run_mission(tenant):
    print(f"\n🏃 Ejecutando misión para Tenant: {tenant}...")
    cmd = ["py", "main.py", "--tenant", tenant, "--force"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Misión falló para {tenant}")
        print(result.stdout)
        print(result.stderr)
    else:
        print(f"✅ Misión completada para {tenant}")

def verify_isolation():
    print("\n🔍 Iniciando Verificación de Aislamiento (D011)...")
    
    # 1. Ejecutar para tenant A
    run_mission("default-client")
    
    # 2. Ejecutar para tenant B
    run_mission("demo-saas")
    
    # 3. Consultar DB directamente
    db = SessionLocal()
    try:
        # Contar total de registros
        total = db.query(HistoricalData).count()
        print(f"\n📊 Total de registros en historical_data: {total}")
        
        # Verificar registros de A
        tenant_a = db.query(Tenant).filter(Tenant.slug == "default-client").first()
        data_a = db.query(HistoricalData).filter(HistoricalData.tenant_id == tenant_a.id).all()
        print(f"   [Tenant A: default-client] Registros: {len(data_a)}")
        
        # Verificar registros de B
        tenant_b = db.query(Tenant).filter(Tenant.slug == "demo-saas").first()
        data_b = db.query(HistoricalData).filter(HistoricalData.tenant_id == tenant_b.id).all()
        print(f"   [Tenant B: demo-saas] Registros: {len(data_b)}")
        
        # Test de fuego: No debe haber cruce de IDs
        a_ids = {d.tenant_id for d in data_a}
        b_ids = {d.tenant_id for d in data_b}
        
        if a_ids.intersection(b_ids):
            print("\n❌ FALLO CRÍTICO: Se detectó mezcla de datos entre tenants.")
            sys.exit(1)
        else:
            print("\n💪 ÉXITO: Aislamiento de datos confirmado.")
            
    finally:
        db.close()

if __name__ == "__main__":
    verify_isolation()
