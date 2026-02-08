"""
-----------------------------------------------------------------------
SCRIPT: comms_skill.py
DIRECTIVA: D007_Comunicador
ROL: Sistema de Notificaciones y Comunicación
-----------------------------------------------------------------------
"""
import os
import json
from datetime import datetime
from pathlib import Path

# Intentar cargar dotenv si está disponible
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# CONFIGURACIÓN
ROOT_DIR = Path(__file__).parent.parent
REPORTS_DIR = ROOT_DIR / "reports"

# Configuración de Webhook (desde .env)
WEBHOOK_URL = os.getenv("ANTIGRAVITY_WEBHOOK_URL", None)
WEBHOOK_ENABLED = os.getenv("ANTIGRAVITY_WEBHOOK_ENABLED", "false").lower() == "true"

# Importar logger de D002
try:
    from logger_skill import create_logger
    logger = create_logger("comms_skill")
except ImportError:
    logger = None


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


def send_notification(message: str, channel: str = "default") -> bool:
    """
    Envía una notificación a un canal externo.
    
    Por ahora imprime en consola. Preparado para usar Webhook real.
    
    Args:
        message: Mensaje a enviar
        channel: Canal de destino (default, critical, info)
        
    Returns:
        True si el envío fue exitoso
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_event("INFO", f"Preparando notificación para canal: {channel}")
    
    # Formato del mensaje
    formatted_message = f"[{timestamp}] [{channel.upper()}] {message}"
    
    # Simular envío a canal externo
    print("\n" + "📡" * 25)
    print(f">>> [COMMS] Enviando a Canal Externo: {message}")
    print("📡" * 25 + "\n")
    
    log_event("SUCCESS", f"Notificación enviada: {message[:50]}...")
    
    # Si hay webhook configurado, preparar para envío real
    if WEBHOOK_ENABLED and WEBHOOK_URL:
        return _send_to_webhook(formatted_message)
    
    return True


def send_critical_alert(error_message: str) -> bool:
    """
    Envía una alerta crítica inmediata.
    
    Args:
        error_message: Mensaje de error crítico
        
    Returns:
        True si el envío fue exitoso
    """
    log_event("WARNING", f"Alerta crítica disparada: {error_message}")
    
    alert = f"🚨 ALERTA CRÍTICA: {error_message}"
    
    print("\n" + "🚨" * 25)
    print(f">>> [COMMS/CRITICAL] {alert}")
    print("🚨" * 25 + "\n")
    
    return send_notification(alert, channel="critical")


def send_mission_summary(mission_name: str, success: bool, steps_completed: int) -> bool:
    """
    Envía un resumen de misión completada.
    
    Args:
        mission_name: Nombre de la misión
        success: Si la misión fue exitosa
        steps_completed: Número de pasos completados
        
    Returns:
        True si el envío fue exitoso
    """
    status = "✅ ÉXITO" if success else "❌ FALLIDA"
    
    message = f"Misión {mission_name}: {status} | Pasos: {steps_completed}"
    
    log_event("INFO", f"Enviando resumen de misión: {mission_name}")
    
    return send_notification(message, channel="missions")


def send_report_notification(report_path: str) -> bool:
    """
    Envía notificación de que un nuevo reporte fue generado.
    
    Args:
        report_path: Ruta al reporte generado
        
    Returns:
        True si el envío fue exitoso
    """
    report_name = Path(report_path).name if report_path else "Unknown"
    
    message = f"📊 Nuevo Reporte Generado: {report_name}"
    
    return send_notification(message, channel="reports")


def _send_to_webhook(message: str) -> bool:
    """
    Envía mensaje a un webhook configurado.
    
    Args:
        message: Mensaje a enviar
        
    Returns:
        True si el envío fue exitoso
    """
    if not WEBHOOK_URL:
        log_event("WARNING", "Webhook URL no configurada en .env")
        return False
    
    try:
        import requests
        
        payload = {
            "text": message,
            "timestamp": datetime.now().isoformat(),
            "source": "Antigravity System"
        }
        
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        
        if response.status_code == 200:
            log_event("SUCCESS", "Mensaje enviado a webhook exitosamente")
            return True
        else:
            log_event("ERROR", f"Webhook respondió con código: {response.status_code}")
            return False
            
    except ImportError:
        log_event("WARNING", "requests no instalado, usando modo simulación")
        return True
    except Exception as e:
        log_event("ERROR", f"Error enviando a webhook: {str(e)}")
        return False


def get_latest_report() -> str:
    """
    Obtiene el último reporte generado.
    
    Returns:
        Contenido del último reporte o None
    """
    if not REPORTS_DIR.exists():
        return None
    
    reports = sorted(REPORTS_DIR.glob("REPORTE_EJECUTIVO_*.md"), reverse=True)
    
    if not reports:
        return None
    
    try:
        with open(reports[0], 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        log_event("ERROR", f"Error leyendo reporte: {str(e)}")
        return None


def save_log():
    """Guarda el log del comunicador."""
    if logger:
        logger.save()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("📡 COMMS SKILL - Test de Comunicación")
    print("="*60 + "\n")
    
    # Test 1: Notificación básica
    print("Test 1: Notificación básica")
    send_notification("Mensaje de prueba del sistema Antigravity")
    
    # Test 2: Alerta crítica
    print("\nTest 2: Alerta crítica")
    send_critical_alert("Error de prueba para validar alertas")
    
    # Test 3: Resumen de misión
    print("\nTest 3: Resumen de misión")
    send_mission_summary("TEST_MISSION", True, 3)
    
    # Guardar log
    save_log()
    
    print("="*60)
    print("✅ Tests de comunicación completados")
    print("="*60 + "\n")
