import React from 'react';
import { SafeAreaView, StatusBar } from 'react-native';
import { AuthProvider } from './src/hooks/useAuth';
import { TenantProvider } from './src/context/TenantContext';
import DashboardScreen from './src/components/DashboardScreen';

export default function App() {
  return (
    <AuthProvider>
      <TenantProvider>
        <SafeAreaView style={{ flex: 1, backgroundColor: '#001a11' }}>
          <StatusBar barStyle="light-content" />
          <DashboardScreen />
        </SafeAreaView>
      </TenantProvider>
    </AuthProvider>
  );
}