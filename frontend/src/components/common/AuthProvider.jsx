import { useCallback, useEffect, useMemo, useState } from 'react';
import api from '../../services/api';
import { AuthContext } from '../../hooks/useAuth';

const saveSession = (data) => {
  localStorage.setItem('token', data.token);
  localStorage.setItem('user', JSON.stringify(data.user));
};

const clearSession = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
};

// Satu state login untuk seluruh aplikasi. Sebelumnya tiap komponen memanggil useAuth
// dengan state sendiri, jadi App masih menganggap user login setelah Keluar.
const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  // Tanpa token tidak ada yang perlu dicek ke server
  const [loading, setLoading] = useState(() => Boolean(localStorage.getItem('token')));

  useEffect(() => {
    if (!localStorage.getItem('token')) return;
    api
      .get('/auth/me')
      .then(({ data }) => setUser(data))
      .catch(() => {
        clearSession();
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (email, password) => {
    const { data } = await api.post('/auth/login', { email, password });
    saveSession(data);
    setUser(data.user);
    return data.user;
  }, []);

  const register = useCallback(async (email, password, username) => {
    const { data } = await api.post('/auth/register', { email, password, username });
    saveSession(data);
    setUser(data.user);
    return data.user;
  }, []);

  const logout = useCallback(() => {
    clearSession();
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ user, loading, login, register, logout }),
    [user, loading, login, register, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthProvider;
