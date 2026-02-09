"""
Heartbeat Skill - Validación de Salud del Sistema
D008: Módulo de monitoreo para ejecuciones automáticas

Función principal: Analizar logs recientes y reportar salud del sistema.
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Ruta absoluta al proyecto
ROOT_DIR = Path(__file__).parent.parent
EXECUTIONS_DIR = ROOT_DIR / "executions"
REPORTS_DIR = ROOT_DIR / "reports"


class HeartbeatMonitor:
    """
    Monitor de salud del sistema Antigravity.
    
    Analiza logs recientes para detectar:
    - Ejecuciones exitosas vs fallidas
    - Errores recurrentes
    - Tiempo desde última ejecución exitosa
    """
    
    def __init__(self):
        self.timestamp = datetime.now()
        self.health_status = {
            'timestamp': self.timestamp.isoformat(),
            'overall_health': 'UNKNOWN',
            'logs_analyzed': 0,
            'errors_found': 0,
            'success_found': 0,
            'last_execution': None,
            'issues': []
        }
    
    def check_executions_dir(self) -> bool:
        """Verifica que /executions exista y tenga contenido."""
        if not EXECUTIONS_DIR.exists():
            self.health_status['issues'].append("Carpeta /executions no existe")
            return False
        
        logs = list(EXECUTIONS_DIR.glob("*.log"))
        if not logs:
            self.health_status['issues'].append("No hay logs en /executions")
            return False
        
        return True
    
    def analyze_recent_logs(self, hours: int = 24) -> dict:
        """
        Analiza logs de las últimas N horas.
        
        Args:
            hours: Número de horas hacia atrás para analizar
            
        Returns:
            Diccionario con estadísticas de salud
        """
        if not self.check_executions_dir():
            self.health_status['overall_health'] = 'CRITICAL'
            return self.health_status
        
        cutoff_time = self.timestamp - timedelta(hours=hours)
        log_files = list(EXECUTIONS_DIR.glob("*.log"))
        
        recent_logs = []
        for log_file in log_files:
            # Extraer timestamp del nombre del archivo
            # Formato: YYYYMMDD_HHMMSS_ffffff_nombre.log
            try:
                filename = log_file.stem
                date_part = filename[:15]  # YYYYMMDD_HHMMSS
                log_time = datetime.strptime(date_part, "%Y%m%d_%H%M%S")
                
                if log_time > cutoff_time:
                    recent_logs.append({
                        'file': log_file,
                        'time': log_time,
                        'name': filename
                    })
            except (ValueError, IndexError):
                # Skip archivos con formato inválido
                continue
        
        # Ordenar por tiempo (más reciente primero)
        recent_logs.sort(key=lambda x: x['time'], reverse=True)
        
        self.health_status['logs_analyzed'] = len(recent_logs)
        
        if recent_logs:
            self.health_status['last_execution'] = recent_logs[0]['time'].isoformat()
        else:
            self.health_status['issues'].append(f"No hay logs en las últimas {hours} horas")
            self.health_status['overall_health'] = 'WARNING'
            return self.health_status
        
        # Analizar contenido de logs recientes
        for log_info in recent_logs[:10]:  # Analizar máximo 10 logs más recientes
            try:
                content = log_info['file'].read_text(encoding='utf-8')
                
                # Contar errores y éxitos
                error_count = content.count('[ERROR]')
                success_count = content.count('[SUCCESS]')
                
                self.health_status['errors_found'] += error_count
                self.health_status['success_found'] += success_count
                
            except Exception as e:
                self.health_status['issues'].append(f"Error leyendo {log_info['file'].name}: {e}")
        
        # Determinar salud general
        self._calculate_overall_health()
        
        return self.health_status
    
    def _calculate_overall_health(self):
        """Calcula el estado de salud general basado en métricas."""
        errors = self.health_status['errors_found']
        successes = self.health_status['success_found']
        issues = len(self.health_status['issues'])
        
        if errors > 10 or issues > 3:
            self.health_status['overall_health'] = 'CRITICAL'
        elif errors > 5 or issues > 1:
            self.health_status['overall_health'] = 'WARNING'
        elif errors > 0:
            self.health_status['overall_health'] = 'DEGRADED'
        elif successes > 0:
            self.health_status['overall_health'] = 'HEALTHY'
        else:
            self.health_status['overall_health'] = 'UNKNOWN'
    
    def generate_health_report(self) -> str:
        """
        Genera un reporte de salud en formato markdown.
        
        Returns:
            Ruta al archivo de reporte generado
        """
        timestamp_str = self.timestamp.strftime("%Y%m%d_%H%M%S")
        report_filename = f"HEALTH_REPORT_{timestamp_str}.md"
        report_path = REPORTS_DIR / report_filename
        
        # Determinar emoji según estado
        health_emoji = {
            'HEALTHY': '💚',
            'DEGRADED': '💛',
            'WARNING': '🟠',
            'CRITICAL': '🔴',
            'UNKNOWN': '⚪'
        }.get(self.health_status['overall_health'], '⚪')
        
        content = f"""# {health_emoji} Reporte de Salud - Antigravity

**Generado:** {self.timestamp.strftime("%Y-%m-%d %H:%M:%S")}
**Estado General:** {self.health_status['overall_health']}

---

## 📊 Métricas

| Métrica | Valor |
|---------|-------|
| Logs Analizados | {self.health_status['logs_analyzed']} |
| Errores Encontrados | {self.health_status['errors_found']} |
| Operaciones Exitosas | {self.health_status['success_found']} |
| Última Ejecución | {self.health_status['last_execution'] or 'N/A'} |

---

## 🔍 Issues Detectados

"""
        if self.health_status['issues']:
            for issue in self.health_status['issues']:
                content += f"- ⚠️ {issue}\n"
        else:
            content += "*No se detectaron issues.*\n"
        
        content += f"""
---

## 🎯 Recomendaciones

"""
        # Añadir recomendaciones según estado
        if self.health_status['overall_health'] == 'CRITICAL':
            content += "1. 🔴 **ACCIÓN URGENTE**: Revisar logs de errores inmediatamente\n"
            content += "2. 🔴 Ejecutar diagnóstico manual del sistema\n"
        elif self.health_status['overall_health'] == 'WARNING':
            content += "1. 🟠 Revisar errores recientes en /executions\n"
            content += "2. 🟠 Verificar conectividad y recursos\n"
        elif self.health_status['overall_health'] == 'DEGRADED':
            content += "1. 💛 Monitorear próximas ejecuciones\n"
            content += "2. 💛 Revisar errores menores cuando sea posible\n"
        else:
            content += "1. 💚 Sistema operando normalmente\n"
            content += "2. 💚 Mantener monitoreo regular\n"
        
        content += """
---

*Generado automáticamente por Heartbeat Skill (D008)*
"""
        
        # Guardar reporte
        report_path.write_text(content, encoding='utf-8')
        
        return str(report_path)
    
    def run_check(self, hours: int = 24, verbose: bool = True) -> bool:
        """
        Ejecuta el chequeo completo de salud.
        
        Args:
            hours: Horas hacia atrás para analizar
            verbose: Si debe imprimir resultados
            
        Returns:
            True si el sistema está saludable, False si hay problemas
        """
        if verbose:
            print("\n" + "="*60)
            print("💓 HEARTBEAT - Chequeo de Salud del Sistema")
            print("="*60)
        
        # Analizar logs
        self.analyze_recent_logs(hours)
        
        # Generar reporte
        report_path = self.generate_health_report()
        
        if verbose:
            health_emoji = {
                'HEALTHY': '💚',
                'DEGRADED': '💛',
                'WARNING': '🟠',
                'CRITICAL': '🔴',
                'UNKNOWN': '⚪'
            }.get(self.health_status['overall_health'], '⚪')
            
            print(f"\n{health_emoji} Estado General: {self.health_status['overall_health']}")
            print(f"📊 Logs Analizados: {self.health_status['logs_analyzed']}")
            print(f"❌ Errores: {self.health_status['errors_found']}")
            print(f"✅ Éxitos: {self.health_status['success_found']}")
            
            if self.health_status['issues']:
                print("\n⚠️ Issues detectados:")
                for issue in self.health_status['issues']:
                    print(f"   - {issue}")
            
            print(f"\n📁 Reporte guardado: {report_path}")
            print("="*60 + "\n")
        
        # Retornar True si está saludable
        return self.health_status['overall_health'] in ['HEALTHY', 'DEGRADED']


def check_health(hours: int = 24) -> dict:
    """
    Función de conveniencia para chequear la salud del sistema.
    
    Args:
        hours: Horas hacia atrás para analizar
        
    Returns:
        Diccionario con estado de salud
    """
    monitor = HeartbeatMonitor()
    monitor.run_check(hours)
    return monitor.health_status


def main():
    """Punto de entrada para ejecución desde línea de comandos."""
    monitor = HeartbeatMonitor()
    is_healthy = monitor.run_check()
    
    # Exit code: 0 si saludable, 1 si hay problemas
    return 0 if is_healthy else 1


if __name__ == "__main__":
    sys.exit(main())
