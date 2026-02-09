# D010_Mantenimiento.md

## METADATA
- **ID:** D010
- **Nombre:** Sistema Inmunológico (Purga y Respaldo)
- **Estado:** PENDIENTE
- **Dependencias:** D001, D002

## 1. OBJETIVO (SKILL)
Gestionar el espacio en disco y la relevancia de los datos mediante la purga de logs antiguos y la rotación de archivos de datos.

## 2. REGLAS DE NEGOCIO
1. **Retención:** Mantener solo los últimos 30 días de logs en `/executions`.
2. **Respaldo:** Antes de purgar, el Brain (D003) debe extraer un resumen de "Lecciones Históricas" para no perder conocimiento.
3. **Optimización:** Comprimir archivos de datos antiguos en una carpeta `/archive`.