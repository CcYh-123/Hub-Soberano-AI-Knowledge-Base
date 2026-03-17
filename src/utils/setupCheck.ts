import { fromTenant } from '../lib/supabase';



import { useTenant } from '../context/TenantContext';
import { Logger } from './Logger';

export const verifySupabaseSetup = async () => {
  // Se asume que este chequeo corre en un contexto React donde TenantProvider está montado.
  const { tenantId } = useTenant();
  const tablesToCheck = ['profiles', 'parcelas', 'movimientos_stock', 'insumos_stock'];
  const results: Record<string, boolean> = {};

  try {
    for (const table of tablesToCheck) {
      // Attempt a lightweight query to check existence
      const { error } = await fromTenant(table, tenantId).select('id').limit(0);
      
      if (error && error.code === '42P01') { // undefined_table
        results[table] = false;
        await Logger.log('ERROR', `Table ${table} is missing in Supabase`);
      } else {
        results[table] = true;
      }
    }
    return results;
  } catch (e: any) {
    await Logger.log('ERROR', 'Environment validation failed', e);
    throw e;
  }
};
