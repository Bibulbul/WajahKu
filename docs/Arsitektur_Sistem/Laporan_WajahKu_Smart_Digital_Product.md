# LAPORAN SMART DIGITAL PRODUCT: WajahKu.id

## 1. Ringkasan Eksekutif (Executive Summary)

* **Masalah:** Banyak orang Indonesia kesulitan mengenali kondisi kulit wajah mereka dan sering salah pilih produk skincare. Akses ke dermatologis terbatas, sementara produk tanpa izin BPOM beredar luas.
* **Solusi Digital:** WajahKu.id adalah aplikasi web/mobile yang menganalisis foto wajah pakai model EfficientNetB0 untuk deteksi kondisi kulit otomatis, lalu kasih rekomendasi produk skincare yang sudah terverifikasi BPOM.
* **Target Pengguna:** Masyarakat Indonesia usia 18-60 tahun yang aktif cari informasi skincare tapi gak punya akses mudah ke konsultasi dermatologis.

## 2. Arsitektur Sistem (System Architecture)

* **Diagram Arsitektur:** Sudah dibuat dalam bentuk HTML (file: WajahKu_Arsitektur_Sistem.html)

* **Spesifikasi Teknologi (Tech Stack):**
    * **Perangkat Keras/Sensor:** Kamera smartphone atau webcam laptop untuk ambil foto wajah. Gak perlu hardware khusus di sisi server.
    * **Backend & API:** Python dengan FastAPI atau Django REST Framework. Endpoint utama: upload foto, analisis kulit, ambil rekomendasi produk, riwayat scan, autentikasi user.
    * **Kecerdasan Buatan/Algoritma/Model/Dataset:** 
        * Model: EfficientNetB0 dari Hugging Face dengan fine-tuning pakai transfer learning
        * Task: Multi-label classification untuk deteksi 4-6 kondisi kulit (jerawat, berminyak, kering, kusam, kemerahan, keriput, kombinasi)
        * Preprocessing: MediaPipe Face Mesh untuk face detection dan cropping sebelum masuk ke model
        * Dataset: Acne04 Dataset (1,457 gambar dengan 18,983 bounding box annotations) yang diaugmentasi dengan flip, rotasi, dan brightness adjustment
        * Baseline model sudah dibuat di Google Colab
        * Metrik: Akurasi, Precision, Recall, F1-Score per kelas, Confusion Matrix
    * **Frontend/Antarmuka:** 
        * Web: React.js + Vite dengan Fetch API untuk halaman utama, hasil scan, dan riwayat
        * Mobile: React Native (Expo) atau Flutter buat akses kamera native
        * Admin: React atau Django Admin untuk manajemen data produk BPOM dan monitoring statistik scan

## 3. Rancangan Fitur Inti (Core Features)

### Deteksi Kondisi Kulit Otomatis (AI Skin Analysis)
* **Fungsi:** Analisis foto wajah yang diupload user secara otomatis pakai computer vision untuk identifikasi kondisi kulit aktif.
* **Input Data:** Foto wajah (JPG/PNG) dari frontend. Sebelum masuk model, foto diproses MediaPipe untuk deteksi dan crop area wajah agar model fokus ke region yang relevan.
* **Output/Aksi:** Sistem kasih label kondisi kulit yang terdeteksi (bisa lebih dari satu, misal: "Berjerawat + Berminyak") plus confidence score tiap kondisi. Kalau confidence score rendah atau kondisi berat terdeteksi, sistem otomatis munculin disclaimer untuk konsultasi ke dokter kulit.

### Rekomendasi Produk Skincare Terverifikasi BPOM
* **Fungsi:** Kasih daftar produk skincare yang sesuai kondisi kulit user, diambil dari database internal yang dikurasi dan semua punya nomor izin edar BPOM.
* **Input Data:** Label kondisi kulit hasil deteksi AI (misal: "Berjerawat", "Berminyak") dipake sebagai parameter query ke database produk.
* **Output/Aksi:** Sistem tampilkan daftar produk dalam bentuk kartu yang muat: nama produk, kategori (face wash, toner, moisturizer), nomor BPOM, rating rata-rata review user, dan link ke e-commerce eksternal (Shopee/Tokopedia). 100% produk yang ditampilkan dijamin terverifikasi BPOM.

### Riwayat Scan & Dashboard Pengguna
* **Fungsi:** Simpan dan tampilkan histori hasil analisis kulit user dari waktu ke waktu, jadi user bisa track perkembangan kondisi kulitnya.
* **Input Data:** Setiap hasil scan yang berhasil diproses (foto, hasil deteksi, tanggal scan) disimpan ke database terhubung ke akun user.
* **Output/Aksi:** Halaman riwayat tampilkan daftar scan sebelumnya diurutkan dari terbaru, lengkap dengan thumbnail foto, kondisi yang terdeteksi, dan tanggal. User bisa klik tiap entri untuk lihat detail hasil scan tersebut.

## 4. Alur Data & Cara Kerja (System Workflow)

1. **Pengumpulan Data (Data Collection):** User buka aplikasi dan diarahkan ke halaman kamera. Sebelum ambil foto, user dikasih panduan pencahayaan dan posisi wajah lewat overlay di layar. User kasih consent eksplisit untuk penggunaan data foto sebelum proses dimulai. Foto diambil lewat kamera perangkat atau di-upload dari galeri, lalu ditampilkan preview sebelum dikirim ke server.

2. **Transmisi & Komunikasi (Transmission):** Foto wajah dikirim dari frontend ke Backend REST API pakai HTTP POST request dalam format multipart/form-data. Semua komunikasi dienkripsi pakai HTTPS. Backend validasi format dan ukuran file sebelum terusin ke AI Engine.

3. **Pemrosesan (Processing):** Backend terusin gambar ke AI Engine. AI Engine jalanin face detection pakai MediaPipe Face Mesh untuk crop area wajah otomatis. Hasil cropping diubah ukurannya (resize) dan dinormalisasi sesuai spesifikasi input model EfficientNetB0. Model EfficientNetB0 (yang sudah di-fine-tune) hasilin prediksi multi-label kondisi kulit beserta nilai confidence score. Hasil prediksi dikembaliin ke Backend. Backend lakukan query ke database produk berdasarkan label kondisi kulit yang terdeteksi untuk ambil daftar produk dan saran perawatan yang relevan. Seluruh hasil scan (foto terenkripsi, label, confidence, timestamp) disimpan ke database terhubung akun user.

4. **Eksekusi/Tampilan (Action/Display):** Backend kirim respons JSON ke frontend yang berisi: label kondisi kulit + confidence score, daftar saran perawatan, dan daftar produk rekomendasi. Frontend render hasilnya dalam tampilan terstruktur: Kartu kondisi kulit (warna dan ikon berbeda tiap kondisi) dengan confidence score. Seksi "Yang Harus Kamu Lakukan" berisi poin-poin actionable. Seksi "Produk Rekomendasi" dalam bentuk carousel/list kartu produk dengan badge BPOM dan rating bintang. Kalau confidence rendah atau kondisi terdeteksi berat, muncul notice: "Kondisi ini sebaiknya dikonsultasikan ke dokter kulit." Hasil scan tersimpan otomatis ke halaman Riwayat user.

## 5. Pengujian & Limitasi (Testing & Limitations)

* **Metrik Pengujian:**
    * **Performa Model AI:** Target akurasi klasifikasi kondisi kulit >= 80% pada test set. Evaluasi pakai Precision, Recall, dan F1-Score per kelas kondisi kulit (karena distribusi kelas bisa gak seimbang). Confusion Matrix dipake untuk identifikasi pasangan kondisi yang paling sering salah diklasifikasi.
    * **Performa Sistem:** Response time end-to-end (dari upload foto sampai hasil tampil di layar) ditarget di bawah 10 detik. API endpoint diuji pakai tools seperti Postman atau pytest untuk pastiin semua endpoint jalan sesuai spesifikasi.
    * **Validasi Data Produk:** 100% produk dalam database dipastiin punya nomor izin edar BPOM yang valid (diverifikasi via cekbpom.pom.go.id).
    * **User Testing:** Minimal 20 user uji coba kasih feedback pada masa testing untuk evaluasi kemudahan penggunaan dan relevansi rekomendasi.

* **Limitasi Saat Ini:**
    * **Cakupan Kondisi Kulit Terbatas:** Model cuma dilatih untuk deteksi 4-6 kondisi kulit umum. Kondisi kulit serius seperti eksim, psoriasis, atau kanker kulit di luar cakupan dan akan diarahin ke disclaimer konsultasi dokter.
    * **Kualitas Foto Bergantung User:** Akurasi model sangat dipengaruhi kualitas foto (pencahayaan, posisi wajah, resolusi). Foto yang terlalu gelap, buram, atau gak menampilkan wajah dengan jelas bisa hasilin prediksi yang gak akurat.
    * **Database Produk Statis:** Database produk BPOM dikurasi secara manual (100-200 produk) dan gak diperbarui secara real-time. Perlu proses kurasi berkala oleh tim untuk jaga keakuratan data.
    * **Gak Ada Transaksi Langsung:** Aplikasi cuma sediain link ke e-commerce eksternal (Shopee/Tokopedia); gak ada integrasi pembelian langsung di dalam aplikasi.
    * **Data Review Gak Real-Time:** Rating dan review produk dikumpulkan secara manual atau semi-manual, bukan dari API resmi marketplace, jadi gak mencerminkan kondisi review terkini secara real-time.
    * **Dataset Acne04 Fokus ke Jerawat:** Dataset Acne04 yang dipake punya bias ke kondisi jerawat (acne lesions). Untuk kondisi kulit lain seperti kering atau kusam, perlu augmentasi dataset tambahan atau kombinasi dengan dataset lain untuk hasil yang lebih akurat.
