import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, StyleSheet } from 'react-native';
import { usePurchaseRegistry } from '../hooks/usePurchaseRegistry';
import { PurchaseRecord } from '../data/stock';

export const StockEntryHistory = ({ refreshTrigger }: { refreshTrigger: number }) => {
  const [history, setHistory] = useState<PurchaseRecord[]>([]);
  const { getRecentPurchases } = usePurchaseRegistry();

  useEffect(() => {
    const load = async () => {
      const data = await getRecentPurchases();
      setHistory(data);
    };
    load();
  }, [refreshTrigger]);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Últimos Ingresos</Text>
      {history.length === 0 ? (
        <Text style={styles.empty}>No hay registros recientes.</Text>
      ) : (
        <FlatList
          data={history}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <View style={styles.card}>
              <View style={styles.row}>
                <Text style={styles.insumoName}>{item.nombreInsumo}</Text>
                <Text style={styles.price}>USD {item.precioUnitarioUSD.toFixed(2)}</Text>
              </View>
              <Text style={styles.detail}>
                {item.cantidad} {item.unidadEntrada} - Lote: {item.lote}
              </Text>
              <Text style={styles.provider}>{item.proveedor}</Text>
              <Text style={styles.date}>{new Date(item.fechaRemito).toLocaleDateString()}</Text>
            </View>
          )}
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginTop: 20,
    padding: 10,
  },
  title: {
    color: '#38bdf8',
    fontSize: 18,
    fontWeight: '800',
    marginBottom: 15,
    textTransform: 'uppercase',
  },
  empty: {
    color: '#64748b',
    fontStyle: 'italic',
    textAlign: 'center',
    marginTop: 10,
  },
  card: {
    backgroundColor: 'rgba(255, 255, 255, 0.03)',
    borderRadius: 12,
    padding: 12,
    marginBottom: 10,
    borderLeftWidth: 3,
    borderLeftColor: '#38bdf8',
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  insumoName: {
    color: '#f8fafc',
    fontSize: 16,
    fontWeight: '700',
  },
  price: {
    color: '#10b981',
    fontWeight: '700',
  },
  detail: {
    color: '#94a3b8',
    fontSize: 13,
    marginTop: 4,
  },
  provider: {
    color: '#38bdf8',
    fontSize: 12,
    marginTop: 4,
  },
  date: {
    color: '#475569',
    fontSize: 11,
    marginTop: 2,
    textAlign: 'right',
  },
});
