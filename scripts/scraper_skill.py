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

def mock_scrape(url, tenant_id="default-client"):
    """
    Simulación de scrape (Sustituir por lógica de Apify/BeautifulSoup)
    Incluye manejo de errores para alimentar al Brain (D003).
    """
    log_event("INFO", f"Iniciando extracción para tenant [{tenant_id}] desde: {url}")
    
    try:
        if "fashion" in url or "ropa" in url:
            is_seasonal_change = "season" in url
            result = {
                "status": "success",
                "tenant_id": tenant_id,
                "sector": "fashion",
                "url": url,
                "timestamp": datetime.datetime.now().isoformat(),
                "scraper_version": "1.2.0",
                "products": [
                    {
                        "prenda": "Camisa de Lino",
                        "marca": "Zara",
                        "precio_original": 60,
                        "precio_oferta": 25 if is_seasonal_change else 55,
                        "stock": 0 if "stock" in url else 100,
                        "vistas_24h": 1500 if "viral" in url else 50
                    },
                    {
                        "prenda": "Vestido Floral",
                        "marca": "H&M",
                        "precio_original": 45,
                        "precio_oferta": 15 if is_seasonal_change else 40,
                        "stock": 5,
                        "vistas_24h": 2000 if "viral" in url else 100
                    },
                    {
                        "prenda": "Bolso de Cuero",
                        "marca": "Prada",
                        "precio_original": 1200,
                        "precio_oferta": 600 if is_seasonal_change else 1150,
                        "stock": 2,
                        "vistas_24h": 5000 if "viral" in url else 200
                    }
                ]
            }
            saved_path = save_data(result, filename=f"raw_data_fashion_{tenant_id}.json")
            if saved_path:
                log_event("SUCCESS", f"Extracción de moda completada para {url} (Tenant: {tenant_id})")
                return result
            else:
                raise Exception("Error al guardar datos extraídos")

        # Simulación de éxito con datos inmobiliarios (Existente)
        elif "google" in url or "inmuebles" in url:
            is_drop = "drop" in url
            result = {
                "status": "success",
                "tenant_id": tenant_id,
                "url": url,
                "timestamp": datetime.datetime.now().isoformat(),
                "scraper_version": "1.1.0",
                "properties": [
                    {
                        "zona": "Palermo",
                        "precio": 100000 if is_drop else 125000,
                        "m2": 85,
                        "link": "https://ejemplo.com/p1"
                    },
                    {
                        "zona": "Recoleta",
                        "precio": 150000 if is_drop else 210000,
                        "m2": 70,
                        "link": "https://ejemplo.com/p2"
                    },
                    {
                        "zona": "Villa Crespo",
                        "precio": 70000 if is_drop else 95000,
                        "m2": 65,
                        "link": "https://ejemplo.com/p3"
                    }
                ]
            }
            saved_path = save_data(result, filename=f"raw_data_{tenant_id}.json")
            if saved_path:
                log_event("SUCCESS", f"Extracción inmobiliaria completada para {url} (Tenant: {tenant_id})")
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
