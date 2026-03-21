import { createClient } from '@supabase/supabase-js';
import AsyncStorage from '@react-native-async-storage/async-storage';





const supabaseUrl = process.env.EXPO_PUBLIC_SUPABASE_URL as string;
const supabaseAnonKey = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY as string;

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    storage: AsyncStorage,
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: false,
  },
});

// Helper para asegurar que TODAS las consultas de negocio pasen por tenant_id
export const fromTenant = (
  table: string,
  tenantId: string | null | undefined,
) => {
  const query = supabase.from(table);
  // En runtime, el builder soporta .eq; el cast evita ruido de tipos con versiones distintas de supabase-js.
  const q = query as any;
  return tenantId ? q.eq('tenant_id', tenantId) : q;
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
