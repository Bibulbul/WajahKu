import { Outlet, Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import LogoMark from '../common/LogoMark';
import './UserLayout.css';

const NAV_ITEMS = [
  { to: '/user/home', label: 'Beranda' },
  { to: '/user/camera', label: 'Scan wajah' },
  { to: '/user/history', label: 'Riwayat' },
];

const UserLayout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="user-layout">
      <header className="user-navbar">
        <div className="navbar-container">
          <Link to="/user/home" className="nav-logo" aria-label="WajahKu, ke beranda">
            <LogoMark />
          </Link>

          <nav className="nav-links" aria-label="Menu utama">
            {NAV_ITEMS.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) => `nav-link${isActive ? ' is-active' : ''}`}
              >
                {item.label}
              </NavLink>
            ))}
          </nav>

          <div className="nav-user">
            <span className="nav-username" title={user?.username}>{user?.username}</span>
            <button type="button" onClick={handleLogout} className="user-logout">
              Keluar
            </button>
          </div>
        </div>
      </header>

      <main className="user-content">
        <Outlet context={{ user }} />
      </main>
    </div>
  );
};

export default UserLayout;
