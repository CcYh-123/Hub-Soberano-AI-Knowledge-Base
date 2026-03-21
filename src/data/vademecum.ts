export type TipoInsumo = 'Líquido' | 'Sólido' | 'Semilla';

export interface Insumo {
  id: string;
  nombre: string;
  tipo: TipoInsumo;
  descripcion: string;
}

export const VADEMECUM_BASE: Insumo[] = [
  {
    id: 'G-001',
    nombre: 'Glifosato',
    tipo: 'Líquido',
    descripcion: 'Herbicida Líquido'
  },
  {
    id: '24D-002',
    nombre: '2,4-D',
    tipo: 'Líquido',
    descripcion: 'Herbicida Líquido'
  },
  {
    id: 'U-003',
    nombre: 'Urea',
    tipo: 'Sólido',
    descripcion: 'Fertilizante Sólido'
  },
  {
    id: 'SM-004',
    nombre: 'Semilla Maíz Híbrido',
    tipo: 'Semilla',
    descripcion: 'Semilla'
  },
  {
    id: 'A-005',
    nombre: 'Atrazina',
    tipo: 'Sólido',
    descripcion: 'Herbicida Sólido/WG'
  }
];
