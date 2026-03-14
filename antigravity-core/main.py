from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from typing import List, Dict, Any
from sqlmodel import Session, select, desc
from database import get_session, PriceEvent, Product
from ingestor import process_vendor_list
from inventory_auditor import audit_inventory_health, load_tenant_config
from notifier import send_alert
from auth import get_current_tenant, create_access_token
from report_generator import generate_audit_report
import polars as pl
from datetime import datetime, timedelta
import os

app = FastAPI(
    title="Antigravity API", 
    version="2.0.0",
    description="SaaS Multi-tenant de Protección de Márgenes con Seguridad JWT"
)

# Endpoint para obtener Token (Simulación de Login para el Tenant)
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint para obtener un JWT. 
    En este MVP, el 'username' del formulario actúa como el 'tenant_id'.
    """
    tenant_id = form_data.username
    # En producción aquí validaríamos una API Key o contraseña vinculada al tenant
    access_token = create_access_token(data={"tenant_id": tenant_id})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/ingest")
async def ingest_data(
    data: List[Dict[str, Any]], 
    tenant_id: str = Depends(get_current_tenant),
    session: Session = Depends(get_session)
):
    """
    Recibe una lista de precios. El tenant_id se extrae automáticamente del Token JWT.
    """
    try:
        # 1. Procesar con el ingestor de Polars
        df = process_vendor_list(data, tenant_id)
        
        if df.is_empty():
            return {"status": "NO_DATA", "message": "No se recibieron datos procesables."}

        # 2. Calcular resúmenes (Aumentos)
        increases_df = df.filter(pl.col("delta_erosion") > 0)
        
        total_subieron = len(increases_df)
        perdida_estimada = increases_df["delta_erosion"].sum() if total_subieron > 0 else 0.0
        
        # 3. Guardar en Base de Datos (Eventos de Precio)
        records = df.to_dicts()
        
        for rec in records:
            event = PriceEvent(
                product_sku=rec["product_id"],
                costo_viejo=rec["costo_viejo"],
                costo_nuevo=rec["costo_nuevo"],
                delta_erosion=rec["delta_erosion"],
                tenant_id=tenant_id,
                timestamp=datetime.utcnow()
            )
            session.add(event)
            
        session.commit()

        # 4. Auditoría post-ingesta para detección de ALERTAS
        audit_report = audit_inventory_health(tenant_id)
        capital_leak = audit_report.get("capital_leak", 0)
        
        # Cargar umbral desde config
        tenant_conf = load_tenant_config(tenant_id)
        threshold = tenant_conf.get("alert_threshold_leak", 20.0)
        
        notified = False
        report_id = None
        if capital_leak > threshold:
            # OBTENER TOP 10 PRODUCTOS CRÍTICOS
            statement = select(PriceEvent).where(PriceEvent.tenant_id == tenant_id).order_by(desc(PriceEvent.delta_erosion)).limit(10)
            critical_events = session.exec(statement).all()
            critical_list = [
                {"product_sku": e.product_sku, "costo_viejo": e.costo_viejo, "costo_nuevo": e.costo_nuevo, "delta_erosion": e.delta_erosion}
                for e in critical_events
            ]
            
            # GENERAR PDF
            report_id = generate_audit_report(tenant_id, audit_report, critical_list)
            
            # ENVIAR ALERTA CON LINK
            await send_alert(tenant_id, audit_report, report_id)
            notified = True

        # 5. Respuesta basada en riesgo
        response_status = "ACTION_REQUIRED" if capital_leak > threshold else "STABLE"
        
        return {
            "tenant_id": tenant_id,
            "status": response_status,
            "notified": notified,
            "report_id": report_id,
            "summary": {
                "total_productos_subieron": total_subieron,
                "perdida_estimada_capital": round(perdida_estimada, 2),
                "current_capital_leak": capital_leak
            },
            "processed_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el procesamiento: {str(e)}")

@app.get("/audit")
async def get_inventory_audit(tenant_id: str = Depends(get_current_tenant)):
    """
    Realiza una auditoría de salud de capital. Solo accesible para el tenant del Token.
    """
    try:
        report = audit_inventory_health(tenant_id)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la auditoría: {str(e)}")

@app.get("/download-audit/{report_id}")
async def download_audit_report(report_id: str, tenant_id: str = Depends(get_current_tenant)):
    """
    Descarga segura del reporte PDF. 
    Valida que el reporte pertenezca al tenant del token (basado en el nombre de archivo).
    """
    # Seguridad básica: el nombre del archivo contiene el tenant_id
    if tenant_id not in report_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para acceder a este reporte.")
        
    file_path = os.path.join("reports", report_id)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="El reporte solicitado no existe.")
        
    return FileResponse(file_path, media_type="application/pdf", filename=report_id)

@app.get("/health")
def health_check():
    return {"status": "HEALTHY", "timestamp": datetime.utcnow().isoformat()}

@app.get("/status")
def get_status():
    return {"status": "ONLINE", "system": "ANTIGRAVITY_CORE", "security": "JWT_ENABLED"}
