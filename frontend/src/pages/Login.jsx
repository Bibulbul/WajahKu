import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import './Login.css';

const Login = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login, register } = useAuth();
  const navigate = useNavigate();

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
      setError(err.response?.data?.error || 'Terjadi kesalahan');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          <h1>WajahKu.id</h1>
          <p>Sistem Analisis Kulit Wajah</p>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          <h2>{isLogin ? 'Masuk' : 'Daftar'}</h2>

          {error && <div className="error-message">{error}</div>}

          {!isLogin && (
            <div className="form-group">
              <label>Username</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required={!isLogin}
                placeholder="Masukkan username"
              />
            </div>
          )}

          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="Masukkan email"
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="Masukkan password"
            />
          </div>

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Memproses...' : isLogin ? 'Masuk' : 'Daftar'}
          </button>

          <div className="form-footer">
            {isLogin ? (
              <p>
                Belum punya akun?{' '}
                <a onClick={() => setIsLogin(false)}>Daftar di sini</a>
              </p>
            ) : (
              <p>
                Sudah punya akun?{' '}
                <a onClick={() => setIsLogin(true)}>Masuk di sini</a>
              </p>
            )}
          </div>
        </form>

        <div className="test-accounts">
          <p>Test Accounts:</p>
          <small>User: user@test.com / user123</small>
          <small>Admin: admin@test.com / admin123</small>
        </div>
      </div>
    </div>
  );
};

export default Login;
