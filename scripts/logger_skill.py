"""
Logger Skill - Sistema de Registro y Trazabilidad
D002: Módulo reutilizable para logging de actividades

REFACTORIZACIÓN A01 (2026-02-09):
- Ruta ROOT_DIR absoluta para garantizar persistencia
- Timestamp con milisegundos para evitar colisiones
- Modo 'a' (append) para inmutabilidad
"""

import os
from datetime import datetime
from pathlib import Path


# 🔧 FIX A01: Ruta absoluta usando __file__ para independencia de CWD
ROOT_DIR = Path(__file__).parent.parent
EXECUTIONS_DIR = ROOT_DIR / "executions"


class AntigravityLogger:
    """
    Sistema de logging inmutable con timestamps para trazabilidad completa.
    
    Reglas:
    - Inmutabilidad: Los logs nunca se sobrescriben
    - Estructura: [TIMESTAMP] [NIVEL] [MENSAJE]
    - Persistencia: El log se escribe antes de cerrar el proceso
    
    Refactorización A01:
    - Ruta absoluta garantizada vía ROOT_DIR
    - Timestamp con milisegundos para unicidad
    - Auto-creación de /executions
    """
    
    def __init__(self, script_name: str, executions_dir: Path = None):
        """
        Inicializa el logger para un script específico.
        
        Args:
            script_name: Nombre del script que usa el logger
            executions_dir: Ruta a /executions (default: usa ROOT_DIR/executions)
        """
        self.script_name = script_name
        
        # 🔧 FIX A01: Usar ruta absoluta por defecto
        self.executions_dir = executions_dir if executions_dir else EXECUTIONS_DIR
        
        # Asegurar que sea Path
        if isinstance(self.executions_dir, str):
            self.executions_dir = Path(self.executions_dir)
        
        self.log_entries = []
        
        # Verificar y crear carpeta /executions si no existe
        self._ensure_executions_dir()
        
        # 🔧 FIX A01: Timestamp con milisegundos para evitar colisiones
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        self.log_filename = f"{timestamp}_{script_name}.log"
        self.log_path = self.executions_dir / self.log_filename
        
        # Registrar inicio
        self.info(f"Logger inicializado para: {script_name}")
        self.info(f"Ruta de persistencia: {self.log_path}")
    
    def _ensure_executions_dir(self):
        """
        🔧 FIX A01: Verifica y crea /executions si no existe.
        Logging de la acción para trazabilidad.
        """
        if not self.executions_dir.exists():
            self.executions_dir.mkdir(parents=True, exist_ok=True)
            print(f"[SYSTEM] Carpeta creada: {self.executions_dir}")
        else:
            # Verificar que sea un directorio, no un archivo
            if not self.executions_dir.is_dir():
                raise ValueError(f"Ruta existe pero no es directorio: {self.executions_dir}")
    
    def _format_entry(self, level: str, message: str) -> str:
        """
        Formatea una entrada de log según el estándar D002.
        
        Args:
            level: Nivel del log (INFO, ERROR, SUCCESS, WARNING)
            message: Mensaje a registrar
            
        Returns:
            Entrada formateada: [TIMESTAMP] [NIVEL] [MENSAJE]
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Milisegundos
        return f"[{timestamp}] [{level}] {message}"
    
    def info(self, message: str):
        """Registra un mensaje informativo."""
        entry = self._format_entry("INFO", message)
        self.log_entries.append(entry)
        print(entry)  # También imprime en consola
    
    def error(self, message: str):
        """Registra un error."""
        entry = self._format_entry("ERROR", message)
        self.log_entries.append(entry)
        print(entry)
    
    def success(self, message: str):
        """Registra una operación exitosa."""
        entry = self._format_entry("SUCCESS", message)
        self.log_entries.append(entry)
        print(entry)
    
    def warning(self, message: str):
        """Registra una advertencia."""
        entry = self._format_entry("WARNING", message)
        self.log_entries.append(entry)
        print(entry)
    
    def save(self):
        """
        Persiste el log en disco.
        
        🔧 FIX A01: Usa modo 'a' (append) para inmutabilidad.
        Cada archivo es único por milisegundo, pero si hay colisión,
        el append garantiza que no se pierdan datos.
        """
        try:
            # 🔧 FIX A01: Modo 'a' para append en caso de colisión
            with open(self.log_path, 'a', encoding='utf-8') as f:
                f.write(f"# LOG: {self.script_name}\n")
                f.write(f"# Archivo: {self.log_filename}\n")
                f.write(f"# ROOT_DIR: {ROOT_DIR}\n")
                f.write("=" * 60 + "\n\n")
                f.write("\n".join(self.log_entries))
                f.write("\n\n" + "=" * 60 + "\n")
                f.write(f"# Total de entradas: {len(self.log_entries)}\n")
            
            final_msg = f"Log guardado exitosamente en: {self.log_path}"
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [SUCCESS] {final_msg}")
            return True
        except Exception as e:
            error_msg = f"Error al guardar log: {str(e)}"
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [ERROR] {error_msg}")
            return False
    
    def __enter__(self):
        """Soporte para context manager (with statement)."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Garantiza que el log se guarde incluso si hay errores."""
        if exc_type is not None:
            self.error(f"Excepción capturada: {exc_type.__name__}: {exc_val}")
        self.save()
        return False  # No suprime excepciones


# Función de conveniencia para uso rápido
def create_logger(script_name: str) -> AntigravityLogger:
    """
    Factory function para crear un logger rápidamente.
    Usa la ruta absoluta ROOT_DIR/executions por defecto.
    
    Args:
        script_name: Nombre del script
        
    Returns:
        Instancia de AntigravityLogger
    """
    return AntigravityLogger(script_name)


def get_root_dir() -> Path:
    """Devuelve la ruta raíz del proyecto (para uso externo)."""
    return ROOT_DIR


def get_executions_dir() -> Path:
    """Devuelve la ruta de /executions (para uso externo)."""
    return EXECUTIONS_DIR
