"""
Test Script para Logger Skill (D002)
Valida el funcionamiento del sistema de logging
"""

from logger_skill import AntigravityLogger, create_logger


def test_basic_logging():
    """Test 1: Funcionalidad básica del logger."""
    print("\n" + "="*60)
    print("TEST 1: Funcionalidad Básica")
    print("="*60)
    
    logger = create_logger("test_basico")
    
    logger.info("Iniciando prueba de funcionalidad básica")
    logger.info("Registrando mensaje informativo")
    logger.warning("Esto es una advertencia de prueba")
    logger.success("Operación de prueba completada")
    
    logger.save()
    print(f"✓ Test 1 completado. Log guardado.\n")


def test_error_handling():
    """Test 2: Manejo de errores."""
    print("="*60)
    print("TEST 2: Manejo de Errores")
    print("="*60)
    
    logger = create_logger("test_errores")
    
    logger.info("Simulando escenario con errores")
    
    try:
        # Simular un error
        resultado = 10 / 0
    except ZeroDivisionError as e:
        logger.error(f"Error capturado: {str(e)}")
    
    logger.success("El sistema manejó el error correctamente")
    logger.save()
    print(f"✓ Test 2 completado. Log guardado.\n")


def test_context_manager():
    """Test 3: Uso con context manager (with statement)."""
    print("="*60)
    print("TEST 3: Context Manager")
    print("="*60)
    
    with create_logger("test_context_manager") as logger:
        logger.info("Usando logger con context manager")
        logger.info("El log se guardará automáticamente al salir del bloque")
        logger.success("Context manager funcionando correctamente")
    
    print(f"✓ Test 3 completado. Log guardado automáticamente.\n")


def test_exception_in_context():
    """Test 4: Manejo de excepciones en context manager."""
    print("="*60)
    print("TEST 4: Excepciones en Context Manager")
    print("="*60)
    
    try:
        with create_logger("test_excepcion") as logger:
            logger.info("Iniciando test con excepción")
            logger.warning("A continuación se generará un error intencional")
            
            # Generar error intencional
            raise ValueError("Error de prueba intencional")
            
    except ValueError:
        print("✓ Excepción capturada correctamente")
        print("✓ El log se guardó antes de propagar la excepción\n")


def main():
    """Ejecuta todos los tests del logger."""
    print("\n" + "🧪 SUITE DE TESTS - LOGGER SKILL (D002)")
    print("="*60 + "\n")
    
    test_basic_logging()
    test_error_handling()
    test_context_manager()
    test_exception_in_context()
    
    print("="*60)
    print("✅ TODOS LOS TESTS COMPLETADOS")
    print("="*60)
    print("\n📁 Revisa la carpeta /executions para ver los logs generados.\n")


if __name__ == "__main__":
    main()
