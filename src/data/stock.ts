import { Insumo } from './vademecum';

export interface StockItem {
  insumoId: string;
  nombreInsumo: string;
  cantidadDisponible: number;
  unidad: string;
  costoPromedioPonderado: number; // Costo por unidad base
}

export interface PurchaseRecord {
  id: string;
  insumoId: string;
  nombreInsumo: string;
  proveedor: string;
  fechaRemito: string;
  cantidad: number;
  unidadEntrada: string;
  precioUnitarioUSD: number;
  lote: string;
  vencimiento: string;
  costoBaseUnitario: number;
}

export interface ApplicationInsumo {
  insumoId: string;
  nombre: string;
  dosis: number; // L/ha or Kg/ha
  unidad: string;
  totalAplicado: number;
  costoTotal: number;
}

export interface WeatherData {
  temperatura?: number;
  humedad?: number;
  vientoVelocidad?: number;
  vientoDireccion?: string;
}

export interface ApplicationRecord {
  id: string;
  parcelaId: string;
  nombreParcela: string;
  superficieProductiva: number;
  fecha: string;
  insumos: ApplicationInsumo[];
  clima: WeatherData;
  costoTotalAplicacion: number;
  sincronizado: boolean;
}

// Initial seed for "Farmacia"
export const INITIAL_STOCK: StockItem[] = [
  {
    insumoId: 'G-001',
    nombreInsumo: 'Glifosato',
    cantidadDisponible: 500,
    unidad: 'L',
    costoPromedioPonderado: 12.50
  },
  {
    insumoId: '24D-002',
    nombreInsumo: '2,4-D',
    cantidadDisponible: 200,
    unidad: 'L',
    costoPromedioPonderado: 15.00
  },
  {
    insumoId: 'U-003',
    nombreInsumo: 'Urea',
    cantidadDisponible: 5000,
    unidad: 'Kg',
    costoPromedioPonderado: 0.65
  },
  {
    insumoId: 'SM-004',
    nombreInsumo: 'Semilla Maíz Híbrido',
    cantidadDisponible: 100,
    unidad: 'Unidad/Bolsa',
    costoPromedioPonderado: 210.00
  }
];
