import React, { useState, useEffect } from 'react';
import { 
  View, 
  
  Text, 
  TextInput, 
  TouchableOpacity, 
  
  ScrollView, 
  ActivityIndicator,
  Alert 
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { styles as globalStyles } from './ParcelStyles';
import { SmartVademecumSearch } from './SmartVademecumSearch';
import { Insumo } from '../data/vademecum';
import { calculateApplicationTotal, calculateApplicationCost } from '../utils/vademecumLogic';
import { useStockManager } from '../hooks/useStockManager';
import { useFieldApplication } from '../hooks/useFieldApplication';
import { ApplicationInsumo, WeatherData } from '../data/stock';
import { Picker } from '@react-native-picker/picker';
import { useTenant } from '../context/TenantContext';
import { listarProductosAgro, insertBloqueoLog } from '../lib/localDb';

interface Parcel {
  id: string;
  nombreLote: string;
  superficieProductiva: string;
}

export const FieldApplicationForm = () => {
  const [parcels, setParcels] = useState<Parcel[]>([]);
  const [selectedParcel, setSelectedParcel] = useState<Parcel | null>(null);
  
  // Tank Mix
  const [tankMix, setTankMix] = useState<ApplicationInsumo[]>([]);
  
  // Weather (BPA)
  const [clima, setClima] = useState<WeatherData>({
    temperatura: undefined,
    humedad: undefined,
    vientoVelocidad: undefined,
    vientoDireccion: '',
  });

  const { stock, checkAvailability, deductStock, loading: loadingStock } = useStockManager();
  const { saveApplication, isSaving } = useFieldApplication();
  const { tenantId } = useTenant();
  const [killSwitchActive, setKillSwitchActive] = useState(false);
  const [killSwitchMessage, setKillSwitchMessage] = useState<string | null>(null);
  const [loadingParcels, setLoadingParcels] = useState(true);

  useEffect(() => {
    const loadParcels = async () => {
      try {
        const keys = await AsyncStorage.getAllKeys();
        const parcelKeys = keys.filter(k => k.startsWith('@ParcelaForm:'));
        const parcelData = await AsyncStorage.multiGet(parcelKeys);
        const parsedParcels = parcelData.map(([_, v]) => JSON.parse(v!));
        setParcels(parsedParcels);
      } catch (e) {
        console.error('Error loading parcels', e);
      } finally {
        setLoadingParcels(false);
      }
    };
    loadParcels();
  }, []);

  const validarMargenYKillSwitch = async () => {
    // Si no hay tenant, por seguridad bloqueamos
    if (!tenantId) {
      setKillSwitchActive(true);
      setKillSwitchMessage(
        'Margen Protegido: Costo de insumo excedido o datos desactualizados. Contacte al administrador.',
      );
      return;
    }

    // Si no hay mezcla o parcela, no aplicamos reglas de margen aún
    if (!selectedParcel || tankMix.length === 0) {
      setKillSwitchActive(false);
      setKillSwitchMessage(null);
      return;
    }

    // Kill Switch por datos desactualizados (>24h sin sync)
    const lastSyncRaw = await AsyncStorage.getItem('@LocalDB:LastSyncISO');
    if (!lastSyncRaw) {
      setKillSwitchActive(true);
      setKillSwitchMessage(
        'Margen Protegido: Costo de insumo excedido o datos desactualizados. Contacte al administrador.',
      );
      return;
    }
    const lastSync = new Date(lastSyncRaw).getTime();
    const now = Date.now();
    const diffHours = (now - lastSync) / (1000 * 60 * 60);
    if (Number.isNaN(lastSync) || diffHours > 24) {
      setKillSwitchActive(true);
      setKillSwitchMessage(
        'Margen Protegido: Costo de insumo excedido o datos desactualizados. Contacte al administrador.',
      );
      return;
    }

    // Validación de margen contra productos_agro
    try {
      const productos = await listarProductosAgro(tenantId);
      if (!productos.length) {
        setKillSwitchActive(true);
        setKillSwitchMessage(
          'Margen Protegido: Costo de insumo excedido o datos desactualizados. Contacte al administrador.',
        );
        return;
      }

      let margenCriticoDetectado = false;

      for (const item of tankMix) {
        const prod = productos.find(
          p => p.nombre.toLowerCase() === item.nombre.toLowerCase(),
        );
        if (!prod) {
          // Si no encontramos el producto, asumimos datos desactualizados
          setKillSwitchActive(true);
          setKillSwitchMessage(
            'Margen Protegido: Costo de insumo excedido o datos desactualizados. Contacte al administrador.',
          );
          return;
        }

        const price = prod.precio_venta || 0;
        const cost = prod.costo_reposicion || 0;
        if (price <= 0) {
          continue;
        }
        const margin = (price - cost) / price;
        if (margin < 0.15) {
          margenCriticoDetectado = true;
          await insertBloqueoLog(prod.nombre, margin * 100, tenantId);
        }
      }

      if (margenCriticoDetectado) {
        setKillSwitchActive(true);
        setKillSwitchMessage(
          'Margen Protegido: Costo de insumo excedido o datos desactualizados. Contacte al administrador.',
        );
      } else {
        setKillSwitchActive(false);
        setKillSwitchMessage(null);
      }
    } catch (_e) {
      setKillSwitchActive(true);
      setKillSwitchMessage(
        'Margen Protegido: Costo de insumo excedido o datos desactualizados. Contacte al administrador.',
      );
    }
  };

  useEffect(() => {
    // Revalidar cada vez que cambia mezcla, parcela o tenant
    void validarMargenYKillSwitch();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tenantId, selectedParcel, tankMix]);

  const handleInsumoSelected = (insumo: Insumo, unidad: string) => {
    const stockItem = stock.find(s => s.insumoId === insumo.id);
    
    // Initialize with 0 dose
    const newItem: ApplicationInsumo = {
      insumoId: insumo.id,
      nombre: insumo.nombre,
      dosis: 0,
      unidad,
      totalAplicado: 0,
      costoTotal: 0
    };
    
    setTankMix(prev => [...prev, newItem]);
  };

  const updateDose = (index: number, doseStr: string) => {
    const dose = parseFloat(doseStr) || 0;
    if (!selectedParcel) return;

    const sup = parseFloat(selectedParcel.superficieProductiva) || 0;
    const total = calculateApplicationTotal(dose, sup);
    
    const stockItem = stock.find(s => s.insumoId === tankMix[index].insumoId);
    const costo = calculateApplicationCost(total, stockItem?.costoPromedioPonderado || 0);

    const updatedMix = [...tankMix];
    updatedMix[index] = {
      ...updatedMix[index],
      dosis: dose,
      totalAplicado: total,
      costoTotal: costo
    };
    setTankMix(updatedMix);
  };

  const onSave = async () => {
    if (killSwitchActive) {
      return;
    }
    if (!selectedParcel) {
      Alert.alert('Error', 'Selecciona una parcela primero.');
      return;
    }
    if (tankMix.length === 0) {
      Alert.alert('Error', 'Agrega al menos un insumo a la mezcla.');
      return;
    }

    // Validate Stock
    for (const item of tankMix) {
      if (!checkAvailability(item.insumoId, item.totalAplicado)) {
        Alert.alert('Stock Insuficiente', `No hay suficiente ${item.nombre} en la farmacia.`);
        return;
      }
    }

    try {
      // 1. Save Application
      const record = await saveApplication(
        selectedParcel.id,
        selectedParcel.nombreLote,
        parseFloat(selectedParcel.superficieProductiva),
        tankMix,
        clima
      );

      // 2. Deduct Stock (Offline-First)
      for (const item of tankMix) {
        await deductStock(item.insumoId, item.totalAplicado);
      }

      Alert.alert('Éxito', 'Aplicación registrada y stock actualizado localmente.');
      
      // Reset form
      setTankMix([]);
      setSelectedParcel(null);
    } catch (e) {
      Alert.alert('Error', 'No se pudo guardar la aplicación.');
    }
  };

  const totalCostoMezcla = tankMix.reduce((acc, curr) => acc + curr.costoTotal, 0);

  if (loadingStock || loadingParcels) {
    return <ActivityIndicator style={{ marginTop: 50 }} color="#38bdf8" />;
  }

  return (
    <ScrollView style={globalStyles.container} contentContainerStyle={{ paddingBottom: 100 }}>
      <View style={globalStyles.glassCard}>
        <Text style={globalStyles.headerTitle}>Nueva Aplicación</Text>
        
        {/* Parcela Selection */}
        <View style={globalStyles.inputGroup}>
          <Text style={globalStyles.label}>Seleccionar Parcela</Text>
          <View style={[globalStyles.input, { padding: 0 }]}>
            <Picker
              selectedValue={selectedParcel?.id}
              onValueChange={(itemValue) => {
                const p = parcels.find(x => x.id === itemValue);
                setSelectedParcel(p || null);
              }}
              style={{ color: '#fff' }}
              dropdownIconColor="#38bdf8"
            >
              <Picker.Item label="Seleccione..." value={undefined} color="#64748b" />
              {parcels.map(p => (
                <Picker.Item key={p.id} label={`${p.nombreLote} (${p.superficieProductiva} ha)`} value={p.id} />
              ))}
            </Picker>
          </View>
        </View>

        {/* Carga de Mezcla */}
        <Text style={[globalStyles.label, { marginTop: 10 }]}>Mezcla de Tanque</Text>
        <SmartVademecumSearch onInsumoSelected={handleInsumoSelected} />

        {tankMix.map((item, index) => (
          <View key={item.insumoId} style={styles.insumoCard}>
            <Text style={styles.insumoName}>{item.nombre}</Text>
            <View style={globalStyles.row}>
              <View style={[globalStyles.inputGroup, { width: '45%' }]}>
                <Text style={styles.smallLabel}>Dosis ({item.unidad}/ha)</Text>
                <TextInput
                  style={globalStyles.input}
                  keyboardType="decimal-pad"
                  placeholder="0.000"
                  placeholderTextColor="#64748b"
                  onChangeText={(text) => updateDose(index, text)}
                />
              </View>
              <View style={[globalStyles.inputGroup, { width: '45%' }]}>
                <Text style={styles.smallLabel}>Total Necesario</Text>
                <Text style={styles.displayValue}>{item.totalAplicado.toFixed(3)} {item.unidad}</Text>
              </View>
            </View>
            <Text style={styles.costText}>Costo Est.: USD {item.costoTotal.toFixed(2)}</Text>
          </View>
        ))}

        {/* Clima (BPA) */}
        <Text style={[globalStyles.label, { marginTop: 20 }]}>Condiciones Climáticas (BPA)</Text>
        <View style={globalStyles.row}>
          <View style={[globalStyles.inputGroup, { width: '30%' }]}>
            <Text style={styles.smallLabel}>Temp (°C)</Text>
            <TextInput
              style={globalStyles.input}
              keyboardType="numeric"
              onChangeText={(v) => setClima({ ...clima, temperatura: parseFloat(v) })}
            />
          </View>
          <View style={[globalStyles.inputGroup, { width: '30%' }]}>
            <Text style={styles.smallLabel}>HR (%)</Text>
            <TextInput
              style={globalStyles.input}
              keyboardType="numeric"
              onChangeText={(v) => setClima({ ...clima, humedad: parseFloat(v) })}
            />
          </View>
          <View style={[globalStyles.inputGroup, { width: '30%' }]}>
            <Text style={styles.smallLabel}>Viento (km/h)</Text>
            <TextInput
              style={globalStyles.input}
              keyboardType="numeric"
              onChangeText={(v) => setClima({ ...clima, vientoVelocidad: parseFloat(v) })}
            />
          </View>
        </View>

        {/* Total Cost Section */}
        <View style={styles.footerSummary}>
          <Text style={styles.totalLabel}>Costo Total Aplicación</Text>
          <Text style={styles.totalValue}>USD {totalCostoMezcla.toFixed(2)}</Text>
        </View>

        {killSwitchActive && (
          <View
            style={{
              marginTop: 20,
              padding: 16,
              borderRadius: 12,
              backgroundColor: '#dc2626',
              borderWidth: 2,
              borderColor: '#fbbf24',
            }}
          >
            <Text
              style={{
                color: '#fefce8',
                fontSize: 14,
                fontWeight: '900',
                textAlign: 'center',
              }}
            >
              {killSwitchMessage}
            </Text>
          </View>
        )}

        <TouchableOpacity 
          style={[globalStyles.gpsButton, { backgroundColor: '#10b981', marginTop: 20 }]} 
          onPress={onSave}
          disabled={isSaving || killSwitchActive}
        >
          {isSaving ? <ActivityIndicator color="#fff" /> : <Text style={globalStyles.gpsButtonText}>Confirmar Aplicación</Text>}
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = {
  insumoCard: {
    backgroundColor: 'rgba(255,255,255,0.02)',
    padding: 15,
    borderRadius: 12,
    marginTop: 10,
    borderWidth: 1,
    borderColor: 'rgba(56, 189, 248, 0.1)',
  },
  insumoName: {
    color: '#f1f5f9',
    fontWeight: '700',
    fontSize: 16,
    marginBottom: 8,
  },
  smallLabel: {
    color: '#94a3b8',
    fontSize: 11,
    marginBottom: 4,
  },
  displayValue: {
    color: '#38bdf8',
    fontSize: 18,
    fontWeight: '700',
    marginTop: 10,
  },
  costText: {
    color: '#10b981',
    fontSize: 12,
    fontWeight: '600',
    textAlign: 'right',
  },
  footerSummary: {
    marginTop: 25,
    paddingTop: 15,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,255,255,0.1)',
    alignItems: 'flex-end',
  },
  totalLabel: {
    color: '#94a3b8',
    fontSize: 12,
    textTransform: 'uppercase',
  },
  totalValue: {
    color: '#f8fafc',
    fontSize: 24,
    fontWeight: '900',
  }
};
