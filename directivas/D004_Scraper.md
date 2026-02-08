# D004_Scraper.md

## METADATA
- **ID:** D004
- **Nombre:** Skill de Extracción de Datos (Scraper)
- **Estado:** PENDIENTE DE CONSTRUCCIÓN
- **Dependencias:** D001, D002, D003

## 1. OBJETIVO (SKILL)
Desarrollar una capacidad de extracción de datos web robusta que entregue resultados en JSON y registre cada intento en el sistema de logs.

## 2. REGLAS DE NEGOCIO (RULES)
1. **Seguridad:** Las APIs (como Apify) deben leerse desde el archivo `.env`. Nunca hardcoded.
2. **Determinismo:** Si una URL falla, el error debe ser capturado por el Logger (D002) y analizado por el Cerebro (D003).
3. **Estructura:** Los datos extraídos deben guardarse en una nueva carpeta `/data`.

## 3. WORKFLOW
1. **Petición:** El script recibe una URL.
2. **Extracción:** Ejecuta la lógica de scrape.
3. **Almacenamiento:** Guarda el resultado en `/data/raw_data.json`.
4. **Retroalimentación:** El Brain Skill analiza si la estructura del sitio cambió y actualiza la KNOWLEDGE_BASE.