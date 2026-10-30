# Data produk skincare wajah (DB-03, DB-04)

1. Salin `produk_template.csv` menjadi `produk.csv`, lalu isi satu produk per baris (Excel boleh, simpan sebagai CSV).
2. Jalankan dari root repo: `python -m ml.produk_skincare`.
3. Perbaiki baris di `produk_ditolak.csv` (kolom `alasan`), jalankan lagi.
4. Serahkan `produk_tambahan.sql` ke Backend untuk dimasukkan ke database.

| Kolom | Wajib | Isi |
|---|---|---|
| nama | ya | Nama produk seperti di kemasan, mis. `Acne Care Face Wash` |
| merek | ya | Mis. `Wardah` |
| kategori | tidak | `cleanser`, `toner`, `serum`, `moisturizer`, `sunscreen`, `mask`, `exfoliant`. Kosong = ditebak dari nama |
| deskripsi | tidak | Satu kalimat. Kosong = memakai nama |
| harga | ya | Rupiah, mis. `35000` atau `Rp 35.000` |
| nomor_bpom | ya | Nomor notifikasi kosmetik, mis. `NA18201200345` |
| bahan_aktif | ya | Bahan aktif utama dipisah koma, nama Inggris seperti di kemasan, mis. `Salicylic Acid, Niacinamide` |
| jenis_bpom | tidak | Jenis/bentuk produk dari hasil cek BPOM |
| bpom_dicek_tanggal | tidak | Tanggal nomor dicek di cekbpom.pom.go.id, `YYYY-MM-DD`. Kosong = belum terverifikasi |
| sumber_url | tidak | Halaman resmi merek tempat data diambil |
| diambil_tanggal | tidak | `YYYY-MM-DD` |
| catatan | tidak | Bebas |

Yang ditolak otomatis: nomor bukan notifikasi kosmetik, riasan (lipstik, bedak, maskara, foundation, dll.), rambut, tubuh, parfum, kuku, pasta gigi, bahan aktif kosong, dan nomor BPOM dobel.

Cek nomor BPOM satu per satu lewat halaman pencarian resmi cekbpom.pom.go.id. Situs itu memblokir crawler AI di `robots.txt` dan tidak punya API resmi, jadi jangan diambil massal.

Prioritas pencarian produk: caffeine (kantung mata) dan retinol, bakuchiol, atau peptide (kerutan), karena datanya masih sedikit.
