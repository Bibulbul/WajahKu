import { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import api from '../../services/api';
import FaceDots from '../../components/common/FaceDots';
import { SKIN_ISSUES, SKIN_TYPES, formatRelative, parseScanDate } from '../../constants/skin';
import './History.css';

// Backend membatasi riwayat ke 50 scan terbaru (LIMIT 50 di routes/scan.py)
const HISTORY_LIMIT = 50;
const MAX_ISSUES = 3;

const summarize = (scan) => {
  const keys = scan.conditions_detected;
  const scores = scan.confidence_scores;
  const typeKey = keys.find((key) => key in SKIN_TYPES);
  const issues = keys
    .filter((key) => key in SKIN_ISSUES)
    .sort((a, b) => (scores[b] ?? 0) - (scores[a] ?? 0))
    .map((key) => SKIN_ISSUES[key]);
  let skinType = 'Jenis kulit tidak tercatat';
  if (typeKey === 'jenis_belum_pasti') skinType = 'Jenis kulit belum pasti';
  else if (typeKey) skinType = `Kulit ${SKIN_TYPES[typeKey].toLowerCase()}`;
  return { skinType, issues };
};

// Riwayat sudah urut terbaru dulu dari backend; dikelompokkan per bulan
const groupByMonth = (scans) => {
  const groups = [];
  for (const scan of scans) {
    const date = parseScanDate(scan.scan_date);
    const label = date.toLocaleDateString('id-ID', { month: 'long', year: 'numeric' });
    const last = groups[groups.length - 1];
    if (last?.label === label) last.items.push({ scan, date });
    else groups.push({ label, items: [{ scan, date }] });
  }
  return groups;
};

const ScanRow = ({ scan, date }) => {
  const { skinType, issues } = summarize(scan);
  const fullDate = date.toLocaleDateString('id-ID', { dateStyle: 'long' });
  const extra = issues.length - MAX_ISSUES;

  return (
    <li>
      <Link to={`/user/results/${scan.id}`} className="history-row">
        <img
          className="history-thumb"
          src={`/${scan.photo_path}`}
          alt={`Foto scan ${fullDate}`}
          loading="lazy"
        />
        <div className="history-row-text">
          <time dateTime={date.toISOString()} title={fullDate} className="history-date">
            {formatRelative(date)}
          </time>
          <p className="history-type">{skinType}</p>
          {issues.length ? (
            <ul className="history-issues">
              {issues.slice(0, MAX_ISSUES).map((issue) => (
                <li key={issue}>{issue}</li>
              ))}
              {extra > 0 && <li className="history-more">+{extra} lainnya</li>}
            </ul>
          ) : (
            <p className="history-none">Tidak ada masalah kulit terdeteksi</p>
          )}
        </div>
        <span className="history-open" aria-hidden="true">Lihat hasil</span>
      </Link>
    </li>
  );
};

const History = () => {
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const fetchHistory = useCallback(async () => {
    try {
      const { data } = await api.get('/history');
      setScans(data);
    } catch (err) {
      console.error('Error fetching history:', err);
      setError(true);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const retry = () => {
    setLoading(true);
    setError(false);
    fetchHistory();
  };

  const total = scans.length;
  const countText = total >= HISTORY_LIMIT ? `${HISTORY_LIMIT} scan terbaru` : `${total} scan`;

  return (
    <div className="history-page">
      <header className="history-header">
        <div>
          <h1>Riwayat scan</h1>
          {!loading && !error && total > 0 && <p className="history-count">{countText}</p>}
        </div>
        <Link to="/user/camera" className="btn-primary history-button">Scan baru</Link>
      </header>

      <div aria-live="polite">
        {loading && (
          <div className="history-loading" role="status">
            <span className="history-sr-only">Memuat riwayat scan…</span>
            {[0, 1, 2].map((i) => (
              <div key={i} className="history-placeholder" />
            ))}
          </div>
        )}

        {!loading && error && (
          <div className="history-message">
            <div className="history-face">
              <FaceDots mood="sad" />
            </div>
            <p>Riwayat scan belum bisa dimuat. Periksa koneksi lalu coba lagi.</p>
            <button type="button" className="btn-secondary history-button" onClick={retry}>
              Coba lagi
            </button>
          </div>
        )}

        {!loading && !error && total === 0 && (
          <div className="history-message">
            <div className="history-face">
              <FaceDots mood="idle" />
            </div>
            <p>Belum ada scan. Hasil pertamamu muncul di sini.</p>
          </div>
        )}

        {!loading && !error && total > 0 && (
          <div className="history-groups">
            {groupByMonth(scans).map((group, index) => (
              <section key={group.label} aria-labelledby={`history-month-${index}`}>
                <h2 id={`history-month-${index}`} className="history-month">{group.label}</h2>
                <ul className="history-list">
                  {group.items.map(({ scan, date }) => (
                    <ScanRow key={scan.id} scan={scan} date={date} />
                  ))}
                </ul>
              </section>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default History;
