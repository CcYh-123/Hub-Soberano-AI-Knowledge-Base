# D007_Comunicador.md

## METADATA
- **ID:** D007
- **Nombre:** Skill de Notificaciones y Comunicación
- **Estado:** PENDIENTE DE CONSTRUCCIÓN
- **Dependencias:** D002, D005, D006

## 1. OBJETIVO (SKILL)
Habilitar la capacidad de enviar el resumen del `reports/REPORTE_EJECUTIVO.md` a un servicio externo mediante HTTP Requests.

## 2. REGLAS DE NEGOCIO (RULES)
1. **Seguridad**: Los Webhooks o Tokens deben estar en el `.env`.
2. **Prioridad**: Los errores críticos detectados por el Logger (D002) deben disparar una alerta inmediata.
3. **Brevedad**: Las notificaciones deben ser resúmenes ejecutivos, no el log completo.

## 3. WORKFLOW
1. **Detección**: El Orquestador (D006) finaliza una misión.
2. **Activación**: El Comunicador lee el último reporte generado.
3. **Envío**: Realiza un POST a la URL configurada.