"""
-----------------------------------------------------------------------
SCRIPT: reporter_skill.py
DIRECTIVA: D005_Reporter
ROL: Generador de Reportes Inteligentes
-----------------------------------------------------------------------
"""
import os
import json
import uuid
from datetime import datetime
from pathlib import Path

# CONFIGURACIÓN
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
REPORTS_DIR = ROOT_DIR / "reports"
KNOWLEDGE_BASE = ROOT_DIR / "KNOWLEDGE_BASE.md"

# Crear carpeta /reports si no existe
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Importar logger de D002
try:
    from logger_skill import create_logger
    logger = create_logger("reporter_skill")
except ImportError:
    logger = None
    print("⚠️ Logger no disponible, usando fallback")


def log_event(level, message):
    """Wrapper para compatibilidad con el ecosistema."""
    if logger:
        if level == "INFO":
            logger.info(message)
        elif level == "ERROR":
            logger.error(message)
        elif level == "SUCCESS":
            logger.success(message)
        elif level == "WARNING":
            logger.warning(message)
    else:
        print(f"[{level}] {message}")


def read_data_files():
    """Lee todos los archivos JSON de /data."""
    log_event("INFO", "Leyendo archivos de datos desde /data")
    
    data_files = []
    
    if not DATA_DIR.exists():
        log_event("WARNING", "Carpeta /data no existe")
        return data_files
    
    json_files = list(DATA_DIR.glob("*.json"))
    
    if not json_files:
        log_event("WARNING", "No se encontraron archivos JSON en /data")
        return data_files
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                content = json.load(f)
                data_files.append({
                    'filename': json_file.name,
                    'path': str(json_file),
                    'data': content
                })
                log_event("INFO", f"Archivo cargado: {json_file.name}")
        except Exception as e:
            log_event("ERROR", f"Error leyendo {json_file.name}: {str(e)}")
    
    log_event("SUCCESS", f"{len(data_files)} archivos de datos cargados")
    return data_files


def read_knowledge_base():
    """Lee las lecciones aprendidas de KNOWLEDGE_BASE.md."""
    log_event("INFO", "Leyendo base de conocimiento")
    
    if not KNOWLEDGE_BASE.exists():
        log_event("WARNING", "KNOWLEDGE_BASE.md no existe")
        return None
    
    try:
        with open(KNOWLEDGE_BASE, 'r', encoding='utf-8') as f:
            content = f.read()
            log_event("SUCCESS", "Base de conocimiento cargada")
            return content
    except Exception as e:
        log_event("ERROR", f"Error leyendo KNOWLEDGE_BASE.md: {str(e)}")
        return None


def generate_insights(data_files, knowledge_content):
    """Genera insights cruzando datos con conocimiento."""
    insights = []
    
    # Insight 1: Resumen de datos
    total_files = len(data_files)
    successful_scrapes = sum(1 for d in data_files if d['data'].get('status') == 'success')
    
    insights.append({
        'tipo': 'Resumen de Extracción',
        'contenido': f"Se procesaron {total_files} archivos de datos, {successful_scrapes} extracciones exitosas."
    })
    
    # Insight 2: Análisis de timestamps
    timestamps = []
    for d in data_files:
        if 'timestamp' in d['data']:
            timestamps.append(d['data']['timestamp'])
    
    if timestamps:
        insights.append({
            'tipo': 'Análisis Temporal',
            'contenido': f"Datos recolectados entre {min(timestamps)} y {max(timestamps)}"
        })
    
    # Insight 3: Estado del conocimiento
    if knowledge_content:
        if "No se detectaron errores" in knowledge_content:
            insights.append({
                'tipo': 'Estado del Sistema',
                'contenido': "✅ El sistema opera sin errores detectados en el último análisis."
            })
        else:
            insights.append({
                'tipo': 'Estado del Sistema',
                'contenido': "⚠️ Se detectaron patrones de error. Revisar KNOWLEDGE_BASE.md para detalles."
            })
    
    return insights


def generate_report(data_files, knowledge_content, insights):
    """Genera el reporte ejecutivo en formato Markdown."""
    execution_id = str(uuid.uuid4())[:8].upper()
    timestamp = datetime.now()
    date_str = timestamp.strftime("%Y%m%d")
    datetime_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    report_filename = f"REPORTE_EJECUTIVO_{date_str}.md"
    report_path = REPORTS_DIR / report_filename
    
    log_event("INFO", f"Generando reporte: {report_filename}")
    
    # Construir contenido del reporte
    content = f"""# 📊 REPORTE EJECUTIVO ANTIGRAVITY

**Fecha de Generación:** {datetime_str}  
**ID de Ejecución:** {execution_id}  
**Generado por:** D005_Reporter

---

## 📈 Resumen Ejecutivo

Este reporte consolida los datos extraídos por el sistema Antigravity y las lecciones aprendidas por el Brain System.

---

## 📁 Datos Procesados

**Total de Archivos:** {len(data_files)}

"""
    
    # Añadir detalle de cada archivo de datos
    for i, data_file in enumerate(data_files, 1):
        content += f"### {i}. {data_file['filename']}\n"
        content += f"**Ruta:** `{data_file['path']}`\n\n"
        content += "**Contenido:**\n```json\n"
        content += json.dumps(data_file['data'], indent=2, ensure_ascii=False)
        content += "\n```\n\n"
    
    # Añadir insights
    content += "---\n\n## 💡 Insights Generados\n\n"
    
    for insight in insights:
        content += f"### {insight['tipo']}\n"
        content += f"{insight['contenido']}\n\n"
    
    # Añadir extracto de la base de conocimiento
    content += "---\n\n## 🧠 Extracto de Base de Conocimiento\n\n"
    
    if knowledge_content:
        # Extraer solo el resumen
        lines = knowledge_content.split('\n')
        summary_lines = []
        capture = False
        
        for line in lines:
            if "## 📊 Resumen de Análisis" in line:
                capture = True
            elif line.startswith("## ") and capture:
                break
            elif capture:
                summary_lines.append(line)
        
        if summary_lines:
            content += "\n".join(summary_lines).strip()
        else:
            content += "*Ver KNOWLEDGE_BASE.md para detalles completos.*"
    else:
        content += "*Base de conocimiento no disponible.*"
    
    # Footer
    content += f"""

---

## 📋 Metadata del Reporte

| Campo | Valor |
|-------|-------|
| **ID Ejecución** | {execution_id} |
| **Timestamp** | {datetime_str} |
| **Archivos Procesados** | {len(data_files)} |
| **Insights Generados** | {len(insights)} |
| **Directiva** | D005_Reporter |

---

*Este reporte fue generado automáticamente por el Sistema Antigravity.*
"""
    
    # Guardar reporte
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(content)
        log_event("SUCCESS", f"Reporte generado exitosamente: {report_filename}")
        return str(report_path)
    except Exception as e:
        log_event("ERROR", f"Error al guardar reporte: {str(e)}")
        return None


def generate_executive_report():
    """Función principal que ejecuta el flujo completo de generación."""
    print("\n" + "="*60)
    print("📊 REPORTER SKILL - Generación de Reporte Ejecutivo")
    print("="*60 + "\n")
    
    log_event("INFO", "Iniciando generación de reporte ejecutivo")
    
    # Paso 1: Leer datos
    print("📁 Paso 1: Leyendo datos de /data...")
    data_files = read_data_files()
    
    if not data_files:
        log_event("WARNING", "No hay datos para procesar")
        print("⚠️ No se encontraron datos. El reporte estará vacío.\n")
    
    # Paso 2: Leer base de conocimiento
    print("🧠 Paso 2: Leyendo base de conocimiento...")
    knowledge_content = read_knowledge_base()
    
    # Paso 3: Generar insights
    print("💡 Paso 3: Generando insights...")
    insights = generate_insights(data_files, knowledge_content)
    log_event("INFO", f"{len(insights)} insights generados")
    
    # Paso 4: Generar reporte
    print("📝 Paso 4: Generando reporte ejecutivo...")
    report_path = generate_report(data_files, knowledge_content, insights)
    
    # Guardar log
    if logger:
        logger.save()
    
    print("\n" + "="*60)
    if report_path:
        print(f"✅ Reporte generado exitosamente")
        print(f"📁 Ubicación: {report_path}")
    else:
        print("❌ Error al generar reporte")
    print("="*60 + "\n")
    
    return report_path


if __name__ == "__main__":
    generate_executive_report()
