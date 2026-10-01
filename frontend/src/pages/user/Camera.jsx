import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import './Camera.css';

const Camera = () => {
  const [mode, setMode] = useState('choose'); // 'choose', 'webcam', 'preview'
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [facingMode, setFacingMode] = useState('user'); // 'user' (depan) atau 'environment' (belakang)

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);
  const streamRef = useRef(null);
  const navigate = useNavigate();

  // Matikan stream kamera ketika unmount atau ganti mode
  const stopCameraStream = () => {
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
    setError('');
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

      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      console.error('Kamera Error:', err);
      setError('Tidak dapat mengakses kamera. Pastikan izin kamera telah diberikan.');
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
          setError('Gagal mengambil gambar dari kamera.');
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
    if (!file) return;

    if (!['image/jpeg', 'image/jpg', 'image/png'].includes(file.type)) {
      setError('Format file tidak didukung. Gunakan JPG, JPEG, atau PNG');
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      setError('Ukuran file terlalu besar. Maksimal 5MB');
      return;
    }

    setSelectedFile(file);
    setError('');

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
      setError(err.response?.data?.error || 'Terjadi kesalahan saat mengunggah foto');
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

  return (
    <div className="camera-page">
      <div className="container">
        <div className="camera-header">
          <h1>Pemindaian Wajah</h1>
          <p>Ambil foto langsung melalui kamera atau unggah dari perangkat</p>
        </div>

        <div className="camera-container">
          {/* MODES 1: OPSI PILIHAN */}
          {mode === 'choose' && (
            <div className="choose-area">
              <div className="option-card" onClick={() => startCamera('user')}>
                <div className="icon-box">
                  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path>
                    <circle cx="12" cy="13" r="4"></circle>
                  </svg>
                </div>
                <h3>Buka Kamera</h3>
                <p>Ambil foto wajah secara langsung</p>
              </div>

              <div className="option-divider">atau</div>

              <div className="option-card" onClick={() => fileInputRef.current?.click()}>
                <div className="icon-box">
                  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                    <circle cx="8.5" cy="8.5" r="1.5"></circle>
                    <polyline points="21 15 16 10 5 21"></polyline>
                  </svg>
                </div>
                <h3>Unggah Foto</h3>
                <p>Pilih file dari galeri atau komputer (JPG, PNG)</p>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/jpeg,image/jpg,image/png"
                  onChange={handleFileSelect}
                  style={{ display: 'none' }}
                />
              </div>
            </div>
          )}

          {/* MODE 2: LIVE WEBCAM */}
          {mode === 'webcam' && (
            <div className="webcam-area">
              <div className="video-wrapper">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  className={facingMode === 'user' ? 'mirror' : ''}
                />
                <canvas ref={canvasRef} style={{ display: 'none' }} />
              </div>

              <div className="webcam-controls">
                <button type="button" onClick={resetAll} className="btn-secondary">
                  Batal
                </button>

                <button type="button" onClick={capturePhoto} className="btn-capture">
                  <span className="capture-circle"></span>
                </button>

                <button type="button" onClick={toggleFacingMode} className="btn-secondary btn-icon-only" title="Ganti Kamera">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="23 4 23 10 17 10"></polyline>
                    <polyline points="1 20 1 14 7 14"></polyline>
                    <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
                  </svg>
                </button>
              </div>
            </div>
          )}

          {/* MODE 3: PREVIEW FOTO */}
          {mode === 'preview' && preview && (
            <div className="preview-area">
              <img src={preview} alt="Preview Wajah" />
              <div className="preview-actions">
                <button onClick={resetAll} className="btn-secondary">
                  Ganti Foto
                </button>
                <button
                  onClick={handleUpload}
                  disabled={loading}
                  className="btn-primary"
                >
                  {loading ? 'Menganalisis...' : 'Analisis Sekarang'}
                </button>
              </div>
            </div>
          )}

          {error && <div className="error-message">{error}</div>}

          {loading && (
            <div className="loading-overlay">
              <div className="spinner"></div>
              <p>Sistem sedang memproses foto Anda...</p>
              <small>Proses ini membutuhkan beberapa detik</small>
            </div>
          )}
        </div>

        <div className="tips">
          <h3>Tips Foto Terbaik</h3>
          <ul>
            <li>Gunakan pencahayaan yang cukup dan merata</li>
            <li>Pastikan seluruh wajah terlihat jelas tanpa terhalang</li>
            <li>Hindari penggunaan filter atau pengeditan gambar</li>
            <li>Posisikan wajah tepat di tengah area foto</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Camera;
