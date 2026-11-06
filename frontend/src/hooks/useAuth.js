import { createContext, useContext } from 'react';

// Diisi AuthProvider, supaya semua komponen membaca user yang sama
export const AuthContext = createContext(null);

export const useAuth = () => {
  const auth = useContext(AuthContext);
  if (!auth) throw new Error('useAuth harus dipakai di dalam AuthProvider');
  return auth;
};
