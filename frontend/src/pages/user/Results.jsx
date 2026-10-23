import { useEffect, useRef, useState } from 'react';
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

// Kategori produk di database masih bahasa Inggris
const CATEGORIES = {
  cleanser: 'Pembersih',
  exfoliant: 'Eksfoliator',
  mask: 'Masker',
  moisturizer: 'Pelembap',
  serum: 'Serum',
  sunscreen: 'Tabir surya',
  toner: 'Toner',
};

const formatPrice = new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 });

const ProductCard = ({ product }) => (
  <li className="product-card">
    <span className="product-category">{CATEGORIES[product.category] ?? product.category}</span>
    <h3>{product.name}</h3>
    <p className="product-brand">{product.brand}</p>
    <p className="product-price">{formatPrice.format(product.price)}</p>
    <div className="product-meta">
      <span className="product-bpom">BPOM {product.bpom_number}</span>
      {product.review_count > 0 ? (
        <span className="product-rating">
          <span aria-hidden="true">★ </span>
          {product.avg_rating.toLocaleString('id-ID', { maximumFractionDigits: 1 })} dari 5
          <span className="product-reviews"> ({product.review_count} ulasan)</span>
        </span>
      ) : (
        <span className="product-rating product-reviews">Belum ada ulasan</span>
      )}
    </div>
  </li>
);

const shortLabel = (key, condition) => SKIN_TYPES[key] ?? SKIN_ISSUES[key] ?? condition.name;

// Langkah perawatan per kondisi. Lebih dari satu kondisi dipisah per tab
// (pola tablist WAI-ARIA: panah kiri/kanan, Home, End).
const Routines = ({ groups }) => {
  const [active, setActive] = useState(0);
  const tabRefs = useRef([]);

  const select = (index) => {
    const next = (index + groups.length) % groups.length;
    setActive(next);
    tabRefs.current[next]?.focus();
  };

  const onKeyDown = (e) => {
    const keys = { ArrowRight: active + 1, ArrowLeft: active - 1, Home: 0, End: groups.length - 1 };
    if (e.key in keys) {
      e.preventDefault();
      select(keys[e.key]);
    }
  };

  const steps = (group) => (
    <ol className="routine-steps">
      {group.steps.map((step) => (
        <li key={step.step_number}>
          <span className="routine-number" aria-hidden="true">{step.step_number}</span>
          <div>
            <h3>{step.step_title}</h3>
            <p>{step.step_description}</p>
          </div>
        </li>
      ))}
    </ol>
  );

  if (groups.length === 1) return steps(groups[0]);

  return (
    <>
      <div className="routine-tabs" role="tablist" aria-label="Kondisi kulit">
        {groups.map((group, index) => (
          <button
            key={group.key}
            ref={(el) => (tabRefs.current[index] = el)}
            type="button"
            role="tab"
            id={`routine-tab-${group.key}`}
            aria-selected={index === active}
            aria-controls={`routine-panel-${group.key}`}
            tabIndex={index === active ? 0 : -1}
            className="routine-tab"
            onClick={() => setActive(index)}
            onKeyDown={onKeyDown}
          >
            {group.label}
          </button>
        ))}
      </div>
      {groups.map((group, index) => (
        <div
          key={group.key}
          role="tabpanel"
          id={`routine-panel-${group.key}`}
          aria-labelledby={`routine-tab-${group.key}`}
          hidden={index !== active}
          className="routine-panel"
        >
          {steps(group)}
        </div>
      ))}
    </>
  );
};

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

  const { scan, conditions, recommendations, products } = data;
  const date = parseScanDate(scan.scan_date);
  const { type, issues, all } = orderConditions(conditions);
  const routineGroups = all
    .filter(([key]) => recommendations?.[key]?.length)
    .map(([key, condition]) => ({ key, label: shortLabel(key, condition), steps: recommendations[key] }));
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

      {routineGroups.length > 0 && (
        <section className="results-section" aria-labelledby="results-routine-title">
          <h2 id="results-routine-title">Yang harus kamu lakukan</h2>
          <p className="results-section-lead">
            Langkah perawatan untuk tiap kondisi, berurutan dari yang dipakai lebih dulu.
          </p>
          <Routines groups={routineGroups} />
        </section>
      )}

      {products?.length > 0 && (
        <section className="results-section results-products" aria-labelledby="results-products-title">
          <h2 id="results-products-title">Produk terdaftar BPOM</h2>
          {/* Backend memilih produk secara acak, belum berdasarkan hasil scan */}
          <p className="results-section-lead products-note">
            Contoh produk dari katalog WajahKu. Produk ini belum dipilih berdasarkan hasil scanmu,
            jadi cek kandungannya dulu sebelum membeli.
          </p>
          <ul className="product-list" tabIndex={0} aria-label="Daftar produk, bisa digeser">
            {products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </ul>
        </section>
      )}

      <div className="results-actions results-footer-actions">
        <Link to="/user/camera" className="btn-primary results-button">Scan lagi</Link>
        <Link to="/user/history" className="btn-secondary results-button">Lihat riwayat</Link>
      </div>
    </div>
  );
};

export default Results;
