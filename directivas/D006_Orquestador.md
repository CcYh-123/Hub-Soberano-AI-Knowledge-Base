# D006_Orquestador.md

## METADATA
- **ID:** D006
- **Nombre:** Orquestador Central de Misiones
- **Estado:** PENDIENTE DE CONSTRUCCIÓN
- **Dependencias:** D001, D002, D003, D004, D005

## 1. OBJETIVO (SKILL)
Crear un punto de entrada único (`main.py`) que pueda ejecutar flujos completos (Scrape -> Log -> Brain -> Report) con un solo comando.

## 2. REGLAS DE NEGOCIO (RULES)
1. **Modularidad:** El orquestador no escribe lógica nueva; llama a los scripts existentes en `/scripts`.
2. **Resiliencia:** Si un paso del flujo falla, el orquestador debe llamar al Brain (D003) para documentar el error antes de detenerse.
3. **Reporte Automático:** Toda ejecución exitosa debe terminar generando un reporte en `/reports`.

## 3. WORKFLOW
1. **Entrada:** Recibe el nombre de la misión (ej. "FULL_CYCLE").
2. **Ejecución:** Dispara Scraper -> Brain -> Reporter en secuencia.
3. **Cierre:** Actualiza el Mapa del Sistema y sincroniza Git.