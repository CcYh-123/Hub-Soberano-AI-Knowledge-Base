import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { ParcelReportData } from '../hooks/useReporting';

const glassBg = 'rgba(15, 23, 42, 0.7)';
const cyan = '#38bdf8';
const green = '#10b981';

// ==========================================
// Vista 1: Resumen Financiero por Lote
// ==========================================
export const FinancialReportView = ({ reports }: { reports: ParcelReportData[] }) => {
  return (
    <ScrollView style={styles.container}>
      {reports.map(report => (
        <View key={report.parcelId} style={styles.card}>
          <View style={styles.header}>
            <Text style={styles.title}>{report.nombre}</Text>
            <Text style={styles.badge}>{report.cultivo}</Text>
          </View>
          
          <View style={styles.statsRow}>
            <View style={styles.stat}>
              <Text style={styles.statLabel}>Superficie</Text>
              <Text style={styles.statValue}>{report.superficie} ha</Text>
            </View>
            <View style={styles.stat}>
              <Text style={styles.statLabel}>Costo Acum.</Text>
              <Text style={styles.statValue}>${report.costoTotal.toFixed(2)}</Text>
            </View>
            <View style={styles.stat}>
              <Text style={styles.statLabel}>$/ha</Text>
              <Text style={styles.statValue}>${(report.costoTotal / report.superficie).toFixed(2)}</Text>
            </View>
          </View>

          {report.margenProyectado !== undefined && (
            <View style={styles.marginContainer}>
              <Text style={styles.marginLabel}>Margen Bruto Proyectado</Text>
              <Text style={[styles.marginValue, report.margenProyectado < 0 && { color: '#ef4444' }]}>
                ${report.margenProyectado.toFixed(2)} USD
              </Text>
            </View>
          )}
        </View>
      ))}
    </ScrollView>
  );
};

// ==========================================
// Vista 2: Libro de Campo (BPA)
// ==========================================
export const FieldBookView = ({ reports }: { reports: ParcelReportData[] }) => {
  const allApps = reports.flatMap(r => r.aplicaciones.map(a => ({ ...a, parcelName: r.nombre })))
    .sort((a, b) => new Date(b.fecha).getTime() - new Date(a.fecha).getTime());

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.sectionTitle}>Registro Técnico de Aplicaciones</Text>
      {allApps.map(app => (
        <View key={app.id} style={styles.bpaCard}>
          <View style={styles.bpaHeader}>
            <Text style={styles.bpaDate}>{new Date(app.fecha).toLocaleDateString()}</Text>
            <Text style={styles.bpaParcel}>{app.parcelName}</Text>
          </View>
          
          <View style={styles.bpaContent}>
            <Text style={styles.bpaLabel}>Insumos/Mezcla:</Text>
            {app.insumos.map((i, idx) => (
              <Text key={idx} style={styles.bpaItem}>• {i.nombre} - Dosis: {i.dosisHectarea} {i.unidadBase}/ha (Lote: {i.lote || 'N/A'})</Text>
            ))}
          </View>

          <View style={styles.weatherRow}>
            <Text style={styles.weatherText}>🌡️ {app.condicionesClimaticas.temperatura}°C</Text>
            <Text style={styles.weatherText}>💧 {app.condicionesClimaticas.humedad}%</Text>
            <Text style={styles.weatherText}>💨 {app.condicionesClimaticas.viento.velocidad} km/h {app.condicionesClimaticas.viento.direccion}</Text>
          </View>
        </View>
      ))}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 10 },
  card: { backgroundColor: glassBg, borderRadius: 12, padding: 15, marginBottom: 15, borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)' },
  header: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 15 },
  title: { color: '#fff', fontSize: 18, fontWeight: '700' },
  badge: { backgroundColor: cyan, color: '#000', paddingHorizontal: 8, paddingVertical: 2, borderRadius: 4, fontSize: 12, fontWeight: '700' },
  statsRow: { flexDirection: 'row', justifyContent: 'space-between', borderTopWidth: 1, borderTopColor: 'rgba(255,255,255,0.05)', paddingTop: 12 },
  stat: { alignItems: 'center' },
  statLabel: { color: '#94a3b8', fontSize: 10, textTransform: 'uppercase' },
  statValue: { color: '#f8fafc', fontSize: 14, fontWeight: '600', marginTop: 3 },
  marginContainer: { marginTop: 15, padding: 10, backgroundColor: 'rgba(16, 185, 129, 0.1)', borderRadius: 8, alignItems: 'center' },
  marginLabel: { color: '#94a3b8', fontSize: 11, marginBottom: 2 },
  marginValue: { color: green, fontSize: 18, fontWeight: '900' },
  sectionTitle: { color: cyan, fontSize: 14, fontWeight: '800', marginBottom: 10, textTransform: 'uppercase' },
  bpaCard: { backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: 8, padding: 12, marginBottom: 10, borderLeftWidth: 3, borderLeftColor: cyan },
  bpaHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 8 },
  bpaDate: { color: cyan, fontSize: 12, fontWeight: '700' },
  bpaParcel: { color: '#fff', fontSize: 12, fontWeight: '600' },
  bpaContent: { marginBottom: 8 },
  bpaLabel: { color: '#94a3b8', fontSize: 11, marginBottom: 4 },
  bpaItem: { color: '#f8fafc', fontSize: 13, marginLeft: 5 },
  weatherRow: { flexDirection: 'row', justifyContent: 'space-around', borderTopWidth: 1, borderTopColor: 'rgba(255,255,255,0.05)', paddingTop: 8 },
  weatherText: { color: '#64748b', fontSize: 11 }
});
