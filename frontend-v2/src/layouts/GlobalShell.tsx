import { Outlet, NavLink } from 'react-router-dom';
import { Search, Sun, Moon } from 'lucide-react';
import { cn } from '../lib/utils';
import { useTheme } from '../lib/theme';

const NAV = [
  { label: 'Control Tower', path: '/', end: true },
  { label: 'Schedule', path: '/schedule' },
  { label: 'Field Capture', path: '/field-capture' },
  { label: 'Reconciliation', path: '/reconciliation' },
  { label: 'Evidence', path: '/evidence' },
  { label: 'Reports', path: '/reports' },
];

export function GlobalShell() {
  const [theme, toggle] = useTheme();
  return (
    <div className="min-h-screen flex flex-col bg-bg">
      <header className="h-14 border-b border-line bg-bg flex items-center px-8 shrink-0 sticky top-0 z-40">
        <div className="font-bold tracking-[0.3em] text-ink text-base mr-10">SATYA</div>
        <nav className="flex items-center gap-8 h-full">
          {NAV.map(({ label, path, end }) => (
            <NavLink key={path} to={path} end={end}
              className={({ isActive }) => cn('h-14 flex items-center text-[12px] tracking-[0.18em] uppercase border-b-2 transition-colors',
                isActive ? 'border-brand text-ink font-semibold' : 'border-transparent text-ink-3 hover:text-ink-2')}>
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="ml-auto flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-ink-3" />
            <input placeholder="Search activities, events…"
              className="bg-surface border border-line rounded-sm pl-9 pr-3 py-1.5 text-sm text-ink placeholder-ink-3 w-64 focus:outline-none focus:border-ink-3 font-mono" />
          </div>
          <button onClick={toggle} title={theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'}
            className="w-8 h-8 bg-surface-2 border border-line rounded-sm flex items-center justify-center text-ink-2 hover:text-ink">
            {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>
          <div className="w-8 h-8 bg-surface-2 border border-line rounded-sm flex items-center justify-center text-sm font-semibold text-ink">R</div>
        </div>
      </header>
      <main className="flex-1 min-w-0"><Outlet /></main>
    </div>
  );
}
