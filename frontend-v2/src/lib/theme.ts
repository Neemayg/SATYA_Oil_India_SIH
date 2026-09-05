import { useEffect, useState } from 'react';

export type Theme = 'dark' | 'light';
const KEY = 'satya.theme';

function read(): Theme {
  try { return localStorage.getItem(KEY) === 'light' ? 'light' : 'dark'; } catch { return 'dark'; }
}
function apply(t: Theme) {
  if (t === 'light') document.documentElement.setAttribute('data-theme', 'light');
  else document.documentElement.removeAttribute('data-theme');
}

apply(read());

export function useTheme(): [Theme, () => void] {
  const [t, setT] = useState<Theme>(read);
  useEffect(() => { apply(t); try { localStorage.setItem(KEY, t); } catch {} }, [t]);
  return [t, () => setT(x => (x === 'dark' ? 'light' : 'dark'))];
}
