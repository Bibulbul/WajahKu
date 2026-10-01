### 1. Overview & Problem Statement

**Overview**
WajahKu.id adalah aplikasi web/mobile berbasis AI yang menganalisis kondisi kesehatan kulit wajah pengguna dari foto, memberikan diagnosis kondisi kulit secara universal (jerawat, minyak berlebih, kusam, kering, kemerahan, dll), lalu merekomendasikan tindakan perawatan dan produk skincare yang telah terverifikasi BPOM, dilengkapi ulasan pengguna lain sebagai social proof.

**Problem Statement**
Banyak masyarakat Indonesia kesulitan menentukan kondisi kulit wajah mereka secara objektif dan sering salah memilih produk skincare karena:
- Tidak memahami kondisi kulit sendiri secara akurat (self-diagnosis yang bias)
- Kurangnya akses mudah ke dermatologis untuk konsultasi rutin
- Maraknya produk skincare tanpa izin BPOM yang berpotensi berbahaya
- Minimnya informasi ulasan yang terpusat dan kredibel sebelum membeli produk

### 2. Goals & Success Metrics

| Goal | Metrik Sukses |
|---|---|
| Deteksi kondisi kulit akurat | Model mencapai akurasi klasifikasi ≥ 80% pada test set |
| Rekomendasi produk relevan & aman | 100% produk yang direkomendasikan terverifikasi BPOM |
| Pengalaman pengguna baik | Waktu proses dari upload foto sampai hasil < 10 detik |
| MVP dapat didemokan | Aplikasi berhasil deploy ke production sebelum minggu ke-16 |
| Adopsi dalam demo/testing | Minimal 20 pengguna uji coba memberikan feedback pada masa testing |

### 3. User Persona & User Stories

**Persona: "Rani, 22 tahun, mahasiswi"**
Sering berjerawat karena stres kuliah, bingung pilih skincare karena banyak review yang saling bertentangan di media sosial, budget terbatas sehingga butuh rekomendasi produk yang efektif dan terjangkau.

**User Stories**
- Sebagai pengguna, saya ingin memfoto wajah saya agar sistem bisa menganalisis kondisi kulit saya secara otomatis.
- Sebagai pengguna, saya ingin melihat penjelasan kondisi kulit saya dengan bahasa yang mudah dipahami (bukan istilah medis rumit).
- Sebagai pengguna, saya ingin mendapat rekomendasi produk yang sudah terverifikasi BPOM agar merasa aman menggunakannya.
- Sebagai pengguna, saya ingin melihat ulasan pengguna lain terhadap produk yang direkomendasikan sebelum memutuskan membeli.
- Sebagai pengguna, saya ingin tahu langkah perawatan apa yang harus saya lakukan, bukan cuma nama produk.

### 4. Scope

**In-Scope (MVP)**
- Deteksi 4–6 kondisi kulit utama: jerawat, berminyak, kering, kusam, kemerahan/iritasi, kombinasi
- Rekomendasi kategori tindakan perawatan (misal: cuci muka 2x sehari, gunakan sunscreen)
- Rekomendasi produk dari database kurasi (100–200 produk ber-BPOM)
- Menampilkan rating rata-rata ulasan produk (bisa diambil dari data yang di-crawl/manual)
- Web dashboard untuk melihat riwayat hasil scan pengguna

**Out-of-Scope (untuk versi ini)**
- Diagnosis penyakit kulit serius (eksim, psoriasis, kanker kulit) — akan diarahkan ke rekomendasi konsultasi dokter
- Transaksi pembelian produk langsung di dalam app (cukup link ke e-commerce eksternal)
- Sistem review real-time terintegrasi API resmi e-commerce (kemungkinan besar tidak tersedia gratis)
- Personalisasi jangka panjang berbasis riwayat cuaca/lokasi/gaya hidup

### 5. Functional Requirements

| Modul | Requirement | Prioritas | Acceptance Criteria |
|---|---|---|---|
| Upload Foto | User dapat mengambil/upload foto wajah | Must Have | Foto berhasil ter-upload dan tampil preview sebelum submit |
| Deteksi Kondisi Kulit | Sistem mengklasifikasi kondisi kulit dari foto | Must Have | Hasil klasifikasi tampil dengan confidence score |
| Rekomendasi Tindakan | Sistem memberi saran perawatan berbasis hasil deteksi | Must Have | Saran ditampilkan dalam bahasa awam, minimal 2-3 poin actionable |
| Rekomendasi Produk | Sistem menampilkan produk BPOM yang sesuai | Must Have | Setiap produk menampilkan nomor BPOM dan status "terverifikasi" |
| Tampilan Ulasan | Sistem menampilkan rating/ulasan produk | Should Have | Rating rata-rata dan jumlah ulasan tampil di kartu produk |
| Riwayat Scan | User dapat melihat histori scan sebelumnya | Should Have | List riwayat terurut berdasarkan tanggal, bisa lihat detail tiap scan |
| Web Dashboard Admin | Tim dapat memonitor data & mengelola database produk | Should Have | Admin dapat tambah/edit/hapus data produk |
| Disclaimer Medis | Sistem menampilkan peringatan untuk kondisi parah | Must Have | Muncul notice "konsultasikan ke dokter" jika confidence rendah/kondisi berat |
| Autentikasi | User dapat login/register | Nice to Have | Login berhasil menyimpan sesi user untuk riwayat personal |

### 6. Non-Functional Requirements

- **Privasi**: Foto wajah pengguna adalah data sensitif — harus ada consent eksplisit sebelum upload, dan kebijakan retensi data yang jelas (misal foto dihapus otomatis setelah X hari, atau disimpan terenkripsi).
- **Performa**: Waktu respons AI Engine idealnya di bawah 10 detik per analisis.
- **Keamanan**: Autentikasi dengan hashing password standar, API endpoint dilindungi token/JWT.
- **Skalabilitas**: Tidak perlu skala besar untuk MVP, tapi arsitektur harus modular agar mudah dikembangkan.
- **Aksesibilitas**: UI harus jelas dibaca, kontras warna cukup untuk pengguna dengan low vision.

### 7. System Architecture (High-Level)

```
[Mobile/Web App] 
      | (foto wajah)
      v
[REST API - Backend]
      | (kirim ke AI Engine)
      v
[AI Engine: Model Klasifikasi Kulit]
      | (hasil klasifikasi)
      v
[REST API] --> [Database: hasil scan, produk, review]
      |
      v
[Web Dashboard: monitoring & manajemen data]
```

Komponen:
- **Frontend (Mobile/Web)**: Upload foto, tampilkan hasil, riwayat scan
- **REST API**: Autentikasi, validasi input, orkestrasi ke AI Engine, akses database
- **AI Engine**: Model computer vision untuk klasifikasi kondisi kulit
- **Database**: Menyimpan data user, hasil scan, database produk BPOM, data ulasan
- **Web Dashboard**: Untuk tim/admin memonitor dan mengelola data produk

### 8. AI/ML Requirements

- **Dataset kandidat**: Kombinasi dataset publik seperti Acne04 Dataset, Facial Skin Disease Dataset (Kaggle), atau dataset serupa untuk kondisi kulit umum.
- **Pendekatan model**: Fine-tuning model CNN pretrained (ResNet/EfficientNet/MobileNet — pilih yang ringan untuk mobile) menggunakan transfer learning, bukan training dari nol.
- **Output model**: Multi-label atau multi-class classification (kondisi kulit bisa lebih dari satu sekaligus, misal berjerawat + berminyak).
- **Metrik evaluasi**: Akurasi, precision, recall, F1-score per kelas kondisi kulit. Confusion matrix untuk analisis kesalahan klasifikasi.
- **Preprocessing**: Face detection/cropping (misal pakai MediaPipe Face Mesh) sebelum klasifikasi, untuk memastikan model fokus pada area wajah saja.

### 9. Data Requirements

- **Data BPOM**: Kurasi manual dari pencarian publik cekbpom.pom.go.id untuk 100–200 produk skincare populer, disimpan sebagai database internal (nomor BPOM, nama produk, kategori, kandungan aktif).
- **Data E-commerce**: Link produk ke marketplace (Shopee/Tokopedia) disimpan manual atau melalui pencarian berbasis nama produk (tanpa API resmi karena keterbatasan akses).
- **Data Review**: Bisa dikumpulkan manual dari review publik di marketplace/media sosial untuk sampel produk yang dikurasi, disimpan sebagai rating rata-rata + jumlah ulasan.

### 10. User Flow

1. User membuka aplikasi dan diminta izin akses kamera/upload foto.
2. User memfoto wajah (dengan panduan pencahayaan yang cukup di layar).
3. Foto dikirim ke backend, diproses AI Engine.
4. Sistem menampilkan hasil: kondisi kulit terdeteksi beserta confidence score.
5. Sistem menampilkan rekomendasi tindakan perawatan dalam bahasa sederhana.
6. Sistem menampilkan daftar produk yang sesuai, lengkap dengan status BPOM dan rating ulasan.
7. User dapat klik produk untuk diarahkan ke halaman e-commerce (link eksternal).
8. Hasil scan tersimpan di riwayat user untuk referensi selanjutnya.

### 11. Wireframe/UI Notes (Deskripsi Tekstual)

- **Halaman Utama**: Tombol besar "Scan Wajah Sekarang", ilustrasi singkat cara kerja app.
- **Halaman Kamera**: Panduan overlay wajah (agar user foto dengan posisi tepat), tombol capture.
- **Halaman Hasil**: Kartu kondisi kulit terdeteksi (dengan ikon/warna berbeda per kondisi), diikuti section "Yang Harus Kamu Lakukan" (list actionable), lalu section "Produk Rekomendasi" (carousel/list kartu produk dengan foto, nama, badge BPOM, rating bintang).
- **Halaman Riwayat**: List kartu hasil scan sebelumnya, diurutkan tanggal terbaru.
- **Dashboard Admin (Web)**: Tabel manajemen produk (CRUD), statistik jumlah scan per kondisi kulit.

### 12. Risks & Mitigations

| Risiko | Mitigasi |
|---|---|
| Model salah klasifikasi kondisi serius sebagai ringan | Tambahkan disclaimer tegas + threshold confidence untuk redirect ke "konsultasi dokter" |
| Data foto wajah bocor/disalahgunakan | Enkripsi data, kebijakan retensi jelas, consent eksplisit |
| Data BPOM/review tidak update | Tetapkan proses kurasi berkala oleh tim, tandai tanggal update data |
| Rekomendasi produk dianggap sebagai "obat" | Gunakan bahasa "perawatan kulit" bukan "pengobatan", hindari klaim medis berlebihan |
| Scope terlalu besar untuk 16 minggu | Kunci MVP di 4-6 kondisi kulit dan 100-200 produk saja, jangan tambah fitur di tengah jalan |

### 13. Timeline & Milestones (16 Minggu)

| Minggu | Fokus |
|---|---|
| 1 | Penentuan judul, dataset/model, setup GitHub Projects |
| 2 | Validasi model AI, desain arsitektur sistem & fitur |
| 3–4 | Penulisan dokumen proposal, finalisasi PRD dan desain database |
| 5–6 | Kurasi dataset kondisi kulit, mulai training/fine-tuning model awal |
| 7–8 | Bangun REST API (auth, endpoint upload, integrasi AI Engine) |
| 9–10 | Bangun frontend mobile/web (upload foto, tampilan hasil) |
| 11–12 | Integrasi database produk BPOM + review, bangun web dashboard admin |
| 13 | Testing end-to-end, perbaikan bug, refinement UI/UX |
| 14 | User testing terbatas, kumpulkan feedback |
| 15 | Deployment ke production, revisi akhir |
| 16 | Pembuatan poster/video demo, showcase final |

### 14. Open Questions

- Apakah kondisi kulit yang dideteksi cukup 4-6 kategori, atau tim ingin menambah/mengurangi?
- Bagaimana strategi kurasi data review produk — manual satu-satu atau ada cara semi-otomatis (scraping terbatas)?
- Apakah aplikasi berbentuk web app, mobile app, atau keduanya (mengingat arsitektur di silabus menyebutkan mobile untuk input dan web untuk dashboard)?
- Siapa yang bertanggung jawab untuk update database BPOM secara berkala setelah MVP selesai (di luar scope akademik, tapi baik didiskusikan)?

---

*Dokumen ini adalah starting point — silakan didiskusikan dan disesuaikan bersama anggota tim sebelum difinalisasi sebagai bagian dari dokumen proposal.*
