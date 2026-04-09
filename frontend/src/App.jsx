import { Link, Route, Routes, useLocation } from 'react-router-dom';
import AdminDashboard from './pages/admin/AdminDashboard';
import MtsDashboard from './pages/mts/MtsDashboard';

export default function App() {
  const location = useLocation();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <p className="eyebrow">FINANCE SECURITY PORTFOLIO</p>
          <h1>MTS FDS</h1>
          <p className="sidebar-copy">가상 주식 MTS, 모의매매, 이상거래탐지, 관리자 운영 콘솔</p>
        </div>
        <nav>
          <Link className={location.pathname === '/' ? 'active' : ''} to="/">사용자 MTS</Link>
          <Link className={location.pathname === '/admin' ? 'active' : ''} to="/admin">관리자 콘솔</Link>
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
