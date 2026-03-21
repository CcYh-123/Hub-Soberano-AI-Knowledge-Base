import React, { useState } from 'react';
import { 
  View, 
  Text, 
  TextInput, 
  TouchableOpacity, 
  StyleSheet, 
  Alert, 
  ActivityIndicator 
} from 'react-native';
import { supabase } from '../lib/supabase';

export const LoginScreen = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    setLoading(true);
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) Alert.alert('Error de Acceso', error.message);
    setLoading(false);
  };

  return (
    <View style={styles.container}>
      <View style={styles.glassCard}>
        <Text style={styles.logoText}>ANTIGRAVITY</Text>
        <Text style={styles.tagline}>Sovereign Agro Systems</Text>
        
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Email Corporativo</Text>
          <TextInput
            style={styles.input}
            placeholder="usuario@empresa.com"
            placeholderTextColor="#64748b"
            autoCapitalize="none"
            value={email}
            onChangeText={setEmail}
          />
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Password</Text>
          <TextInput
            style={styles.input}
            placeholder="••••••••"
            placeholderTextColor="#64748b"
            secureTextEntry
            value={password}
            onChangeText={setPassword}
          />
        </View>

        <TouchableOpacity 
          style={styles.loginBtn} 
          onPress={handleLogin}
          disabled={loading}
        >
          {loading ? <ActivityIndicator color="#000" /> : <Text style={styles.loginText}>ENTRAR AL GALPÓN</Text>}
        </TouchableOpacity>
        
        <Text style={styles.footerNote}>Sincronización Offline Activada</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#020617',
    justifyContent: 'center',
    padding: 20,
  },
  glassCard: {
    backgroundColor: 'rgba(15, 23, 42, 0.8)',
    borderRadius: 24,
    padding: 30,
    borderWidth: 1,
    borderColor: 'rgba(56, 189, 248, 0.2)',
  },
  logoText: {
    color: '#fff',
    fontSize: 32,
    fontWeight: '900',
    textAlign: 'center',
    letterSpacing: 2,
  },
  tagline: {
    color: '#38bdf8',
    textAlign: 'center',
    fontSize: 12,
    fontWeight: '700',
    marginBottom: 40,
    textTransform: 'uppercase',
  },
  inputGroup: {
    marginBottom: 20,
  },
  label: {
    color: '#94a3b8',
    fontSize: 12,
    fontWeight: '800',
    marginBottom: 8,
    textTransform: 'uppercase',
  },
  input: {
    backgroundColor: 'rgba(0, 0, 0, 0.3)',
    borderRadius: 12,
    padding: 15,
    color: '#fff',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.05)',
  },
  loginBtn: {
    backgroundColor: '#38bdf8',
    borderRadius: 12,
    padding: 18,
    alignItems: 'center',
    marginTop: 10,
  },
  loginText: {
    color: '#000',
    fontWeight: '900',
    fontSize: 16,
  },
  footerNote: {
    color: '#475569',
    textAlign: 'center',
    marginTop: 20,
    fontSize: 11,
  }
});
