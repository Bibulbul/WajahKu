import { useEffect, useState, useCallback } from 'react';
import api from '../../services/api';
import { SKIN_ISSUES, SKIN_TYPES, formatRelative, parseScanDate } from '../../constants/skin';
import './AdminDashboard.css';

const label = (key) => SKIN_TYPES[key] ?? SKIN_ISSUES[key] ?? key;

const STATS = [
  { key: 'total_scans', label: 'Scan' },
  { key: 'total_users', label: 'Pengguna' },
  { key: 'total_products', label: 'Produk' },
  { key: 'total_reviews', label: 'Ulasan produk' },
];

const formatCount = new Intl.NumberFormat('id-ID');

// Satu seri: jumlah scan per kondisi. Bar satu warna diurutkan dari terbanyak,
// angka di ujung bar, dan tetap berupa tabel supaya terbaca pembaca layar.
const ConditionChart = ({ distribution, totalScans }) => {
  const rows = Object.entries(distribution).sort((a, b) => b[1] - a[1]);
  if (!rows.length) return <p className="dash-empty">Belum ada scan.</p>;
  const max = rows[0][1];

  return (
    <table className="dash-chart">
      <caption className="dash-sr-only">Jumlah scan per kondisi kulit, dari yang terbanyak</caption>
      <thead className="dash-sr-only">
        <tr>
          <th scope="col">Kondisi</th>
          <th scope="col">Jumlah scan</th>
        </tr>
      </thead>
      <tbody>
        {rows.map(([key, count]) => {
          const share = totalScans ? Math.round((count / totalScans) * 100) : 0;
          return (
            <tr key={key}>
              <th scope="row" className="dash-chart-label">{label(key)}</th>
              <td>
                <div className="dash-chart-cell">
                  <span className="dash-bar" style={{ '--bar': `${(count / max) * 100}%` }} aria-hidden="true" />
                  <span className="dash-chart-value">{formatCount.format(count)}</span>
                  <span className="dash-tooltip" aria-hidden="true">
                    {formatCount.format(count)} dari {formatCount.format(totalScans)} scan ({share}%)
                  </span>
                </div>
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
};

const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const fetchStats = useCallback(async () => {
    try {
      const { data } = await api.get('/admin/stats');
      setStats(data);
    } catch (err) {
      console.error('Error fetching stats:', err);
      setError(true);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  const retry = () => {
    setLoading(true);
    setError(false);
    fetchStats();
  };

  return (
    <div className="admin-dashboard">
      <h1>Dashboard</h1>

      <div aria-live="polite">
        {loading && (
          <div className="dash-loading" role="status">
            <span className="dash-sr-only">Memuat statistik…</span>
            <div className="dash-placeholder dash-placeholder-row" />
            <div className="dash-placeholder dash-placeholder-block" />
          </div>
        )}

        {!loading && error && (
          <div className="dash-message">
            <p>Statistik belum bisa dimuat. Periksa koneksi lalu coba lagi.</p>
            <button type="button" className="dash-retry" onClick={retry}>Coba lagi</button>
          </div>
        )}

        {!loading && !error && stats && (
          <>
            <dl className="dash-stats">
              {STATS.map((item) => (
                <div key={item.key} className="dash-stat">
                  <dt>{item.label}</dt>
                  <dd>{formatCount.format(stats[item.key])}</dd>
                </div>
              ))}
            </dl>

            <div className="dash-panels">
              <section className="dash-panel" aria-labelledby="dash-conditions-title">
                <h2 id="dash-conditions-title">Kondisi yang paling sering terdeteksi</h2>
                <p className="dash-panel-lead">Satu scan bisa punya lebih dari satu kondisi.</p>
                <ConditionChart distribution={stats.condition_distribution} totalScans={stats.total_scans} />
              </section>

              <section className="dash-panel" aria-labelledby="dash-recent-title">
                <h2 id="dash-recent-title">Scan terbaru</h2>
                {stats.recent_scans.length ? (
                  <ul className="dash-recent">
                    {stats.recent_scans.map((scan) => {
                      const date = parseScanDate(scan.scan_date);
                      return (
                        <li key={scan.id}>
                          <div className="dash-recent-head">
                            <strong>{scan.username || scan.email || 'Pengguna terhapus'}</strong>
                            <time dateTime={date.toISOString()} title={date.toLocaleString('id-ID')}>
                              {formatRelative(date)}
                            </time>
                          </div>
                          <ul className="dash-tags">
                            {scan.conditions_detected.map((key) => (
                              <li key={key} className={key in SKIN_TYPES ? '' : 'is-issue'}>{label(key)}</li>
                            ))}
                          </ul>
                        </li>
                      );
                    })}
                  </ul>
                ) : (
                  <p className="dash-empty">Belum ada scan.</p>
                )}
              </section>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;
