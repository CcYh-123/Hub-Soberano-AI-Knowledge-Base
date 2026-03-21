"""
-----------------------------------------------------------------------
SCRIPT: ingestor.py
ROL: Ingestor de Datos Ultra-Rápido (Polars Engine)
DIRECTIVA: D004_Scraper / D018_Storage
-----------------------------------------------------------------------
"""

import os
import sys
from pathlib import Path

# Intentar importar polars. Si falla, avisar al usuario.
try:
    import polars as pl
except ImportError:
    print("\n[!] ERROR: Polars no está instalado en el entorno.")
    print("[!] Por favor, ejecuta: pip install polars")
    pl = None

def ingest_csv(file_path):
    """
    Lee un archivo CSV usando Polars, normaliza los headers a minúsculas
    y devuelve un DataFrame listo para procesar.
    """
    if pl is None:
        return None

    path = Path(file_path)
    if not path.exists():
        print(f"[!] Error: El archivo {file_path} no existe.")
        return None

    print(f"[*] Ingestando: {path.name}...")
    
    # Lectura y normalización de headers (limpieza básica)
    try:
        df = pl.read_csv(file_path)
        
        # Normalizar headers a minúsculas
        df = df.rename({col: col.lower().strip() for col in df.columns})
        
        print(f"[+] Ingesta exitosa: {len(df)} registros encontrados.")
        print(f"[+] Columnas detectadas: {df.columns}")
        
        return df
    except Exception as e:
        print(f"[!] Erro durante la ingesta: {e}")
        return None

def prepare_for_executor(df):
    """
    Convierte el DataFrame de Polars a una estructura compatible
    con price_rule_executor.py (lista de diccionarios).
    """
    if df is None:
        return []
        
    # El ejecutor espera una lista de reglas
    # Aquí podríamos mapear columnas del CSV a la estructura de reglas
    return df.to_dicts()

if __name__ == "__main__":
    # Ejemplo de uso/test
    sample_csv = "data/input_sample.csv"
    
    # Crear carpeta data si no existe para el test
    os.makedirs("data", exist_ok=True)
    
    if not os.path.exists(sample_csv):
        # Crear un dummy CSV para probar si polars estuviera instalado
        with open(sample_csv, "w") as f:
            f.write("ID,SECTOR,ADJUSTMENT,DESC\n")
            f.write("RULE_CSV_01,pharmacy,0.15,Ajuste desde CSV\n")
            f.write("RULE_CSV_02,fashion,-0.10,Promo CSV\n")

    data = ingest_csv(sample_csv)
    if data is not None:
        rules = prepare_for_executor(data)
        print(f"[*] Datos listos para el motor: {rules}")
