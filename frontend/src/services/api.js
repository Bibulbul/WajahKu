import axios from 'axios';

// Alamat backend. Kosong = sama dengan alamat frontend: saat development lewat proxy di
// vite.config.js, saat production lewat server yang meneruskan /api dan /static ke Flask.
// Isi VITE_API_URL (lihat .env.example) kalau backend ada di domain lain.
const API_URL = (import.meta.env.VITE_API_URL ?? '').replace(/\/$/, '');

// Backend menyimpan foto scan sebagai path relatif, mis. static/uploads/abc.jpg
export const fileUrl = (path) => `${API_URL}/${path}`;

const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - attach JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && !error.config.url.includes('/auth/')) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
