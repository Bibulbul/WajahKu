# WajahKu
## Database (PostgreSQL)

Backend memakai PostgreSQL. Tabel, produk seed, dan akun uji dibuat otomatis saat server start.

1. Siapkan database kosong, pilih salah satu:
   - Lokal: pasang PostgreSQL, lalu `createdb wajahku`
   - Cloud gratis (Neon/Supabase): buat project, salin connection string-nya
2. Isi `DATABASE_URL` sebelum `python app.py` (default: `postgresql://postgres:postgres@localhost:5432/wajahku`):
   ```
   $env:DATABASE_URL = "postgresql://user:password@host:5432/wajahku"   # PowerShell
   export DATABASE_URL="postgresql://user:password@host:5432/wajahku"   # bash
   ```
3. Test (`python -m pytest`) membuat schema sementara di database yang sama lalu menghapusnya.
   Pakai `TEST_DATABASE_URL` kalau ingin test memakai database lain.

Di server deploy, isi `DATABASE_URL` dari penyedia database bersama `APP_ENV=production`, `SECRET_KEY`, dan `JWT_SECRET_KEY`.
