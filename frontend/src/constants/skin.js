// Disalin dari TYPE_LABELS dan SKIN_CONDITIONS di services/classifier.py.
// Backend hanya mengirim key di beberapa endpoint, jadi nama tampilan dipegang di sini.
// Perbarui bersama kalau label di classifier.py berubah.
export const SKIN_TYPES = {
  kombinasi: 'Kombinasi',
  kering: 'Kering',
  normal: 'Normal',
  berminyak: 'Berminyak',
  jenis_belum_pasti: 'Belum pasti',
};

export const SKIN_ISSUES = {
  jerawat: 'Jerawat',
  komedo: 'Komedo hitam',
  flek: 'Flek hitam',
  pori: 'Pori-pori besar',
  kusam: 'Kulit kusam',
  kemerahan: 'Kemerahan',
  kerutan: 'Kerutan',
};

// SQLite menyimpan CURRENT_TIMESTAMP dalam UTC tanpa penanda zona
export const parseScanDate = (value) => new Date(`${value.replace(' ', 'T')}Z`);

const relativeTime = new Intl.RelativeTimeFormat('id', { numeric: 'auto' });

export const formatRelative = (date) => {
  const seconds = Math.round((date.getTime() - Date.now()) / 1000);
  const units = [
    ['year', 31536000],
    ['month', 2592000],
    ['week', 604800],
    ['day', 86400],
    ['hour', 3600],
    ['minute', 60],
  ];
  for (const [unit, size] of units) {
    if (Math.abs(seconds) >= size) return relativeTime.format(Math.round(seconds / size), unit);
  }
  return 'baru saja';
};
