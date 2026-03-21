import { useState, useCallback } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { generateUUID } from '../utils/uuid';
import { PurchaseRecord } from '../data/stock';

const PURCHASES_STORAGE_KEY = '@Logistica:Purchases';

export const usePurchaseRegistry = () => {
  const [isSaving, setIsSaving] = useState(false);

  const registerPurchase = useCallback(async (purchaseData: Omit<PurchaseRecord, 'id'>) => {
    setIsSaving(true);
    try {
      const id = generateUUID();
      const record: PurchaseRecord = { ...purchaseData, id };

      const existingStr = await AsyncStorage.getItem(PURCHASES_STORAGE_KEY);
      const existing = existingStr ? JSON.parse(existingStr) : [];
      
      // Add to start for history visibility
      const updated = [record, ...existing];
      await AsyncStorage.setItem(PURCHASES_STORAGE_KEY, JSON.stringify(updated));

      return record;
    } catch (e) {
      console.error('Failed to register purchase', e);
      throw e;
    } finally {
      setIsSaving(false);
    }
  }, []);

  const getRecentPurchases = async (): Promise<PurchaseRecord[]> => {
    try {
      const str = await AsyncStorage.getItem(PURCHASES_STORAGE_KEY);
      return str ? JSON.parse(str).slice(0, 10) : [];
    } catch (e) {
      return [];
    }
  };

  return { registerPurchase, getRecentPurchases, isSaving };
};
