import { useEffect, useState, useCallback } from 'react';
import api from '../../services/api';
import './AdminDashboard.css';

const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchStats = useCallback(async () => {
    try {
      const { data } = await api.get('/admin/stats');
      setStats(data);
    } catch (err) {
      console.error('Error fetching stats:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  if (loading) {
    return <div className="loading-container"><div className="spinner"></div></div>;
  }

  return (
    <div className="admin-dashboard">
      <h1>Dashboard Admin</h1>
      
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
            </svg>
          </div>
          <div className="stat-content">
            <h3>{stats.total_scans}</h3>
            <p>Total Scan</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
              <circle cx="9" cy="7" r="4"></circle>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
            </svg>
          </div>
          <div className="stat-content">
            <h3>{stats.total_users}</h3>
            <p>Total Pengguna</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
            </svg>
          </div>
          <div className="stat-content">
            <h3>{stats.total_products}</h3>
            <p>Total Produk</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
          </div>
          <div className="stat-content">
            <h3>{stats.total_reviews}</h3>
            <p>Total Ulasan</p>
          </div>
        </div>
      </div>

      <div className="dashboard-content">
        <div className="conditions-chart">
          <h2>Distribusi Kondisi Kulit</h2>
          <div className="chart-bars">
            {Object.entries(stats.condition_distribution).map(([condition, count]) => {
              const maxCount = Math.max(...Object.values(stats.condition_distribution));
              const percentage = (count / maxCount) * 100;
              
              return (
                <div key={condition} className="chart-bar">
                  <span className="bar-label">{condition}</span>
                  <div className="bar-track">
                    <div className="bar-fill" style={{ width: `${percentage}%` }}></div>
                  </div>
                  <span className="bar-value">{count}</span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="recent-scans">
          <h2>Scan Terbaru</h2>
          <div className="scans-table">
            {stats.recent_scans.map((scan) => (
              <div key={scan.id} className="scan-row">
                <div className="scan-user">
                  <strong>{scan.username || scan.email}</strong>
                  <small>{new Date(scan.scan_date).toLocaleString('id-ID')}</small>
                </div>
                <div className="scan-conditions">
                  {scan.conditions_detected.map((cond, idx) => (
                    <span key={idx} className="condition-badge">{cond}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
