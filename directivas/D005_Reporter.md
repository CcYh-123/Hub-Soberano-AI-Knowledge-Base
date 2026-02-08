# D005_Reporter.md

## METADATA
- **ID:** D005
- **Nombre:** Generador de Reportes y Dashboards
- **Estado:** PENDIENTE DE CONSTRUCCIÓN
- **Dependencias:** D001, D002, D003, D004

## 1. OBJETIVO (SKILL)
Transformar datos crudos de `/data` y lecciones de `KNOWLEDGE_BASE.md` en un reporte final en formato Markdown o PDF.

## 2. REGLAS DE NEGOCIO (RULES)
1. **Integridad:** El reporte debe incluir siempre la fecha de generación y el ID de la ejecución.
2. **Fuentes:** Solo puede usar datos validados que existan en `/data`.
3. **Distribución:** El archivo final se guardará en una nueva carpeta `/reports`.

## 3. WORKFLOW
1. **Recolección:** Lee los JSON de `/data`.
2. **Síntesis:** Cruza los datos con la base de conocimiento para añadir "Insights".
3. **Generación:** Crea el archivo `reports/REPORTE_EJECUTIVO_YYYYMMDD.md`.