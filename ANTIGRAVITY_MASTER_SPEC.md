# 🛰️ Hybrid SaaS: Event-Driven Pricing Engine with Continuous Inflation-Adjusted Margin Protection
**Nombre Comercial**: Antigravity Hub | **Versión**: 2.2 | **Nivel**: 9/10

## 1. ESTADO ACTUAL
- Motor matemático de capitalización continua ($e^{rt}$) operativo.
- Margin Guardian y Price Rule Executor funcionales.
- Dashboard V2 con simulación What-If y Profit Gap Widget activo.

## 2. PRIORIDADES TÁCTICAS (NUEVO ORDEN)
- **P1: Fase 8 — Parametrización Total (INICIAR AHORA)**: Desacoplar variables fijas (5% inflación, 25% margen) a un archivo `config.yaml`.
- **P2: Fase 10 — Deploy & DB Migration**: Preparar el salto de SQLite a PostgreSQL (Supabase) y deploy a la nube.
- **P3: Fase 9 — Login + Onboarding**: Implementar multi-tenancy y autenticación.
- **P4: Fase 7 — EventBus**: Migrar a arquitectura asincrónica orientada a eventos.

## 3. INSTRUCCIÓN OPERATIVA
Identificar todos los 'hardcodes' en los scripts de la carpeta `scripts/` (especialmente tasas de inflación y márgenes objetivo) y centralizarlos en un sistema de configuración dinámico.
