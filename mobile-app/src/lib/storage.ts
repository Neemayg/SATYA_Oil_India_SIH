import AsyncStorage from '@react-native-async-storage/async-storage';
import { Observation, Settings, Activity } from './types';

const K = { obs: 'satya.obs.v2', settings: 'satya.settings.v2', acts: 'satya.activities.v2' };

export const DEFAULT_SETTINGS: Settings = {
  signedIn: false,
  name: '',
  crew: 'Field Crew',
  role: 'FIELD',
  projectId: 'PRJ-NBG-2026',
  serverUrl: 'http://31.42.125.16:8000',
};

async function read<T>(key: string, fallback: T): Promise<T> {
  try { const raw = await AsyncStorage.getItem(key); return raw ? (JSON.parse(raw) as T) : fallback; } catch { return fallback; }
}
async function write(key: string, v: unknown) { try { await AsyncStorage.setItem(key, JSON.stringify(v)); } catch {} }

export const loadObservations = () => read<Observation[]>(K.obs, []);
export const saveObservations = (v: Observation[]) => write(K.obs, v);
export const loadSettings = async () => ({ ...DEFAULT_SETTINGS, ...(await read<Partial<Settings>>(K.settings, {})) });
export const saveSettings = (v: Settings) => write(K.settings, v);
export const loadActivities = () => read<Activity[]>(K.acts, []);
export const saveActivities = (v: Activity[]) => write(K.acts, v);
