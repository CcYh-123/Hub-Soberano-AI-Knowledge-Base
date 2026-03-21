import { Insumo, TipoInsumo, VADEMECUM_BASE } from '../data/vademecum';

export interface SmartData {
  unidadBase: string;
  mermaPorcentaje: number;
}

/**
 * Parses user-friendly units to their multiplier against the base.
 * @param unidadEntrada Original unit string (e.g. "Bidón 20L")
 * @returns Multiplier for base unit (e.g. 20)
 */
const parseUnidadMultiple = (unidadEntrada: string): number => {
  const cleanStr = unidadEntrada.toLowerCase().trim();
  
  if (cleanStr.includes('bidón 20l') || cleanStr.includes('bidon 20l')) return 20;
  if (cleanStr.includes('bidón 5l') || cleanStr.includes('bidon 5l')) return 5;
  if (cleanStr.includes('bolsa 50kg')) return 50;
  if (cleanStr.includes('bolsa 25kg')) return 25;
  if (cleanStr.includes('bolsa 80000')) return 80000; // Semillas
  
  // Try regex to extract numbers if format like "X L" or "X Kg"
  const match = cleanStr.match(/(\d+(?:\.\d+)?)/);
  if (match) {
      // If it explicitly says just 'l', 'kg', 'cc', 'ml' etc.
      if (cleanStr === 'l' || cleanStr === 'litro' || cleanStr === 'litros') return 1;
      if (cleanStr === 'kg' || cleanStr === 'kilos' || cleanStr === 'kilogramos') return 1;
      
      // If no explicit base string match but starts with number and unit
      // This is a simplified fallback
  }

  return 1; // Fallback multiplicador 1
}

/**
 * Valida que el insumo no use unidades incompatibles con su tipo.
 */
export const validarUnidadInsumo = (tipoInsumo: TipoInsumo, unidadEntrada: string): boolean => {
  const cleanUnit = unidadEntrada.toLowerCase();
  const liquidUnits = ['l', 'litro', 'litros', 'cc', 'ml', 'bidón', 'bidon'];
  const solidUnits = ['kg', 'kilo', 'kilos', 'gramo', 'gr', 'bolsa'];
  
  if (tipoInsumo === 'Sólido') {
    return !liquidUnits.some(lu => cleanUnit.includes(lu));
  }
  
  if (tipoInsumo === 'Líquido') {
    return !solidUnits.some(su => cleanUnit.includes(su) && !cleanUnit.includes('bidon')); // Bidon might have kg in some contexts, but usually is Liquid. Assumes standard agro.
  }

  return true; // Semillas or others
};

/**
 * Retorna los default inteligentes de acuerdo a las reglas de negocio.
 */
export const getInsumoSmartData = (nombreInsumo: string | Insumo): SmartData | null => {
  let insumo: Insumo | undefined;
  
  if (typeof nombreInsumo === 'string') {
    insumo = VADEMECUM_BASE.find(i => i.nombre.toLowerCase() === nombreInsumo.toLowerCase());
  } else {
    insumo = nombreInsumo;
  }

  if (!insumo) return null;

  switch (insumo.tipo) {
    case 'Líquido':
      return { unidadBase: 'L', mermaPorcentaje: 1.5 };
    case 'Sólido':
      return { unidadBase: 'Kg', mermaPorcentaje: 1.0 };
    case 'Semilla':
      return { unidadBase: 'Unidad/Bolsa', mermaPorcentaje: 0.2 };
    default:
      return { unidadBase: 'Unidad', mermaPorcentaje: 0 };
  }
};

/**
 * Motor de Conversión de Precisión.
 * IMPORTANTE: Toda matemática usa 3 decimales para evitar acumulación de errores.
 */
export const convertToBaseUnit = (
  cantidad: number, 
  unidadEntrada: string, 
  tipoInsumo: TipoInsumo
): number => {
  
  if (!validarUnidadInsumo(tipoInsumo, unidadEntrada)) {
    throw new Error(`Incompatibilidad de unidad. No se puede usar '${unidadEntrada}' para un insumo tipo '${tipoInsumo}'.`);
  }

  const multiplicador = parseUnidadMultiple(unidadEntrada);
  
  // Math operation
  const rawResult = cantidad * multiplicador;
  
  // Format to exactly 3 decimals, then parse back to number
  return parseFloat(rawResult.toFixed(3));
};

/**
 * Calcula el total necesario basado en dosis y superficie.
 */
export const calculateApplicationTotal = (dosis: number, superficie: number): number => {
  return parseFloat((dosis * superficie).toFixed(3));
};

/**
 * Calcula el costo total basado en cantidad y costo unitario.
 */
export const calculateApplicationCost = (cantidad: number, costoUnitario: number): number => {
  return parseFloat((cantidad * costoUnitario).toFixed(3));
};
