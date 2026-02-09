import os
import shutil
import subprocess
from pathlib import Path

# Configuración de Rutas
PRIVATE_ROOT = Path(__file__).parent.parent.absolute()
PUBLIC_ROOT = PRIVATE_ROOT.parent / "Antigravity_Dashboard"
DOCS_SRC = PRIVATE_ROOT / "docs"

def deploy():
    print("🚀 Inmiciando Sincronización Frontend (D015)...")
    
    if not DOCS_SRC.exists():
        print("❌ Error: Carpeta /docs no encontrada en el proyecto privado.")
        return False
    
    if not PUBLIC_ROOT.exists():
        print(f"📁 Creando carpeta destino: {PUBLIC_ROOT}")
        PUBLIC_ROOT.mkdir(parents=True, exist_ok=True)
    
    # 1. Limpiar contenido viejo en la vitrina pública (excepto .git)
    print("🧹 Limpiando vitrina pública...")
    for item in PUBLIC_ROOT.iterdir():
        if item.name == ".git":
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()
    
    # 2. Copiar contenido nuevo
    print(f"📦 Copiando contenido desde {DOCS_SRC}...")
    for item in DOCS_SRC.iterdir():
        dest = PUBLIC_ROOT / item.name
        if item.is_dir():
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)
    
    # 3. Git Operations en el repo público
    print("🛰️ Sincronizando repositorio público...")
    try:
        # Verificar si es un repo git
        if not (PUBLIC_ROOT / ".git").exists():
            print("🌱 Inicializando repositorio git público...")
            subprocess.run(["git", "init"], cwd=str(PUBLIC_ROOT), check=True)
            # Aquí podrías añadir el remote si el usuario lo proporciona
        
        subprocess.run(["git", "add", "."], cwd=str(PUBLIC_ROOT), check=True)
        subprocess.run(["git", "commit", "-m", "UPDATE: Strategic Dashboard Sync (Automated)"], cwd=str(PUBLIC_ROOT), check=True)
        
        # El push fallará si no hay remote, pero el commit local es éxito
        print("✅ Sincronización local completada.")
        return True
    except Exception as e:
        print(f"⚠️ Error en Git del Dashboard: {e}")
        return True # Retornamos True porque los archivos ya se copiaron

if __name__ == "__main__":
    deploy()
