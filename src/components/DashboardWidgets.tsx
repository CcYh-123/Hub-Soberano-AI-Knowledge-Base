import React from 'react';
import { View, Text, StyleSheet, FlatList } from 'react-native';
import {
  StockItem,
} from '../data/stock';
import {
  ExpenseByCrop,
  ParcelInvestment,
  ActivityFeedItem
} from '../hooks/useDashboardMetrics';
import { useAuth } from '../hooks/useAuth';

const glassBg = 'rgba(15, 23, 42, 0.7)'; // Deep dark background for outdoor contrast
const glassBorder = 'rgba(56, 189, 248, 0.3)'; // Cyan accent border

// ==========================================
// Widget 1: Alertas de Galpón (Low Stock)
// ==========================================
export const LowStockWidget = ({ stock }: { stock: StockItem[] }) => (
  <View style={styles.widgetCard}>
    <Text style={styles.widgetTitle}>⚠️ Alertas de Galpón (Top 5 Bajos)</Text>
    {stock.length === 0 ? (
      <Text style={styles.emptyText}>Inventario en niveles óptimos.</Text>
    ) : (
      stock.map((item, idx) => (
        <View key={item.insumoId + idx} style={styles.row}>
          <Text style={styles.itemTextMain} numberOfLines={1}>{item.nombreInsumo}</Text>
          <Text style={[styles.itemTextAlert, item.cantidadDisponible <= 0 && { color: '#ef4444' }]}>
            {item.cantidadDisponible.toFixed(2)} {item.unidad}
          </Text>
        </View>
      ))
    )}
  </View>
);

// ==========================================
// Widget 2: Resumen de Gastos por Cultivo
// ==========================================
export const CropExpensesWidget = ({ expenses }: { expenses: ExpenseByCrop[] }) => {
  const { profile } = useAuth();

  if (profile?.role === 'OPERADOR') return null; // Security: Hide financial metrics from operators

  return (
    <View style={styles.widgetCard}>
      <Text style={styles.widgetTitle}>📊 Inversión por Cultivo (USD)</Text>
      {expenses.length === 0 ? (
        <Text style={styles.emptyText}>No hay gastos registrados en campaña.</Text>
      ) : (
        expenses.map((exp, idx) => (
          <View key={exp.cultivo + idx} style={styles.row}>
            <Text style={styles.itemTextMain}>{exp.cultivo}</Text>
            <Text style={styles.itemTextMoney}>${exp.totalUSD.toFixed(2)}</Text>
          </View>
        ))
      )}
    </View>
  );
};

// ==========================================
// Widget 3: Mapa de Calor (Inversión por Parcela)
// ==========================================
export const ParcelHeatmapWidget = ({ parcels }: { parcels: ParcelInvestment[] }) => {
  const { profile } = useAuth();
  if (profile?.role === 'OPERADOR') return null;

  // Encontrar el máximo para calcular el porcentaje visual de la "barra"
  const maxInversion = parcels.length > 0 ? parcels[0].totalInvested : 0;

  return (
    <View style={styles.widgetCard}>
      <Text style={styles.widgetTitle}>🔥 Mapa de Inversión (Top Parcelas)</Text>
      {parcels.length === 0 ? (
        <Text style={styles.emptyText}>Sin actividad en lotes.</Text>
      ) : (
        parcels.slice(0, 5).map((p, idx) => {
          const widthPct = maxInversion > 0 ? (p.totalInvested / maxInversion) * 100 : 0;
          return (
            <View key={p.parcelName + idx} style={styles.barContainer}>
              <View style={styles.row}>
                <Text style={styles.itemTextMain}>{p.parcelName}</Text>
                <Text style={styles.itemTextMoney}>${p.totalInvested.toFixed(2)}</Text>
              </View>
              <View style={styles.barTrack}>
                <View style={[styles.barFill, { width: `${widthPct}%` }]} />
              </View>
            </View>
          );
        })
      )}
    </View>
  );
};

// ==========================================
// Widget 4: Actividad Reciente (Feed)
// ==========================================
export const RecentActivityWidget = ({ feed }: { feed: ActivityFeedItem[] }) => (
  <View style={[styles.widgetCard, { paddingBottom: 5 }]}>
    <Text style={styles.widgetTitle}>⏱️ Actividad Reciente</Text>
    {feed.length === 0 ? (
      <Text style={styles.emptyText}>Sin movimientos recientes.</Text>
    ) : (
      feed.map((act, idx) => (
        <View key={act.id + idx} style={styles.feedItem}>
          <View style={styles.feedIconContainer}>
            <Text style={styles.feedIcon}>{act.type === 'APPLICATION' ? '🚜' : '📦'}</Text>
          </View>
          <View style={styles.feedContent}>
            <View style={styles.row}>
              <Text style={styles.feedTitleMain} numberOfLines={1}>{act.title}</Text>
              <Text style={act.type === 'PURCHASE' ? styles.feedTextPositive : styles.feedTextNegative}>
                {act.amountText}
              </Text>
            </View>
            <Text style={styles.feedSubtitle} numberOfLines={1}>{act.subtitle}</Text>
            <Text style={styles.feedTime}>{new Date(act.date).toLocaleDateString()} {new Date(act.date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</Text>
          </View>
        </View>
      ))
    )}
  </View>
);

// ==========================================
// Estilos Alto Contraste (Outdoor Mode)
// ==========================================
const styles = StyleSheet.create({
  widgetCard: {
    backgroundColor: glassBg,
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: glassBorder,
    // Sombra para dar profundidad en UI
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.5,
    shadowRadius: 8,
    elevation: 5,
  },
  widgetTitle: {
    color: '#38bdf8', // Cyan brillante
    fontSize: 16,
    fontWeight: '800',
    marginBottom: 12,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  emptyText: {
    color: '#94a3b8',
    fontStyle: 'italic',
    textAlign: 'center',
    paddingVertical: 10,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 6,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: 'rgba(255,255,255,0.1)',
  },
  itemTextMain: {
    color: '#f8fafc',
    fontSize: 15,
    fontWeight: '600',
    flex: 1,
  },
  itemTextAlert: {
    color: '#fbbf24', // Ambar
    fontSize: 15,
    fontWeight: '800',
  },
  itemTextMoney: {
    color: '#10b981', // Verde esmeralda alto contraste
    fontSize: 15,
    fontWeight: '800',
  },
  // Bar Chart (Heatmap)
  barContainer: {
    marginBottom: 8,
  },
  barTrack: {
    height: 6,
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 3,
    marginTop: 4,
    overflow: 'hidden',
  },
  barFill: {
    height: '100%',
    backgroundColor: '#ef4444', // Rojo intenso para mostrar donde se "quema" el dinero
    borderRadius: 3,
  },
  // Feed List
  feedItem: {
    flexDirection: 'row',
    marginBottom: 12,
  },
  feedIconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(56, 189, 248, 0.1)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  feedIcon: {
    fontSize: 20,
  },
  feedContent: {
    flex: 1,
    justifyContent: 'center',
  },
  feedTitleMain: {
    color: '#f8fafc',
    fontSize: 14,
    fontWeight: '700',
    flex: 1,
    marginRight: 8,
  },
  feedTextPositive: {
    color: '#38bdf8',
    fontSize: 13,
    fontWeight: '800',
  },
  feedTextNegative: {
    color: '#ef4444',
    fontSize: 13,
    fontWeight: '800',
  },
  feedSubtitle: {
    color: '#94a3b8',
    fontSize: 12,
    marginTop: 2,
  },
  feedTime: {
    color: '#475569',
    fontSize: 10,
    marginTop: 2,
    textTransform: 'uppercase',
  }
});
