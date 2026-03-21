import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useAuth } from '../hooks/useAuth';



type TenantContextType = {
  tenantId: string | null;
  setTenantId: (id: string | null) => void;
  loadingTenant: boolean;
};

const TenantContext = createContext<TenantContextType>({
  tenantId: null,
  setTenantId: () => {},
  loadingTenant: true,
});

const STORAGE_KEY = '@Tenant:Id';

export const TenantProvider = ({ children }: { children: React.ReactNode }) => {
  const { profile } = useAuth();
  const [tenantId, setTenantIdState] = useState('tenant_agro_test');
  const [loadingTenant, setLoadingTenant] = useState(true);

  const persistTenant = useCallback(async (id: string | null) => {
    try {
      if (id) {
        await AsyncStorage.setItem(STORAGE_KEY, id);
      } else {
        await AsyncStorage.removeItem(STORAGE_KEY);
      }
    } catch (e) {
      console.warn('No se pudo persistir tenant_id localmente', e);
    }
  }, []);

  const setTenantId = useCallback(
    (id: string | null) => {
      setTenantIdState(id);
      void persistTenant(id);
    },
    [persistTenant],
  );

  useEffect(() => {
    const bootstrap = async () => {
      try {
        const stored = await AsyncStorage.getItem(STORAGE_KEY);
        if (stored && stored.trim() !== '') {
          setTenantIdState(stored);
        } else {
          setTenantIdState('tenant_agro_test'); // BYPASS ABSOLUTO
        }
      } finally {
        setLoadingTenant(false);
      }
    };
    void bootstrap();
  }, []);

  useEffect(() => {
    if (profile && (profile as any).org_id) {
      const derivedTenant = (profile as any).org_id as string;
      if (derivedTenant && derivedTenant !== tenantId) {
        setTenantId(derivedTenant);
      }
    }
  }, [profile, tenantId, setTenantId]);

  return (
    <TenantContext.Provider value={{ tenantId, setTenantId, loadingTenant }}>
      {children}
    </TenantContext.Provider>
  );
};

export const useTenant = () => useContext(TenantContext);

