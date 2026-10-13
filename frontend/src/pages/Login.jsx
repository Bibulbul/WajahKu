import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import FaceDots from '../components/common/FaceDots';
import PoreField from '../components/common/PoreField';
import LogoMark from '../components/common/LogoMark';
import './Login.css';

// Urutan kerja analisis WajahKu, ditampilkan bergantian di panel kanan
const ANALYSIS_STEPS = [
  'Mendeteksi wajah di foto',
  'Membaca jenis kulit',
  'Memeriksa area dahi',
  'Memeriksa area pipi',
  'Memeriksa area dagu',
  'Menyusun rutinitas perawatan',
];

const AnalysisFeed = () => {
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrent((i) => (i + 1) % ANALYSIS_STEPS.length);
    }, 2400);
    return () => clearInterval(timer);
  }, []);

  // Langkah yang sedang berjalan di atas, dua langkah sebelumnya di bawahnya.
  // Di awal putaran belum ada langkah sebelumnya, jadi barisnya kosong.
  const rows = [0, 1, 2].map((offset) => ({ index: current - offset, running: offset === 0 }));

  return (
    <ul className="analysis-feed" aria-hidden="true">
      {rows.map(({ index, running }, position) =>
        index < 0 ? (
          <li key={`empty-${position}`} className={`feed-row feed-row-${position}`}>
            <span className="feed-dot" />
            <span className="feed-skeleton" />
          </li>
        ) : (
          <li key={`${index}-${running}`} className={`feed-row feed-row-${position}`}>
            <span className="feed-dot" />
            <span className="feed-text">
              {ANALYSIS_STEPS[index]}
              {running && <span className="feed-caret" />}
            </span>
            <span className={`feed-status ${running ? 'is-running' : 'is-done'}`}>
              {running ? 'Berjalan' : 'Selesai'}
            </span>
          </li>
        )
      )}
    </ul>
  );
};

const Login = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeField, setActiveField] = useState(null);
  const [errorCount, setErrorCount] = useState(0);
  const [stacked, setStacked] = useState(false);

  const { login, register } = useAuth();
  const navigate = useNavigate();

  // Di layar kecil form ada di bawah wajah, di layar lebar form ada di kiri
  useEffect(() => {
    const query = window.matchMedia('(max-width: 900px)');
    const update = () => setStacked(query.matches);
    update();
    query.addEventListener('change', update);
    return () => query.removeEventListener('change', update);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      let user;
      if (isLogin) {
        user = await login(email, password);
      } else {
        user = await register(email, password, username);
      }

      // Route based on role
      if (user.role === 'admin') {
        navigate('/admin/dashboard');
      } else {
        navigate('/user/home');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Gagal terhubung ke server. Cek koneksi lalu coba lagi.');
      setErrorCount((n) => n + 1);
    } finally {
      setLoading(false);
    }
  };

  const switchMode = () => {
    setIsLogin((value) => !value);
    setError('');
  };

  let mood = 'idle';
  if (loading) mood = 'busy';
  else if (activeField === 'password') mood = 'shy';
  else if (error) mood = 'sad';
  else if (activeField) mood = 'watching';

  const fieldProps = (name) => ({
    onFocus: () => setActiveField(name),
    onBlur: () => setActiveField(null),
  });

  return (
    <div className="login-page">
      <div className="login-frame">
        <section className="login-main">
          <PoreField quietSelector=".login-form" />
          <header className="login-topbar">
            <LogoMark className="login-brand" />
            <div className="login-switch">
              <span>{isLogin ? 'Belum punya akun?' : 'Sudah punya akun?'}</span>
              <button type="button" className="btn-secondary btn-small" onClick={switchMode}>
                {isLogin ? 'Daftar' : 'Masuk'}
              </button>
            </div>
          </header>

          <form className="login-form" onSubmit={handleSubmit}>
            <h2>{isLogin ? 'Selamat datang lagi' : 'Buat akunmu'}</h2>
            <p className="login-sub">
              {isLogin
                ? 'Masuk untuk melihat hasil scan dan rutinitas perawatanmu.'
                : 'Setelah daftar, kamu bisa langsung scan wajah pertamamu.'}
            </p>

            {error && <div className="error-message" role="alert">{error}</div>}

            {!isLogin && (
              <div className="form-group">
                <label htmlFor="username">Username</label>
                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required={!isLogin}
                  autoComplete="username"
                  {...fieldProps('username')}
                />
              </div>
            )}

            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
                {...fieldProps('email')}
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete={isLogin ? 'current-password' : 'new-password'}
                {...fieldProps('password')}
              />
              <p className="field-hint">Tenang, dia menutup mata.</p>
            </div>

            <button type="submit" className="btn-primary login-submit" disabled={loading}>
              {loading ? 'Memproses…' : isLogin ? 'Masuk' : 'Buat akun'}
            </button>

            <p className="login-switch-inline">
              {isLogin ? 'Belum punya akun?' : 'Sudah punya akun?'}{' '}
              <button type="button" className="link-button" onClick={switchMode}>
                {isLogin ? 'Daftar' : 'Masuk'}
              </button>
            </p>
          </form>


          <footer className="login-footer">
            <span>© 2026 WajahKu</span>
            <details className="test-accounts">
              <summary>Akun uji</summary>
              <p>user@test.com / user123</p>
              <p>admin@test.com / admin123</p>
            </details>
          </footer>
        </section>

        <section className="login-stage">
          <LogoMark className="login-brand stage-brand" />
          <div className="stage-copy">
            <h1>Kenali kulitmu dari satu foto.</h1>
            <p>
              WajahKu membaca jenis kulit dan masalah di dahi, pipi, dan dagu,
              lalu menyusun rutinitas perawatan untukmu.
            </p>
          </div>

          <div className="stage-face">
            <FaceDots
              mood={mood}
              shakeKey={errorCount}
              lookDirection={stacked ? { x: 0, y: 1 } : { x: -1, y: 0.3 }}
            />
          </div>

          <AnalysisFeed />
        </section>
      </div>
    </div>
  );
};

export default Login;
