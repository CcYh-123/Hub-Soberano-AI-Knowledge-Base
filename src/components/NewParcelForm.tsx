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
import { Picker } from '@react-native-picker/picker';
import * as Location from 'expo-location'; // Assuming Expo, fallback to standard if needed
import { useOfflineForm } from '../hooks/useOfflineForm';
import { styles } from './ParcelStyles';

const CULTIVOS = [
  'Soja 1°', 
  'Soja 2°', 
  'Maíz Temprano', 
  'Maíz Tardío', 
  'Trigo', 
  'Barbecho'
];

export const NewParcelForm = () => {
  const { data, updateField, handleBlur, isLoading, id } = useOfflineForm();
  const [isCapturingGPS, setIsCapturingGPS] = useState(false);

  const captureGPS = async () => {
    setIsCapturingGPS(true);
    try {
      let { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permiso denegado', 'Se requiere acceso a la ubicación.');
        return;
      }

      let location = await Location.getCurrentPositionAsync({});
      updateField('latitude', location.coords.latitude);
      updateField('longitude', location.coords.longitude);
      
      // Auto-save after GPS capture
      handleBlur(); 
    } catch (error) {
      Alert.alert('Error', 'No se pudo obtener la ubicación GPS.');
    } finally {
      setIsCapturingGPS(false);
    }
  };

  if (isLoading) {
    return (
      <View style={[styles.container, { justifyContent: 'center' }]}>
        <ActivityIndicator size="large" color="#38bdf8" />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ paddingBottom: 100 }}>
      <View style={styles.glassCard}>
        <Text style={styles.headerTitle}>Nueva Parcela</Text>
        <Text style={styles.headerSubtitle}>ID: {id}</Text>

        {/* Nombre del Lote */}
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Nombre del Lote</Text>
          <TextInput
            style={styles.input}
            placeholder="Ej: La Soberana 1"
            placeholderTextColor="#64748b"
            value={data.nombreLote}
            onChangeText={(text) => updateField('nombreLote', text)}
            onBlur={handleBlur}
          />
        </View>

        {/* Superficies */}
        <View style={styles.row}>
          <View style={[styles.inputGroup, styles.halfInput]}>
            <Text style={styles.label}>Sup. Declarada (ha)</Text>
            <TextInput
              style={styles.input}
              keyboardType="decimal-pad"
              placeholder="0.000"
              placeholderTextColor="#64748b"
              value={data.superficieDeclarada}
              onChangeText={(text) => updateField('superficieDeclarada', text)}
              onBlur={handleBlur}
            />
          </View>
          <View style={[styles.inputGroup, styles.halfInput]}>
            <Text style={styles.label}>Sup. Productiva (ha)</Text>
            <TextInput
              style={styles.input}
              keyboardType="decimal-pad"
              placeholder="0.000"
              placeholderTextColor="#64748b"
              value={data.superficieProductiva}
              onChangeText={(text) => updateField('superficieProductiva', text)}
              onBlur={handleBlur}
            />
          </View>
        </View>

        {/* Cultivo Actual */}
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Cultivo Actual</Text>
          <View style={styles.pickerContainer}>
            <Picker
              selectedValue={data.cultivoActual}
              onValueChange={(val) => {
                updateField('cultivoActual', val);
                handleBlur();
              }}
              style={styles.picker}
              dropdownIconColor="#38bdf8"
            >
              <Picker.Item label="Seleccionar cultivo..." value="" color="#94a3b8" />
              {CULTIVOS.map((c) => (
                <Picker.Item key={c} label={c} value={c} />
              ))}
            </Picker>
          </View>
        </View>

        {/* Cultivo Antecesor */}
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Cultivo Antecesor</Text>
          <View style={styles.pickerContainer}>
            <Picker
              selectedValue={data.cultivoAntecesor}
              onValueChange={(val) => {
                updateField('cultivoAntecesor', val);
                handleBlur();
              }}
              style={styles.picker}
              dropdownIconColor="#38bdf8"
            >
              <Picker.Item label="Seleccionar cultivo..." value="" color="#94a3b8" />
              {CULTIVOS.map((c) => (
                <Picker.Item key={c} label={c} value={c} />
              ))}
            </Picker>
          </View>
        </View>

        {/* GPS Capture */}
        <TouchableOpacity 
          style={styles.gpsButton} 
          onPress={captureGPS}
          disabled={isCapturingGPS}
        >
          {isCapturingGPS ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <>
              <Text style={styles.gpsButtonText}>Capturar GPS</Text>
            </>
          )}
        </TouchableOpacity>

        {(data.latitude && data.longitude) && (
          <View style={styles.coordsContainer}>
            <Text style={styles.coordsText}>
              Lat: {data.latitude.toFixed(6)} | Lng: {data.longitude.toFixed(6)}
            </Text>
          </View>
        )}
      </View>
    </ScrollView>
  );
};
