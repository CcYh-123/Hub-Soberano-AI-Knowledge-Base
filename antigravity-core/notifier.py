import httpx
from sqlmodel import Session, select
from database import engine, TenantConfiguration
import json

def register_webhook(tenant_id: str, webhook_url: str):
    """
    Registra o actualiza la URL de webhook para un inquilino.
    """
    with Session(engine) as session:
        statement = select(TenantConfiguration).where(TenantConfiguration.tenant_id == tenant_id)
        config = session.exec(statement).first()
        
        if config:
            config.webhook_url = webhook_url
        else:
            config = TenantConfiguration(tenant_id=tenant_id, webhook_url=webhook_url)
            session.add(config)
            
        session.commit()
    return {"status": "SUCCESS", "tenant_id": tenant_id}

async def send_alert(tenant_id: str, audit_summary: dict, report_id: str = None):
    """
    Envía una alerta conversacional al webhook registrado del tenant.
    """
    with Session(engine) as session:
        statement = select(TenantConfiguration).where(TenantConfiguration.tenant_id == tenant_id)
        config = session.exec(statement).first()
        
        if not config or not config.webhook_url:
            print(f"Skipping alert: No webhook registered for {tenant_id}")
            return
        
        capital_leak = audit_summary.get("capital_leak", 0)
        
        # Link de descarga si existe reporte
        download_url = f"http://localhost:8000/download-audit/{report_id}" if report_id else "N/A"
        
        # Payload conversacional para WhatsApp/Webhooks
        payload = {
            "tenant_id": tenant_id,
            "severity": "CRITICAL" if capital_leak > 100 else "WARNING",
            "message": f"⚠️ Alerta de Erosión: Se detectó una brecha de capital de ${capital_leak}.",
            "report_url": download_url,
            "action_url": f"https://antigravity.hub/update/{tenant_id}"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(config.webhook_url, json=payload, timeout=5.0)
                print(f"Alert sent to {tenant_id}. Status: {response.status_code}")
        except Exception as e:
            print(f"Failed to send alert to {tenant_id}: {e}")

if __name__ == "__main__":
    # Prueba rápida: Registrar y simular
    import asyncio
    register_webhook("tenant_test_001", "https://httpbin.org/post")
    asyncio.run(send_alert("tenant_test_001", {"capital_leak": 145.50}))
