import React, { useState, useCallback, useEffect } from 'react';
import {
  ScrollView,
  View,
  Text,
  StyleSheet,
  RefreshControl,
  TouchableOpacity,
  Alert
} from 'react-native';
import { useDashboardMetrics } from '../hooks/useDashboardMetrics';
import {
  LowStockWidget,
  CropExpensesWidget,
  ParcelHeatmapWidget,
  RecentActivityWidget
} from './DashboardWidgets';

import { useTenant } from '../context/TenantContext';
import { useAuth } from '../hooks/useAuth';
import { initLocalDb, listarProductosAgro } from '../lib/localDb';

export const DashboardScreen = () => {
  const { tenantId } = useTenant();
  const { profile } = useAuth(); // Var viva de autenticación
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  useEffect(() => {
    if (tenantId) {
      initLocalDb(tenantId)
        .then(() => console.log('✅ Local DB inicializada con tenant', tenantId))
        .catch(e => console.error('❌ Error inicializando DB local', e));
    }
  }, [tenantId]);

  const {
    loading,
    lowStock,
    cropExpenses,
    parcelHeatmap,
    recentActivity
  } = useDashboardMetrics(refreshTrigger);

  const onRefresh = useCallback(() => {
    setRefreshTrigger(prev => prev + 1);
  }, []);

  const handleCheckEngine = async () => {
    // BYPASS: Usamos el tenant directo en el botón para que ignore Auth si no hay.
    const bypassTenant = tenantId || 'tenant_agro_test';
    
    try {
      const productos = await listarProductosAgro(bypassTenant);
      
      const martir = productos.find(p => p.nombre.includes('Glifosato') || p.nombre.includes('Mártir'));
      if (martir) {
        // Margen Real = ((Precio Mercado - Costo Tenant) / Precio Mercado) * 100
        const margen = ((martir.precio_venta - martir.costo_reposicion) / martir.precio_venta) * 100;
        const ganancia = martir.precio_venta - martir.costo_reposicion;
        console.log(`✅ Glifosato — Precio Mercado: $${martir.precio_venta} | Costo: $${martir.costo_reposicion} | Margen Real: ${margen.toFixed(2)}%`);
        Alert.alert(
          '🌱 Motor Mártir — PRECIO REAL',
          `Precio Mercado: $${martir.precio_venta.toFixed(2)}\n` +
          `Costo Tenant:      $${martir.costo_reposicion.toFixed(2)}\n` +
          `─────────────────────\n` +
          `Ganancia/u:        $${ganancia.toFixed(2)}\n` +
          `📈 Margen Real:  ${margen.toFixed(2)}%`
        );
      } else {
        console.log('No se encontró el Mártir en la SQLite local con tenant:', bypassTenant);
        Alert.alert('Fallo DB', 'No se encontró el Glifosato Mártir.');
      }
    } catch (error) {
      console.error('❌ Error de conexión con SQLite', error);
      Alert.alert('Fallo DB', 'Explotó la conexión local con SQLite.');
    }
  };

  return (
    <View style={styles.container}>
      {/* Background Gradient Effect (Mental Model of glassmorphism host) */}
      <View style={styles.bgGlow1} />
      <View style={styles.bgGlow2} />

      <ScrollView
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl
            refreshing={loading && refreshTrigger > 0}
            onRefresh={onRefresh}
            tintColor="#38bdf8"
            colors={['#38bdf8']}
          />
        }
      >
        <Text style={styles.mainHeader}>North Star Profitability</Text>
        <Text style={styles.subHeader}>Sincronizado Localmente (Offline)</Text>

        <TouchableOpacity style={styles.actionButton} onPress={handleCheckEngine}>
          <Text style={styles.actionButtonText}>EJECUTAR MOTOR MÁRTIR</Text>
        </TouchableOpacity>

        <View style={styles.widgetsContainer}>
          <LowStockWidget stock={lowStock} />

          <ParcelHeatmapWidget parcels={parcelHeatmap} />

          <CropExpensesWidget expenses={cropExpenses} />

          <RecentActivityWidget feed={recentActivity} />
        </View>

        <Text style={styles.footerText}>Desliza para actualizar</Text>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#020617', // Extremely dark slate
  },
  bgGlow1: {
    position: 'absolute',
    top: -100,
    left: -50,
    width: 300,
    height: 300,
    backgroundColor: 'rgba(14, 165, 233, 0.15)', // Light blue glow
    borderRadius: 150,
  },
  bgGlow2: {
    position: 'absolute',
    bottom: -50,
    right: -100,
    width: 400,
    height: 400,
    backgroundColor: 'rgba(56, 189, 248, 0.05)', // Indigo glow
    borderRadius: 200,
  },
  scrollContent: {
    padding: 16,
    paddingTop: 40,
    paddingBottom: 60,
  },
  mainHeader: {
    fontSize: 28,
    fontWeight: '900',
    color: '#f8fafc',
    marginBottom: 4,
    letterSpacing: -0.5,
  },
  subHeader: {
    fontSize: 14,
    color: '#38bdf8',
    fontWeight: '600',
    marginBottom: 24,
    textTransform: 'uppercase',
  },
  widgetsContainer: {
    flex: 1,
  },
  footerText: {
    textAlign: 'center',
    color: '#64748b',
    fontSize: 12,
    marginTop: 20,
    fontStyle: 'italic',
  },
  actionButton: {
    backgroundColor: '#38bdf8',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 20,
    shadowColor: '#38bdf8',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 8,
    elevation: 5,
  },
  actionButtonText: {
    color: '#020617',
    fontWeight: '900',
    fontSize: 16,
    letterSpacing: 1,
  }
});

export default DashboardScreen;
