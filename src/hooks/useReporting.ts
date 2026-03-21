import { useState, useCallback } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { ApplicationRecord } from '../data/stock';

const STORAGE_KEYS = {
  PARCELAS: '@AgroApp:Parcelas',
  APLICACIONES: '@Logistica:Aplicaciones',
};

export interface ReportFilters {
  cultivo?: string;
  parcelId?: string;
  fechaInicio?: string;
  fechaFin?: string;
}

export interface ParcelReportData {
  parcelId: string;
  nombre: string;
  cultivo: string;
  superficie: number;
  costoTotal: number;
  aplicaciones: ApplicationRecord[];
  margenProyectado?: number;
}

export const useReporting = () => {
  const [loading, setLoading] = useState(false);

  const getFilteredApplications = useCallback(async (filters: ReportFilters) => {
    const rawApps = await AsyncStorage.getItem(STORAGE_KEYS.APLICACIONES);
    const applications: ApplicationRecord[] = rawApps ? JSON.parse(rawApps) : [];

    return applications.filter(app => {
      let matches = true;
      if (filters.parcelId && app.parcelId !== filters.parcelId) matches = false;
      if (filters.fechaInicio && new Date(app.fecha) < new Date(filters.fechaInicio)) matches = false;
      if (filters.fechaFin && new Date(app.fecha) > new Date(filters.fechaFin)) matches = false;
      return matches;
    });
  }, []);

  const getParcelReports = useCallback(async (filters: ReportFilters, proyeccion?: { rinde: number, precio: number }) => {
    setLoading(true);
    try {
      const rawParcels = await AsyncStorage.getItem(STORAGE_KEYS.PARCELAS);
      const parcels = rawParcels ? JSON.parse(rawParcels) : [];
      const apps = await getFilteredApplications(filters);

      const reports: ParcelReportData[] = parcels
        .filter((p: any) => !filters.cultivo || p.cultivoActual === filters.cultivo)
        .map((p: any) => {
          const parcelApps = apps.filter(a => a.parcelId === p.id);
          const totalCost = parcelApps.reduce((acc, a) => acc + a.costoTotalUSD, 0);
          
          let margen = undefined;
          if (proyeccion) {
            const ingresoProyectado = p.superficieProductiva * proyeccion.rinde * proyeccion.precio;
            margen = ingresoProyectado - totalCost;
          }

          return {
            parcelId: p.id,
            nombre: p.nombre,
            cultivo: p.cultivoActual,
            superficie: p.superficieProductiva,
            costoTotal: totalCost,
            aplicaciones: parcelApps,
            margenProyectado: margen
          };
        });

      return reports;
    } finally {
      setLoading(false);
    }
  }, [getFilteredApplications]);

  return { loading, getParcelReports, getFilteredApplications };
};
