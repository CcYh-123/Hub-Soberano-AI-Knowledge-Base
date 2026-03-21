import { VADEMECUM_BASE } from './src/data/vademecum.ts';
import { getInsumoSmartData, convertToBaseUnit, validarUnidadInsumo } from './src/utils/vademecumLogic.ts';

console.log("--- TEST VADEMECUM ---");

const glifo = VADEMECUM_BASE[0];
const urea = VADEMECUM_BASE[2];

// Test Smart Data Inference
console.log("Glifosato Inference:", getInsumoSmartData(glifo));
console.log("Urea Inference:", getInsumoSmartData(urea));

// Test Conversion & Precision
console.log("Convert 2.5 of Urea in Bolsa 50kg:", convertToBaseUnit(2.5, "Bolsa 50kg", urea.tipo)); // Should be 125.000
console.log("Convert 1.105 of Glifosato in Bidón 20L:", convertToBaseUnit(1.105, "Bidón 20L", glifo.tipo)); // Should be 22.100

// Test Validations
console.log("Valid Urea in L:", validarUnidadInsumo(urea.tipo, "L")); // Should be false
console.log("Valid Glifo in L:", validarUnidadInsumo(glifo.tipo, "L")); // Should be true

try {
    convertToBaseUnit(1, "Bidón 20L", urea.tipo);
    console.log("FAILED: Should have thrown an error for Urea in 20L");
} catch(e: any) {
    console.log("PASSED Validation Catch:", e.message);
}

try {
    convertToBaseUnit(1, "Bolsa 25kg", glifo.tipo);
    console.log("FAILED: Should have thrown an error for Glifo in 25kg");
} catch(e: any) {
    console.log("PASSED Validation Catch:", e.message);
}
