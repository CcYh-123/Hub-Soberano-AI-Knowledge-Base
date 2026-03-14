from sqlmodel import Session, select, func
from database import engine, Product, PriceEvent
from math_engine import calculate_replacement_value, calculate_capital_gap
import yaml
import os

def load_tenant_config(tenant_id: str):
    """
    Carga la configuración del tenant desde config.yaml local.
    """
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    if not os.path.exists(config_path):
        # Default fallback si no existe el archivo
        return {"tasa_inflacion_diaria": 0.0016} # ~5% mensual
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    # Buscamos la config del tenant específico o el global
    tenant_data = config.get("tenants", {}).get(tenant_id, {})
    return {
        "tasa_inflacion_diaria": tenant_data.get("tasa_inflacion_diaria", 
                                                config.get("economy", {}).get("daily_inflation", 0.0016)),
        "alert_threshold_leak": tenant_data.get("alert_threshold_leak",
                                               config.get("economy", {}).get("alert_threshold_leak", 20.0))
    }

def audit_inventory_health(tenant_id: str):
    """
    Realiza la auditoría de salud del inventario para un inquilino.
    """
    with Session(engine) as session:
        # 1. Obtener todos los productos del tenant
        statement = select(Product).where(Product.tenant_id == tenant_id)
        products = session.exec(statement).all()
        
        if not products:
            return {
                "inventory_health_score": 100,
                "capital_leak": 0.0,
                "suggested_global_markup": 0.0,
                "message": "Sin inventario para auditar."
            }
        
        total_historical_value = 0.0
        total_replacement_value = 0.0
        
        tenant_conf = load_tenant_config(tenant_id)
        tasa_r = tenant_conf["tasa_inflacion_diaria"]
        
        for prod in products:
            # En una implementación real tendríamos la fecha de compra.
            # Aquí simularemos 15 días en stock según el estándar del proyecto.
            dias_t = 15 
            
            # Valor histórico (lo que pagó según DB)
            costo_h = prod.current_cost
            total_historical_value += costo_h
            
            # Valor de Reposición Real (Costo original proyectado por inflación del estante)
            # Nota: El usuario pidió comparar con el último price_event TAMBIÉN.
            # Buscaremos el último evento de precio para este SKU
            event_stmt = select(PriceEvent).where(
                PriceEvent.product_sku == prod.sku,
                PriceEvent.tenant_id == tenant_id
            ).order_by(PriceEvent.timestamp.desc()).limit(1)
            
            last_event = session.exec(event_stmt).first()
            
            # El costo de reposición es el mayor entre el mercado actual y la proyección inflacionaria
            costo_mercado = last_event.costo_nuevo if last_event else costo_h
            costo_proyectado = calculate_replacement_value(costo_h, dias_t, tasa_r)
            
            valor_rep = max(costo_mercado, costo_proyectado)
            total_replacement_value += valor_rep
            
        capital_leak = total_replacement_value - total_historical_value
        
        # Cálculo de Score de Salud (Proporcional a la brecha)
        # Si la brecha es 0, score es 100. Si pierde el 50% del valor, score cae.
        leak_ratio = (capital_leak / total_historical_value) if total_historical_value > 0 else 0
        health_score = max(0, 100 - (leak_ratio * 100))
        
        # Markup sugerido para recuperar la brecha
        suggested_markup = (capital_leak / total_historical_value * 100) if total_historical_value > 0 else 0
        
        return {
            "inventory_health_score": round(health_score, 2),
            "capital_leak": round(capital_leak, 2),
            "suggested_global_markup": round(suggested_markup, 2),
            "reference": {
                "total_historical": round(total_historical_value, 2),
                "total_replacement": round(total_replacement_value, 2)
            }
        }
