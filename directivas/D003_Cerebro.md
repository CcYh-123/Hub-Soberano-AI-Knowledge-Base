# D003_Cerebro.md

## METADATA
- **ID:** D003
- **Nombre:** Módulo de Aprendizaje y Refactorización (Cerebro)
- **Estado:** PENDIENTE DE CONSTRUCCIÓN
- **Dependencias:** D001 (Mapa), D002 (Logger)

## 1. OBJETIVO (SKILL)
Desarrollar un flujo que analice los archivos en `/executions` y extraiga "Lecciones Aprendidas" para actualizar automáticamente las directivas o reglas del sistema.

## 2. REGLAS DE NEGOCIO (RULES)
1. **Validación de Errores:** Si un log contiene la palabra "ERROR", el Cerebro debe identificar la causa raíz.
2. **Capitalización:** Si un script es exitoso, el Cerebro debe guardar el snippet de código útil en una base de conocimientos.
3. **No Duplicidad:** No se deben registrar lecciones repetidas; el sistema debe consolidar el conocimiento.

## 3. WORKFLOW (APRENDIZAJE)
1. **Lectura:** El sistema lee los logs de `/executions`.
2. **Análisis:** Identifica patrones de fallo (ej. comandos de terminal incorrectos).
3. **Actualización:** Escribe o modifica un archivo llamado `KNOWLEDGE_BASE.md` en la raíz.

## 4. SALIDA
- Archivo `scripts/brain_skill.py`.
- Archivo `KNOWLEDGE_BASE.md` (Base de Conocimiento).