import { Link, Route, Routes } from 'react-router-dom';
import AdminDashboard from './pages/admin/AdminDashboard';
import MtsDashboard from './pages/mts/MtsDashboard';

export default function App() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <h1>MTS FDS</h1>
        <nav>
          <Link to="/">MTS</Link>
          <Link to="/admin">Admin Console</Link>
        </nav>
      </aside>
      <main className="content">
        <Routes>
          <Route path="/" element={<MtsDashboard />} />
          <Route path="/admin" element={<AdminDashboard />} />
        </Routes>
      </main>
    </div>
  );
}
