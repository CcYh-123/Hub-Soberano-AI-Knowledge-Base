import { createClient, PostgrestFilterBuilder } from '@supabase/supabase-js';
import AsyncStorage from '@react-native-async-storage/async-storage';




const supabaseUrl = process.env.SUPABASE_URL || '';
const supabaseAnonKey = process.env.SUPABASE_ANON_KEY || '';

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    storage: AsyncStorage,
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: false,
  },
});

// Helper para asegurar que TODAS las consultas de negocio pasen por tenant_id
export const fromTenant = <T = any>(
  table: string,
  tenantId: string | null | undefined,
): PostgrestFilterBuilder<T> => {
  const query = supabase.from<T>(table);
  return tenantId ? query.eq('tenant_id', tenantId) : query;
};

// Session Validation & Offline Handling Interceptor
export const handleSupabaseError = async (error: any, fallbackAction: () => Promise<void>) => {
  if (error?.message === 'JWT expired' || error?.status === 401) {
    console.warn('Sesión expirada o inválida. Guardando operación en cola local...');
    await fallbackAction(); // Save to AsyncStorage queue
    return { error: 'SESSION_EXPIRED_SAVED_LOCALLY' };
  }
  return { error };
};
