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

import argparse
import sys
import os
from datetime import datetime
from pathlib import Path

# Agregar scripts al path para imports
ROOT_DIR = Path(__file__).parent
SCRIPTS_DIR = ROOT_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

# Importar skills del sistema (resto de imports igual)
try:
    from logger_skill import create_logger
    from scraper_skill import mock_scrape
    from brain_skill import create_brain
    from reporter_skill import generate_executive_report, read_data_files
    from comms_skill import send_notification, send_mission_summary, send_critical_alert
    from heartbeat_skill import check_health
    from notifier_skill import send_notification as send_external_notification
    from cleaner_skill import run_maintenance, get_maintenance_status
    from web_skill import generate_web
    from core.storage_engine import process_trends, load_history
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    print("   Asegúrate de que todos los scripts existen en /scripts")
    sys.exit(1)


class AntigravityOrchestrator:
    
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
    
    
    def run_full_mission(self, target_url: str = "https://www.google.com", force: bool = False):
        """
        Ejecuta el ciclo completo de la misión Antigravity.
        Args:
            target_url: URL objetivo
            force: Si es True, salta las restricciones de tiempo del scheduler.
        """
        print("\n" + "="*70)
        print("🚀 ANTIGRAVITY - ORQUESTADOR CENTRAL")
        print(f"📋 Misión: {self.mission_name}")
        print(f"⏰ Inicio: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        if force:
             print("\033[95m[BYPASS] MODO FORCE DETECTADO: Ejecutando auditoría completa ahora.\033[0m")
        print("="*70)
        
        self.log("INFO", f"=== INICIO DE MISIÓN: {self.mission_name} ===")
        self.log("INFO", f"URL objetivo: {target_url}")
        if force:
            self.log("WARNING", "EJECUCIÓN FORZADA ACTIVADA")
        
        maintenance_data = ""
        
        try:
            # ... (Resto de pasos igual, pero pasando 'force' a check_scheduler implícitamente o explícitamente)

            # ============================================================
            # PASO 0: MANTENIMIENTO (D010 - Cleaner)
            # ============================================================
            self.run_step(
                "D010_Cleaner: Mantenimiento del Sistema",
                run_maintenance,
                retention_days=7
            )
            maintenance_data = get_maintenance_status(retention_days=7)
            
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
            # PASO 2: ANÁLISIS (D003 - Brain) + SECTORES (D014)
            # ============================================================
            brain = create_brain() 
            logs_data = self.run_step("D003_Brain: Lectura de Logs", brain.read_logs)
            error_analysis = self.run_step("D003_Brain: Análisis de Errores", brain.analyze_errors, logs_data)
            success_patterns = self.run_step("D003_Brain: Patrones de Éxito", brain.extract_success_patterns, logs_data)
            
            # Cargar Configuración Sector Activo
            import json
            config_path = ROOT_DIR / "config_sector.json"
            active_sector = "real_estate"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    active_sector = config.get('active_sector', 'real_estate')

            # SCHEDULER CHECK (D020)
            history = load_history()
            if not check_scheduler(active_sector, history, force=force):
                self.log("WARNING", f"⏳ SCHEDULER: Saltando ejecución de {active_sector}. Tiempo no cumplido.")
                print(f"⏳ SCHEDULER: {active_sector} al día. Saltando ejecución.")
                return # Detener misión completa

            # Cargar Datos y Procesar según Sector Activo
            data_files = read_data_files()
            
            # PASO 2.5: Análisis de Memoria Histórica (D018)
            data_files = self.run_step("D018_Storage: Análisis de Tendencias", process_trends, data_files)
            
            if active_sector == "fashion":
                    try:
                        from sectors.fashion.fashion_skill import FashionSkill
                        f_skill = FashionSkill()
                        for entry in data_files:
                            if entry['data'].get('sector') == 'fashion':
                                products = entry['data'].get('products', [])
                                entry['data']['products'] = f_skill.process_products(products)
                                self.log("INFO", f"Procesados {len(products)} productos de Moda")
                    except Exception as e:
                        self.log("WARNING", f"Skill de Moda no procesado: {e}")

            opportunities = self.run_step("D003_Brain: Detección de Oportunidades", brain.analyze_properties, data_files)
            
            knowledge = self.run_step(
                "D003_Brain: Consolidación", 
                brain.consolidate_knowledge, 
                error_analysis, 
                success_patterns,
                opportunities=opportunities
            )
            self.run_step("D003_Brain: Actualización KB", brain.update_knowledge_base, knowledge)        # ============================================================
            # PASO 3: REPORTERÍA (D005 - Reporter)
            # ============================================================
            report_path = self.run_step(
                "D005_Reporter: Generación de Reporte",
                generate_executive_report,
                data_files,
                maintenance_report=maintenance_data
            )
            
            # ============================================================
            # WEB INTERFACE: Generación de Interfaz Pública (D013)
            # ============================================================
            self.run_step(
                "D013_Web: Generación de Interfaz",
                generate_web
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
            if force:
                print("\033[95m[!] EJECUCIÓN FORZADA COMPLETADA\033[0m")
            print("="*70)
            print(f"📊 Pasos ejecutados: {len(self.results['steps_completed'])}")
            print(f"📁 Reporte generado: {report_path}")
            print("="*70 + "\n")
            
            # ============================================================
            # PASO 4: COMUNICACIÓN (D007 - Comms)
            # ============================================================
            self.run_step(
                "D007_Comms: Notificación de Éxito",
                send_mission_summary,
                self.mission_name,
                True,
                len(self.results['steps_completed'])
            )
            
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
            
            # Enviar alerta crítica
            try:
                send_critical_alert(str(e))
            except:
                pass
            
            self.results['success'] = False
            self.results['end_time'] = datetime.now().isoformat()
            self.results['critical_error'] = str(e)
        
        finally:
            # Guardar log de la misión
            self.logger.save()
        
        return self.results


def get_seconds(value: int, unit: str) -> int:
    """Convierte unidad de tiempo a segundos."""
    unit = unit.lower()
    if 'minute' in unit:
        return value * 60
    elif 'hour' in unit:
        return value * 3600
    elif 'day' in unit:
        return value * 86400
    return 0

def check_scheduler(sector_name: str, history_data: dict, force: bool = False) -> bool:
    """
    Verifica si se debe ejecutar el sector según configuración.
    Returns: True si se debe ejecutar, False si se debe saltar.
    Args:
        force: Si es True, siempre retorna True (salta validación).
    """
    if force:
        # Mensaje ya impreso en el orquestador o aquí si se prefiere redundancia
        return True

    scheduler_path = ROOT_DIR / "config" / "scheduler.json"
    if not scheduler_path.exists():
        return True
        
    try:
        with open(scheduler_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            sector_config = config.get('sectors', {}).get(sector_name)
            
            if not sector_config:
                return True
                
            # Buscar último timestamp del sector en historial
            last_run = None
            for item in history_data.values():
                if item.get('sector') == sector_name:
                    ts = datetime.fromisoformat(item.get('last_updated'))
                    if last_run is None or ts > last_run:
                        last_run = ts
            
            if not last_run:
                return True
                
            delta = (datetime.now() - last_run).total_seconds()
            interval = get_seconds(sector_config['value'], sector_config['unit'])
            
            if delta < interval:
                return False
            return True
            
    except Exception as e:
        print(f"⚠️ Error en scheduler: {e}")
        return True

def run_full_mission(target_url: str = "https://www.google.com", force: bool = False):
    """
    Función de conveniencia para ejecutar una misión completa.
    
    Args:
        target_url: URL objetivo para scraping
        force: Forzar ejecución
        
    Returns:
        Resultados de la misión
    """
    orchestrator = AntigravityOrchestrator("FULL_CYCLE")
    return orchestrator.run_full_mission(target_url, force=force)


def main():
    """Punto de entrada principal del sistema Antigravity."""
    parser = argparse.ArgumentParser(description="Antigravity System Orchestrator")
    parser.add_argument("--force", action="store_true", help="Forzar ejecución ignorando scheduler (D022)")
    args = parser.parse_args()

    print("\n" + "🌌"*35)
    print("\n        A N T I G R A V I T Y   S Y S T E M")
    print("              Orquestador Central v1.2")
    print("                    Nivel 7")
    print("\n" + "🌌"*35 + "\n")
    
    # Ejecutar misión completa
    results = run_full_mission(force=args.force)
    
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
    
    # ============================================================
    # HEARTBEAT: Validación de salud post-ejecución (D008)
    # ============================================================
    print("\n💓 Ejecutando Heartbeat D008...")
    health = check_health(hours=1)
    print(f"   Estado de salud: {health['overall_health']}")
    
    # ============================================================
    # NOTIFIER: Envío a canal externo (D009)
    # ============================================================
    print("\n📣 Ejecutando Notifier D009...")
    notification_result = send_external_notification()
    print(f"   Modo: {notification_result['mode']}")
    print(f"   Resultado: {'✅' if notification_result['success'] else '⚠️'} {notification_result['message']}")
    
    print("\n🔮 Sistema Antigravity - Nivel 8 Operativo\n")
    
    return 0 if results['success'] else 1


if __name__ == "__main__":
    sys.exit(main())
