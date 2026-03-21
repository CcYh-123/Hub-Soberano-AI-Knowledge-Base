import { useState, useCallback } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { generateUUID } from '../utils/uuid';
import { ApplicationRecord, ApplicationInsumo, WeatherData } from '../data/stock';
import { handleSupabaseError } from '../lib/supabase';
import { Logger } from '../utils/Logger';

const APPLICATIONS_STORAGE_KEY = '@Registry:Applications';
const PARCEL_EXPENSES_PREFIX = '@Expenses:Parcel:';

export const useFieldApplication = () => {
  const [isSaving, setIsSaving] = useState(false);

  const saveApplication = useCallback(async (
    parcelId: string,
    nombreParcela: string,
    superficie: number,
    insumos: ApplicationInsumo[],
    clima: WeatherData
  ) => {
    setIsSaving(true);
    try {
      const id = generateUUID();
      const costoTotal = insumos.reduce((acc, curr) => acc + curr.costoTotal, 0);
      
      const record: ApplicationRecord = {
        id,
        parcelaId: parcelId,
        nombreParcela,
        superficieProductiva: superficie,
        fecha: new Date().toISOString(),
        insumos,
        clima,
        costoTotalAplicacion: parseFloat(costoTotal.toFixed(3)),
        sincronizado: false,
      };

      // 1. Save to global application registry
      const existingAppsStr = await AsyncStorage.getItem(APPLICATIONS_STORAGE_KEY);
      const existingApps = existingAppsStr ? JSON.parse(existingAppsStr) : [];
      existingApps.push(record);
      await AsyncStorage.setItem(APPLICATIONS_STORAGE_KEY, JSON.stringify(existingApps));

      // 2. Save as 'Egreso' for the specific parcel
      const expenseKey = `${PARCEL_EXPENSES_PREFIX}${parcelId}`;
      const existingExpensesStr = await AsyncStorage.getItem(expenseKey);
      const existingExpenses = existingExpensesStr ? JSON.parse(existingExpensesStr) : [];
      existingExpenses.push({
        id: generateUUID(),
        tipo: 'Aplicación',
        descripcion: `Aplicación en ${nombreParcela}`,
        monto: record.costoTotalAplicacion,
        fecha: record.fecha,
        refId: id
      });
      await AsyncStorage.setItem(expenseKey, JSON.stringify(existingExpenses));

      return record;
    } catch (e: any) {
      await Logger.log('ERROR', 'Failed to save application', e);
      await handleSupabaseError(e, async () => {
        // Fallback: Operations are already partially saved via AsyncStorage in this hook
      });
      throw e;
    } finally {
      setIsSaving(false);
    }
  }, []);

  return {
    saveApplication,
    isSaving
  };
};
