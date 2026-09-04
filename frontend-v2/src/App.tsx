import { Routes, Route, Navigate } from 'react-router-dom';
import { GlobalShell } from './layouts/GlobalShell';
import { ReconciliationDesk } from './pages/ReconciliationDesk';

function App() {
  return (
    <Routes>
      <Route path="/" element={<GlobalShell />}>
        {/* Redirect root to reconciliation for now since it's the main focus */}
        <Route index element={<Navigate to="/reconciliation" replace />} />
        <Route path="reconciliation" element={<ReconciliationDesk />} />
        <Route path="*" element={<div className="p-6 text-industrial-400">Under Construction</div>} />
      </Route>
    </Routes>
  );
}

export default App;
