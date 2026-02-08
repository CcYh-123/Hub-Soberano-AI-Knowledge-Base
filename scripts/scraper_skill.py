"""
-----------------------------------------------------------------------
SCRIPT: scraper_skill.py
DIRECTIVA: D004_Scraper
ROL: Extracción de Datos con Trazabilidad
-----------------------------------------------------------------------
"""
import os
import json
import datetime
from pathlib import Path

# CONFIGURACIÓN
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"

# Crear carpeta /data si no existe
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Importar logger de D002
try:
    from logger_skill import create_logger
    logger = create_logger("scraper_skill")
    
    def log_event(level, message):
        """Wrapper para compatibilidad con el código original."""
        if level == "INFO":
            logger.info(message)
        elif level == "ERROR":
            logger.error(message)
        elif level == "SUCCESS":
            logger.success(message)
        elif level == "WARNING":
            logger.warning(message)
except ImportError:
    # Fallback si no está disponible el logger
    def log_event(level, message):
        print(f"[{level}] {message}")

def save_data(data, filename="raw_data.json"):
    """Guarda los datos extraídos en la carpeta /data"""
    path = DATA_DIR / filename
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        log_event("INFO", f"Datos guardados exitosamente en {filename}")
        return str(path)
    except Exception as e:
        log_event("ERROR", f"Error al guardar datos: {str(e)}")
        return None

def mock_scrape(url):
    """
    Simulación de scrape (Sustituir por lógica de Apify/BeautifulSoup)
    Incluye manejo de errores para alimentar al Brain (D003).
    """
    log_event("INFO", f"Iniciando extracción desde: {url}")
    
    try:
        # Simulación de éxito
        if "google" in url:
            result = {
                "status": "success",
                "url": url,
                "content": "Sample Search Data",
                "timestamp": datetime.datetime.now().isoformat(),
                "scraper_version": "1.0.0"
            }
            saved_path = save_data(result)
            if saved_path:
                log_event("SUCCESS", f"Scraping completado exitosamente para {url}")
                return result
            else:
                raise Exception("Error al guardar datos extraídos")
        else:
            # Simulación de fallo para probar el Brain
            raise Exception("Estructura de sitio no reconocida o Error de Conexión")
            
    except Exception as e:
        log_event("ERROR", f"Fallo en Scraper: {str(e)}")
        print(f"⚠️ Error detectado. El Brain (D003) analizará esto en la próxima ejecución.")
        return None
    finally:
        # Guardar log si está disponible
        try:
            logger.save()
        except:
            pass

if __name__ == "__main__":
    # Prueba de ejecución
    print("\n" + "="*60)
    print("🕷️  SCRAPER SKILL - Ejecución de Prueba")
    print("="*60 + "\n")
    
    test_url = "https://www.google.com"
    print(f"📍 URL de prueba: {test_url}")
    result = mock_scrape(test_url)
    
    if result:
        print(f"\n✅ Extracción exitosa")
        print(f"📁 Datos guardados en: /data/raw_data.json")
    else:
        print(f"\n❌ Extracción fallida")
        print(f"📝 Error registrado en logs para análisis del Brain")
    
    print("\n" + "="*60 + "\n")
