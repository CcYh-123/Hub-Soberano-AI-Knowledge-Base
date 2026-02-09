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
            if "|" in line:
                cells = [c.strip() for c in line.split("|") if c.strip() or line.count("|") > 1]
                if not cells: continue
                
                # Ignorar separadores de tabla
                if all(re.match(r'^[-:]+$', c) for c in cells):
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
                        # Resaltado de Oportunidades
                        cell_style = "px-6 py-4 whitespace-nowrap text-sm text-gray-700"
                        if "OPORTUNIDAD" in c:
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
    
    # Separadores
    html = html.replace('---', '<hr class="my-10 border-t border-gray-200">')
    
    # Párrafos
    html = html.replace('\n\n', '</p><p class="mb-4 text-gray-600">')
    
    return html

def generate_web():
    """Genera el index.html en la carpeta docs."""
    print("🌐 Iniciando Generación de Interfaz Web (D013)...")
    
    report_path = get_latest_report()
    if not report_path:
        print("❌ Error: No se encontró ningún reporte ejecutivo para convertir.")
        return False
    
    print(f"📄 Procesando reporte: {report_path.name}")
    md_content = report_path.read_text(encoding='utf-8')
    content_html = parse_md_to_html(md_content)
    
    # Template Maestro con Tailwind CSS
    template = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Antigravity - Strategic Console</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; background-color: #f8fafc; }}
        .glass {{ background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(10px); }}
    </style>
</head>
<body class="p-4 md:p-12">
    <div class="max-w-6xl mx-auto glass shadow-2xl rounded-3xl p-8 md:p-12 border border-white">
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-12">
            <div>
                <span class="text-indigo-600 font-bold tracking-widest text-xs uppercase mb-2 block">Enterprise Real Estate Intelligence</span>
                <h1 class="text-5xl font-extrabold text-slate-900 tracking-tight">Antigravity <span class="text-indigo-600">v1.3</span></h1>
            </div>
            <div class="mt-4 md:mt-0 text-right">
                <p class="text-sm text-slate-500">Última actualización</p>
                <p class="text-lg font-semibold text-slate-800">{datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            </div>
        </div>
        
        <div class="prose prose-slate max-w-none">
            {content_html}
        </div>
        
        <footer class="mt-20 pt-8 border-t border-slate-200 text-center text-slate-400 text-sm">
            <p>Antigravity System &copy; 2026 | Arquitectura Soberana React + Supabase + FastAPI</p>
        </footer>
    </div>
</body>
</html>"""
    
    # Asegurar carpeta docs
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Guardar index.html
    INDEX_HTML.write_text(template, encoding='utf-8')
    print(f"✅ Interfaz generada con éxito en: {INDEX_HTML}")
    return True

if __name__ == "__main__":
    generate_web()
