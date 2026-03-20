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

// ── Fase 5 - Fuel: URL del Puente (localtunnel) ─────────────────────────────
// Para actualizar el túnel: cambiar solo esta constante.
const BRIDGE_URL = 'https://seven-humans-hang.loca.lt';

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

  // Semáforo: >20% verde, >=15% amarillo, <15% rojo
  const getSemaforo = (margen: number): string => {
    if (margen >= 20) return '🟢';
    if (margen >= 15) return '🟡';
    return '🔴';
  };

  const renderLineas = (productos: { nombre: string; precio_venta: number; costo_reposicion: number }[]) =>
    productos.map(p => {
      const ganancia = p.precio_venta - p.costo_reposicion;
      const margen = (ganancia / p.precio_venta) * 100;
      console.log(`${getSemaforo(margen)} ${p.nombre} — Margen: ${margen.toFixed(2)}% | Ganancia: $${ganancia.toFixed(2)}/u`);
      return `${getSemaforo(margen)} ${p.nombre}: ${margen.toFixed(2)}% ($${ganancia.toFixed(2)}/u)`;
    });

  const handleCheckEngine = async () => {
    const bypassTenant = tenantId || 'tenant_agro_test';

    // ── BRIDGE FIRST: fetch al túnel localtunnel ─────────────────────────
    try {
      console.log(`🌐 Conectando al puente: ${BRIDGE_URL}/get-martires`);
      const resp = await fetch(`${BRIDGE_URL}/get-martires`, {
        method: 'GET',
        headers: {
          'bypass-tunnel-reminder': 'true',  // Header requerido por localtunnel
          'Content-Type': 'application/json',
        },
      });

      if (!resp.ok) throw new Error(`HTTP ${resp.status} — ${resp.statusText}`);

      const json = await resp.json();
      const productos = json.productos ?? [];

      if (productos.length === 0) throw new Error('El puente devolvió lista vacía');

      const lineas = renderLineas(productos);
      Alert.alert(
        '🌐 Motor Mártir — Puente Activo',
        `[Bridge: ${BRIDGE_URL}]\n\n` + lineas.join('\n')
      );
      return; // Éxito — no necesita fallback

    } catch (bridgeError: any) {
      const bridgeMsg = bridgeError?.message || 'Error desconocido en el puente';
      console.warn(`⚠️ Bridge falló (${bridgeMsg}), activando fallback SQLite...`);
    }

    // ── FALLBACK: SQLite local ───────────────────────────────────────────
    try {
      const productos = await listarProductosAgro(bypassTenant);

      if (!productos || productos.length === 0) {
        Alert.alert('Fallo Total', 'Sin puente y sin datos locales.');
        return;
      }

      const lineas = renderLineas(productos);
      Alert.alert(
        '📦 Motor Mártir — Modo Offline',
        `[Fuente: SQLite Local]\n\n` + lineas.join('\n')
      );

    } catch (localError: any) {
      const msg = localError?.message || JSON.stringify(localError) || 'Error desconocido';
      console.error('❌ Error Motor Mártir (SQLite):', msg);
      Alert.alert('🔴 Error de Puente', `Bridge: Falló\nSQLite: ${msg}`);
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
        
        <View style={styles.offlineStatusContainer}>
          <View style={styles.statusDot} />
          <Text style={styles.offlineStatusText}>Sincronizado Localmente (Soberanía Offline)</Text>
        </View>

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
  offlineStatusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(56, 189, 248, 0.1)',
    alignSelf: 'flex-start',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: 'rgba(56, 189, 248, 0.3)',
    marginBottom: 20,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#38bdf8',
    marginRight: 8,
    shadowColor: '#38bdf8',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 1,
    shadowRadius: 4,
  },
  offlineStatusText: {
    fontSize: 11,
    color: '#38bdf8',
    fontWeight: '800',
    letterSpacing: 0.5,
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
