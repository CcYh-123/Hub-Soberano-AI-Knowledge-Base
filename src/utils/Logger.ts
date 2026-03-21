import AsyncStorage from '@react-native-async-storage/async-storage';

const LOG_STORAGE_KEY = '@System:Logs';

export interface LogEntry {
  timestamp: string;
  level: 'INFO' | 'WARN' | 'ERROR';
  message: string;
  context?: any;
}

export class Logger {
  static async log(level: 'INFO' | 'WARN' | 'ERROR', message: string, context?: any) {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      context,
    };

    // Print to console for dev
    if (level === 'ERROR') console.error(`[${level}] ${message}`, context);
    else console.log(`[${level}] ${message}`);

    try {
      const existingLogsStr = await AsyncStorage.getItem(LOG_STORAGE_KEY);
      const logs = existingLogsStr ? JSON.parse(existingLogsStr) : [];
      logs.push(entry);
      
      // Keep only last 100 logs to save space
      const trimmedLogs = logs.slice(-100);
      await AsyncStorage.setItem(LOG_STORAGE_KEY, JSON.stringify(trimmedLogs));
    } catch (e) {
      console.error('Failed to save log to local storage', e);
    }
  }

  static async getLogs(): Promise<LogEntry[]> {
    const logsStr = await AsyncStorage.getItem(LOG_STORAGE_KEY);
    return logsStr ? JSON.parse(logsStr) : [];
  }

  static async clearLogs() {
    await AsyncStorage.removeItem(LOG_STORAGE_KEY);
  }
}
