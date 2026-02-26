# 📄 DIRECTIVA D012: Monetización

**Estado:** ACTIVA
**Versión:** 1.0.0
**Rol:** Arquitecto de Ingresos

## 1. Misión
Transformar Antigravity de una herramienta táctica a un producto comercial (SaaS) mediante el control de acceso basado en suscripciones.

## 2. Niveles de Suscripción

| Nivel | Acceso | Restricciones |
|-------|--------|---------------|
| **Gratis** | Reportes Históricos, Dashboard Básico | No puede ejecutar Scraper, No puede usar el Simulador What-If. |
| **Pro** | Scraper Ilimitado, Simulador What-If, Exportación PDF | Acceso total a todas las herramientas de soberanía técnica. |

## 3. Reglas de Operación (Reglamento)
1. **Verificación Premisional**: El `Orquestador` debe consultar el `subscription_tier` del tenant antes de iniciar cualquier proceso de escritura o captura de datos.
2. **Puente API**: El `api_bridge.py` debe bloquear con `403 Forbidden` los endpoints restringidos para usuarios 'Free'.
3. **Flujo de Pago**: Integración con Stripe para convertir usuarios mediante un enlace de Checkout.
4. **Persistencia**: El estatus de suscripción se almacena en la tabla `tenants`.

## 4. Auditoría
- Logs de intentos de acceso denegados por nivel de suscripción.
- Eventos de 'Upgrade' capturados en el Logger (D002).
