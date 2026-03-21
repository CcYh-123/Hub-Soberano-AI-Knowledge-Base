import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  TouchableOpacity, 
  StyleSheet, 
  TextInput, 
  ScrollView 
} from 'react-native';
import { useReporting, ParcelReportData } from '../hooks/useReporting';
import { FinancialReportView, FieldBookView } from './ReportViews';
import { exportReport } from '../utils/reportExporter';

export const ReportingScreen = () => {
  const [viewType, setViewType] = useState<'FINANCIAL' | 'BPA'>('FINANCIAL');
  const [reports, setReports] = useState<ParcelReportData[]>([]);
  const [proyeccion, setProyeccion] = useState({ rinde: '', precio: '' });
  const { loading, getParcelReports } = useReporting();

  const loadData = async () => {
    const data = await getParcelReports({}, 
      proyeccion.rinde && proyeccion.precio 
        ? { rinde: parseFloat(proyeccion.rinde), precio: parseFloat(proyeccion.precio) }
        : undefined
    );
    setReports(data || []);
  };

  useEffect(() => {
    loadData();
  }, [proyeccion]);

  const handleExport = () => {
    exportReport(`Reporte_${viewType}_${new Date().toISOString().split('T')[0]}`, reports);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.header}>Reportes de Campaña</Text>
      
      {/* Toggles */}
      <View style={styles.toggleRow}>
        <TouchableOpacity 
          style={[styles.toggleBtn, viewType === 'FINANCIAL' && styles.toggleBtnActive]}
          onPress={() => setViewType('FINANCIAL')}
        >
          <Text style={[styles.toggleText, viewType === 'FINANCIAL' && styles.toggleTextActive]}>Financiero</Text>
        </TouchableOpacity>
        <TouchableOpacity 
          style={[styles.toggleBtn, viewType === 'BPA' && styles.toggleBtnActive]}
          onPress={() => setViewType('BPA')}
        >
          <Text style={[styles.toggleText, viewType === 'BPA' && styles.toggleTextActive]}>Libro de Campo</Text>
        </TouchableOpacity>
      </View>

      {viewType === 'FINANCIAL' && (
        <View style={styles.filterBox}>
          <Text style={styles.filterTitle}>Proyección de Margen</Text>
          <View style={styles.row}>
            <TextInput
              style={styles.input}
              placeholder="Rinde (tn/ha)"
              placeholderTextColor="#64748b"
              keyboardType="decimal-pad"
              value={proyeccion.rinde}
              onChangeText={v => setProyeccion(p => ({ ...p, rinde: v }))}
            />
            <TextInput
              style={styles.input}
              placeholder="Precio ($/tn)"
              placeholderTextColor="#64748b"
              keyboardType="decimal-pad"
              value={proyeccion.precio}
              onChangeText={v => setProyeccion(p => ({ ...p, precio: v }))}
            />
          </View>
        </View>
      )}

      {viewType === 'FINANCIAL' ? <FinancialReportView reports={reports} /> : <FieldBookView reports={reports} />}

      <TouchableOpacity style={styles.exportBtn} onPress={handleExport}>
        <Text style={styles.exportText}>Exportar JSON / Compartir</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#020617', padding: 16, paddingTop: 40 },
  header: { fontSize: 24, fontWeight: '900', color: '#fff', marginBottom: 20 },
  toggleRow: { flexDirection: 'row', backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: 12, padding: 4, marginBottom: 20 },
  toggleBtn: { flex: 1, paddingVertical: 10, alignItems: 'center', borderRadius: 10 },
  toggleBtnActive: { backgroundColor: '#38bdf8' },
  toggleText: { color: '#94a3b8', fontWeight: '700' },
  toggleTextActive: { color: '#000' },
  filterBox: { backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: 12, padding: 12, marginBottom: 15 },
  filterTitle: { color: '#38bdf8', fontSize: 12, fontWeight: '800', marginBottom: 8, textTransform: 'uppercase' },
  row: { flexDirection: 'row', justifyContent: 'space-between' },
  input: { flex: 0.48, backgroundColor: 'rgba(0,0,0,0.2)', color: '#fff', padding: 10, borderRadius: 8, fontSize: 14 },
  exportBtn: { backgroundColor: '#10b981', padding: 16, borderRadius: 12, alignItems: 'center', marginTop: 10 },
  exportText: { color: '#000', fontWeight: '900', textTransform: 'uppercase' }
});
