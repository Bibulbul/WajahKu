# Laporan Quiz 1: Project Wajahku.id

**Mata Kuliah:** Internet Programming II  

---

# Bagian 1. Identitas dan Topik Proyek Aplikasi

## 1.1 Nama Aplikasi
**WajahKu.id**

## 1.2 Deskripsi Singkat dan Tujuan Utama

WajahKu.id adalah aplikasi berbasis web dan mobile yang membantu pengguna mengenali kondisi kulit wajahnya secara mandiri. Pengguna cukup mengambil atau mengunggah foto wajah, lalu sistem menganalisisnya dengan model kecerdasan buatan (EfficientNetB0 yang di-*fine-tune*) untuk mendeteksi kondisi kulit seperti jerawat, kulit berminyak, kering, atau kusam. Dari hasil analisis tersebut, aplikasi menampilkan saran perawatan dan daftar produk skincare yang sudah memiliki izin edar BPOM. Pengguna juga dapat melihat riwayat pemindaian untuk memantau perkembangan kulitnya dari waktu ke waktu.

**Masalah yang ingin diselesaikan:**
- Banyak orang kesulitan mengenali jenis dan kondisi kulitnya sendiri,
  sehingga sering salah memilih produk perawatan.
- Akses konsultasi ke dokter kulit masih terbatas, baik dari sisi biaya,
  jarak, maupun waktu tunggu.
- Produk skincare tanpa izin BPOM masih banyak beredar dan sulit dibedakan
  oleh pengguna awam, sehingga berisiko bagi kesehatan kulit.

**Tujuan utama:**
1. Menyediakan analisis awal kondisi kulit yang cepat dan mudah diakses
   hanya dengan foto dari kamera ponsel.
2. Memandu pengguna memilih produk yang aman dengan hanya menampilkan
   produk terverifikasi BPOM.
3. Membantu pengguna memantau kondisi kulit secara berkala melalui riwayat
   pemindaian.
4. Mendorong pengguna berkonsultasi ke dokter kulit ketika hasil analisis
   menunjukkan tingkat keyakinan rendah atau kondisi yang tergolong berat.

> **Catatan:** WajahKu.id merupakan alat bantu skrining awal dan tidak
> menggantikan diagnosis dokter.

## 1.3 Target Pengguna Utama

Masyarakat Indonesia berusia 18-60 tahun yang aktif mencari informasi perawatan kulit, tetapi belum memiliki akses yang mudah untuk berkonsultasi dengan dokter kulit. Pengguna diasumsikan sudah terbiasa menggunakan smartphone dan berbelanja online (misalnya melalui Shopee atau Tokopedia), namun belum tentu memiliki pengetahuan mendalam tentang kandungan atau jenis kulit. Karena itu, antarmuka aplikasi dirancang sederhana dan ramah bagi pengguna awam.

---

## Bagian 2. Resume Modul Digital Awareness

## Modul 1: There's a whole new world out there!

Modul pertama ini mengajak saya melihat lagi seberapa jauh teknologi sudah masuk ke kegiatan sehari-hari. Dulu kita harus datang ke bank untuk mengurus tabungan, membuka peta kertas untuk mencari alamat, atau pergi ke toko untuk membeli barang. Sekarang semuanya bisa dilakukan lewat ponsel dengan mobile banking, GPS, dan e-commerce. Perpindahan dari cara analog ke digital ini membuat banyak pekerjaan lebih cepat, lebih murah, lebih efisien, dan tidak lagi terbatas jarak.

Meski begitu, modul ini juga mengingatkan bahwa ada harga yang harus dibayar di dunia yang baru ini, yaitu dunia digital. Terlalu lama menatap layar ponsel atau laptop bisa mengganggu mata, tidur, bahkan kondisi mental. Data pribadi kita juga ikut beredar di mana-mana, dan tidak semua orang punya perangkat atau sinyal yang sama baiknya (digital divide). Bagi saya, poin terpentingnya adalah teknologi harus dipakai dengan sadar, bukan sekedar ikut-ikutan.

## Modul 2: You'll Need Some Basic Tools

Modul ini membahas bekal dasar sebelum kita bisa nyaman di dunia digital. Perangkat seperti laptop dan ponsel butuh sistem operasi (Windows, macOS, Android, iOS) yang bertugas mengatur perangkat keras sekaligus menjadi tempat aplikasi berjalan. Di atasnya ada aplikasi dan browser yang kita pakai untuk mengerjakan tugas tertentu.

Modul ini juga menekankan kebiasaan yang sering diremehkan, yaitu merapikan file dan folder. Dengan penamaan dan struktur yang jelas, file lebih mudah dicari, baik di penyimpanan lokal maupun cloud. Soal keamanan, langkah paling dasar adalah kata sandi yang kuat, yaitu panjang dan menggabungkan huruf besar, huruf kecil, angka, dan simbol, serta tidak dipakai berulang di banyak akun. Perangkat lunak juga perlu diperbarui rutin karena update sering berisi perbaikan celah keamanan.

## Modul 3: This is how you get around and find what you're looking for

Di modul ini saya belajar bahwa browser adalah "pintu masuk" ke internet yang mengubah kode web menjadi halaman yang bisa dibaca dan diklik. Mencari informasi pun ada tekniknya. Kata kunci yang spesifik dan operator pencarian tingkat lanjut membuat hasil lebih tepat, dan caranya sedikit berbeda antara mencari file di komputer sendiri dengan mencari di web.

Bagian yang menurut saya paling relevan untuk developer adalah soal hak cipta. Karya yang dilindungi copyright tidak boleh dipakai sembarangan dan biasanya punya syarat lisensi. Sebaliknya, karya public domain atau open-source boleh dipakai dan dimodifikasi, sering kali dengan syarat mencantumkan sumbernya. Jadi sebelum memakai gambar, ikon, atau library, kita perlu mengecek lisensinya lebih dulu.

## Modul 4: It just keeps getting better

Modul keempat membahas perkembangan teknologi, terutama kecerdasan buatan (AI). AI sekarang dipakai untuk mengotomatiskan pekerjaan, menganalisis data, dan memberi layanan yang disesuaikan dengan penggunanya. Namun AI juga membawa tanggung jawab hasilnya bisa bias, cara kerjanya tidak selalu transparan, dan data pengguna yang dipakai untuk melatihnya harus dijaga privasinya.

Selain itu, modul ini membahas etika berinternet atau netiquette. Intinya, berperilaku di internet sebaiknya sama sopannya dengan di dunia nyata: menghargai perbedaan pendapat, tidak asal menyebarkan berita yang belum jelas kebenarannya (hoax), dan ikut menjaga ruang digital tetap aman. Tanggung jawab digital ini berlaku bagi pengguna maupun pembuat aplikasi.

## Modul 5: Even Though It's Digital, It is Real, With Real Consequences

Pesan utama modul ini adalah apa yang terjadi di dunia digital punya akibat nyata. Data pribadi sensitif (PII) seperti NIK, nomor telepon, alamat, dan data keuangan bisa disalahgunakan untuk pencurian identitas atau penipuan jika jatuh ke tangan yang salah. Karena itu kita perlu berhati-hati dalam membagikan data dan waspada terhadap pesan atau tautan yang mencurigakan.

Modul ini juga menjelaskan bahwa jejak digital sulit dihapus. Unggahan atau komentar yang sudah tersebar bisa tetap ada bertahun-tahun, sehingga kita perlu berpikir dulu sebelum memposting. Untuk komunikasi negatif seperti cyberbullying, langkah yang dianjurkan antara lain tidak membalas dengan emosi, menyimpan bukti, memblokir dan melapor. Terakhir, pembajakan software atau konten (piracy) adalah tindakan ilegal yang merugikan pembuat karya, jadi sebaiknya dihindari.

## Modul 6: Learn About Anything and Everything

Modul terakhir berfokus pada kemampuan menyelesaikan masalah teknis sendiri. Saat ada gangguan, misalnya internet putus atau halaman gagal dimuat, kita diajak berpikir runtut: kenali gejalanya, cek koneksi dan perangkat, coba restart, lalu persempit sumber masalahnya sedikit demi sedikit, bukan langsung panik.

Modul ini juga mengajak kita jujur menilai skill digital diri sendiri (skills gap). Teknologi berubah cepat, jadi kemampuan belajar mandiri, membaca dokumentasi, dan mencoba tools baru sangat menentukan apakah kita tetap relevan. Untuk saya sebagai mahasiswa, ini pengingat bahwa belajar tidak berhenti di kelas.

## Bagian 3. Hubungan dan Implementasi pada Topik Proyek

> **Soal 1:** Bagaimana rancangan aplikasi dapat mempermudah tugas sehari-hari pengguna? Apa proses "analog/tradisional" dari topik proyekmu yang berhasil disederhanakan menjadi digital.

Tanpa aplikasi seperti WajahKu.id, orang yang ingin merawat kulit biasanya
menempuh proses analog yang panjang dan tidak pasti:
1. Mengira-ngira sendiri jenis kulitnya lewat cermin, atau bertanya ke
   teman dan keluarga.
2. Membuat janji dan datang langsung ke dokter kulit, yang membutuhkan
   biaya, waktu tunggu, dan jarak tempuh.
3. Membeli produk berdasarkan iklan atau ulasan, lalu mencoba satu per satu
   (*trial and error*).
4. Mengecek keaslian izin edar produk secara manual ke situs BPOM, itu pun
   kalau ingat.
5. Mengingat-ingat sendiri apakah kondisi kulitnya membaik atau memburuk.

WajahKu.id menyederhanakan proses tersebut menjadi alur digital yang singkat: foto wajah, analisis AI, saran perawatan, lalu daftar produk yang sudah terverifikasi BPOM. Pengguna tidak perlu lagi menebak-nebak, karena hasilnya keluar dalam hitungan detik (target kurang dari 10 detik). Verifikasi BPOM juga sudah dilakukan oleh tim di sisi database, sehingga pengguna tidak perlu mengeceknya satu per satu. Fitur riwayat scan menggantikan kebiasaan mencatat atau membandingkan foto secara manual,
karena perkembangan kulit tersimpan otomatis lengkap dengan tanggalnya.

> **Soal 2:** Jika aplikasimu memiliki fitur penyimpanan file atau pendaftaran akun, bagaimana kamu merancang struktur penyimpanan file yang intuitif bagi pengguna awam? Bagaimana kamu membantu pengguna membuat kata sandi yang aman?

**Struktur penyimpanan yang intuitif.** Aplikasi ini tidak meminta
pengguna mengelola file sendiri. Semua hasil scan disimpan otomatis di satu
tempat, yaitu halaman **Riwayat**, dengan struktur yang sudah dirapikan:
- Daftar diurutkan dari yang terbaru.
- Setiap entri berisi thumbnail foto, kondisi kulit yang terdeteksi, dan
  tanggal, sehingga pengguna mengenalinya tanpa perlu membaca nama file.
- Pengguna bisa mengetuk entri untuk melihat detail hasilnya.
- Sebagai usulan tambahan, pengguna dapat menghapus satu entri atau seluruh
  riwayatnya kapan saja.

Nama file di server dibuat otomatis oleh sistem (misalnya memakai ID unik
dan tanggal), bukan dari nama file asli pengguna, supaya rapi dan tidak
membocorkan informasi.

**Membantu pengguna membuat kata sandi yang aman.**
- Saat pendaftaran, tampil *password strength meter* (lemah, sedang, kuat)
  yang berubah secara langsung saat pengguna mengetik.
- Ada daftar centang syarat: minimal 8 karakter, mengandung huruf besar,
  huruf kecil, angka, dan simbol.
- Ada tombol tampilkan/sembunyikan kata sandi agar pengguna tidak salah
  ketik, terutama di layar ponsel.
- Kata sandi yang terlalu umum (misalnya "12345678" atau "password")
  ditolak, dan pengguna diberi tips membuat *passphrase* yang mudah diingat
  tapi panjang.
- Di sisi backend, kata sandi tidak pernah disimpan dalam bentuk asli,
  melainkan di-*hash* dengan algoritma seperti bcrypt atau Argon2.

> **Soal 3:** Bagaimana kamu mendesain fitur pencarian (search bar) di dalam aplikasi agar pengguna dapat mencari informasi dengan mudah? Selain itu, sebutkan asset eksternal yang digunakan dalam aplikasi (library, API, gambar, icon). Apakah asset-aset tersebut berlisensi open-source, public domain, atau memiliki hak cipta khusus yang wajib dicantumkan?

**Rancangan search bar.** Search bar ditempatkan di halaman rekomendasi
produk dan halaman riwayat, karena di situlah pengguna paling sering
mencari sesuatu. Rancangannya:
- Pengguna bisa mencari berdasarkan **nama produk, kategori** (face wash,
  toner, moisturizer), atau **kondisi kulit** (misalnya "jerawat").
- Ada saran otomatis (*autocomplete*) saat mengetik, dan pencarian tetap
  bekerja walau ada salah ketik ringan atau huruf besar-kecil berbeda.
- Ada filter cepat berupa *chip* (kondisi kulit, kategori, rating) supaya
  pengguna tidak perlu mengetik.
- Di halaman riwayat, pengguna bisa memfilter berdasarkan tanggal atau
  kondisi yang terdeteksi.
- Bila tidak ada hasil, aplikasi menampilkan pesan yang membantu (misalnya
  "Produk tidak ditemukan, coba kata kunci lain atau lihat rekomendasi
  sesuai hasil scan-mu"), bukan halaman kosong.

**Aset eksternal yang digunakan.**

- **React.js dan Vite** dipakai untuk frontend web. Keduanya berlisensi
  MIT (open-source).
- **React Native (Expo) atau Flutter** dipakai untuk aplikasi mobile.
  Berlisensi MIT atau BSD (open-source).
- **FastAPI atau Django REST Framework** dipakai untuk backend dan API.
  Berlisensi MIT atau BSD (open-source).
- **MediaPipe Face Mesh** dipakai untuk mendeteksi dan memotong (crop)
  area wajah. Berlisensi Apache 2.0 (open-source).
- **EfficientNetB0 (Hugging Face)** dipakai sebagai model klasifikasi
  kondisi kulit. Lisensinya mengikuti *model card* di Hugging Face,
  umumnya Apache 2.0.
- **Dataset Acne04** dipakai untuk melatih model. Dataset ini ditujukan
  untuk keperluan riset/akademik, sehingga wajib mencantumkan sitasi
  makalah aslinya.
- **Ikon (misalnya Lucide atau Font Awesome Free)** dipakai untuk
  antarmuka. Berlisensi ISC atau CC BY 4.0, dan ikon Font Awesome Free
  perlu dicantumkan atribusinya.
- **Data BPOM (cekbpom.pom.go.id)** dipakai sebagai rujukan verifikasi
  izin edar. Ini data publik pemerintah.
- **Foto/logo produk** untuk kartu produk berstatus berhak cipta merek,
  sehingga hanya dipakai bila ada izin atau diganti dengan ilustrasi
  sendiri.

Semua aset open-source dicantumkan pada halaman "Tentang" dan berkas
`LICENSES`/`README` di repository. Dataset glowmix disitasi sesuai
ketentuan penciptanya. Foto produk dari marketplace tidak diambil
sembarangan karena berhak cipta, sehingga kartu produk hanya memuat teks,
ikon kategori, dan tautan ke halaman produknya.

> **Soal 4:** Jika aplikasimu memiliki fitur interaksi sosial, bagaimana kamu mencegah pelanggaran etika digital di dalamnya? Jika aplikasi menggunakan fitur pintar berbasis AI, bagaimana kamu memastikan AI tersebut bekerja secara etis dan bertanggung jawab bagi pengguna?

**Interaksi sosial.** Versi saat ini tidak memiliki fitur sosial seperti
komentar, forum, atau chat antarpengguna. Rating produk dikumpulkan secara
manual atau semi-manual oleh tim, sehingga risiko perundungan, ujaran
kebencian, dan hoaks antarpengguna sangat kecil. Bila di masa depan
pengguna boleh menulis ulasan, saya akan menambahkan panduan komunitas,
tombol lapor, dan moderasi sebelum ulasan tampil.

**AI yang etis dan bertanggung jawab.**
- **Transparan.** Hasil selalu disertai *confidence score* dan disclaimer
  bahwa aplikasi ini alat skrining awal, bukan diagnosis medis.
- **Human in the loop.** Bila confidence rendah atau kondisi terdeteksi
  berat, sistem otomatis menyarankan konsultasi ke dokter kulit. Kondisi di
  luar cakupan model (eksim, psoriasis, kanker kulit) juga diarahkan ke
  dokter.
- **Persetujuan eksplisit.** Pengguna harus memberi consent sebelum foto
  diproses, dan dijelaskan untuk apa foto dipakai.
- **Menyadari bias.** Dataset Acne04 condong ke kondisi jerawat, dan
  keragaman warna kulit pada data pelatihan bisa memengaruhi akurasi. Hal
  ini dicatat secara terbuka sebagai limitasi, dievaluasi per kelas
  (Precision, Recall, F1-Score), dan diperbaiki dengan augmentasi serta
  data tambahan.
- **Rekomendasi tidak menyesatkan.** Produk hanya berasal dari database
  terkurasi berizin BPOM, dan tautan e-commerce ditandai jelas sebagai
  tautan eksternal.
- **Data tidak disalahgunakan.** Foto pengguna tidak dipakai untuk melatih
  ulang model tanpa persetujuan terpisah.

> **Soal 5:** Data pribadi sensitif (PII) apa saja yang dikumpulkan oleh aplikasimu? Bagaimana cara kamu melindungi data tersebut agar tidak bocor atau disalahgunakan? Bagaimana aplikasi meminimalkan risiko pengguna menjadi korban penipuan siber di platformmu?

**Data yang dikumpulkan:**
- Foto wajah, yang merupakan data biometrik dan tergolong sensitif.
- Hasil analisis kondisi kulit, yang berkaitan dengan kesehatan.
- Data akun: nama/username, email, dan kata sandi (dalam bentuk hash).
- Riwayat scan (tanggal dan hasil).

Aplikasi **tidak** meminta NIK, alamat rumah, nomor telepon, maupun data
keuangan, karena tidak ada transaksi di dalam aplikasi.

**Cara melindungi data:**
- **Data minimization:** hanya mengumpulkan yang benar-benar dibutuhkan.
- **Consent eksplisit** sebelum foto diproses, sesuai prinsip pelindungan
  data pribadi (UU No. 27 Tahun 2022 tentang PDP).
- **HTTPS** untuk seluruh komunikasi antara frontend dan backend.
- **Enkripsi foto** saat disimpan di database/penyimpanan.
- **Hashing kata sandi** dan autentikasi pengguna pada setiap endpoint
  riwayat, sehingga pengguna hanya bisa melihat datanya sendiri.
- **Validasi file** (format dan ukuran) di backend untuk mencegah unggahan
  berbahaya.
- **Kontrol pengguna:** pengguna dapat menghapus riwayat scan dan akunnya.
- Admin hanya mengakses statistik, bukan foto pribadi pengguna.

**Meminimalkan risiko penipuan siber:**
- Aplikasi tidak menerima pembayaran dan tidak pernah meminta OTP, PIN,
  atau data kartu.
- Setiap produk menampilkan nomor BPOM yang bisa dicek ke situs resmi,
  sehingga pengguna terhindar dari produk ilegal atau palsu.
- Tautan hanya mengarah ke Shopee/Tokopedia, dengan pemberitahuan bahwa
  pengguna akan meninggalkan aplikasi. Tim menyarankan membeli dari toko
  resmi.
- Aplikasi menampilkan peringatan edukatif agar pengguna waspada terhadap
  pihak yang mengatasnamakan WajahKu.id.

> **Soal 6:** Ketika aplikasi mengalami masalah teknis (misalnya kehilangan koneksi internet atau kegagalan memuat data), bagaimana aplikasi mengomunikasikannya kepada pengguna? Tuliskan contoh rancangan pesan error ramah pengguna yang memandu pengguna melakukan troubleshooting mandiri secara mudah.

Prinsipnya, pesan error harus memakai bahasa sehari-hari, menjelaskan
apa yang terjadi, tidak menyalahkan pengguna, dan memberi langkah
konkret yang bisa dicoba. Kode teknis disimpan di log, bukan ditampilkan.

- **Tidak ada koneksi internet**
  - Pesan: **"Koneksimu sedang terputus."** Foto belum bisa dianalisis
    tanpa internet.
  - Langkah yang dipandu: 1) cek Wi-Fi atau data seluler, 2) matikan lalu
    nyalakan mode pesawat, 3) tekan **Coba Lagi**.

- **Upload foto gagal atau timeout**
  - Pesan: **"Foto belum berhasil terkirim."** Kemungkinan sinyal sedang
    lemah. Fotomu masih tersimpan di perangkat.
  - Langkah yang dipandu: pindah ke tempat dengan sinyal lebih baik, lalu
    tekan **Kirim Ulang**.

- **Wajah tidak terdeteksi**
  - Pesan: **"Kami belum bisa melihat wajahmu dengan jelas."**
  - Langkah yang dipandu: 1) cari tempat dengan cahaya terang, 2) hadapkan
    wajah lurus ke kamera, 3) lepas masker atau kacamata, lalu tekan
    **Ambil Ulang**.

- **Format atau ukuran file salah**
  - Pesan: **"File ini belum bisa diproses."**
  - Langkah yang dipandu: gunakan foto JPG atau PNG dengan ukuran maksimal
    sesuai batas yang ditampilkan.

- **Server bermasalah**
  - Pesan: **"Ups, ada gangguan di sistem kami."** Ini bukan kesalahanmu.
  - Langkah yang dipandu: tunggu beberapa menit lalu coba lagi. Jika masih
    terjadi, hubungi kami lewat menu **Bantuan**.

- **Riwayat atau produk gagal dimuat**
  - Pesan: **"Data belum bisa ditampilkan."**
  - Langkah yang dipandu: tarik layar ke bawah untuk memuat ulang, atau
    periksa koneksimu.

Aplikasi juga memakai indikator *loading*, tombol **Coba Lagi** yang jelas,
dan halaman **Bantuan/FAQ** sebagai tempat pengguna belajar
mengatasi masalah sendiri (*self-troubleshooting*).
