import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import LogoMark from '../common/LogoMark';
import './AdminLayout.css';

// Halaman Pengaturan belum ada (rute masih placeholder), jadi tidak ditampilkan di menu
const NAV_ITEMS = [
  { to: '/admin/dashboard', label: 'Dashboard' },
  { to: '/admin/products', label: 'Produk' },
];

const AdminLayout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="admin-layout">
      <aside className="admin-sidebar">
        <div className="admin-brand">
          <LogoMark />
          <span className="admin-badge">Admin</span>
        </div>

        <nav className="admin-nav" aria-label="Menu admin">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => `admin-nav-link${isActive ? ' is-active' : ''}`}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="admin-account">
          <span className="admin-email" title={user?.email}>{user?.email}</span>
          <button type="button" onClick={handleLogout} className="admin-logout">
            Keluar
          </button>
        </div>
      </aside>

      <main className="admin-content">
        <Outlet />
      </main>
    </div>
  );
};

export default AdminLayout;
