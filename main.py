"""
===============================================================================
                          ANTIGRAVITY - ORQUESTADOR CENTRAL
                                    main.py
                               DIRECTIVA: D006
===============================================================================
Punto de entrada único para ejecutar flujos completos del sistema Antigravity.
Coordina: Scraper (D004) -> Brain (D003) -> Reporter (D005)
Con trazabilidad completa vía Logger (D002) y actualización del Mapa (D001)
===============================================================================
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Agregar scripts al path para imports
ROOT_DIR = Path(__file__).parent
SCRIPTS_DIR = ROOT_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

# Importar skills del sistema
try:
    from logger_skill import create_logger
    from scraper_skill import mock_scrape
    from brain_skill import create_brain
    from reporter_skill import generate_executive_report
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    print("   Asegúrate de que todos los scripts existen en /scripts")
    sys.exit(1)


class AntigravityOrchestrator:
    """
    Orquestador Central del Sistema Antigravity.
    
    Coordina la ejecución secuencial de todos los subsistemas:
    - Scraper (D004): Extracción de datos
    - Brain (D003): Análisis y aprendizaje
    - Reporter (D005): Generación de reportes
    
    Con trazabilidad completa vía Logger (D002).
    """
    
    def __init__(self, mission_name: str = "FULL_CYCLE"):
        """
        Inicializa el orquestador.
        
        Args:
            mission_name: Nombre de la misión a ejecutar
        """
        self.mission_name = mission_name
        self.start_time = datetime.now()
        self.logger = create_logger(f"orchestrator_{mission_name}")
        self.results = {
            'mission': mission_name,
            'start_time': self.start_time.isoformat(),
            'steps_completed': [],
            'steps_failed': [],
            'success': False
        }
    
    def log(self, level: str, message: str):
        """Registra un evento con el logger."""
        if level == "INFO":
            self.logger.info(message)
        elif level == "ERROR":
            self.logger.error(message)
        elif level == "SUCCESS":
            self.logger.success(message)
        elif level == "WARNING":
            self.logger.warning(message)
    
    def run_step(self, step_name: str, step_function, *args, **kwargs):
        """
        Ejecuta un paso de la misión con manejo de errores.
        
        Args:
            step_name: Nombre del paso
            step_function: Función a ejecutar
            *args, **kwargs: Argumentos para la función
            
        Returns:
            Resultado de la función o None si falla
        """
        self.log("INFO", f"Iniciando paso: {step_name}")
        print(f"\n🔄 Ejecutando: {step_name}...")
        
        try:
            result = step_function(*args, **kwargs)
            self.results['steps_completed'].append(step_name)
            self.log("SUCCESS", f"Paso completado: {step_name}")
            print(f"   ✅ {step_name} completado")
            return result
        except Exception as e:
            error_msg = f"Error en {step_name}: {str(e)}"
            self.results['steps_failed'].append({
                'step': step_name,
                'error': str(e)
            })
            self.log("ERROR", error_msg)
            print(f"   ❌ {step_name} falló: {str(e)}")
            raise
    
    def run_full_mission(self, target_url: str = "https://www.google.com"):
        """
        Ejecuta el ciclo completo de la misión Antigravity.
        
        Flujo: Scraper -> Brain -> Reporter
        
        Args:
            target_url: URL objetivo para el scraping
            
        Returns:
            Diccionario con resultados de la misión
        """
        print("\n" + "="*70)
        print("🚀 ANTIGRAVITY - ORQUESTADOR CENTRAL")
        print(f"📋 Misión: {self.mission_name}")
        print(f"⏰ Inicio: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        self.log("INFO", f"=== INICIO DE MISIÓN: {self.mission_name} ===")
        self.log("INFO", f"URL objetivo: {target_url}")
        
        try:
            # ============================================================
            # PASO 1: EXTRACCIÓN (D004 - Scraper)
            # ============================================================
            scrape_result = self.run_step(
                "D004_Scraper: Extracción de Datos",
                mock_scrape,
                target_url
            )
            
            if not scrape_result:
                self.log("WARNING", "Scraping no retornó datos, continuando con análisis")
            
            # ============================================================
            # PASO 2: APRENDIZAJE (D003 - Brain)
            # ============================================================
            brain = create_brain()
            knowledge = self.run_step(
                "D003_Brain: Análisis y Aprendizaje",
                brain.learn
            )
            
            # ============================================================
            # PASO 3: REPORTERÍA (D005 - Reporter)
            # ============================================================
            report_path = self.run_step(
                "D005_Reporter: Generación de Reporte",
                generate_executive_report
            )
            
            # ============================================================
            # CIERRE DE MISIÓN
            # ============================================================
            self.results['success'] = True
            self.results['end_time'] = datetime.now().isoformat()
            self.results['report_path'] = report_path
            
            self.log("SUCCESS", f"=== MISIÓN {self.mission_name} COMPLETADA ===")
            
            print("\n" + "="*70)
            print("✅ MISIÓN COMPLETADA EXITOSAMENTE")
            print("="*70)
            print(f"📊 Pasos ejecutados: {len(self.results['steps_completed'])}")
            print(f"📁 Reporte generado: {report_path}")
            print("="*70 + "\n")
            
        except Exception as e:
            # ============================================================
            # MANEJO DE ERRORES - Aprendizaje del fallo
            # ============================================================
            self.log("ERROR", f"=== MISIÓN {self.mission_name} FALLIDA ===")
            self.log("ERROR", f"Error crítico: {str(e)}")
            
            print("\n" + "="*70)
            print("❌ MISIÓN FALLIDA")
            print(f"   Error: {str(e)}")
            print("="*70)
            
            # Intentar que el Brain aprenda del error
            try:
                self.log("INFO", "Ejecutando Brain para aprender del error...")
                brain = create_brain()
                brain.learn()
                self.log("SUCCESS", "Brain procesó el error para aprendizaje futuro")
            except Exception as brain_error:
                self.log("ERROR", f"Brain también falló: {str(brain_error)}")
            
            self.results['success'] = False
            self.results['end_time'] = datetime.now().isoformat()
            self.results['critical_error'] = str(e)
        
        finally:
            # Guardar log de la misión
            self.logger.save()
        
        return self.results


def run_full_mission(target_url: str = "https://www.google.com"):
    """
    Función de conveniencia para ejecutar una misión completa.
    
    Args:
        target_url: URL objetivo para scraping
        
    Returns:
        Resultados de la misión
    """
    orchestrator = AntigravityOrchestrator("FULL_CYCLE")
    return orchestrator.run_full_mission(target_url)


def main():
    """Punto de entrada principal del sistema Antigravity."""
    print("\n" + "🌌"*35)
    print("\n        A N T I G R A V I T Y   S Y S T E M")
    print("              Orquestador Central v1.0")
    print("                    Nivel 6")
    print("\n" + "🌌"*35 + "\n")
    
    # Ejecutar misión completa
    results = run_full_mission()
    
    # Resumen final
    print("\n" + "="*70)
    print("📋 RESUMEN DE MISIÓN")
    print("="*70)
    print(f"   Misión: {results['mission']}")
    print(f"   Estado: {'✅ ÉXITO' if results['success'] else '❌ FALLIDA'}")
    print(f"   Pasos completados: {len(results['steps_completed'])}")
    
    if results['steps_completed']:
        for step in results['steps_completed']:
            print(f"      ✓ {step}")
    
    if results['steps_failed']:
        print(f"   Pasos fallidos: {len(results['steps_failed'])}")
        for step_info in results['steps_failed']:
            print(f"      ✗ {step_info['step']}: {step_info['error']}")
    
    print("="*70)
    print("\n🔮 Sistema Antigravity - Nivel 6 Operativo\n")
    
    return 0 if results['success'] else 1


if __name__ == "__main__":
    sys.exit(main())
