import { useEffect, useState } from 'react';
import { Link, useOutletContext } from 'react-router-dom';
import api from '../../services/api';
import FaceDots from '../../components/common/FaceDots';
import { SKIN_ISSUES, SKIN_TYPES, formatRelative, parseScanDate } from '../../constants/skin';
import './UserHome.css';

// Backend membatasi riwayat ke 50 scan terbaru (LIMIT 50 di routes/scan.py)
const HISTORY_LIMIT = 50;

const summarize = (scan) => {
  const keys = scan.conditions_detected;
  const scores = scan.confidence_scores;
  const typeKey = keys.find((key) => key in SKIN_TYPES);
  const issues = keys
    .filter((key) => key in SKIN_ISSUES)
    .sort((a, b) => (scores[b] ?? 0) - (scores[a] ?? 0))
    .slice(0, 3)
    .map((key) => SKIN_ISSUES[key]);
  return { skinType: typeKey ? SKIN_TYPES[typeKey] : null, issues };
};

const formatTotal = (total) => (total >= HISTORY_LIMIT ? `${HISTORY_LIMIT}+` : String(total));

const LatestScan = ({ scan }) => {
  const date = parseScanDate(scan.scan_date);
  const { skinType, issues } = summarize(scan);

  return (
    <article className="data-card latest-card data-enter">
      <time
        className="latest-date"
        dateTime={date.toISOString()}
        title={date.toLocaleString('id-ID', { dateStyle: 'long', timeStyle: 'short' })}
      >
        {formatRelative(date)}
      </time>

      <dl className="latest-facts">
        <div>
          <dt>Jenis kulit</dt>
          <dd>{skinType ?? 'Tidak tercatat'}</dd>
        </div>
        <div>
          <dt>Masalah kulit</dt>
          <dd>
            {issues.length ? (
              <ul className="latest-issues">
                {issues.map((issue) => (
                  <li key={issue}>{issue}</li>
                ))}
              </ul>
            ) : (
              'Tidak ada yang terdeteksi'
            )}
          </dd>
        </div>
      </dl>

      <Link to={`/user/results/${scan.id}`} className="latest-open">
        Lihat hasil <span className="latest-arrow" aria-hidden="true">→</span>
      </Link>
    </article>
  );
};

// Ringkasan dari data riwayat yang sama. Riwayat dibatasi 50 scan, jadi tanggal
// scan pertama hanya pasti kalau total di bawah batas itu.
const ScanSummary = ({ scans }) => {
  const total = scans.length;
  const first = total ? parseScanDate(scans[total - 1].scan_date) : null;

  // Kalau riwayat terpotong, scan tertua yang dimuat hanya batas atas tanggal scan pertama
  const firstScan = first ? (
    <>
      {total >= HISTORY_LIMIT && 'Paling lambat '}
      <time dateTime={first.toISOString()}>
        {first.toLocaleDateString('id-ID', { dateStyle: 'long' })}
      </time>
    </>
  ) : (
    'Belum ada'
  );

  return (
    <div className="data-card summary-card data-enter">
      <dl className="summary-facts">
        <div>
          <dt>Total scan</dt>
          <dd>{formatTotal(total)}</dd>
        </div>
        <div>
          <dt>Scan pertama</dt>
          <dd>{firstScan}</dd>
        </div>
      </dl>
      {total > 0 && (
        <Link to="/user/history" className="summary-link">
          Buka riwayat
        </Link>
      )}
    </div>
  );
};

// Blok datar selama memuat. Tetap di tempat lalu memudar saat data datang,
// sementara kartu data muncul di sel grid yang sama (crossfade tanpa layout shift).
const Placeholder = ({ loading, label }) => (
  <div
    className={`data-placeholder${loading ? '' : ' is-done'}`}
    role={loading ? 'status' : undefined}
    aria-hidden={loading ? undefined : true}
  >
    {loading && <span className="home-sr-only">{label}</span>}
  </div>
);

const UserHome = () => {
  const { user } = useOutletContext() ?? {};
  // Saat tombol scan disorot, wajah ikut melirik ke tombol itu
  const [ctaActive, setCtaActive] = useState(false);
  const [scans, setScans] = useState([]);
  const [status, setStatus] = useState('loading');
  const [reloadKey, setReloadKey] = useState(0);

  // 401 sudah ditangani interceptor di api.js
  useEffect(() => {
    let active = true;
    api
      .get('/history')
      .then(({ data }) => {
        if (!active) return;
        setScans(data);
        setStatus('ready');
      })
      .catch(() => {
        if (active) setStatus('error');
      });
    return () => {
      active = false;
    };
  }, [reloadKey]);

  const retry = () => {
    setStatus('loading');
    setReloadKey((key) => key + 1);
  };

  const ctaProps = {
    onMouseEnter: () => setCtaActive(true),
    onMouseLeave: () => setCtaActive(false),
    onFocus: () => setCtaActive(true),
    onBlur: () => setCtaActive(false),
  };

  // Maskot ikut keadaan data riwayat
  let mood = 'idle';
  if (ctaActive) mood = 'watching';
  else if (status === 'loading') mood = 'busy';
  else if (status === 'error') mood = 'sad';

  const loading = status === 'loading';

  return (
    <div className="user-home">
      <section className="home-stage">
        <div className="home-stage-copy">
          {user?.username && (
            <p className="home-greeting home-rise" style={{ '--rise-order': 0 }}>
              Halo, {user.username}.
            </p>
          )}
          <h1 className="home-rise" style={{ '--rise-order': 1 }}>
            Siap cek kulitmu hari ini?
          </h1>
          <p className="home-lead home-rise" style={{ '--rise-order': 2 }}>
            Jawab empat pertanyaan singkat dan kirim satu foto wajah. WajahKu menentukan jenis
            kulitmu dari jawabanmu, memeriksa dahi, bawah mata, hidung, pipi, dan dagu, lalu
            menyusun rutinitas perawatan.
          </p>
          <div className="home-actions home-rise" style={{ '--rise-order': 3 }}>
            <Link to="/user/camera" className="btn-primary home-cta" {...ctaProps}>
              Mulai scan wajah
            </Link>
          </div>
        </div>

        <div className="home-face">
          <FaceDots mood={mood} lookDirection={{ x: -1, y: 0.6 }} />
        </div>
      </section>

      <div className="home-data">
        <section className="home-data-main" aria-labelledby="home-latest-title">
          <h2 id="home-latest-title">Scan terakhir</h2>
          <div className="data-slot" aria-live="polite">
            <Placeholder loading={loading} label="Memuat scan terakhir…" />

            {status === 'error' && (
              <div className="data-card data-empty data-enter">
                <p>Riwayat scan belum bisa dimuat.</p>
                <button type="button" className="home-retry" onClick={retry}>
                  Coba lagi
                </button>
              </div>
            )}

            {status === 'ready' && scans.length === 0 && (
              <div className="data-card data-empty data-enter">
                <p>Belum ada scan. Hasil pertamamu muncul di sini.</p>
              </div>
            )}

            {status === 'ready' && scans.length > 0 && <LatestScan scan={scans[0]} />}
          </div>
        </section>

        <section className="home-data-side" aria-labelledby="home-summary-title">
          <h2 id="home-summary-title">Ringkasan</h2>
          <div className="data-slot">
            <Placeholder loading={loading} label="Memuat ringkasan…" />

            {status === 'error' && (
              <div className="data-card data-empty data-enter">
                <p>Belum bisa dimuat.</p>
              </div>
            )}

            {status === 'ready' && <ScanSummary scans={scans} />}
          </div>
        </section>
      </div>

      <footer className="home-note">
        <p>
          Hasil WajahKu adalah perkiraan AI, bukan diagnosis dokter. Kalau ada keluhan kulit
          yang mengganggu, periksakan ke dokter kulit.
        </p>
      </footer>
    </div>
  );
};

export default UserHome;
