import { useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { StockItem, PurchaseRecord, ApplicationRecord } from '../data/stock';

const STORAGE_KEYS = {
  PARCELAS: '@AgroApp:Parcelas',
  STOCK: '@Logistica:Stock',
  APLICACIONES: '@Logistica:Aplicaciones',
  COMPRAS: '@Logistica:Purchases'
};

export interface ExpenseByCrop {
  cultivo: string;
  totalUSD: number;
}

export interface ParcelInvestment {
  parcelName: string;
  totalInvested: number;
}

export interface ActivityFeedItem {
  id: string;
  type: 'APPLICATION' | 'PURCHASE';
  date: string;
  title: string;
  subtitle: string;
  amountText: string;
}

export const useDashboardMetrics = (refreshTrigger: number) => {
  const [loading, setLoading] = useState(true);
  
  const [lowStock, setLowStock] = useState<StockItem[]>([]);
  const [cropExpenses, setCropExpenses] = useState<ExpenseByCrop[]>([]);
  const [parcelHeatmap, setParcelHeatmap] = useState<ParcelInvestment[]>([]);
  const [recentActivity, setRecentActivity] = useState<ActivityFeedItem[]>([]);

  useEffect(() => {
    const loadMetrics = async () => {
      setLoading(true);
      try {
        // Fetch all local persistent data
        const [rawParcelas, rawStock, rawApps, rawComps] = await Promise.all([
          AsyncStorage.getItem(STORAGE_KEYS.PARCELAS),
          AsyncStorage.getItem(STORAGE_KEYS.STOCK),
          AsyncStorage.getItem(STORAGE_KEYS.APLICACIONES),
          AsyncStorage.getItem(STORAGE_KEYS.COMPRAS),
        ]);

        const parcelas = rawParcelas ? JSON.parse(rawParcelas) : [];
        const stock: StockItem[] = rawStock ? JSON.parse(rawStock) : [];
        const applications: ApplicationRecord[] = rawApps ? JSON.parse(rawApps) : [];
        const purchases: PurchaseRecord[] = rawComps ? JSON.parse(rawComps) : [];

        // 1. Low Stock (Top 5 lowest available units > 0)
        // Note: For a strictly perfect system we'd compare against thresholds, 
        // but for now we sort by raw amount or percentage. We'll simply sort by quantity.
        const sortedStock = [...stock]
          .filter(s => s.cantidadDisponible < 50) // Arbitrary conceptual threshold for "low"
          .sort((a, b) => a.cantidadDisponible - b.cantidadDisponible)
          .slice(0, 5);
        setLowStock(sortedStock);

        // Map parcels for quick lookups
        const parcelMap = new Map<string, any>();
        parcelas.forEach((p: any) => parcelMap.set(p.id, p));

        // 2 & 3. Crop Expenses & Parcel Heatmap
        const cropMap = new Map<string, number>();
        const heatMap = new Map<string, number>();

        applications.forEach(app => {
          const parcel = parcelMap.get(app.parcelId);
          if (parcel) {
            // Aggregate by Crop
            const crop = parcel.cultivoActual || 'Sin Cultivo';
            const currentCropTotal = cropMap.get(crop) || 0;
            cropMap.set(crop, currentCropTotal + app.costoTotalUSD);

            // Aggregate by Parcel Name (Heatmap concept)
            const currentParcelTotal = heatMap.get(parcel.nombre) || 0;
            heatMap.set(parcel.nombre, currentParcelTotal + app.costoTotalUSD);
          }
        });

        setCropExpenses(
          Array.from(cropMap.entries())
            .map(([cultivo, totalUSD]) => ({ cultivo, totalUSD }))
            .sort((a, b) => b.totalUSD - a.totalUSD) // Highest first
        );

        setParcelHeatmap(
          Array.from(heatMap.entries())
            .map(([parcelName, totalInvested]) => ({ parcelName, totalInvested }))
            .sort((a, b) => b.totalInvested - a.totalInvested)
        );

        // 4. Activity Feed (Merge Applications and Purchases)
        const mappedApps: ActivityFeedItem[] = applications.map(a => ({
          id: a.id,
          type: 'APPLICATION',
          date: a.fecha,
          title: `Aplicación en ${parcelMap.get(a.parcelId)?.nombre || 'Parcela'}`,
          subtitle: a.insumos.map(i => `${i.nombre} (${i.dosisHectarea}${i.unidadBase}/ha)`).join(', '),
          amountText: `-$${a.costoTotalUSD.toFixed(2)} USD`,
        }));

        const mappedPurchases: ActivityFeedItem[] = purchases.map(p => ({
          id: p.id,
          type: 'PURCHASE',
          date: p.fechaRemito,
          title: `Ingreso de ${p.nombreInsumo}`,
          subtitle: `Prov: ${p.proveedor} | Lote: ${p.lote}`,
          amountText: `+${p.cantidad} ${p.unidadEntrada}`,
        }));

        const combinedActivity = [...mappedApps, ...mappedPurchases]
          .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
          .slice(0, 5); // Take top 5 recent

        setRecentActivity(combinedActivity);

      } catch (e) {
        console.error('Error loading dashboard metrics:', e);
      } finally {
        setLoading(false);
      }
    };

    loadMetrics();
  }, [refreshTrigger]);

  return { loading, lowStock, cropExpenses, parcelHeatmap, recentActivity };
};
