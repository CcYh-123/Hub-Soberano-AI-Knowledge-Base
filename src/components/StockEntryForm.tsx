import React, { useState } from 'react';
import { 
  View, 
  Text, 
  TextInput, 
  TouchableOpacity, 
  ScrollView, 
  ActivityIndicator,
  Alert 
} from 'react-native';
import { styles as globalStyles } from './ParcelStyles';
import { SmartVademecumSearch } from './SmartVademecumSearch';
import { Insumo } from '../data/vademecum';
import { convertToBaseUnit } from '../utils/vademecumLogic';
import { useStockManager } from '../hooks/useStockManager';
import { usePurchaseRegistry } from '../hooks/usePurchaseRegistry';

export const StockEntryForm = ({ onEntrySaved }: { onEntrySaved: () => void }) => {
  const [selectedInsumo, setSelectedInsumo] = useState<Insumo | null>(null);
  const [form, setForm] = useState({
    proveedor: '',
    cantidad: '',
    unidadEntrada: '',
    precioUnitario: '',
    lote: '',
    vencimiento: '',
  });

  const { addStock } = useStockManager();
  const { registerPurchase, isSaving } = usePurchaseRegistry();

  const handleInsumoSelected = (insumo: Insumo, unidad: string) => {
    setSelectedInsumo(insumo);
    setForm(prev => ({ ...prev, unidadEntrada: unidad }));
  };

  const handleSave = async () => {
    if (!selectedInsumo || !form.proveedor || !form.cantidad || !form.precioUnitario || !form.lote) {
      Alert.alert('Incompleto', 'Por favor complete todos los campos obligatorios.');
      return;
    }

    try {
      const qty = parseFloat(form.cantidad);
      const price = parseFloat(form.precioUnitario);
      
      // 1. Convert to Base Unit
      const cantidadBase = convertToBaseUnit(qty, form.unidadEntrada, selectedInsumo.tipo);
      const costoPorBase = price / (cantidadBase / qty); // Cost per L or Kg

      // 2. Update CMP and Sum Stock
      await addStock(selectedInsumo.id, cantidadBase, costoPorBase);

      // 3. Registry purchase history
      await registerPurchase({
        insumoId: selectedInsumo.id,
        nombreInsumo: selectedInsumo.nombre,
        proveedor: form.proveedor,
        fechaRemito: new Date().toISOString(),
        cantidad: qty,
        unidadEntrada: form.unidadEntrada,
        precioUnitarioUSD: price,
        lote: form.lote,
        vencimiento: form.vencimiento,
        costoBaseUnitario: costoPorBase
      });

      Alert.alert('Éxito', 'Insumo ingresado y CMP actualizado.');
      
      // Reset
      setForm({
        proveedor: '',
        cantidad: '',
        unidadEntrada: '',
        precioUnitario: '',
        lote: '',
        vencimiento: '',
      });
      setSelectedInsumo(null);
      onEntrySaved();
    } catch (e: any) {
      Alert.alert('Error', e.message || 'No se pudo procesar el ingreso.');
    }
  };

  return (
    <ScrollView style={globalStyles.glassCard} nestedScrollEnabled={true}>
      <Text style={globalStyles.headerTitle}>Ingreso a Galpón</Text>

      <View style={globalStyles.inputGroup}>
        <Text style={globalStyles.label}>Proveedor</Text>
        <TextInput
          style={globalStyles.input}
          placeholder="Nombre del proveedor"
          placeholderTextColor="#64748b"
          value={form.proveedor}
          onChangeText={(v) => setForm({ ...form, proveedor: v })}
        />
      </View>

      <SmartVademecumSearch 
        onInsumoSelected={handleInsumoSelected}
        initialUnidad={form.unidadEntrada}
      />

      {selectedInsumo && (
        <View style={{ marginTop: 10 }}>
          <View style={globalStyles.row}>
            <View style={[globalStyles.inputGroup, { width: '45%' }]}>
              <Text style={globalStyles.label}>Cantidad</Text>
              <TextInput
                style={globalStyles.input}
                keyboardType="decimal-pad"
                placeholder="0.000"
                value={form.cantidad}
                onChangeText={(v) => setForm({ ...form, cantidad: v })}
              />
            </View>
            <View style={[globalStyles.inputGroup, { width: '45%' }]}>
              <Text style={globalStyles.label}>Precio Unit. (USD)</Text>
              <TextInput
                style={globalStyles.input}
                keyboardType="decimal-pad"
                placeholder="0.00"
                value={form.precioUnitario}
                onChangeText={(v) => setForm({ ...form, precioUnitario: v })}
              />
            </View>
          </View>

          <View style={globalStyles.row}>
            <View style={[globalStyles.inputGroup, { width: '45%' }]}>
              <Text style={globalStyles.label}>Lote</Text>
              <TextInput
                style={globalStyles.input}
                placeholder="N° de Lote"
                value={form.lote}
                onChangeText={(v) => setForm({ ...form, lote: v })}
              />
            </View>
            <View style={[globalStyles.inputGroup, { width: '45%' }]}>
              <Text style={globalStyles.label}>Vencimiento</Text>
              <TextInput
                style={globalStyles.input}
                placeholder="AAAA-MM-DD"
                value={form.vencimiento}
                onChangeText={(v) => setForm({ ...form, vencimiento: v })}
              />
            </View>
          </View>

          <TouchableOpacity 
            style={[globalStyles.gpsButton, { backgroundColor: '#38bdf8' }]} 
            onPress={handleSave}
            disabled={isSaving}
          >
            {isSaving ? <ActivityIndicator color="#fff" /> : <Text style={globalStyles.gpsButtonText}>Registrar Ingreso</Text>}
          </TouchableOpacity>
        </View>
      )}
    </ScrollView>
  );
};
