import { useState, useEffect, useCallback } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { generateUUID } from '../utils/uuid';

interface FormState {
  id: string;
  nombreLote: string;
  superficieDeclarada: string;
  superficieProductiva: string;
  cultivoActual: string;
  cultivoAntecesor: string;
  latitude?: number;
  longitude?: number;
}

const STORAGE_KEY_PREFIX = '@ParcelaForm:';

export const useOfflineForm = (formId?: string) => {
  const [id] = useState(formId || generateUUID());
  const [data, setData] = useState<FormState>({
    id,
    nombreLote: '',
    superficieDeclarada: '',
    superficieProductiva: '',
    cultivoActual: '',
    cultivoAntecesor: '',
  });
  const [isLoading, setIsLoading] = useState(true);

  // Load initial data if exists
  useEffect(() => {
    const loadData = async () => {
      try {
        const savedData = await AsyncStorage.getItem(`${STORAGE_KEY_PREFIX}${id}`);
        if (savedData) {
          setData(JSON.parse(savedData));
        }
      } catch (e) {
        console.error('Failed to load form data', e);
      } finally {
        setIsLoading(false);
      }
    };
    loadData();
  }, [id]);

  // Auto-save logic
  const saveToStorage = useCallback(async (currentData: FormState) => {
    try {
      await AsyncStorage.setItem(`${STORAGE_KEY_PREFIX}${id}`, JSON.stringify(currentData));
      console.log('Form auto-saved:', id);
    } catch (e) {
      console.error('Failed to save form data', e);
    }
  }, [id]);

  const updateField = (field: keyof FormState, value: any) => {
    setData((prev) => {
      const newData = { ...prev, [field]: value };
      
      // Logic: Productiva default to Declarada if empty
      if (field === 'superficieDeclarada' && !prev.superficieProductiva) {
        newData.superficieProductiva = value;
      }
      
      return newData;
    });
  };

  const handleBlur = () => {
    saveToStorage(data);
  };

  return {
    data,
    updateField,
    handleBlur,
    isLoading,
    id
  };
};
