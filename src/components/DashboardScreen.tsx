import React, { useState, useCallback, useEffect } from 'react';
import {
  ScrollView,
  View,
  Text,
  StyleSheet,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { useDashboardMetrics } from '../hooks/useDashboardMetrics';
import {
  LowStockWidget,
  CropExpensesWidget,
  ParcelHeatmapWidget,
  RecentActivityWidget,
} from './DashboardWidgets';

import { useTenant } from '../context/TenantContext';

const defaultFetchHeaders: Record<string, string> = {
  Accept: 'application/json',
  'ngrok-skip-browser-warning': '6907',
};

type AgroProduct = {
  sku?: string;
  margin?: number;
  gap?: number;
  stock?: number;
  cost_supa?: number;
  price?: number;
  suggested_price?: number;
};

/** Base URL sin barra final — debe coincidir con ngrok (EXPO_PUBLIC_DASHBOARD_URL en .env raíz Expo). */
function dashboardBaseUrl(): string {
  const raw = process.env.EXPO_PUBLIC_DASHBOARD_URL ?? 'http://127.0.0.1:3000';
  return raw.trim().replace(/\/+$/, '');
}

export const DashboardScreen = () => {
  const { tenantId } = useTenant();
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const [agroLoading, setAgroLoading] = useState(true);
  const [agroGapMoney, setAgroGapMoney] = useState<number | null>(null);
  const [agroRecuperado, setAgroRecuperado] = useState(0);
  const [agroProducts, setAgroProducts] = useState<AgroProduct[]>([]);
  const [agroError, setAgroError] = useState<string | null>(null);

  const {
    loading: metricsLoading,
    lowStock,
    cropExpenses,
    parcelHeatmap,
    recentActivity,
  } = useDashboardMetrics(refreshTrigger);

  const loadAgroReport = useCallback(async () => {
    setAgroLoading(true);
    setAgroError(null);
    const base = dashboardBaseUrl();
    try {
      // Equivale a: `${EXPO_PUBLIC_DASHBOARD_URL}/api/latest-report?sector=agro` (sin barra final en la base)
      const url = `${base}/api/latest-report?sector=agro`;
      const res = await fetch(url, { headers: defaultFetchHeaders });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const json = await res.json();
      const list = Array.isArray(json.products) ? (json.products as AgroProduct[]) : [];
      const gapMoney =
        list.reduce((s, p) => s + (Number(p.gap) || 0), 0) ||
        (typeof json.gap === 'number' ? json.gap : 0);
      setAgroGapMoney(gapMoney);
      setAgroRecuperado(typeof json.recuperado === 'number' ? json.recuperado : 0);
      setAgroProducts(list);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      setAgroError(msg);
      setAgroGapMoney(null);
      setAgroProducts([]);
    } finally {
      setAgroLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAgroReport();
  }, [loadAgroReport, refreshTrigger]);

  const onRefresh = useCallback(() => {
    setRefreshTrigger((prev) => prev + 1);
  }, []);

  const refreshing = agroLoading || (metricsLoading && refreshTrigger > 0);

  const labelSku = (p: AgroProduct) => String(p.sku ?? '—');

  return (
    <View style={styles.container}>
      <View style={styles.bgGlow1} />
      <View style={styles.bgGlow2} />

      <ScrollView
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl
            refreshing={!!refreshing && refreshTrigger > 0}
            onRefresh={onRefresh}
            tintColor="#38bdf8"
            colors={['#38bdf8']}
          />
        }
      >
        <View style={styles.headerRow}>
          <View style={styles.titleRow}>
            <Text style={styles.titleAntigravity}>Antigravity </Text>
            <Text style={styles.titleHubAccent}>Hub</Text>
          </View>
          <View style={styles.liveBadge}>
            <Text style={styles.liveBadgeText}>LIVE</Text>
          </View>
        </View>
        <Text style={styles.subtitle}>Radar AGRO — mismo /api/latest-report que la web</Text>
        {tenantId ? (
          <Text style={styles.tenantHint}>Tenant: {tenantId}</Text>
        ) : null}

        <Text style={styles.apiHint} numberOfLines={2}>
          EXPO_PUBLIC_DASHBOARD_URL → {dashboardBaseUrl()}
        </Text>

        {agroError ? (
          <View style={styles.errorBanner}>
            <Text style={styles.errorText}>
              No se pudo cargar: {agroError}. Revisá la URL en .env raíz y que Next esté
              publicado.
            </Text>
          </View>
        ) : null}

        <View style={styles.metricsRow}>
          <View style={[styles.metricCard, styles.metricCardDanger]}>
            <Text style={styles.metricLabel}>GAP de ganancia</Text>
            {agroLoading && agroGapMoney === null ? (
              <ActivityIndicator color="#991b1b" style={{ marginVertical: 12 }} />
            ) : (
              <Text style={styles.metricValueLarge}>
                ${(agroGapMoney ?? 0).toLocaleString('es-AR')}
              </Text>
            )}
            <Text style={styles.metricHint}>Σ gap monetario (mismo total que la web)</Text>
          </View>

          <View style={[styles.metricCard, styles.metricCardOk]}>
            <Text style={styles.metricLabel}>Ya recuperado</Text>
            <Text style={styles.metricValueLarge}>
              ${agroRecuperado.toLocaleString('es-AR')}
            </Text>
            <Text style={styles.metricHint}>API recuperado</Text>
          </View>
        </View>

        <Text style={styles.sectionTitle}>Radar de Márgenes</Text>
        <Text style={styles.sectionSub}>SKU · Margen real · Stock (sincronizado con el Dashboard)</Text>

        {agroProducts.length === 0 && !agroLoading ? (
          <View style={styles.emptyCard}>
            <Text style={styles.emptyText}>
              Sin productos críticos o motor desconectado.
            </Text>
          </View>
        ) : (
          agroProducts.map((p, idx) => {
            const m = Number(p.margin);
            const critical = !Number.isFinite(m) || m < 25;
            return (
              <View
                key={`${labelSku(p)}-${idx}`}
                style={[styles.productRow, critical && styles.productRowCritical]}
              >
                <Text style={styles.productSku} numberOfLines={3}>
                  {labelSku(p)}
                </Text>
                <View style={styles.radarCols}>
                  <View style={styles.radarCol}>
                    <Text style={styles.radarColLabel}>Margen</Text>
                    <Text style={[styles.radarColValue, critical ? styles.marginBad : styles.marginOk]}>
                      {Number.isFinite(m) ? `${m.toFixed(1)}%` : '—'}
                    </Text>
                  </View>
                  <View style={styles.radarCol}>
                    <Text style={styles.radarColLabel}>Stock</Text>
                    <Text style={styles.radarColValue}>
                      {p.stock != null ? String(p.stock) : '—'}
                    </Text>
                  </View>
                  <View style={styles.radarCol}>
                    <Text style={styles.radarColLabel}>Gap $</Text>
                    <Text style={styles.radarColValueMuted}>
                      {Number(p.gap ?? 0).toLocaleString('es-AR')}
                    </Text>
                  </View>
                </View>
              </View>
            );
          })
        )}

        {agroLoading && agroProducts.length > 0 ? (
          <ActivityIndicator color="#38bdf8" style={{ marginTop: 8 }} />
        ) : null}

        <Text style={styles.widgetsSectionTitle}>Operaciones locales</Text>
        <View style={styles.widgetsContainer}>
          <LowStockWidget stock={lowStock} />
          <ParcelHeatmapWidget parcels={parcelHeatmap} />
          <CropExpensesWidget expenses={cropExpenses} />
          <RecentActivityWidget feed={recentActivity} />
        </View>

        <Text style={styles.footerText}>Desliza para actualizar · datos = web (sector AGRO)</Text>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#020617',
  },
  bgGlow1: {
    position: 'absolute',
    top: -100,
    left: -50,
    width: 300,
    height: 300,
    backgroundColor: 'rgba(14, 165, 233, 0.12)',
    borderRadius: 150,
  },
  bgGlow2: {
    position: 'absolute',
    bottom: -50,
    right: -100,
    width: 400,
    height: 400,
    backgroundColor: 'rgba(56, 189, 248, 0.05)',
    borderRadius: 200,
  },
  scrollContent: {
    padding: 16,
    paddingTop: 36,
    paddingBottom: 60,
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 6,
  },
  titleRow: {
    flex: 1,
    flexDirection: 'row',
    flexWrap: 'wrap',
    alignItems: 'baseline',
  },
  titleAntigravity: {
    fontSize: 26,
    fontWeight: '900',
    color: '#f8fafc',
    letterSpacing: -0.5,
  },
  titleHubAccent: {
    fontSize: 26,
    fontWeight: '900',
    color: '#2563eb',
    letterSpacing: -0.5,
  },
  liveBadge: {
    backgroundColor: 'rgba(16, 185, 129, 0.2)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: 'rgba(16, 185, 129, 0.45)',
  },
  liveBadgeText: {
    fontSize: 11,
    fontWeight: '900',
    color: '#34d399',
    letterSpacing: 1.2,
  },
  subtitle: {
    fontSize: 11,
    color: '#94a3b8',
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: 0.8,
    marginBottom: 4,
  },
  tenantHint: {
    fontSize: 10,
    color: '#64748b',
    marginBottom: 2,
  },
  apiHint: {
    fontSize: 9,
    color: '#475569',
    marginBottom: 16,
  },
  errorBanner: {
    backgroundColor: 'rgba(239, 68, 68, 0.15)',
    borderWidth: 1,
    borderColor: 'rgba(239, 68, 68, 0.4)',
    borderRadius: 10,
    padding: 12,
    marginBottom: 16,
  },
  errorText: {
    color: '#fecaca',
    fontSize: 12,
    lineHeight: 18,
  },
  metricsRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 20,
  },
  metricCard: {
    flex: 1,
    borderRadius: 16,
    padding: 14,
    borderWidth: 2,
  },
  metricCardDanger: {
    backgroundColor: 'rgba(239, 68, 68, 0.12)',
    borderColor: 'rgba(239, 68, 68, 0.45)',
  },
  metricCardOk: {
    backgroundColor: 'rgba(16, 185, 129, 0.12)',
    borderColor: 'rgba(16, 185, 129, 0.45)',
  },
  metricLabel: {
    fontSize: 11,
    fontWeight: '700',
    color: '#94a3b8',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 6,
  },
  metricValueLarge: {
    fontSize: 26,
    fontWeight: '900',
    color: '#f8fafc',
  },
  metricHint: {
    fontSize: 10,
    color: '#64748b',
    marginTop: 6,
  },
  sectionTitle: {
    fontSize: 17,
    fontWeight: '800',
    color: '#e2e8f0',
    marginBottom: 4,
  },
  sectionSub: {
    fontSize: 11,
    color: '#64748b',
    marginBottom: 12,
  },
  emptyCard: {
    padding: 20,
    borderRadius: 12,
    backgroundColor: 'rgba(51, 65, 85, 0.35)',
    marginBottom: 16,
  },
  emptyText: {
    color: '#94a3b8',
    textAlign: 'center',
    fontSize: 13,
  },
  productRow: {
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'rgba(51, 65, 85, 0.8)',
    backgroundColor: 'rgba(15, 23, 42, 0.6)',
    padding: 12,
    marginBottom: 10,
  },
  productRowCritical: {
    borderColor: 'rgba(239, 68, 68, 0.45)',
    backgroundColor: 'rgba(239, 68, 68, 0.08)',
  },
  productSku: {
    fontSize: 14,
    fontWeight: '700',
    color: '#f1f5f9',
    marginBottom: 10,
  },
  radarCols: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 8,
  },
  radarCol: {
    flex: 1,
  },
  radarColLabel: {
    fontSize: 10,
    color: '#64748b',
    fontWeight: '700',
    textTransform: 'uppercase',
    marginBottom: 4,
  },
  radarColValue: {
    fontSize: 15,
    fontWeight: '800',
    color: '#e2e8f0',
  },
  radarColValueMuted: {
    fontSize: 14,
    fontWeight: '700',
    color: '#94a3b8',
  },
  marginBad: {
    color: '#f87171',
  },
  marginOk: {
    color: '#4ade80',
  },
  widgetsSectionTitle: {
    fontSize: 14,
    fontWeight: '800',
    color: '#94a3b8',
    marginTop: 8,
    marginBottom: 10,
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  widgetsContainer: {
    flex: 1,
  },
  footerText: {
    textAlign: 'center',
    color: '#64748b',
    fontSize: 11,
    marginTop: 20,
    fontStyle: 'italic',
  },
});

export default DashboardScreen;
