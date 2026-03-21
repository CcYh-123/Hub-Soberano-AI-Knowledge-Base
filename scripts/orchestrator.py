"""
-----------------------------------------------------------------------
SCRIPT: orchestrator.py
DIRECTIVA: D006_Orquestador
ROL: Orquestador Central del Sistema Antigravity (Soberanía Técnica)
-----------------------------------------------------------------------
"""
import os
import sys
import importlib
import argparse
from pathlib import Path

# 🔧 CONFIGURACIÓN DE RUTAS
# El orquestador reside en /scripts
SCRIPTS_DIR = Path(__file__).parent
ROOT_DIR = SCRIPTS_DIR.parent

# Asegurar que el directorio de scripts esté en el path para importaciones dinámicas
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

try:
    from logger_skill import AntigravityLogger
    from heartbeat_skill import HeartbeatMonitor
except ImportError:
    print("❌ Error crítico: Asegúrese de que logger_skill.py y heartbeat_skill.py existan en /scripts")
    sys.exit(1)

class AntigravityOrchestrator:
    """
    Clase maestra para orquestar el ciclo de vida FULL_CYCLE de Antigravity.
    Diseñada bajo los principios de Soberanía y Multi-tenancy.
    """
    
    def __init__(self, tenant_id="default-client"):
        """
        Inicializa el orquestador para un cliente específico.
        
        Args:
            tenant_id: ID del cliente/tenant para aislamiento de datos.
        """
        self.tenant_id = tenant_id
        # El orquestador tiene su propio log de sesión
        self.logger = AntigravityLogger(f"orchestrator_{self.tenant_id}")
        self.logger.info(f"[LAUNCH] Orquestador Antigravity iniciado [Tenant: {self.tenant_id}]")
    
    def run_step(self, step_name: str):
        """
        Ejecuta un paso individual importando dinámicamente el skill correspondiente.
        
        Args:
            step_name: Nombre corto del paso (scraper, brain, etc.)
        """
        self.logger.info(f"--- INICIO PASO: {step_name.upper()} ---")
        
        try:
            # 1. Importación dinámica según requerimiento (importlib)
            module_name = f"{step_name}_skill"
            self.logger.info(f"Importando {module_name}...")
            
            # Recargar módulo si ya existe para evitar estado sucio
            if module_name in sys.modules:
                skill_module = importlib.reload(sys.modules[module_name])
            else:
                skill_module = importlib.import_module(module_name)
            
            # 2. Despacho inteligente según el skill
            # Cada skill tiene una interfaz ligeramente diferente en el sistema viejo
            if step_name == "scraper":
                # Scraper soporta tenant_id y requiere una URL
                url = os.getenv("SCRAPER_TARGET_URL", "https://www.google.com")
                self.logger.info(f"Ejecutando mock_scrape para {url}")
                skill_module.mock_scrape(url=url, tenant_id=self.tenant_id)
            
            elif step_name == "brain":
                # El cerebro requiere instanciación y learn()
                brain = skill_module.create_brain()
                brain.learn()
            
            elif step_name == "reporter":
                # El generador de reportes es una función directa
                skill_module.generate_executive_report()
            
            elif step_name == "notifier":
                # El notificador envía el último reporte generado
                skill_module.send_notification()
            
            elif step_name == "cleaner":
                # El limpiador realiza mantenimiento de logs y archivos
                skill_module.run_maintenance()
            
            else:
                # Fallback genérico: intentar llamar a main() si existe
                if hasattr(skill_module, 'main'):
                    self.logger.info(f"Ejecutando main() genérico para {module_name}")
                    skill_module.main()
                else:
                    self.logger.warning(f"No se encontró punto de entrada estándar para {module_name}")
            
            self.logger.success(f"--- FIN PASO: {step_name.upper()} COMPLETADO ---")
            
        except Exception as e:
            error_msg = f"Fallo crítico en el paso {step_name}: {str(e)}"
            self.logger.error(error_msg)
            # En modo orquestador, un paso fallido no detiene el ciclo completo (Resiliencia)
            print(f"WARN: {error_msg}")

    def run_full_cycle(self):
        """
        Ejecuta la secuencia maestra FULL_CYCLE:
        Scraper -> Brain -> Reporter -> Notifier -> Cleaner
        """
        self.logger.info("[CYCLE] Iniciando FULL_CYCLE estratégico...")
        
        steps = ["scraper", "brain", "reporter", "notifier", "cleaner"]
        
        for step in steps:
            self.run_step(step)
            
        self.logger.success("[FINISH] FULL_CYCLE completado exitosamente.")
        
        # 3. Reporte de Salud (Heartbeat) al finalizar
        self.logger.info("[HEARTBEAT] Generando reporte de salud final...")
        HeartbeatMonitor().run_check()
        self.logger.info("Sesión de orquestación finalizada.")
        self.logger.save()

def main():
    """
    Punto de entrada CLI para el orquestador.
    Uso: python scripts/orchestrator.py --mission FULL_CYCLE --tenant demo-saas
    """
    parser = argparse.ArgumentParser(description="Antigravity System Orchestrator")
    parser.add_argument(
        "--mission", 
        type=str, 
        choices=["FULL_CYCLE", "scraper", "brain", "reporter", "notifier", "cleaner"],
        default="FULL_CYCLE",
        help="Misión a ejecutar (Ciclo completo o paso individual)"
    )
    parser.add_argument(
        "--tenant", 
        type=str, 
        default="default-client",
        help="ID del cliente para aislamiento de datos"
    )
    
    args = parser.parse_args()
    
    orchestrator = AntigravityOrchestrator(tenant_id=args.tenant)
    
    if args.mission == "FULL_CYCLE":
        orchestrator.run_full_cycle()
    else:
        orchestrator.run_step(args.mission)
        orchestrator.logger.save()

if __name__ == "__main__":
    main()
