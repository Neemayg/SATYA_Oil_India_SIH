import { Outlet, NavLink } from 'react-router-dom';
import { Search, User } from 'lucide-react';

const NAV_ITEMS = [
  { label: 'Control Tower', path: '/' },
  { label: 'Schedule', path: '/schedule' },
  { label: 'Field Capture', path: '/field-capture' },
  { label: 'Reconciliation', path: '/reconciliation' },
  { label: 'Evidence', path: '/evidence' },
  { label: 'Reports', path: '/reports' },
];

export function GlobalShell() {
  return (
    <div className="min-h-screen bg-industrial-950 flex flex-col text-industrial-300">
      {/* Top Navigation */}
      <header className="h-14 border-b border-industrial-800 flex items-center px-6 shrink-0 bg-industrial-950 z-50">
        <div className="flex items-center gap-10">
          <div className="font-bold text-white tracking-[0.2em] text-lg">
            SATYA
          </div>
          
          <nav className="flex items-center gap-8 h-full">
            {NAV_ITEMS.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `text-sm tracking-wide h-14 flex items-center border-b-2 transition-colors ${
                    isActive
                      ? 'border-accent-500 text-white font-medium'
                      : 'border-transparent text-industrial-400 hover:text-industrial-200'
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>

        <div className="ml-auto flex items-center gap-4">
          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-industrial-500" />
            <input
              type="text"
              placeholder="Search activities, events..."
              className="bg-industrial-900 border border-industrial-800 rounded px-9 py-1.5 text-sm text-white placeholder-industrial-500 focus:outline-none focus:border-industrial-600 focus:ring-1 focus:ring-industrial-600 w-64 transition-all"
            />
          </div>
          
          {/* Avatar Placeholder */}
          <div className="w-8 h-8 bg-industrial-800 rounded border border-industrial-700 flex items-center justify-center text-sm font-medium text-white">
            R
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 flex overflow-hidden">
        <Outlet />
      </main>
    </div>
  );
}
