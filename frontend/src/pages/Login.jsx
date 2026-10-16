import { useEffect, useRef, useState } from 'react';
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

const STACKED_QUERY = '(max-width: 900px)';

// Hanya tampil saat development, sesuai akun yang dibuat di database/db.py
const TEST_ACCOUNTS = [
  { label: 'User', email: 'user@test.com', password: 'user123' },
  { label: 'Admin', email: 'admin@test.com', password: 'admin123' },
];

const checkEmail = (value) => {
  if (!value.trim()) return 'Isi emailnya dulu ya.';
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim())) return 'Format emailnya belum pas.';
  return '';
};

const describeError = (err, isLogin) => {
  if (!err.response) return 'Server lagi tidak bisa dihubungi. Coba sebentar lagi.';
  // Jangan sebut mana yang salah, email atau password
  if (isLogin && err.response.status === 401) return 'Email atau password-nya belum cocok.';
  return err.response.data?.error || 'Server lagi tidak bisa dihubungi. Coba sebentar lagi.';
};

// Arah lirikan saat mengetik: makin panjang teks, pupil makin ikut ke ujung kolom
const lookAtText = (length, stacked) => {
  const progress = Math.min(length / 28, 1);
  return stacked
    ? { x: -0.8 + progress * 1.6, y: 1 }
    : { x: -1 + progress * 0.6, y: 0.2 + progress * 0.2 };
};

const Login = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [usernameError, setUsernameError] = useState('');
  const [formError, setFormError] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeField, setActiveField] = useState(null);
  const [errorCount, setErrorCount] = useState(0);
  const [stacked, setStacked] = useState(() => window.matchMedia(STACKED_QUERY).matches);

  const emailRef = useRef(null);
  const passwordRef = useRef(null);
  const usernameRef = useRef(null);

  const { login, register } = useAuth();
  const navigate = useNavigate();

  // Di layar kecil panggung disembunyikan, wajah kecil pindah ke atas form
  useEffect(() => {
    const query = window.matchMedia(STACKED_QUERY);
    const update = () => setStacked(query.matches);
    query.addEventListener('change', update);
    return () => query.removeEventListener('change', update);
  }, []);

  const clearErrors = () => {
    setEmailError('');
    setPasswordError('');
    setUsernameError('');
    setFormError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (loading) return;

    const emailProblem = checkEmail(email);
    const passwordProblem = password ? '' : 'Isi password-nya dulu ya.';
    const usernameProblem = !isLogin && !username.trim() ? 'Isi username-nya dulu ya.' : '';
    setEmailError(emailProblem);
    setPasswordError(passwordProblem);
    setUsernameError(usernameProblem);
    setFormError('');

    if (usernameProblem || emailProblem || passwordProblem) {
      const firstInvalid = usernameProblem ? usernameRef : emailProblem ? emailRef : passwordRef;
      firstInvalid.current?.focus();
      return;
    }

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
      setFormError(describeError(err, isLogin));
      setErrorCount((n) => n + 1);
    } finally {
      setLoading(false);
    }
  };

  const switchMode = () => {
    setIsLogin((value) => !value);
    clearErrors();
  };

  const fillTestAccount = (account) => {
    setIsLogin(true);
    setEmail(account.email);
    setPassword(account.password);
    clearErrors();
  };

  let mood = 'idle';
  if (loading) mood = 'busy';
  else if (activeField === 'password') mood = 'shy';
  else if (formError) mood = 'sad';
  else if (activeField) mood = 'watching';

  let lookDirection = stacked ? { x: 0, y: 1 } : { x: -1, y: 0.3 };
  if (activeField === 'email') lookDirection = lookAtText(email.length, stacked);
  else if (activeField === 'username') lookDirection = lookAtText(username.length, stacked);

  const faceProps = { mood, shakeKey: errorCount, lookDirection };

  const fieldProps = (name, onBlur) => ({
    onFocus: () => setActiveField(name),
    onBlur: () => {
      setActiveField(null);
      onBlur?.();
    },
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

          <form className="login-form" onSubmit={handleSubmit} noValidate>
            {stacked && (
              <div className="login-face-mini">
                <FaceDots {...faceProps} />
              </div>
            )}

            <h2>{isLogin ? 'Selamat datang lagi' : 'Buat akunmu'}</h2>
            <p className="login-sub">
              {isLogin
                ? 'Masuk untuk melihat hasil scan dan rutinitas perawatanmu.'
                : 'Setelah daftar, kamu bisa langsung scan wajah pertamamu.'}
            </p>

            {!isLogin && (
              <div className="form-group">
                <label htmlFor="username">Username</label>
                <input
                  ref={usernameRef}
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => {
                    setUsername(e.target.value);
                    setUsernameError('');
                  }}
                  autoComplete="username"
                  aria-invalid={Boolean(usernameError)}
                  aria-describedby="username-error"
                  {...fieldProps('username')}
                />
                <p id="username-error" className="field-error" aria-live="polite">{usernameError}</p>
              </div>
            )}

            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                ref={emailRef}
                id="email"
                type="email"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  setEmailError('');
                }}
                placeholder="adira@email.com"
                autoComplete="email"
                aria-invalid={Boolean(emailError)}
                aria-describedby="email-error"
                {...fieldProps('email', () => setEmailError(checkEmail(email)))}
              />
              <p id="email-error" className="field-error" aria-live="polite">{emailError}</p>
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <div className="password-field">
                <input
                  ref={passwordRef}
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    setPasswordError('');
                  }}
                  autoComplete={isLogin ? 'current-password' : 'new-password'}
                  aria-invalid={Boolean(passwordError)}
                  aria-describedby="password-error"
                  {...fieldProps('password')}
                />
                <button
                  type="button"
                  className="password-toggle"
                  aria-controls="password"
                  aria-label={showPassword ? 'Sembunyikan password' : 'Lihat password'}
                  // Klik dengan mouse tidak memindahkan fokus dari kolom password
                  onMouseDown={(e) => e.preventDefault()}
                  onClick={() => setShowPassword((value) => !value)}
                >
                  {showPassword ? 'Sembunyikan' : 'Lihat'}
                </button>
              </div>
              <p className={`field-hint${activeField === 'password' ? ' is-visible' : ''}`}>
                Tenang, dia menutup mata.
              </p>
              <p id="password-error" className="field-error" aria-live="polite">{passwordError}</p>
            </div>

            <p className="field-error form-error" aria-live="polite">{formError}</p>

            <button type="submit" className="btn-primary login-submit" disabled={loading}>
              {loading ? (isLogin ? 'Memeriksa…' : 'Membuat akun…') : isLogin ? 'Masuk' : 'Buat akun'}
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
            {import.meta.env.DEV && (
              <div className="test-accounts">
                <span>Akun uji:</span>
                {TEST_ACCOUNTS.map((account) => (
                  <button
                    key={account.email}
                    type="button"
                    className="link-button"
                    onClick={() => fillTestAccount(account)}
                  >
                    {account.label}
                  </button>
                ))}
              </div>
            )}
          </footer>
        </section>

        {!stacked && (
          <section className="login-stage">
            <div className="stage-copy">
              <h1>Kenali kulitmu dari satu foto.</h1>
              <p>
                WajahKu membaca jenis kulit dan masalah di dahi, pipi, dan dagu,
                lalu menyusun rutinitas perawatan untukmu.
              </p>
            </div>

            <div className="stage-face">
              <FaceDots {...faceProps} />
            </div>

            <AnalysisFeed />
          </section>
        )}
      </div>
    </div>
  );
};

export default Login;
