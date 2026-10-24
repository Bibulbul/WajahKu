import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import FaceDots from '../../components/common/FaceDots';
import './Camera.css';

const STACKED_QUERY = '(max-width: 640px)';

// Arah lirikan maskot ke tombol yang sedang disorot. Di HP maskot ada di atas tombol.
const LOOK = {
  camera: { wide: { x: -1, y: 0.1 }, stacked: { x: -0.3, y: 1 } },
  upload: { wide: { x: -1, y: 0.6 }, stacked: { x: -0.3, y: 1 } },
};

const Camera = () => {
  const [mode, setMode] = useState('choose'); // 'choose', 'webcam', 'preview'
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [errorCount, setErrorCount] = useState(0);
  const [facingMode, setFacingMode] = useState('user'); // 'user' (depan) atau 'environment' (belakang)
  const [hovered, setHovered] = useState(null);
  const [stacked, setStacked] = useState(() => window.matchMedia(STACKED_QUERY).matches);

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);
  const streamRef = useRef(null);
  const cameraRequest = useRef(0); // naik tiap kamera dimatikan; stream yang datang terlambat langsung dimatikan
  const navigate = useNavigate();

  useEffect(() => {
    const query = window.matchMedia(STACKED_QUERY);
    const update = () => setStacked(query.matches);
    query.addEventListener('change', update);
    return () => query.removeEventListener('change', update);
  }, []);

  const showError = (message) => {
    setError(message);
    setErrorCount((n) => n + 1);
  };

  // Matikan stream kamera ketika unmount atau ganti mode
  const stopCameraStream = () => {
    cameraRequest.current += 1;
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
  };

  useEffect(() => {
    return () => {
      stopCameraStream();
    };
  }, []);

  // Jalankan webcam
  const startCamera = async (facing = facingMode) => {
    stopCameraStream();
    const request = cameraRequest.current;
    setError('');
    setHovered(null);
    setMode('webcam');

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: facing,
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
        audio: false,
      });

      if (request !== cameraRequest.current) {
        // Sudah ada permintaan kamera yang lebih baru (tombol ditekan cepat) atau halaman ditinggal
        stream.getTracks().forEach((track) => track.stop());
        return;
      }
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play().catch(() => {});
      }
    } catch (err) {
      if (request !== cameraRequest.current) return;
      console.error('Kamera Error:', err);
      showError('Kamera tidak bisa dibuka. Izinkan akses kamera di browser, atau unggah foto saja.');
      setMode('choose');
    }
  };

  // Ganti kamera depan / belakang
  const toggleFacingMode = () => {
    const nextFacing = facingMode === 'user' ? 'environment' : 'user';
    setFacingMode(nextFacing);
    startCamera(nextFacing);
  };

  // Tangkap gambar dari video feed
  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');

    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;

    // Jika kamera depan, mirrorkan canvas agar sesuai preview
    if (facingMode === 'user') {
      context.translate(canvas.width, 0);
      context.scale(-1, 1);
    }

    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(
      (blob) => {
        if (!blob) {
          showError('Foto dari kamera gagal diambil. Coba sekali lagi.');
          return;
        }
        const file = new File([blob], `scan-${Date.now()}.jpg`, { type: 'image/jpeg' });
        setSelectedFile(file);

        const dataUrl = canvas.toDataURL('image/jpeg');
        setPreview(dataUrl);

        stopCameraStream();
        setMode('preview');
      },
      'image/jpeg',
      0.9
    );
  };

  // Handle upload dari file lokal
  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    // Kosongkan supaya memilih file yang sama lagi tetap memicu onChange
    e.target.value = '';
    if (!file) return;

    if (!['image/jpeg', 'image/jpg', 'image/png'].includes(file.type)) {
      showError('Formatnya belum didukung. Pakai foto JPG atau PNG.');
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      showError('Ukuran foto lebih dari 5MB. Pilih foto yang lebih kecil.');
      return;
    }

    setSelectedFile(file);
    setError('');
    setHovered(null);

    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result);
      setMode('preview');
    };
    reader.readAsDataURL(file);
  };

  // Kirim ke backend
  const handleUpload = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setError('');

    const formData = new FormData();
    formData.append('photo', selectedFile);

    try {
      const { data } = await api.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      navigate(`/user/results/${data.scan_id}`);
    } catch (err) {
      // Pesan dari backend sudah spesifik, misalnya "Wajah tidak terdeteksi..."
      showError(err.response?.data?.error || 'Server lagi tidak bisa dihubungi. Coba sebentar lagi.');
      setLoading(false);
    }
  };

  // Reset pilihan
  const resetAll = () => {
    stopCameraStream();
    setSelectedFile(null);
    setPreview(null);
    setError('');
    setMode('choose');
  };

  const hoverProps = (name) => ({
    onMouseEnter: () => setHovered(name),
    onMouseLeave: () => setHovered(null),
    onFocus: () => setHovered(name),
    onBlur: () => setHovered(null),
  });

  let mood = 'idle';
  if (loading) mood = 'busy';
  else if (error) mood = 'sad';
  else if (hovered) mood = 'watching';

  const lookDirection = hovered
    ? LOOK[hovered][stacked ? 'stacked' : 'wide']
    : { x: stacked ? 0 : -1, y: stacked ? 1 : 0.3 };

  const errorMessage = (
    <p className="camera-error" aria-live="polite">
      {error}
    </p>
  );

  return (
    <div className="camera-page">
      {/* MODE 1: PILIH CARA */}
      {mode === 'choose' && (
        <section className="camera-choose">
          <div className="camera-copy">
            <h1>Ambil foto wajahmu.</h1>
            <p className="camera-lead">
              Pakai kamera sekarang atau pilih foto dari galeri. Hasil analisis muncul beberapa
              detik setelah foto dikirim.
            </p>

            <div className="camera-options">
              <button
                type="button"
                className="btn-primary camera-option"
                onClick={() => startCamera('user')}
                {...hoverProps('camera')}
              >
                Buka kamera
              </button>
              <button
                type="button"
                className="btn-secondary camera-option"
                onClick={() => fileInputRef.current?.click()}
                {...hoverProps('upload')}
              >
                Unggah foto
              </button>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/jpg,image/png"
                onChange={handleFileSelect}
                className="camera-file-input"
                tabIndex={-1}
                aria-hidden="true"
              />
            </div>
            <p className="camera-hint">JPG atau PNG, maksimal 5MB.</p>

            {errorMessage}
          </div>

          <div className="camera-stage">
            <div className="camera-face">
              <FaceDots mood={mood} shakeKey={errorCount} lookDirection={lookDirection} />
            </div>
          </div>

          <p className="camera-tips">
            Biar hasilnya akurat: pakai cahaya alami yang merata, lepas makeup dan filter, lalu
            hadapkan seluruh wajah ke kamera.
          </p>
        </section>
      )}

      {/* MODE 2: KAMERA LANGSUNG */}
      {mode === 'webcam' && (
        <section className="camera-live" aria-label="Kamera">
          <div className="video-frame">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className={facingMode === 'user' ? 'mirror' : ''}
              aria-label="Tampilan kamera"
            />
            {/* Panduan posisi wajah: oval dari titik, seperti maskot */}
            <svg className="face-guide" viewBox="0 0 100 100" aria-hidden="true">
              <ellipse cx="50" cy="47" rx="29" ry="39" />
            </svg>
            <p className="video-hint">Posisikan wajah di dalam oval</p>
            <canvas ref={canvasRef} hidden />
          </div>

          <div className="live-controls">
            <button type="button" onClick={resetAll} className="btn-secondary live-side">
              Batal
            </button>
            <button type="button" onClick={capturePhoto} className="btn-capture" aria-label="Ambil foto">
              <span className="capture-dot" />
            </button>
            <button type="button" onClick={toggleFacingMode} className="btn-secondary live-side">
              Ganti kamera
            </button>
          </div>

          {errorMessage}
        </section>
      )}

      {/* MODE 3: PRATINJAU */}
      {mode === 'preview' && preview && (
        <section className="camera-preview">
          <img src={preview} alt="Pratinjau foto wajah yang akan dianalisis" />

          <div className="preview-side">
            <div className="preview-face">
              <FaceDots mood={mood} shakeKey={errorCount} lookDirection={{ x: stacked ? 0 : -1, y: 0.4 }} />
            </div>

            {loading ? (
              <div className="preview-status" role="status">
                <h1>Menganalisis fotomu…</h1>
                <p>Biasanya hanya beberapa detik. Jangan tutup halaman ini.</p>
              </div>
            ) : (
              <div className="preview-status">
                <h1>Sudah pas?</h1>
                <p>Pastikan seluruh wajah terlihat jelas dan tidak buram.</p>
              </div>
            )}

            <div className="preview-actions">
              <button
                type="button"
                onClick={handleUpload}
                disabled={loading}
                className="btn-primary camera-option"
              >
                {loading ? 'Menganalisis…' : 'Analisis foto'}
              </button>
              <button type="button" onClick={resetAll} disabled={loading} className="btn-secondary camera-option">
                Ganti foto
              </button>
            </div>

            {errorMessage}
          </div>
        </section>
      )}
    </div>
  );
};

export default Camera;
