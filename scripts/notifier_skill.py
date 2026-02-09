"""
Notifier Skill - Sistema de Notificaciones Externas
D009: Módulo para enviar reportes a servicios externos (Discord, Slack, Telegram)

Soporta:
- Webhooks configurados via .env (WEBHOOK_URL)
- Modo fallback con logging si no hay URL configurada
- Envío del último reporte generado en /reports
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Intentar importar requests
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Rutas absolutas
ROOT_DIR = Path(__file__).parent.parent
REPORTS_DIR = ROOT_DIR / "reports"
ENV_FILE = ROOT_DIR / ".env"
SCRIPTS_DIR = ROOT_DIR / "scripts"

# Añadir scripts al path para importar logger
sys.path.insert(0, str(SCRIPTS_DIR))

try:
    from logger_skill import create_logger
except ImportError:
    # Fallback si no se puede importar
    class FallbackLogger:
        def info(self, msg): print(f"[INFO] {msg}")
        def warning(self, msg): print(f"[WARNING] {msg}")
        def error(self, msg): print(f"[ERROR] {msg}")
        def success(self, msg): print(f"[SUCCESS] {msg}")
        def save(self): pass
    def create_logger(name): return FallbackLogger()


def load_env() -> dict:
    """
    Carga variables de entorno desde .env file.
    
    Returns:
        Diccionario con variables de entorno
    """
    env_vars = {}
    
    if ENV_FILE.exists():
        try:
            content = ENV_FILE.read_text(encoding='utf-8')
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip().strip('"').strip("'")
        except Exception as e:
            print(f"[WARNING] Error leyendo .env: {e}")
    
    return env_vars


def get_latest_report() -> tuple:
    """
    Obtiene el archivo de reporte más reciente en /reports.
    
    Returns:
        Tuple (path, content) del reporte más reciente, o (None, None) si no hay
    """
    if not REPORTS_DIR.exists():
        return None, None
    
    # Buscar archivos .md en reports
    report_files = list(REPORTS_DIR.glob("*.md"))
    
    if not report_files:
        return None, None
    
    # Ordenar por fecha de modificación (más reciente primero)
    report_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    latest = report_files[0]
    
    try:
        content = latest.read_text(encoding='utf-8')
        return latest, content
    except Exception as e:
        return latest, f"[ERROR leyendo reporte: {e}]"


def extract_summary(content: str, max_chars: int = 2000) -> str:
    """
    Extrae un resumen del contenido del reporte para notificación.
    
    Args:
        content: Contenido completo del reporte
        max_chars: Máximo de caracteres a enviar
        
    Returns:
        Resumen truncado si es necesario
    """
    if not content:
        return "Sin contenido de reporte."
    
    # Para Discord/Slack, limitar el tamaño
    if len(content) > max_chars:
        return content[:max_chars] + "\n\n... [Truncado - Ver reporte completo]"
    
    return content


def send_discord_notification(webhook_url: str, content: str, report_name: str) -> bool:
    """
    Envía notificación a Discord via webhook.
    
    Args:
        webhook_url: URL del webhook de Discord
        content: Contenido a enviar
        report_name: Nombre del archivo de reporte
        
    Returns:
        True si se envió exitosamente
    """
    if not REQUESTS_AVAILABLE:
        return False
    
    payload = {
        "username": "Antigravity Bot",
        "content": f"**📊 Reporte: {report_name}**\n\n```md\n{content}\n```"
    }
    
    # Discord tiene límite de 2000 chars, ajustar
    if len(payload["content"]) > 2000:
        payload["content"] = payload["content"][:1900] + "\n```\n... [Truncado]"
    
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        return response.status_code in [200, 204]
    except Exception as e:
        print(f"[ERROR] Fallo enviando a Discord: {e}")
        return False


def send_slack_notification(webhook_url: str, content: str, report_name: str) -> bool:
    """
    Envía notificación a Slack via webhook.
    """
    if not REQUESTS_AVAILABLE:
        return False
    
    payload = {
        "text": f"📊 *Reporte Antigravity: {report_name}*",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"```{extract_summary(content, 1500)}```"
                }
            }
        ]
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] Fallo enviando a Slack: {e}")
        return False


def send_generic_webhook(webhook_url: str, content: str, report_name: str) -> bool:
    """
    Envía notificación a un webhook genérico.
    """
    if not REQUESTS_AVAILABLE:
        return False
    
    payload = {
        "source": "Antigravity",
        "timestamp": datetime.now().isoformat(),
        "report_name": report_name,
        "summary": extract_summary(content, 2000)
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        return response.status_code in [200, 201, 204]
    except Exception as e:
        print(f"[ERROR] Fallo enviando webhook: {e}")
        return False


def detect_webhook_type(url: str) -> str:
    """
    Detecta el tipo de webhook basado en la URL.
    
    Returns:
        'discord', 'slack', o 'generic'
    """
    url_lower = url.lower()
    if 'discord' in url_lower:
        return 'discord'
    elif 'slack' in url_lower or 'hooks.slack' in url_lower:
        return 'slack'
    else:
        return 'generic'


def send_notification(logger=None) -> dict:
    """
    Función principal: envía el último reporte al webhook configurado.
    
    Args:
        logger: Instancia de AntigravityLogger (opcional)
        
    Returns:
        Diccionario con resultado de la operación
    """
    # Crear logger si no se proporciona
    if logger is None:
        logger = create_logger("notifier_d009")
    
    result = {
        'success': False,
        'mode': 'unknown',
        'message': '',
        'report_sent': None
    }
    
    logger.info("=== D009 NOTIFIER: Iniciando ===")
    
    # 1. Verificar si requests está disponible
    if not REQUESTS_AVAILABLE:
        logger.warning("Librería 'requests' no disponible. Instalar con: pip install requests")
        result['mode'] = 'fallback'
        result['message'] = 'requests no instalado'
    
    # 2. Cargar configuración (Prioridad: os.environ > .env)
    env_vars = load_env()
    webhook_url = os.getenv('WEBHOOK_URL') or env_vars.get('WEBHOOK_URL', '')
    
    # 3. Modo fallback si no hay URL
    if not webhook_url:
        logger.warning("WARNING: Notificación simulada - URL de Webhook no configurada")
        logger.info("Para configurar: añade WEBHOOK_URL=https://... en el archivo .env")
        result['mode'] = 'simulated'
        result['message'] = 'Webhook URL no configurada - notificación simulada'
        
        # Aún así, verificar que el reporte existe
        report_path, report_content = get_latest_report()
        if report_path:
            logger.info(f"Reporte detectado: {report_path.name}")
            logger.info(f"[SIMULADO] Se habría enviado: {len(report_content)} caracteres")
            result['report_sent'] = str(report_path.name)
            result['success'] = True
        else:
            logger.warning("No se encontraron reportes en /reports")
        
        logger.save()
        return result
    
    # 4. Obtener último reporte
    report_path, report_content = get_latest_report()
    
    if not report_path:
        logger.error("No se encontró ningún reporte en /reports")
        result['message'] = 'No hay reportes para enviar'
        logger.save()
        return result
    
    logger.info(f"Reporte a enviar: {report_path.name}")
    result['report_sent'] = report_path.name
    
    # 5. Detectar tipo de webhook y enviar
    webhook_type = detect_webhook_type(webhook_url)
    logger.info(f"Tipo de webhook detectado: {webhook_type}")
    
    summary = report_content
    
    # Detección de oportunidad inmobiliaria (v1.1)
    if "OPORTUNIDAD DE INVERSIÓN" in report_content:
        summary = "🚨 ¡Oportunidad detectada! Revisa el reporte adjunto.\n\n" + summary
    
    # Para Discord/Slack, limitar el tamaño
    
    if webhook_type == 'discord':
        success = send_discord_notification(webhook_url, summary, report_path.name)
    elif webhook_type == 'slack':
        success = send_slack_notification(webhook_url, summary, report_path.name)
    else:
        success = send_generic_webhook(webhook_url, summary, report_path.name)
    
    # 6. Registrar resultado
    if success:
        logger.success(f"Notificación enviada exitosamente a {webhook_type}")
        result['success'] = True
        result['mode'] = webhook_type
        result['message'] = f'Enviado a {webhook_type}'
    else:
        logger.error(f"Fallo al enviar notificación a {webhook_type}")
        result['mode'] = 'failed'
        result['message'] = f'Error enviando a {webhook_type}'
    
    logger.info("=== D009 NOTIFIER: Finalizado ===")
    logger.save()
    
    return result


def main():
    """Punto de entrada para ejecución desde línea de comandos."""
    print("\n" + "="*60)
    print("📣 NOTIFIER SKILL (D009) - Notificaciones Externas")
    print("="*60)
    
    result = send_notification()
    
    print(f"\n📊 Resultado: {result['mode']}")
    print(f"   Éxito: {'✅' if result['success'] else '❌'}")
    print(f"   Mensaje: {result['message']}")
    if result['report_sent']:
        print(f"   Reporte: {result['report_sent']}")
    
    print("="*60 + "\n")
    
    return 0 if result['success'] else 1


if __name__ == "__main__":
    sys.exit(main())
