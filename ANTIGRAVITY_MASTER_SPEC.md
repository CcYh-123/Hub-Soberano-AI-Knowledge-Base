# 🛰️ ANTIGRAVITY: Multi-Tenant Margin Protection (v2026)
**Arquitectura**: Monolito Modular ("Lasaña") | **Seguridad**: RLS Native (PostgreSQL)

## 1. DEFINICIÓN DE ACTIVO
Sistema de defensa financiera para farmacias que detecta erosión de capital mediante el cálculo de $e^{rt}$ y comparación de deltas de costo en tiempo real.

## 2. ESTRUCTURA MULTI-TENANT (AISLAMIENTO TOTAL)
Todas las tablas DEBEN contener la columna `tenant_id` para cumplir con el esquema de aislamiento lógico.
- **Table Products**: `id, tenant_id, sku, name, current_cost, sale_price`
- **Table Price_Events**: `id, tenant_id, product_id, old_cost, new_cost, delta, timestamp`

## 3. PRIORIDADES FASE 3 (MAÑANA)
- **P1: Ingestor Quirúrgico**: Script `ingestor.py` usando Polars para procesar listas con `tenant_id` inyectado.
- **P2: Parametrización por Inquilino**: Configuración `config.yaml` que asocie márgenes y tasas de inflación a cada `tenant_id`.
- **P3: Invisible Driver**: Generar el JSON de salida para el bot de WhatsApp (Alerta de pérdida real).

## 4. REGLA DE ORO
"Main es sagrado". No se sube código que no pase la validación de aislamiento de datos.