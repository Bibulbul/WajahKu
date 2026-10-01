import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../../services/api';
import './Results.css';

const Results = () => {
  const { scanId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchResults();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [scanId]);

  const fetchResults = async () => {
    try {
      const { data: result } = await api.get(`/scans/${scanId}`);
      setData(result);
    } catch {
      setError('Gagal memuat hasil scan');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Memuat hasil...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="error-container">
        <p>{error || 'Data tidak ditemukan'}</p>
        <Link to="/user/home" className="btn-primary">Kembali ke Beranda</Link>
      </div>
    );
  }

  return (
    <div className="results-page">
      <div className="container">
        <div className="results-header">
          <h1>Hasil Analisis Kulit</h1>
          <p>Berikut adalah hasil analisis kondisi kulit wajah Anda</p>
        </div>

        <div className="results-grid">
          <div className="photo-section">
            <img src={`/${data.scan.photo_path}`} alt="Scan" />
            <small>Scan pada: {new Date(data.scan.scan_date).toLocaleString('id-ID')}</small>
          </div>

          <div className="conditions-section">
            <h2>Kondisi Terdeteksi</h2>
            {Object.entries(data.conditions).map(([key, condition]) => (
              <div key={key} className="condition-card">
                <div className="condition-header">
                  <h3>{condition.name}</h3>
                  <span className="confidence">{condition.confidence}%</span>
                </div>
                <p>{condition.description}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="recommendations-section">
          <h2>Rekomendasi Perawatan</h2>
          {Object.entries(data.recommendations).map(([condition, steps]) => (
            <div key={condition} className="recommendation-group">
              <h3>{data.conditions[condition].name}</h3>
              <div className="steps-list">
                {steps.map((step) => (
                  <div key={step.step_number} className="step-card">
                    <div className="step-num">{step.step_number}</div>
                    <div className="step-content">
                      <h4>{step.step_title}</h4>
                      <p>{step.step_description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {data.products && data.products.length > 0 && (
          <div className="products-section">
            <h2>Produk Rekomendasi</h2>
            <div className="products-grid">
              {data.products.map((product) => (
                <div key={product.id} className="product-card">
                  <h3>{product.name}</h3>
                  <p className="brand">{product.brand}</p>
                  <p className="price">Rp {product.price.toLocaleString('id-ID')}</p>
                  <div className="product-meta">
                    <span className="bpom">BPOM {product.bpom_number}</span>
                    {product.avg_rating > 0 && (
                      <span className="rating">★ {product.avg_rating.toFixed(1)}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="actions">
          <Link to="/user/camera" className="btn-secondary">Scan Lagi</Link>
          <Link to="/user/history" className="btn-primary">Lihat Riwayat</Link>
        </div>
      </div>
    </div>
  );
};

export default Results;
