"""
Logger Skill - Sistema de Registro y Trazabilidad
D002: Módulo reutilizable para logging de actividades
"""

import os
from datetime import datetime
from pathlib import Path


class AntigravityLogger:
    """
    Sistema de logging inmutable con timestamps para trazabilidad completa.
    
    Reglas:
    - Inmutabilidad: Los logs nunca se sobrescriben
    - Estructura: [TIMESTAMP] [NIVEL] [MENSAJE]
    - Persistencia: El log se escribe antes de cerrar el proceso
    """
    
    def __init__(self, script_name: str, executions_dir: str = "../executions"):
        """
        Inicializa el logger para un script específico.
        
        Args:
            script_name: Nombre del script que usa el logger
            executions_dir: Ruta relativa o absoluta a la carpeta /executions
        """
        self.script_name = script_name
        self.executions_dir = Path(executions_dir)
        self.log_entries = []
        
        # Crear carpeta /executions si no existe
        self.executions_dir.mkdir(parents=True, exist_ok=True)
        
        # Generar nombre de archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        self.log_filename = f"{timestamp}_{script_name}.log"
        self.log_path = self.executions_dir / self.log_filename
        
        # Registrar inicio
        self.info(f"Logger inicializado para: {script_name}")
    
    def _format_entry(self, level: str, message: str) -> str:
        """
        Formatea una entrada de log según el estándar D002.
        
        Args:
            level: Nivel del log (INFO, ERROR, SUCCESS, WARNING)
            message: Mensaje a registrar
            
        Returns:
            Entrada formateada: [TIMESTAMP] [NIVEL] [MENSAJE]
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
        Debe llamarse al finalizar el script para garantizar inmutabilidad.
        """
        try:
            with open(self.log_path, 'w', encoding='utf-8') as f:
                f.write(f"# LOG: {self.script_name}\n")
                f.write(f"# Archivo: {self.log_filename}\n")
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
    
    Args:
        script_name: Nombre del script
        
    Returns:
        Instancia de AntigravityLogger
    """
    return AntigravityLogger(script_name)
