// expo-sqlite tipos en runtime; firma simplificada para evitar ruido de TS en entorno de scripts
// @ts-ignore
import * as SQLite from 'expo-sqlite';

const DB_NAME = 'database.db';



export type ProductoAgroRow = {
  id: number;
  nombre: string;
  costo_reposicion: number;
  precio_venta: number;
  tenant_id: string;
};

let dbInstance: any | null = null;

export const getDb = () => {
  if (!dbInstance) {
    // @ts-ignore API provista por Expo en runtime
    dbInstance = (SQLite as any).openDatabase(DB_NAME);
  }
  return dbInstance;
};

export const initLocalDb = (tenantId: string = 'demo-local'): Promise<void> => {
  const db = getDb();
  return new Promise((resolve, reject) => {
    db.transaction(
      tx => {
        tx.executeSql(
          `CREATE TABLE IF NOT EXISTS productos_agro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            costo_reposicion REAL NOT NULL DEFAULT 0,
            precio_venta REAL NOT NULL DEFAULT 0,
            tenant_id TEXT NOT NULL
          );`,
        );
        tx.executeSql(
          `CREATE INDEX IF NOT EXISTS idx_productos_agro_tenant
           ON productos_agro (tenant_id);`,
        );

        tx.executeSql(
          `CREATE TABLE IF NOT EXISTS logs_bloqueo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto TEXT NOT NULL,
            margen REAL NOT NULL,
            tenant_id TEXT NOT NULL,
            timestamp TEXT NOT NULL
          );`,
        );
        tx.executeSql(
          `CREATE INDEX IF NOT EXISTS idx_logs_bloqueo_tenant
           ON logs_bloqueo (tenant_id);`,
        );

        // Seed de producto de prueba para sincronizar con la DB de Python
        tx.executeSql(
          `INSERT INTO productos_agro (nombre, costo_reposicion, precio_venta, tenant_id)
           SELECT ?, ?, ?, ?
           WHERE NOT EXISTS (
             SELECT 1 FROM productos_agro
             WHERE nombre = ? AND tenant_id = ?
           );`,
          ['Glifosato Mártir', 100, 105, tenantId, 'Glifosato Mártir', tenantId],
        );
      },
      error => reject(error),
      () => resolve(),
    );
  });
};

export const listarProductosAgro = (tenantId: string): Promise<ProductoAgroRow[]> => {
  const db = getDb();
  return new Promise((resolve, reject) => {
    db.transaction(
      tx => {
        tx.executeSql(
          'SELECT id, nombre, costo_reposicion, precio_venta, tenant_id FROM productos_agro WHERE tenant_id = ?',
          [tenantId],
          (_txObj, result) => {
            resolve((result.rows._array || []) as ProductoAgroRow[]);
          },
        );
      },
      error => reject(error),
    );
  });
};

export const upsertProductoAgro = (
  nombre: string,
  costo_reposicion: number,
  precio_venta: number,
  tenantId: string,
): Promise<void> => {
  const db = getDb();
  return new Promise((resolve, reject) => {
    db.transaction(
      tx => {
        tx.executeSql(
          `INSERT INTO productos_agro (nombre, costo_reposicion, precio_venta, tenant_id)
           VALUES (?, ?, ?, ?)`,
          [nombre, costo_reposicion, precio_venta, tenantId],
        );
      },
      error => reject(error),
      () => resolve(),
    );
  });
};

export const insertBloqueoLog = (
  producto: string,
  margen: number,
  tenantId: string,
): Promise<void> => {
  const db = getDb();
  const ts = new Date().toISOString();
  return new Promise((resolve, reject) => {
    db.transaction(
      tx => {
        tx.executeSql(
          `INSERT INTO logs_bloqueo (producto, margen, tenant_id, timestamp)
           VALUES (?, ?, ?, ?)`,
          [producto, margen, tenantId, ts],
        );
      },
      error => reject(error),
      () => resolve(),
    );
  });
};

