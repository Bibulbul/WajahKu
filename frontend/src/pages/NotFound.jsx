import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import FaceDots from '../components/common/FaceDots';
import LogoMark from '../components/common/LogoMark';
import './NotFound.css';

// Alamat yang tidak cocok dengan rute mana pun. Sebelumnya langsung dilempar ke "/" tanpa penjelasan.
const NotFound = () => {
  const { user } = useAuth();
  const home = !user ? '/login' : user.role === 'admin' ? '/admin/dashboard' : '/user/home';

  return (
    <div className="notfound-page">
      <header className="notfound-topbar">
        <LogoMark />
      </header>

      <main className="notfound-main">
        <div className="notfound-face">
          <FaceDots mood="sad" />
        </div>
        <p className="notfound-code">404</p>
        <h1>Halaman ini tidak ada.</h1>
        <p className="notfound-text">
          Alamatnya mungkin salah ketik, atau halamannya sudah dipindah.
        </p>
        <Link to={home} className="btn-primary notfound-button">
          {user ? 'Kembali ke beranda' : 'Ke halaman masuk'}
        </Link>
      </main>
    </div>
  );
};

export default NotFound;
