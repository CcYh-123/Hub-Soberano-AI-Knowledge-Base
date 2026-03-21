import { Share, Alert } from 'react-native';

export const exportReport = async (title: string, data: any) => {
  try {
    const jsonString = JSON.stringify(data, null, 2);
    const result = await Share.share({
      title: title,
      message: jsonString,
    });

    if (result.action === Share.sharedAction) {
      if (result.activityType) {
        // shared with activity type of result.activityType
      } else {
        // shared
      }
    } else if (result.action === Share.dismissedAction) {
      // dismissed
    }
  } catch (error: any) {
    Alert.alert('Error al Exportar', error.message);
  }
};
