// Kategori produk di database masih bahasa Inggris (nilai yang disimpan tetap sama)
export const CATEGORIES = {
  cleanser: 'Pembersih',
  toner: 'Toner',
  serum: 'Serum',
  moisturizer: 'Pelembap',
  sunscreen: 'Tabir surya',
  mask: 'Masker',
  exfoliant: 'Eksfoliator',
};

export const formatPrice = new Intl.NumberFormat('id-ID', {
  style: 'currency',
  currency: 'IDR',
  maximumFractionDigits: 0,
});
