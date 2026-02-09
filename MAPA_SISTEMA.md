# 🗺️ MAPA DEL SISTEMA ANTIGRAVITY
**Última Actualización:** 2026-02-09 09:23:05
**Directiva Base:** D001_Indexador
**Versión:** Nivel 9 (Sistema con Notificaciones Externas)

---

### 📂 /directivas
- 📄 D001_Indexador.md
- 📄 D002_Logger.md
- 📄 D003_Cerebro.md
- 📄 D004_Scraper.md
- 📄 D005_Reporter.md
- 📄 D006_Orquestador.md
- 📄 D007_Comunicador.md
- 📄 D008_Automatizacion.md
- 📄 D009_Notificaciones.md ✨ **NUEVO**


### 📂 /scripts
- 📄 brain_skill.py
- 📄 comms_skill.py
- 📄 heartbeat_skill.py
- 📄 logger_skill.py (FIX A01)
- 📄 notifier_skill.py ✨ **NUEVO**
- 📄 reporter_skill.py
- 📄 scraper_skill.py
- 📄 script_001_indexador.py
- 📄 test_brain.py
- 📄 test_logger.py


### 📂 /executions
*Logs de ejecución con timestamps únicos*


### 📂 /reports
*Reportes ejecutivos y de salud*


### 📂 / (Raíz)
- 📄 main.py (Orquestador D006 + Heartbeat D008 + Notifier D009)
- 📄 antigravity_run.bat - Lanzador para Task Scheduler
- 📄 .env - Configuración de webhooks (opcional)


---

## 🔗 Flujo de Automatización D008 + D009

```
[Windows Task Scheduler]
        │
        ▼
[antigravity_run.bat]
        │
        ├─▶ [D001] Indexador (Auto-Diagnóstico)
        │
        ├─▶ [D006] main.py (Orquestador)
        │       │
        │       ├─▶ D004 Scraper
        │       ├─▶ D003 Brain
        │       ├─▶ D005 Reporter
        │       ├─▶ D007 Comms (interno)
        │       ├─▶ D008 Heartbeat
        │       └─▶ D009 Notifier → [Discord/Slack/Webhook]
        │
        └─▶ [D008] Heartbeat (Validación Final)
```

---

## 🔧 Configuración de Webhooks (.env)

```env
# Discord Webhook
WEBHOOK_URL=https://discord.com/api/webhooks/...

# Slack Webhook  
# WEBHOOK_URL=https://hooks.slack.com/services/...

# Webhook genérico
# WEBHOOK_URL=https://api.example.com/webhook
```

---

*Sistema Antigravity - Nivel 9 con Notificaciones Externas*
