import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../../services/api';
import FaceDots from '../../components/common/FaceDots';
import { SKIN_ISSUES, SKIN_TYPES, formatRelative, parseScanDate } from '../../constants/skin';
import './Results.css';

// Jenis kulit dulu, lalu masalah kulit dari keyakinan AI tertinggi. Angkanya tidak
// ditampilkan supaya tidak terbaca sebagai tingkat kebenaran.
const orderConditions = (conditions) => {
  const entries = Object.entries(conditions);
  const types = entries.filter(([key]) => key in SKIN_TYPES);
  const issues = entries
    .filter(([key]) => !(key in SKIN_TYPES))
    .sort((a, b) => b[1].confidence - a[1].confidence);
  return { type: types[0] ?? null, issues, all: [...types, ...issues] };
};

const STACKED_QUERY = '(max-width: 640px)';

const Results = () => {
  const { scanId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [stacked, setStacked] = useState(() => window.matchMedia(STACKED_QUERY).matches);

  // Maskot melirik ke foto: di kiri saat desktop, di atas saat HP
  useEffect(() => {
    const query = window.matchMedia(STACKED_QUERY);
    const update = () => setStacked(query.matches);
    query.addEventListener('change', update);
    return () => query.removeEventListener('change', update);
  }, []);

  useEffect(() => {
    fetchResults();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [scanId]);

  const fetchResults = async () => {
    try {
      const { data: result } = await api.get(`/scans/${scanId}`);
      setData(result);
    } catch (err) {
      setError(err.response?.status === 404 ? 'not-found' : 'failed');
    } finally {
      setLoading(false);
    }
  };

  const retry = () => {
    setLoading(true);
    setError('');
    fetchResults();
  };

  if (loading) {
    return (
      <div className="results-page">
        <div className="results-loading" role="status">
          <div className="results-loading-photo" />
          <div className="results-loading-text">
            <div className="results-face">
              <FaceDots mood="busy" />
            </div>
            <p>Memuat hasil scan…</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !data) {
    const notFound = error === 'not-found';
    return (
      <div className="results-page">
        <div className="results-message">
          <div className="results-face">
            <FaceDots mood="sad" />
          </div>
          <h1>{notFound ? 'Scan ini tidak ditemukan.' : 'Hasil scan belum bisa dimuat.'}</h1>
          <p>
            {notFound
              ? 'Mungkin scan sudah tidak ada atau bukan milik akunmu.'
              : 'Periksa koneksi lalu coba lagi.'}
          </p>
          <div className="results-actions">
            {notFound ? (
              <Link to="/user/history" className="btn-primary results-button">Lihat riwayat</Link>
            ) : (
              <button type="button" className="btn-primary results-button" onClick={retry}>
                Coba lagi
              </button>
            )}
            <Link to="/user/home" className="btn-secondary results-button">Kembali ke beranda</Link>
          </div>
        </div>
      </div>
    );
  }

  const { scan, conditions } = data;
  const date = parseScanDate(scan.scan_date);
  const { type, issues, all } = orderConditions(conditions);
  const typeTitle = type
    ? type[0] === 'jenis_belum_pasti'
      ? 'Jenis kulit belum pasti'
      : `Kulit ${SKIN_TYPES[type[0]].toLowerCase()}`
    : 'Hasil scan';

  return (
    <div className="results-page">
      <section className="results-summary">
        <img className="results-photo" src={`/${scan.photo_path}`} alt="Foto wajah yang dianalisis" />

        <div className="results-summary-text">
          <div className="results-face">
            <FaceDots mood="watching" lookDirection={stacked ? { x: 0, y: -1 } : { x: -1, y: 0.2 }} />
          </div>
          <time
            className="results-date"
            dateTime={date.toISOString()}
            title={date.toLocaleString('id-ID', { dateStyle: 'long', timeStyle: 'short' })}
          >
            Scan {formatRelative(date)}
          </time>
          <h1>{typeTitle}</h1>
          {issues.length ? (
            <>
              <p className="results-lead">Yang perlu diperhatikan:</p>
              <ul className="results-issues">
                {issues.map(([key, condition]) => (
                  <li key={key}>{SKIN_ISSUES[key] ?? condition.name}</li>
                ))}
              </ul>
            </>
          ) : (
            <p className="results-lead">Tidak ada masalah kulit yang terdeteksi di foto ini.</p>
          )}
        </div>
      </section>

      <section className="results-section" aria-labelledby="results-conditions-title">
        <h2 id="results-conditions-title">Kondisi kulitmu</h2>
        <ul className="condition-list">
          {all.map(([key, condition]) => {
            const isType = key in SKIN_TYPES;
            return (
              <li key={key} className={`condition-card${isType ? '' : ' is-issue'}`}>
                <span className="condition-kind">{isType ? 'Jenis kulit' : 'Masalah kulit'}</span>
                <h3>{condition.name}</h3>
                <p>{condition.description}</p>
              </li>
            );
          })}
        </ul>
      </section>

      <div className="results-actions results-footer-actions">
        <Link to="/user/camera" className="btn-primary results-button">Scan lagi</Link>
        <Link to="/user/history" className="btn-secondary results-button">Lihat riwayat</Link>
      </div>
    </div>
  );
};

export default Results;
