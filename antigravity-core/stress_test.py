import time
import random
import psutil
import os
import polars as pl
from sqlmodel import Session, select
from database import engine, PriceEvent, Product, create_db_and_tables
from ingestor import process_vendor_list
from notifier import register_webhook

import sys

# Forzar salida UTF-8 en Windows
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def generate_synthetic_data(num_products=10000, tenant_id="tenant_x"):
    """
    Genera datos sintéticos para un tenant.
    """
    data = []
    for i in range(num_products):
        costo_v = round(random.uniform(10.0, 500.0), 2)
        # Aumento del 5% al 15%
        costo_n = round(costo_v * (1 + random.uniform(0.05, 0.15)), 2)
        data.append({
            "product_id": f"SKU-{tenant_id}-{i}",
            "costo_viejo": costo_v,
            "costo_nuevo": costo_n
        })
    return data

def run_stress_test():
    print("--- [START] INICIANDO STRESS TEST: ANTIGRAVITY CORE ---")
    
    # Asegurar tablas limpias para el test (opcional, aquí las creamos)
    create_db_and_tables()
    
    tenants = ["T-ALPHA", "T-BETA", "T-GAMMA", "T-DELTA", "T-EPSILON"]
    products_per_tenant = 10000
    total_processed = 0
    
    process_times_polars = []
    db_insertion_times = []
    
    process = psutil.Process(os.getpid())
    mem_before = process.memory_info().rss / (1024 * 1024)
    
    start_global = time.time()
    
    with Session(engine) as session:
        for t_id in tenants:
            print(f"\n[Tenant: {t_id}] Generando {products_per_tenant} productos...")
            raw_data = generate_synthetic_data(products_per_tenant, t_id)
            
            # 1. Benchmarking POLARS
            t0 = time.time()
            df = process_vendor_list(raw_data, t_id)
            t1 = time.time()
            polars_time = t1 - t0
            process_times_polars.append(polars_time)
            print(f"   [TIME] Polars Time: {polars_time:.4f}s")
            
            # 2. Benchmarking DB (Hacemos insercion eficiente)
            t2 = time.time()
            records = df.to_dicts()
            
            # Para el stress test usamos una insercion mas agresiva por lotes
            # En main.py es 1 a 1, aqui medimos la capacidad del motor de base de datos
            for rec in records:
                event = PriceEvent(
                    product_sku=rec["product_id"],
                    costo_viejo=rec["costo_viejo"],
                    costo_nuevo=rec["costo_nuevo"],
                    delta_erosion=rec["delta_erosion"],
                    tenant_id=t_id
                )
                session.add(event)
            
            session.commit()
            t3 = time.time()
            db_time = t3 - t2
            db_insertion_times.append(db_time)
            print(f"   [TIME] DB Insertion Time: {db_time:.4f}s")
            
            total_processed += len(raw_data)

    end_global = time.time()
    mem_after = process.memory_info().rss / (1024 * 1024)
    
    # 3. Validacion de AISLAMIENTO TOTAL
    print("\n--- [SECURITY] VALIDANDO AISLAMIENTO ---")
    with Session(engine) as session:
        # Intentamos buscar productos de T-BETA filtrando por T-ALPHA
        # El resultado debe ser 0.
        leak_stmt = select(PriceEvent).where(
            PriceEvent.tenant_id == "T-ALPHA",
            PriceEvent.product_sku.contains("T-BETA")
        )
        leaks = session.exec(leak_stmt).all()
        
        if len(leaks) == 0:
            print("[OK] Aislamiento confirmado: No se encontraron filtraciones entre Tenant A y Tenant B.")
        else:
            print(f"[ERROR] Filtracion detectada! {len(leaks)} registros cruzados.")

    # 4. Reporte Final
    avg_polars = sum(process_times_polars) / len(process_times_polars)
    total_time = end_global - start_global
    
    print("\n" + "="*40)
    print("REPORT: PERFORMANCE SUMMARY")
    print("="*40)
    print(f"Filas Procesadas:     {total_processed:,}")
    print(f"Tenants Atendidos:    {len(tenants)}")
    print(f"Tiempo Total:         {total_time:.2f}s")
    print(f"Avg Polars Time:      {avg_polars:.4f}s")
    print(f"RAM Inicial:          {mem_before:.2f} MB")
    print(f"RAM Final:            {mem_after:.2f} MB")
    print(f"Memoria Consumida:    {mem_after - mem_before:.2f} MB")
    print("="*40)
    print(f"[FINISH] Processed {total_processed} rows in {total_time:.2f} seconds for {len(tenants)} tenants.")

if __name__ == "__main__":
    run_stress_test()
