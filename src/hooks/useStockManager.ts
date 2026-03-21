import { useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { StockItem, INITIAL_STOCK } from '../data/stock';
import { handleSupabaseError } from '../lib/supabase';
import { Logger } from '../utils/Logger';

const STOCK_STORAGE_KEY = '@Farmacia:Stock';

export const useStockManager = () => {
  const [stock, setStock] = useState<StockItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStock();
  }, []);

  const loadStock = async () => {
    try {
      const savedStock = await AsyncStorage.getItem(STOCK_STORAGE_KEY);
      if (savedStock) {
        setStock(JSON.parse(savedStock));
      } else {
        // Initialize with seed data if first time
        await AsyncStorage.setItem(STOCK_STORAGE_KEY, JSON.stringify(INITIAL_STOCK));
        setStock(INITIAL_STOCK);
      }
    } catch (e) {
      console.error('Failed to load stock', e);
    } finally {
      setLoading(false);
    }
  };

  const checkAvailability = (insumoId: string, cantidadRequerida: number): boolean => {
    const item = stock.find(s => s.insumoId === insumoId);
    return item ? item.cantidadDisponible >= cantidadRequerida : false;
  };

  const addStock = async (insumoId: string, nuevaCantidad: number, nuevoCosto: number) => {
    try {
      const updatedStock = stock.map(item => {
        if (item.insumoId === insumoId) {
          const stockActual = item.cantidadDisponible;
          const costoAnterior = item.costoPromedioPonderado;
          
          // Recalcular CMP
          const stockTotal = stockActual + nuevaCantidad;
          const nuevoCMP = ((stockActual * costoAnterior) + (nuevaCantidad * nuevoCosto)) / stockTotal;

          return { 
            ...item, 
            cantidadDisponible: parseFloat(stockTotal.toFixed(3)),
            costoPromedioPonderado: parseFloat(nuevoCMP.toFixed(3))
          };
        }
        return item;
      });

      setStock(updatedStock);
      await AsyncStorage.setItem(STOCK_STORAGE_KEY, JSON.stringify(updatedStock));
      await Logger.log('INFO', `Stock actualizado para ${insumoId}`, { nuevaCantidad });
    } catch (e: any) {
      await Logger.log('ERROR', 'Critical storage error in addStock', e);
      await handleSupabaseError(e, async () => {
        // Fallback: Ensure local state at least reflects the change if storage fails partially
      });
    }
  };

  const deductStock = async (insumoId: string, cantidadADeducir: number) => {
    try {
      const updatedStock = stock.map(item => {
        if (item.insumoId === insumoId) {
          return { ...item, cantidadDisponible: parseFloat((item.cantidadDisponible - cantidadADeducir).toFixed(3)) };
        }
        return item;
      });
      setStock(updatedStock);
      await AsyncStorage.setItem(STOCK_STORAGE_KEY, JSON.stringify(updatedStock));
      await Logger.log('INFO', `Stock deducido para ${insumoId}`, { cantidadADeducir });
    } catch (e: any) {
      await Logger.log('ERROR', 'Error deducing stock', e);
    }
  };

  return {
    stock,
    loading,
    checkAvailability,
    deductStock,
    addStock,
    refreshStock: loadStock
  };
};
