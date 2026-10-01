import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import './UserLayout.css';

const UserLayout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="user-layout">
      <nav className="user-navbar">
        <div className="navbar-container">
          <Link to="/user/home" className="nav-logo">
            WajahKu.id
          </Link>
          
          <div className="nav-links">
            <Link to="/user/home">Beranda</Link>
            <Link to="/user/camera">Scan Wajah</Link>
            <Link to="/user/history">Riwayat</Link>
          </div>

          <div className="nav-user">
            <span>{user?.email}</span>
            <button onClick={handleLogout} className="btn-logout">
              Keluar
            </button>
          </div>
        </div>
      </nav>

      <main className="user-content">
        <Outlet />
      </main>
    </div>
  );
};

export default UserLayout;
