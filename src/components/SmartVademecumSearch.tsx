import React, { useState, useEffect, useRef } from 'react';
import { 
  View, 
  Text, 
  TextInput, 
  FlatList, 
  TouchableOpacity, 
  StyleSheet,
  Alert
} from 'react-native';
import { VADEMECUM_BASE, Insumo } from '../data/vademecum';
import { getInsumoSmartData } from '../utils/vademecumLogic';
import { styles as globalStyles } from './ParcelStyles'; // Reusing premium styling

interface SmartVademecumSearchProps {
  onInsumoSelected: (insumo: Insumo, unidad: string, merma: number) => void;
  // External props if we want to bind values to a higher form state
  initialUnidad?: string;
  initialMerma?: number;
}

export const SmartVademecumSearch: React.FC<SmartVademecumSearchProps> = ({ 
  onInsumoSelected,
  initialUnidad = '',
  initialMerma = 0
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isDropdownVisible, setIsDropdownVisible] = useState(false);
  const [filteredInsumos, setFilteredInsumos] = useState<Insumo[]>([]);
  
  const [selectedInsumo, setSelectedInsumo] = useState<Insumo | null>(null);
  
  // Auto-filled states
  const [unidad, setUnidad] = useState(initialUnidad);
  const [merma, setMerma] = useState(initialMerma.toString());
  
  // Track if user manually overrode smart defaults
  const [isManualOverride, setIsManualOverride] = useState(false);

  useEffect(() => {
    if (searchQuery) {
      const results = VADEMECUM_BASE.filter(i => 
        i.nombre.toLowerCase().includes(searchQuery.toLowerCase()) || 
        i.descripcion.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredInsumos(results);
    } else {
      setFilteredInsumos(VADEMECUM_BASE);
    }
  }, [searchQuery]);

  const handleSelect = (insumo: Insumo) => {
    setSelectedInsumo(insumo);
    setSearchQuery(insumo.nombre);
    setIsDropdownVisible(false);

    // Smart Inferences (LOG-001/006)
    const smartData = getInsumoSmartData(insumo);
    if (smartData) {
      setUnidad(smartData.unidadBase);
      setMerma(smartData.mermaPorcentaje.toString());
      setIsManualOverride(false); // Reset warning on fresh selection
      
      onInsumoSelected(insumo, smartData.unidadBase, smartData.mermaPorcentaje);
    }
  };

  const handleManualUnitEdit = (val: string) => {
    setUnidad(val);
    if (selectedInsumo) {
        setIsManualOverride(true);
        // Call callback safely passing float parsed
        onInsumoSelected(selectedInsumo, val, parseFloat(merma) || 0);
    }
  };

  const handleManualMermaEdit = (val: string) => {
    setMerma(val);
    if (selectedInsumo) {
        setIsManualOverride(true);
        onInsumoSelected(selectedInsumo, unidad, parseFloat(val) || 0);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={globalStyles.label}>Buscar Insumo (Vademécum)</Text>
      
      <View style={styles.searchWrapper}>
        <TextInput
          style={[globalStyles.input, isDropdownVisible && styles.inputActive]}
          placeholder="Ej: Glifosato, Urea..."
          placeholderTextColor="#64748b"
          value={searchQuery}
          onChangeText={(text) => {
            setSearchQuery(text);
            setIsDropdownVisible(true);
            if(selectedInsumo && text !== selectedInsumo.nombre) {
                // Clear selection if user starts typing something else
                setSelectedInsumo(null);
                setUnidad('');
                setMerma('');
                setIsManualOverride(false);
            }
          }}
          onFocus={() => setIsDropdownVisible(true)}
        />

        {isDropdownVisible && filteredInsumos.length > 0 && (
          <View style={styles.dropdown}>
            <FlatList
              data={filteredInsumos}
              keyExtractor={(item) => item.id}
              nestedScrollEnabled={true}
              renderItem={({ item }) => (
                <TouchableOpacity 
                  style={styles.dropdownItem}
                  onPress={() => handleSelect(item)}
                >
                  <Text style={styles.dropdownTextBold}>{item.nombre}</Text>
                  <Text style={styles.dropdownTextLight}>{item.descripcion}</Text>
                </TouchableOpacity>
              )}
            />
          </View>
        )}
      </View>

      {/* Auto-filled fields - Only show when an insumo is selected */}
      {selectedInsumo && (
        <View style={styles.inferredDataContainer}>
          <Text style={styles.inferredTitle}>Configuración Sugerida</Text>
          <View style={globalStyles.row}>
            <View style={[globalStyles.inputGroup, globalStyles.halfInput]}>
              <Text style={globalStyles.label}>Unidad de Medida</Text>
              <TextInput
                style={[globalStyles.input, isManualOverride && styles.manualOverrideInput]}
                value={unidad}
                onChangeText={handleManualUnitEdit}
              />
            </View>
            <View style={[globalStyles.inputGroup, globalStyles.halfInput]}>
              <Text style={globalStyles.label}>Merma Esperada (%)</Text>
              <TextInput
                style={[globalStyles.input, isManualOverride && styles.manualOverrideInput]}
                keyboardType="decimal-pad"
                value={merma}
                onChangeText={handleManualMermaEdit}
              />
            </View>
          </View>
          
          {isManualOverride && (
            <View style={styles.warningBox}>
              <Text style={styles.warningIcon}>⚠️</Text>
              <Text style={styles.warningText}>
                Has modificado los valores sugeridos por el Vademécum. Asegúrate de que las conversiones sean correctas.
              </Text>
            </View>
          )}
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginBottom: 20,
    zIndex: 10, // Ensure dropdown overlays other content
  },
  searchWrapper: {
    position: 'relative',
    zIndex: 10,
  },
  inputActive: {
    borderColor: '#38bdf8',
    borderBottomLeftRadius: 0,
    borderBottomRightRadius: 0,
  },
  dropdown: {
    position: 'absolute',
    top: '100%',
    left: 0,
    right: 0,
    maxHeight: 200,
    backgroundColor: 'rgba(30, 41, 59, 0.95)', // Darker slate, less transparent
    borderWidth: 1,
    borderTopWidth: 0,
    borderColor: 'rgba(56, 189, 248, 0.5)',
    borderBottomLeftRadius: 12,
    borderBottomRightRadius: 12,
    overflow: 'hidden', // Ensures rounded corners apply
    elevation: 10, // Shadow for Android
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.5,
    shadowRadius: 15,
  },
  dropdownItem: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.05)',
  },
  dropdownTextBold: {
    color: '#f8fafc',
    fontSize: 16,
    fontWeight: '600',
  },
  dropdownTextLight: {
    color: '#94a3b8',
    fontSize: 12,
    marginTop: 4,
  },
  inferredDataContainer: {
    marginTop: 16,
    padding: 16,
    backgroundColor: 'rgba(56, 189, 248, 0.05)', // Very subtle blue tint
    borderRadius: 16,
    borderWidth: 1,
    borderColor: 'rgba(56, 189, 248, 0.2)',
  },
  inferredTitle: {
    color: '#e2e8f0',
    fontSize: 14,
    fontWeight: '700',
    marginBottom: 12,
  },
  manualOverrideInput: {
    borderColor: '#f59e0b', // Amber warning color
    backgroundColor: 'rgba(245, 158, 11, 0.05)',
  },
  warningBox: {
    flexDirection: 'row',
    backgroundColor: 'rgba(245, 158, 11, 0.1)',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: 'rgba(245, 158, 11, 0.3)',
    marginTop: 8,
    alignItems: 'center',
  },
  warningIcon: {
    fontSize: 18,
    marginRight: 8,
  },
  warningText: {
    color: '#fcd34d',
    fontSize: 12,
    flex: 1,
    lineHeight: 16,
  }
});
