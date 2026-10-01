import { Link } from 'react-router-dom';
import './UserHome.css';

const UserHome = () => {
  return (
    <div className="user-home">
      <section className="hero">
        <div className="container">
          <h1>Kenali Kondisi Kulit Wajahmu</h1>
          <p>Dapatkan analisis kondisi kulit wajah serta rekomendasi produk perawatan yang tepat</p>
          <Link to="/user/camera" className="btn-hero">
            Mulai Scan Sekarang
          </Link>
        </div>
      </section>

      <section className="how-it-works">
        <div className="container">
          <h2>Cara Kerja</h2>
          <div className="steps">
            <div className="step">
              <div className="step-number">1</div>
              <h3>Upload Foto</h3>
              <p>Ambil atau upload foto wajah dengan pencahayaan yang baik</p>
            </div>
            <div className="step">
              <div className="step-number">2</div>
              <h3>Analisis Kulit</h3>
              <p>Sistem kami menganalisis kondisi kulit wajahmu secara menyeluruh</p>
            </div>
            <div className="step">
              <div className="step-number">3</div>
              <h3>Dapatkan Hasil</h3>
              <p>Terima hasil analisis dan rekomendasi produk yang sesuai</p>
            </div>
          </div>
        </div>
      </section>

      <section className="features">
        <div className="container">
          <div className="feature-grid">
            <div className="feature-card">
              <h3>Analisis Akurat</h3>
              <p>Deteksi berbagai kondisi kulit dengan tingkat akurasi tinggi</p>
            </div>
            <div className="feature-card">
              <h3>Produk Terverifikasi</h3>
              <p>Rekomendasi produk dengan nomor BPOM resmi</p>
            </div>
            <div className="feature-card">
              <h3>Riwayat Scan</h3>
              <p>Pantau perkembangan kondisi kulitmu dari waktu ke waktu</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default UserHome;
