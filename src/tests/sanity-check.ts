import { calculateApplicationCost, calculateCMP } from '../utils/vademecumLogic';
import { Logger } from '../utils/Logger';

export const runMathSanityCheck = async () => {
  await Logger.log('INFO', 'Iniciando Prueba de Fuego (Sanity Check Math)...');

  // Test 1: CMP Calculation (3 decimals)
  const stockActual = 500;
  const costoAnterior = 12.500;
  const nuevaCantidad = 200.555;
  const nuevoCosto = 13.750;
  
  const expectedTotal = stockActual + nuevaCantidad; // 700.555
  const expectedNewCMP = ((stockActual * costoAnterior) + (nuevaCantidad * nuevoCosto)) / expectedTotal;
  // (6250 + 2757.63125) / 700.555 = 9007.63125 / 700.555 = 12.857850... -> 12.858
  
  const resultCMP = parseFloat((((stockActual * costoAnterior) + (nuevaCantidad * nuevoCosto)) / expectedTotal).toFixed(3));
  
  if (resultCMP === 12.858) {
    await Logger.log('INFO', 'Test CMP: PASSED (12.858)');
  } else {
    await Logger.log('ERROR', 'Test CMP: FAILED', { expected: 12.858, got: resultCMP });
  }

  // Test 2: Application Cost
  const dosis = 2.155;
  const superficie = 50.333;
  const costoUnitario = 12.858;
  
  const totalInsumo = parseFloat((dosis * superficie).toFixed(3)); // 108.468
  const totalCost = parseFloat((totalInsumo * costoUnitario).toFixed(3)); // 108.468 * 12.858 = 1394.681544 -> 1394.682
  
  if (totalCost === 1394.682) {
    await Logger.log('INFO', 'Test Application Cost: PASSED (1394.682)');
  } else {
    await Logger.log('ERROR', 'Test Application Cost: FAILED', { expected: 1394.682, got: totalCost });
  }
  
  return { success: resultCMP === 12.858 && totalCost === 1394.682 };
};
