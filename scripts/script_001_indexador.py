"""
-----------------------------------------------------------------------
SCRIPT: 001_indexador.py
DIRECTIVA: D001_Indexador
ROL: Crawler Local de Arquitectura
FECHA: 2026-02-08
-----------------------------------------------------------------------
"""

import os
import datetime

# 1. CONFIGURACIÓN
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_FILE = os.path.join(ROOT_DIR, "MAPA_SISTEMA.md")

TARGET_FOLDERS = ["directivas", "scripts", "executions"]
IGNORE_LIST = [".DS_Store", "__pycache__", ".git", ".env", "MAPA_SISTEMA.md", ".gitkeep"]

def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def scan_directory(base_path, target_folder):
    path_to_scan = os.path.join(base_path, target_folder)
    tree_str = f"\n### 📂 /{target_folder}\n"

    if not os.path.exists(path_to_scan):
        return f"\n### ⚠️ {target_folder} (NO ENCONTRADO)\n"
    
    for root, dirs, files in os.walk(path_to_scan):
        dirs[:] = [d for d in dirs if d not in IGNORE_LIST]
        dirs.sort()
        files.sort()

        level = root.replace(path_to_scan, '').count(os.sep)
        indent = ' ' * 4 * level
        
        if root != path_to_scan:
            tree_str += f"{indent}- 📁 **{os.path.basename(root)}/**\n"
            indent += ' ' * 4

        for f in files:
            if f not in IGNORE_LIST:
                tree_str += f"{indent}- 📄 {f}\n"
    return tree_str

def main():
    print(f"[{get_timestamp()}] Generando mapa...")
    content = [
        "# 🗺️ MAPA DEL SISTEMA ANTIGRAVITY",
        f"**Última Actualización:** {get_timestamp()}",
        f"**Directiva Base:** D001_Indexador",
        "\n---"
    ]

    for folder in TARGET_FOLDERS:
        content.append(scan_directory(ROOT_DIR, folder))

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))
    print(f"Done. Archivo creado en: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()