# D001_Indexador.md

## METADATA
- **ID:** D001
- **Nombre:** Indexador de Arquitectura
- **Fecha de Creación:** 2026-02-08
- **Estado:** PENDIENTE DE CONSTRUCCIÓN
- **Prioridad:** ALTA (Infraestructura Core)

## 1. OBJETIVO
Desarrollar un script de Python ("Crawler Local") que mapee la totalidad de la estructura de directorios de `Antigravity_Home` para garantizar visibilidad total sobre el entorno de trabajo.

## 2. ENTRADA (INPUT)
- **Ruta Raíz:** `Antigravity_Home/`
- **Alcance:** Escaneo recursivo de las carpetas:
  - `/directivas`
  - `/scripts`
  - `/executions`

## 3. PROCESO LÓGICO
1. **Inicialización:** Definir la ruta base del proyecto.
2. **Recorrido (Walk):** Iterar sobre todos los directorios y archivos permitidos.
3. **Filtrado:** Ignorar archivos de sistema (ej. `.DS_Store`, `__pycache__`, `.git`).
4. **Detección:** Comparar contra un estado previo (si existe) para identificar "Archivos Nuevos".
5. **Formateo:** Estructurar la información en un árbol jerárquico de texto.

## 4. SALIDA (OUTPUT)
- **Archivo Destino:** `MAPA_SISTEMA.md` (Ubicado en la raíz).
- **Contenido Requerido:**
  - Encabezado con `Fecha` y `Hora` de la última actualización (Timestamp).
  - Estructura de árbol visual de las carpetas.
  - Lista de archivos contenidos en cada directorio.

## 5. RESTRICCIONES TÉCNICAS
- El script debe ser **idempotente** (ejecutarlo múltiples veces produce el mismo resultado actualizado).
- Manejo de errores: Si falta una carpeta core, debe notificarlo pero no romper la ejecución (Soft Fail).