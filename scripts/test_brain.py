"""
Test Script para Brain Skill (D003)
Valida el sistema de aprendizaje y análisis de logs
"""

from brain_skill import create_brain
from logger_skill import create_logger


def create_sample_logs():
    """Crea logs de ejemplo para probar el Brain System."""
    print("\n📝 Creando logs de ejemplo para pruebas...")
    
    # Log 1: Script exitoso
    with create_logger("ejemplo_exitoso") as logger:
        logger.info("Iniciando proceso de ejemplo")
        logger.info("Procesando datos...")
        logger.success("Datos procesados correctamente")
        logger.success("Proceso completado sin errores")
    
    # Log 2: Script con errores
    with create_logger("ejemplo_con_errores") as logger:
        logger.info("Iniciando script con errores simulados")
        logger.error("FileNotFoundError: El archivo 'config.json' no existe")
        logger.error("ModuleNotFoundError: No module named 'requests'")
        logger.info("Intentando recuperación...")
        logger.error("PermissionError: Access denied to /system/config")
    
    # Log 3: Script mixto
    with create_logger("ejemplo_mixto") as logger:
        logger.info("Proceso con resultados mixtos")
        logger.success("Conexión a base de datos establecida")
        logger.warning("Advertencia: Memoria al 80%")
        logger.success("Consulta ejecutada correctamente")
    
    print("   ✓ 3 logs de ejemplo creados\n")


def test_brain_learning():
    """Test principal del Brain System."""
    print("\n" + "="*60)
    print("🧪 TEST: BRAIN SYSTEM (D003)")
    print("="*60)
    
    # Crear logs de ejemplo
    create_sample_logs()
    
    # Crear instancia del Brain
    brain = create_brain()
    
    # Ejecutar ciclo de aprendizaje
    knowledge = brain.learn()
    
    # Validar resultados
    print("\n📋 Validación de Resultados:")
    print("-" * 60)
    
    if knowledge['errors']:
        print(f"✓ Errores detectados: {len(knowledge['errors'])} categorías")
        for error_type in knowledge['errors'].keys():
            print(f"  - {error_type}")
    else:
        print("ℹ️  No se detectaron errores")
    
    if knowledge['successes']:
        print(f"\n✓ Patrones exitosos: {len(knowledge['successes'])}")
    else:
        print("\nℹ️  No se detectaron patrones exitosos")
    
    if knowledge['recommendations']:
        print(f"\n✓ Recomendaciones generadas: {len(knowledge['recommendations'])}")
        for rec in knowledge['recommendations']:
            print(f"  {rec}")
    else:
        print("\nℹ️  No hay recomendaciones")
    
    print("\n" + "="*60)
    print("✅ TEST COMPLETADO")
    print("="*60)
    print("\n📁 Revisa KNOWLEDGE_BASE.md para ver el conocimiento consolidado.\n")


if __name__ == "__main__":
    test_brain_learning()
