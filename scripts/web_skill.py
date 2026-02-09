import os
import re
from pathlib import Path
from datetime import datetime

# Configuración de Rutas
ROOT_DIR = Path(__file__).parent.parent.absolute()
REPORTS_DIR = ROOT_DIR / "reports"
DOCS_DIR = ROOT_DIR / "docs"
INDEX_HTML = DOCS_DIR / "index.html"

def get_latest_report():
    """Busca el REPORTE_EJECUTIVO más reciente."""
    reports = list(REPORTS_DIR.glob("REPORTE_EJECUTIVO_*.md"))
    if not reports:
        return None
    return max(reports, key=os.path.getmtime)

def parse_md_to_html(md_content):
    """Convierte Markdown básico de Antigravity a HTML."""
    html = md_content
    
    # Títulos
    html = re.sub(r'^# (.*)$', r'<h1 class="text-4xl font-bold text-indigo-700 mb-6 border-b-2 border-indigo-200 pb-2">\1</h1>', html, flags=re.M)
    html = re.sub(r'^## (.*)$', r'<h2 class="text-2xl font-semibold text-indigo-600 mt-8 mb-4">\1</h2>', html, flags=re.M)
    html = re.sub(r'^### (.*)$', r'<h3 class="text-xl font-medium text-gray-800 mt-6 mb-2">\1</h3>', html, flags=re.M)
    
    # Tablas (Especial para Antigravity)
    if "|" in html:
        lines = html.split('\n')
        new_lines = []
        in_table = False
        for line in lines:
            if "|" in line.strip():
                # Limpiar celdas ignorando los pipes de los extremos si existen
                cells = [c.strip() for c in line.split("|")]
                if not cells[0]: cells = cells[1:]
                if cells and not cells[-1]: cells = cells[:-1]
                
                if not cells: continue
                
                # Ignorar separadores de tabla (---)
                if all(re.match(r'^[-: ]+$', c) for c in cells):
                    continue
                
                if not in_table:
                    new_lines.append('<div class="overflow-x-auto my-6 shadow-md rounded-lg"><table class="min-w-full divide-y divide-gray-200">')
                    new_lines.append('<thead class="bg-indigo-50"><tr>')
                    for c in cells:
                        new_lines.append(f'<th class="px-6 py-3 text-left text-xs font-medium text-indigo-800 uppercase tracking-wider">{c}</th>')
                    new_lines.append('</tr></thead><tbody class="bg-white divide-y divide-gray-200">')
                    in_table = True
                else:
                    new_lines.append('<tr>')
                    for c in cells:
                        # Resaltado de Oportunidades y Alertas
                        cell_style = "px-6 py-4 whitespace-nowrap text-sm text-gray-700"
                        if "OPORTUNIDAD" in c or "ALERTA" in c:
                            cell_style += " font-bold text-red-600 bg-red-50"
                        new_lines.append(f'<td class="{cell_style}">{c}</td>')
                    new_lines.append('</tr>')
            else:
                if in_table:
                    new_lines.append('</tbody></table></div>')
                    in_table = False
                new_lines.append(line)
        html = '\n'.join(new_lines)

    # Negritas
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong class="font-bold">\1</strong>', html)
    
    # Listas
    html = re.sub(r'^- (.*)$', r'<li class="ml-4 mb-2 list-disc text-gray-700">\1</li>', html, flags=re.M)
    
    # Separadores (Evitar romper tablas si ya se procesaron)
    if not in_table:
        html = re.sub(r'^---$', r'<hr class="my-10 border-t border-gray-200">', html, flags=re.M)
    
    # Párrafos (Solo si no es parte de una tabla)
    # html = html.replace('\n\n', '</p><p class="mb-4 text-gray-600">')
    
    return html

def load_sector_config():
    """Carga la configuración del sector activo."""
    config_path = ROOT_DIR / "config_sector.json"
    if not config_path.exists():
        return None
    try:
        import json
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config
    except:
        return None

def generate_web():
    """Genera el index.html en la carpeta docs."""
    print("🌐 Iniciando Generación de Interfaz Web Multi-Sector (D014)...")
    
    config = load_sector_config()
    active_sector_key = config.get('active_sector', 'real_estate') if config else 'real_estate'
    sectors = config.get('sectors', {}) if config else {}
    active_sector = sectors.get(active_sector_key, {})
    
    sector_name = active_sector.get('name', 'General')
    sector_icon = active_sector.get('icon', '📊')
    
    report_path = get_latest_report()
    if not report_path:
        print("❌ Error: No se encontró ningún reporte ejecutivo para convertir.")
        return False
    
    print(f"📄 Procesando reporte: {report_path.name}")
    md_content = report_path.read_text(encoding='utf-8')
    content_html = parse_md_to_html(md_content)
    
    # Generar Links de Navegación
    nav_links = ""
    for skey, sdata in sectors.items():
        is_active = skey == active_sector_key
        bg_class = "bg-indigo-600 text-white shadow-lg scale-105" if is_active else "text-slate-500 hover:text-indigo-600 hover:bg-white/50"
        nav_links += f"""<a href="#" onclick="switchSector('{skey}')" class="px-4 py-2 rounded-full text-sm font-bold transition-all duration-300 {bg_class}">{sdata['icon']} {sdata['name'].upper()}</a>"""

    # Script para interactividad (D017)
    script_js = f"""
    <script>
    function switchSector(key) {{
        const activeSector = "{active_sector_key}";
        if (key !== activeSector) {{
            alert("⚠️ El sector " + key.toUpperCase() + " no es el foco actual.\\n\\nSolicita a Antigravity: 'Cambia el sector activo a " + key + "' para visualizar su inteligencia comercial.");
        }}
    }}
    </script>
    """

    # Template Maestro con Tailwind CSS
    template = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Antigravity - Multi-Sector Console</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; background-color: #f1f5f9; }}
        .glass {{ background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); }}
        .nav-glass {{ background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(5px); }}
    </style>
</head>
<body class="p-0">
    <!-- Navegación Superior -->
    <nav class="sticky top-0 z-50 nav-glass border-b border-gray-200 py-4 px-8 mb-8">
        <div class="max-w-6xl mx-auto flex justify-between items-center">
            <div class="flex items-center space-x-2">
                <div class="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white font-bold">A</div>
                <span class="font-bold text-slate-800 tracking-tight">Antigravity</span>
            </div>
            <div class="flex space-x-2">
                {nav_links}
            </div>
        </div>
    </nav>

    <div class="max-w-6xl mx-auto glass shadow-2xl rounded-3xl p-8 md:p-12 border border-white mb-12">
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-12">
            <div>
                <span class="text-indigo-600 font-bold tracking-widest text-xs uppercase mb-2 block">Enterprise {sector_name} Intelligence</span>
                <h1 class="text-5xl font-extrabold text-slate-900 tracking-tight">Antigravity <span class="text-indigo-600">v1.4</span></h1>
            </div>
            <div class="mt-4 md:mt-0 text-right">
                <p class="text-sm text-slate-500">Última actualización</p>
                <p class="text-lg font-semibold text-slate-800">{datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            </div>
        </div>
        
        <div class="prose prose-slate max-w-none">
            {content_html}
        </div>
        {script_js}
        
        <footer class="mt-20 pt-8 border-t border-slate-200 text-center text-slate-400 text-sm">
            <p>Antigravity System &copy; 2026 | Arquitectura Multi-Sector D014</p>
        </footer>
    </div>
</body>
</html>"""
    
    # Asegurar carpeta docs
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Guardar index.html
    INDEX_HTML.write_text(template, encoding='utf-8')
    print(f"✅ Interfaz Multi-Sector generada con éxito en: {INDEX_HTML}")
    return True

if __name__ == "__main__":
    generate_web()

if __name__ == "__main__":
    generate_web()
