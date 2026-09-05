import { Platform } from 'react-native';

/** Light theme with high contrast for outdoor use. */
export const C = {
  bg: '#F4F5F7',
  surface: '#FFFFFF',
  surface2: '#EDF0F3',
  border: '#DDE2E8',
  text: '#0F1419',
  muted: '#5A6573',
  dim: '#98A2AE',
  amber: '#D97706',
  amberDim: '#FFF3DC',
  orange: '#E8590C',
  green: '#15803D',
  greenDim: '#E6F6EC',
  red: '#DC2626',
  redDim: '#FDECEC',
  onPrimary: '#FFFFFF',
};

export const MONO = Platform.select({ android: 'monospace', ios: 'Menlo', default: 'monospace' });
export const R = 8;
