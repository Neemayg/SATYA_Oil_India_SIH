import AsyncStorage from '@react-native-async-storage/async-storage';
import { Observation, Settings } from './types';

const OBS_KEY = 'satya.observations';
const SETTINGS_KEY = 'satya.settings';

export const DEFAULT_SETTINGS: Settings = {
  serverUrl: 'http://10.0.2.2:8000',
  projectId: 'NBG',
  author: 'Field Engineer',
};

export async function loadObservations(): Promise<Observation[]> {
  try {
    const raw = await AsyncStorage.getItem(OBS_KEY);
    return raw ? (JSON.parse(raw) as Observation[]) : [];
  } catch {
    return [];
  }
}

export async function saveObservations(list: Observation[]): Promise<void> {
  await AsyncStorage.setItem(OBS_KEY, JSON.stringify(list));
}

export async function loadSettings(): Promise<Settings> {
  try {
    const raw = await AsyncStorage.getItem(SETTINGS_KEY);
    return raw ? { ...DEFAULT_SETTINGS, ...JSON.parse(raw) } : DEFAULT_SETTINGS;
  } catch {
    return DEFAULT_SETTINGS;
  }
}

export async function saveSettings(s: Settings): Promise<void> {
  await AsyncStorage.setItem(SETTINGS_KEY, JSON.stringify(s));
}
