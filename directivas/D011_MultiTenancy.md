# 🌐 Directiva D011: Multi-Tenancy

**Estado:** Propuesta (Ready for implementation)
**Propósito:** Transformar Antigravity en un sistema SaaS (Software as a Service) capaz de aislar datos de múltiples clientes dentro de una misma infraestructura.

---

## 🏛️ Estándares de Aislamiento

1.  **Identidad de Tenant:** Cada cliente debe ser identificado por un `tenant_id` único (UUID v4 o slug alfanumérico).
2.  **Aislamiento de Persistencia:** Queda prohibido el almacenamiento de datos en archivos planos compartidos sin prefijo de tenant.
3.  **Seguridad de Acceso:** Cualquier operación de lectura o escritura (D018 - StorageEngine) DEBE requerir explícitamente el `tenant_id` en sus parámetros.
4.  **Trazabilidad:** Cada ejecución del orquestador (D006) debe estar vinculada a un tenant para propósitos de auditoría y facturación.

## 📊 Esquema de Base de Datos (SaaS Ready)

Se utilizará una base de datos relacional (SQLite para desarrollo local, PostgreSQL para producción) con el siguiente esquema lógico:

### 1. `tenants`
| Campo | Tipo | Descripción |
| --- | --- | --- |
| `id` | UUID (PK) | Identificador único del cliente |
| `name` | String | Nombre de la organización |
| `slug` | String (Unique) | Identificador legible para URLs/Configs |
| `created_at` | Timestamp | Fecha de alta |

### 2. `historical_data`
| Campo | Tipo | Descripción |
| --- | --- | --- |
| `id` | BigInt (PK) | ID único de registro |
| `tenant_id` | UUID (FK) | Vínculo con el cliente |
| `sector` | String | Sector de negocio (pharmacy, fashion, etc.) |
| `item_key` | String | Llave única del ítem dentro del sector |
| `price` | Float | Valor capturado |
| `timestamp` | Timestamp | Fecha exact de captura |
| `metadata` | JSONB | Datos adicionales (tendencias, flags) |

---

## 🚀 Flujo Operativo D011

1.  **Inyección:** El `tenant_id` se inyectará vía variables de entorno o argumentos de comando (`--tenant`).
2.  **Validación:** El orquestador validará la existencia del Tenant antes de disparar cualquier Skill.
3.  **Persistencia:** El Storage Engine filtrará automáticamente cualquier consulta SQL agregando `WHERE tenant_id = current_tenant`.

---
*Generado por el Arquitecto Senior de Antigravity.*
