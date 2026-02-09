# D009_Notificaciones.md

## METADATA
- **ID:** D009
- **Nombre:** Sistema de Notificaciones Externas
- **Estado:** PENDIENTE
- **Dependencias:** D005 (Reporter), D008 (Automatización)

## 1. OBJETIVO (SKILL)
Integrar un servicio de mensajería (Webhook) para enviar el reporte de /reports directamente a un canal externo (Discord, Slack o Telegram).

## 2. REGLAS DE NEGOCIO
1. **Privacidad:** No enviar datos sensibles, solo el resumen del "Brain".
2. **Resiliencia:** Si la notificación falla, el Logger (D002) debe registrar el error para que el Brain aprenda por qué falló la red.