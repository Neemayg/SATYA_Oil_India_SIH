import { Routes, Route } from 'react-router-dom';
import { GlobalShell } from './layouts/GlobalShell';
import { ControlTower } from './pages/ControlTower';
import { Schedule } from './pages/Schedule';
import { FieldCapture } from './pages/FieldCapture';
import { ReconciliationDesk } from './pages/ReconciliationDesk';
import { Evidence } from './pages/Evidence';
import { Reports } from './pages/Reports';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<GlobalShell />}>
        <Route index element={<ControlTower />} />
        <Route path="schedule" element={<Schedule />} />
        <Route path="field-capture" element={<FieldCapture />} />
        <Route path="reconciliation" element={<ReconciliationDesk />} />
        <Route path="reconciliation/:eventId" element={<ReconciliationDesk />} />
        <Route path="evidence" element={<Evidence />} />
        <Route path="evidence/:eventId" element={<Evidence />} />
        <Route path="reports" element={<Reports />} />
        <Route path="*" element={<ControlTower />} />
      </Route>
    </Routes>
  );
}
