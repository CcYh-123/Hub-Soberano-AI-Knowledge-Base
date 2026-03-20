# 📓 Bitácora de Campo — ANTIGRAVITY AGRO

> Registro cronológico de hitos operativos del sistema.  
> Cada entrada representa un avance real, validado en campo, no en simulación.

---

## 🔥 Fase 5 FUEL — Conexión Bidireccional: Lenovo ↔ Android 9

**Fecha:** 20 de marzo de 2026  
**Hora de confirmación:** ~19:30 ART (UTC-3)  
**Estado:** ✅ HITO VALIDADO EN CAMPO

---

### Resumen Ejecutivo

El **Motor Mártir** es funcional en el campo.  
La Lenovo actúa como **servidor de inteligencia de precios local** y el Android 9 del Comandante consume esos datos en tiempo real a través de un túnel HTTP seguro — sin depender de infraestructura en la nube.

---

### Stack Técnico del Puente

| Componente | Tecnología | Estado |
|---|---|---|
| Servidor local | FastAPI + Uvicorn (Python 3.14) | 🟢 Online |
| Exposición remota | LocalTunnel (`lt --port 8000`) | 🟢 Online |
| Cliente móvil | React Native + Expo Go (Android 9) | 🟢 Conectado |
| Fuente de datos | `api_bridge.py` — datos calibrados Fase 3 | 🟢 Activo |
| Fallback Offline | SQLite local (`productos_agro_v2`) | 🛡️ Disponible |

---

### URL del Puente (Sesión 20/03/2026)

```
https://seven-humans-hang.loca.lt
```

> ⚠️ **Nota:** Las URLs de LocalTunnel son efímeras por sesión.  
> Para levantar un nuevo túnel: `lt --port 8000`  
> Actualizar `BRIDGE_URL` en `src/components/DashboardScreen.tsx` (línea ~24).

---

### Endpoints Validados

| Endpoint | Resultado |
|---|---|
| `GET /` | `200 OK` — Heartbeat confirmado |
| `GET /get-martires` | `200 OK` — JSON con 2 productos |

**Respuesta del handshake:**
```json
{
  "status": "ok",
  "fuente": "local_calibrado",
  "total": 2,
  "productos": [
    {
      "nombre": "Glifosato Martir",
      "costo_reposicion": 105.00,
      "precio_venta": 135.00,
      "ganancia": 30.00,
      "margen_pct": 22.22
    },
    {
      "nombre": "Fertilizante Urea",
      "costo_reposicion": 450.00,
      "precio_venta": 580.00,
      "ganancia": 130.00,
      "margen_pct": 22.41
    }
  ]
}
```

---

### Lógica del Motor Mártir (Fase 3 → Fase 5)

```
Margen = (Precio Venta - Costo Reposición) / Precio Venta × 100

Glifosato Mártir:  ($135 - $105) / $135 = 22.22%  🟢 Ganancia: $30/u
Fertilizante Urea: ($580 - $450) / $580 = 22.41%  🟢 Ganancia: $130/u
```

**Semáforo de Rentabilidad:**

| Umbral | Señal | Acción |
|---|---|---|
| Margen ≥ 20% | 🟢 Verde | Saludable — operar normal |
| 15% ≤ Margen < 20% | 🟡 Amarillo | Alerta — revisar costos |
| Margen < 15% | 🔴 Rojo | Riesgo — acción requerida |

---

### Arquitectura de Resiliencia (Bridge First)

```
[Android 9 - Expo Go]
        │
        ▼  fetch + header bypass-tunnel-reminder
[LocalTunnel: seven-humans-hang.loca.lt]
        │
        ▼  proxy HTTP
[Lenovo: FastAPI 0.0.0.0:8000]
        │
        ▼
[api_bridge.py → MARTIRES dict]
        │
   ✅ Responde JSON

   Si falla el bridge:
        │
        ▼
[SQLite Local: productos_agro_v2]
        │
   🛡️ Datos offline garantizados
```

---

### Archivos Clave del Hito

| Archivo | Rol |
|---|---|
| `scripts/api_bridge.py` | Servidor FastAPI — fuente de precios |
| `src/components/DashboardScreen.tsx` | Cliente móvil — Motor Mártir UI |
| `src/lib/localDb.ts` | SQLite local — fallback offline |

---

### Comandos para Reproducir el Hito

```powershell
# Terminal 1 — Servidor de precios
py -m uvicorn scripts.api_bridge:app --host 0.0.0.0 --port 8000

# Terminal 2 — Túnel público
lt --port 8000

# Terminal 3 — App móvil
npx expo start

# Verificar que el puente responde
Invoke-WebRequest -Uri 'http://localhost:8000/get-martires' -UseBasicParsing
```

---

### Firma del Hito

| Campo | Valor |
|---|---|
| **Comandante** | El usuario operativo del sistema |
| **Dispositivo servidor** | Lenovo (Windows, Python 3.14) |
| **Dispositivo cliente** | Android 9 (Expo Go) |
| **Red** | Wi-Fi Local + LocalTunnel |
| **Validado por** | Respuesta HTTP 200 confirmada en ambos extremos |
| **Fase completada** | Fase 5 — FUEL: El Puente de Datos |
| **Próxima fase** | Fase 6 — Sincronización automática de precios de mercado |

---

*"El Motor Mártir ya es funcional en el campo."*  
*— Comandante, 20 de marzo de 2026*

---
