# D008_Automatizacion.md

## METADATA
- **ID:** D008
- **Nombre:** Sistema de Ejecución Recurrente (Heartbeat)
- **Estado:** PENDIENTE DE CONSTRUCCIÓN
- **Dependencias:** D006 (Orquestador)

## 1. OBJETIVO (SKILL)
Crear un archivo de procesamiento por lotes (.bat) y un script de control que permita a Antigravity ejecutarse de forma programada sin intervención humana.

## 2. REGLAS DE NEGOCIO (RULES)
1. **Determinismo**: Debe usar el comando `py` explícitamente.
2. **Auto-Diagnóstico**: Antes de cada ejecución programada, debe correr el Indexador (D001) para validar que el mapa esté al día.
3. **Notificación**: Al finalizar la tarea programada, debe generar un reporte de "Salud de Tarea".

## 3. WORKFLOW
1. **Trigger**: El sistema se activa (vía Windows Task Scheduler).
2. **Ejecución**: Corre `antigravity_run.bat`.
3. **Validación**: El Brain (D003) analiza la ejecución automática para detectar fallos silenciosos.