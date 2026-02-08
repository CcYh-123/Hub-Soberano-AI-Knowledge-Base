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
from logger_skill import create_logger

# CONFIGURACIÓN
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"

# Crear carpeta /data si no existe
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Logger global para el módulo
_module_logger = None

def get_logger():
    """Obtiene o crea el logger del módulo."""
    global _module_logger
    if _module_logger is None:
        _module_logger = create_logger("scraper_skill")
    return _module_logger

def save_data(data, filename="raw_data.json"):
    """Guarda los datos extraídos en la carpeta /data"""
    logger = get_logger()
    path = DATA_DIR / filename
    
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logger.success(f"Datos guardados exitosamente en {filename}")
        return str(path)
    except Exception as e:
        logger.error(f"Error al guardar datos en {filename}: {str(e)}")
        return None

def mock_scrape(url):
    """
    Simulación de scrape (Sustituir por lógica de Apify/BeautifulSoup)
    Incluye manejo de errores para alimentar al Brain (D003).
    """
    logger = get_logger()
    logger.info(f"Iniciando extracción desde: {url}")
    
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
                logger.success(f"Scraping completado exitosamente para {url}")
                return result
            else:
                logger.error("Fallo al guardar datos extraídos")
                return None
        else:
            # Simulación de fallo para probar el Brain
            raise Exception("Estructura de sitio no reconocida o Error de Conexión")
            
    except Exception as e:
        logger.error(f"Fallo en Scraper: {str(e)}")
        print(f"⚠️ Error detectado. El Brain (D003) analizará esto en la próxima ejecución.")
        return None
    finally:
        # Guardar log automáticamente
        logger.save()

def scrape_with_context(url, context_info=None):
    """
    Versión mejorada de scrape con contexto adicional.
    
    Args:
        url: URL a extraer
        context_info: Información adicional de contexto (dict)
    
    Returns:
        Datos extraídos o None si falla
    """
    logger = get_logger()
    logger.info(f"Scraping con contexto: {url}")
    
    if context_info:
        logger.info(f"Contexto: {json.dumps(context_info, ensure_ascii=False)}")
    
    result = mock_scrape(url)
    
    if result and context_info:
        result['context'] = context_info
        save_data(result, f"scrape_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    return result

if __name__ == "__main__":
    # Prueba de ejecución
    print("\n" + "="*60)
    print("🕷️  SCRAPER SKILL - Prueba de Ejecución")
    print("="*60 + "\n")
    
    # Test 1: Scraping exitoso
    print("Test 1: URL válida (Google)")
    test_url = "https://www.google.com"
    result = mock_scrape(test_url)
    print(f"Resultado: {'✅ Éxito' if result else '❌ Fallo'}\n")
    
    # Test 2: Scraping con error
    print("Test 2: URL inválida (para probar error handling)")
    test_url_fail = "https://www.sitio-desconocido.com"
    result_fail = mock_scrape(test_url_fail)
    print(f"Resultado: {'✅ Éxito' if result_fail else '❌ Fallo (esperado)'}\n")
    
    # Test 3: Scraping con contexto
    print("Test 3: Scraping con contexto adicional")
    context = {"project": "Antigravity", "purpose": "Testing D004"}
    result_context = scrape_with_context("https://www.google.com", context)
    print(f"Resultado: {'✅ Éxito' if result_context else '❌ Fallo'}\n")
    
    print("="*60)
    print("✅ Pruebas completadas")
    print("📁 Revisa /data para ver los archivos generados")
    print("📁 Revisa /executions para ver los logs")
    print("="*60 + "\n")
