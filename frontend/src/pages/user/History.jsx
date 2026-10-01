import { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import api from '../../services/api';
import './History.css';

const History = () => {
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchHistory = useCallback(async () => {
    try {
      const { data } = await api.get('/history');
      setScans(data);
    } catch (err) {
      console.error('Error fetching history:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Memuat riwayat...</p>
      </div>
    );
  }

  return (
    <div className="history-page">
      <div className="container">
        <div className="history-header">
          <h1>Riwayat Scan</h1>
          <p>Lihat kembali hasil analisis kulit sebelumnya</p>
        </div>

        {scans.length === 0 ? (
          <div className="empty-state">
            <p>Belum ada riwayat scan</p>
            <Link to="/user/camera" className="btn-primary">Mulai Scan Sekarang</Link>
          </div>
        ) : (
          <div className="history-grid">
            {scans.map((scan) => (
              <Link key={scan.id} to={`/user/results/${scan.id}`} className="history-card">
                <div className="scan-photo">
                  <img src={`/${scan.photo_path}`} alt="Scan" />
                </div>
                <div className="scan-info">
                  <p className="scan-date">
                    {new Date(scan.scan_date).toLocaleDateString('id-ID', {
                      day: 'numeric',
                      month: 'long',
                      year: 'numeric',
                    })}
                  </p>
                  <div className="conditions-tags">
                    {scan.conditions_detected.map((cond, idx) => (
                      <span key={idx} className="condition-tag">
                        {cond}
                      </span>
                    ))}
                  </div>
                  <div className="scan-confidence">
                    {Object.values(scan.confidence_scores).map((score, idx) => (
                      <span key={idx}>{score}%</span>
                    ))}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default History;
