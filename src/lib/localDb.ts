import * as SQLite from 'expo-sqlite';

const DB_NAME = 'database.db';

export type ProductoAgroRow = {
  id: number;
  nombre: string;
  costo_reposicion: number;
  precio_venta: number;
  tenant_id: string;
};

// Singleton db instance using new synchronous API
let dbInstance: SQLite.SQLiteDatabase | null = null;

export const getDb = () => {
  if (!dbInstance) {
    dbInstance = SQLite.openDatabaseSync(DB_NAME);
  }
  return dbInstance;
};

export const initLocalDb = async (tenantId: string = 'tenant_agro_test'): Promise<void> => {
  const db = getDb();
  
  await db.execAsync(
    `CREATE TABLE IF NOT EXISTS productos_agro_v2 (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      nombre TEXT NOT NULL,
      costo_reposicion REAL NOT NULL DEFAULT 0,
      precio_venta REAL NOT NULL DEFAULT 0,
      tenant_id TEXT NOT NULL
    );`
  );
  
  await db.execAsync(
    `CREATE INDEX IF NOT EXISTS idx_productos_agro_tenant_v2
     ON productos_agro_v2 (tenant_id);`
  );

  await db.execAsync(
    `CREATE TABLE IF NOT EXISTS logs_bloqueo (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      producto TEXT NOT NULL,
      margen REAL NOT NULL,
      tenant_id TEXT NOT NULL,
      timestamp TEXT NOT NULL
    );`
  );
  
  await db.execAsync(
    `CREATE INDEX IF NOT EXISTS idx_logs_bloqueo_tenant
     ON logs_bloqueo (tenant_id);`
  );

  // ─── SEMILLA DE MERCADO REAL (CALIBRACIÓN FASE 3) ──────────────────────
  // Glifosato: $135 (Venta) / $105 (Costo) => Margen: 22.22%
  // ─────────────────────────────────────────────────────────────────────────

  // INSERT para instalaciones limpias (primera vez)
  await db.runAsync(
    `INSERT INTO productos_agro_v2 (nombre, costo_reposicion, precio_venta, tenant_id)
     SELECT ?, ?, ?, ?
     WHERE NOT EXISTS (
       SELECT 1 FROM productos_agro_v2
       WHERE nombre = ? AND tenant_id = ?
     );`,
    ['Glifosato Mártir', 105, 135, 'tenant_agro_test', 'Glifosato Mártir', 'tenant_agro_test']
  );

  // UPDATE para dispositivos con la simulación anterior (100/105)
  // Esto garantiza que el precio real se aplique aunque la app ya esté instalada.
  await db.runAsync(
    `UPDATE productos_agro_v2
     SET costo_reposicion = 105, precio_venta = 135
     WHERE nombre = 'Glifosato Mártir'
       AND tenant_id = 'tenant_agro_test';`
  );
};

export const listarProductosAgro = async (tenantId: string): Promise<ProductoAgroRow[]> => {
  const db = getDb();
  // getAllAsync fetches rows directly mapped to the type
  const result = await db.getAllAsync<ProductoAgroRow>(
    'SELECT id, nombre, costo_reposicion, precio_venta, tenant_id FROM productos_agro_v2 WHERE tenant_id = ?',
    [tenantId]
  );
  return result || [];
};

export const upsertProductoAgro = async (
  nombre: string,
  costo_reposicion: number,
  precio_venta: number,
  tenantId: string,
): Promise<void> => {
  const db = getDb();
  await db.runAsync(
    `INSERT INTO productos_agro_v2 (nombre, costo_reposicion, precio_venta, tenant_id)
     VALUES (?, ?, ?, ?)`,
    [nombre, costo_reposicion, precio_venta, tenantId]
  );
};

export const insertBloqueoLog = async (
  producto: string,
  margen: number,
  tenantId: string,
): Promise<void> => {
  const db = getDb();
  const ts = new Date().toISOString();
  await db.runAsync(
    `INSERT INTO logs_bloqueo (producto, margen, tenant_id, timestamp)
     VALUES (?, ?, ?, ?)`,
    [producto, margen, tenantId, ts]
  );
};
