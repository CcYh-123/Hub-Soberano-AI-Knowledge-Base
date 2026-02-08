# D002_Logger.md

## METADATA
- **ID:** D002
- **Nombre:** Sistema de Registro y Trazabilidad (Logger)
- **Estado:** PENDIENTE DE CONSTRUCCIÓN
- **Dependencias:** D001 (Mapa del Sistema)

## 1. OBJETIVO (SKILL)
Crear un módulo de Python reutilizable que permita a cualquier script futuro registrar sus actividades, errores y éxitos en la carpeta `/executions`.

## 2. REGLAS DE NEGOCIO (RULES)
1. **Inmutabilidad:** Los logs nunca deben sobrescribirse; deben usar nombres con timestamp: `YYYYMMDD_HHMM_NombreScript.log`.
2. **Estructura de Datos:** Cada entrada de log debe incluir: [TIMESTAMP] [NIVEL: INFO/ERROR] [MENSAJE].
3. **Persistencia:** Si un script falla, el log debe ser lo último que se escriba antes de cerrar el proceso.

## 3. WORKFLOW (PROCESO)
1. **Inicio:** El script llama al Skill `logger.py`.
2. **Registro:** Durante la ejecución, se envían mensajes al logger.
3. **Cierre:** Se genera un archivo `.log` físico en `/executions`.

## 4. SALIDA
- Un archivo `scripts/logger_skill.py` (Módulo exportable).
- Un archivo de prueba `scripts/test_logger.py`.