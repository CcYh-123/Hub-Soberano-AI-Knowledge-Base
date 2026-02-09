"""
Cleaner Skill - Sistema Inmunológico de Antigravity
D010: Módulo de mantenimiento, purga y respaldo

Funciones:
- Purga de logs antiguos en /executions
- Archivado de datos históricos
- Extracción de lecciones antes de purgar
"""

import os
import sys
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# Rutas absolutas
ROOT_DIR = Path(__file__).parent.parent
EXECUTIONS_DIR = ROOT_DIR / "executions"
REPORTS_DIR = ROOT_DIR / "reports"
DATA_DIR = ROOT_DIR / "data"
ARCHIVE_DIR = ROOT_DIR / "archive"
SCRIPTS_DIR = ROOT_DIR / "scripts"

# Añadir scripts al path
sys.path.insert(0, str(SCRIPTS_DIR))

try:
    from logger_skill import create_logger
except ImportError:
    class FallbackLogger:
        def info(self, msg): print(f"[INFO] {msg}")
        def warning(self, msg): print(f"[WARNING] {msg}")
        def error(self, msg): print(f"[ERROR] {msg}")
        def success(self, msg): print(f"[SUCCESS] {msg}")
        def save(self): pass
    def create_logger(name): return FallbackLogger()


class SystemCleaner:
    """
    Sistema de limpieza y mantenimiento de Antigravity.
    
    Responsabilidades:
    - Purgar logs antiguos (>N días)
    - Archivar datos históricos
    - Mantener espacio en disco optimizado
    """
    
    def __init__(self, retention_days: int = 7):
        """
        Inicializa el limpiador.
        
        Args:
            retention_days: Días de retención para logs (default: 7)
        """
        self.retention_days = retention_days
        self.timestamp = datetime.now()
        self.logger = create_logger("cleaner_d010")
        self.stats = {
            'files_scanned': 0,
            'files_purged': 0,
            'files_archived': 0,
            'bytes_freed': 0,
            'errors': []
        }
    
    def _ensure_archive_dir(self):
        """Asegura que el directorio /archive exista."""
        if not ARCHIVE_DIR.exists():
            ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Creado directorio de archivo: {ARCHIVE_DIR}")
    
    def _get_file_age_days(self, file_path: Path) -> float:
        """
        Calcula la antigüedad de un archivo en días.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Edad en días (float)
        """
        try:
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            age = self.timestamp - mtime
            return age.total_seconds() / 86400  # Convertir a días
        except Exception:
            return 0
    
    def extract_lessons_from_logs(self, log_files: list) -> dict:
        """
        Extrae lecciones de logs antes de purgarlos.
        
        Args:
            log_files: Lista de archivos de log a analizar
            
        Returns:
            Diccionario con resumen de lecciones
        """
        lessons = {
            'total_logs': len(log_files),
            'error_count': 0,
            'success_count': 0,
            'common_errors': {},
            'date_range': {'start': None, 'end': None}
        }
        
        for log_file in log_files:
            try:
                content = log_file.read_text(encoding='utf-8')
                
                # Contar errores y éxitos
                lessons['error_count'] += content.count('[ERROR]')
                lessons['success_count'] += content.count('[SUCCESS]')
                
                # Extraer errores específicos
                for line in content.splitlines():
                    if '[ERROR]' in line:
                        error_type = line.split('[ERROR]')[-1].strip()[:50]
                        lessons['common_errors'][error_type] = \
                            lessons['common_errors'].get(error_type, 0) + 1
                
            except Exception as e:
                self.stats['errors'].append(f"Error leyendo {log_file.name}: {e}")
        
        return lessons
    
    def purge_old_logs(self, dry_run: bool = False) -> dict:
        """
        Purga logs más antiguos que retention_days.
        
        Args:
            dry_run: Si True, solo simula la purga sin borrar
            
        Returns:
            Estadísticas de la operación
        """
        self.logger.info(f"=== D010 CLEANER: Iniciando purga ===")
        self.logger.info(f"Retención: {self.retention_days} días")
        self.logger.info(f"Modo: {'SIMULACIÓN' if dry_run else 'ACTIVO'}")
        
        if not EXECUTIONS_DIR.exists():
            self.logger.warning("Directorio /executions no existe")
            return self.stats
        
        # Obtener todos los archivos de log
        log_files = list(EXECUTIONS_DIR.glob("*.log"))
        self.stats['files_scanned'] = len(log_files)
        
        self.logger.info(f"Archivos escaneados: {len(log_files)}")
        
        # Identificar archivos antiguos
        old_files = []
        for log_file in log_files:
            age_days = self._get_file_age_days(log_file)
            if age_days > self.retention_days:
                old_files.append(log_file)
        
        self.logger.info(f"Archivos antiguos (>{self.retention_days} días): {len(old_files)}")
        
        if not old_files:
            self.logger.success("No hay archivos para purgar")
            return self.stats
        
        # Extraer lecciones antes de purgar
        lessons = self.extract_lessons_from_logs(old_files)
        self.logger.info(f"Lecciones extraídas: {lessons['error_count']} errores, {lessons['success_count']} éxitos")
        
        # Purgar archivos
        for old_file in old_files:
            try:
                file_size = old_file.stat().st_size
                
                if not dry_run:
                    old_file.unlink()
                    self.logger.info(f"Purgado: {old_file.name}")
                else:
                    self.logger.info(f"[DRY-RUN] Se purgaría: {old_file.name}")
                
                self.stats['files_purged'] += 1
                self.stats['bytes_freed'] += file_size
                
            except Exception as e:
                self.stats['errors'].append(f"Error purgando {old_file.name}: {e}")
                self.logger.error(f"Error purgando {old_file.name}: {e}")
        
        self.logger.success(f"Purga completada: {self.stats['files_purged']} archivos, {self.stats['bytes_freed']} bytes liberados")
        
        return self.stats
    
    def archive_old_data(self, dry_run: bool = False) -> int:
        """
        Archiva datos antiguos en /archive.
        
        Args:
            dry_run: Si True, solo simula el archivado
            
        Returns:
            Número de archivos archivados
        """
        self._ensure_archive_dir()
        
        if not DATA_DIR.exists():
            return 0
        
        archived_count = 0
        cutoff_date = self.timestamp - timedelta(days=self.retention_days)
        
        for data_file in DATA_DIR.glob("*.json"):
            age_days = self._get_file_age_days(data_file)
            
            if age_days > self.retention_days:
                archive_path = ARCHIVE_DIR / data_file.name
                
                if not dry_run:
                    try:
                        shutil.move(str(data_file), str(archive_path))
                        self.logger.info(f"Archivado: {data_file.name}")
                        archived_count += 1
                    except Exception as e:
                        self.logger.error(f"Error archivando {data_file.name}: {e}")
                else:
                    self.logger.info(f"[DRY-RUN] Se archivaría: {data_file.name}")
                    archived_count += 1
        
        self.stats['files_archived'] = archived_count
        return archived_count
    
    def get_maintenance_report(self) -> str:
        """
        Genera un reporte de estado de mantenimiento.
        
        Returns:
            Reporte en formato markdown
        """
        report = f"""## 🛠️ Estado de Mantenimiento

**Fecha:** {self.timestamp.strftime("%Y-%m-%d %H:%M:%S")}
**Retención:** {self.retention_days} días

| Métrica | Valor |
|---------|-------|
| Archivos Escaneados | {self.stats['files_scanned']} |
| Archivos Purgados | {self.stats['files_purged']} |
| Archivos Archivados | {self.stats['files_archived']} |
| Espacio Liberado | {self.stats['bytes_freed']:,} bytes |
| Errores | {len(self.stats['errors'])} |

"""
        
        if self.stats['errors']:
            report += "### ⚠️ Errores Encontrados\n"
            for error in self.stats['errors'][:5]:
                report += f"- {error}\n"
        
        return report
    
    def run_maintenance(self, dry_run: bool = False) -> dict:
        """
        Ejecuta el ciclo completo de mantenimiento.
        
        Args:
            dry_run: Si True, solo simula las operaciones
            
        Returns:
            Estadísticas completas
        """
        print("\n" + "="*60)
        print("🛠️ CLEANER SKILL (D010) - Mantenimiento del Sistema")
        print("="*60)
        
        # Purgar logs antiguos
        self.purge_old_logs(dry_run)
        
        # Archivar datos antiguos
        self.archive_old_data(dry_run)
        
        # Mostrar resumen
        print(f"\n📊 Resumen de Mantenimiento:")
        print(f"   Archivos escaneados: {self.stats['files_scanned']}")
        print(f"   Archivos purgados: {self.stats['files_purged']}")
        print(f"   Archivos archivados: {self.stats['files_archived']}")
        print(f"   Espacio liberado: {self.stats['bytes_freed']:,} bytes")
        
        if self.stats['errors']:
            print(f"   ⚠️ Errores: {len(self.stats['errors'])}")
        
        print("="*60 + "\n")
        
        self.logger.save()
        
        return self.stats


def run_maintenance(retention_days: int = 7, dry_run: bool = False) -> dict:
    """
    Función de conveniencia para ejecutar mantenimiento.
    
    Args:
        retention_days: Días de retención
        dry_run: Si True, solo simula
        
    Returns:
        Estadísticas de mantenimiento
    """
    cleaner = SystemCleaner(retention_days)
    return cleaner.run_maintenance(dry_run)


def get_maintenance_status(retention_days: int = 7) -> str:
    """
    Obtiene el estado de mantenimiento sin ejecutar purga.
    
    Returns:
        Reporte de estado en markdown
    """
    cleaner = SystemCleaner(retention_days)
    
    # Solo escanear sin purgar
    if EXECUTIONS_DIR.exists():
        log_files = list(EXECUTIONS_DIR.glob("*.log"))
        cleaner.stats['files_scanned'] = len(log_files)
        
        old_count = 0
        for log_file in log_files:
            if cleaner._get_file_age_days(log_file) > retention_days:
                old_count += 1
        
        cleaner.stats['files_purged'] = old_count  # Candidatos a purga
    
    return cleaner.get_maintenance_report()


def main():
    """Punto de entrada para ejecución desde línea de comandos."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Antigravity Cleaner Skill (D010)')
    parser.add_argument('--days', type=int, default=7, help='Días de retención')
    parser.add_argument('--dry-run', action='store_true', help='Simular sin borrar')
    
    args = parser.parse_args()
    
    stats = run_maintenance(args.days, args.dry_run)
    
    return 0 if len(stats['errors']) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
