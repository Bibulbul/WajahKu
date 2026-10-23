import { useEffect, useId, useState, useCallback } from 'react';
import api from '../../services/api';
import Modal from '../../components/common/Modal';
import { CATEGORIES, formatPrice } from '../../constants/products';
import './ProductManagement.css';

const ProductManagement = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  // { type: 'form', product } untuk tambah/edit, { type: 'delete', product } untuk hapus
  const [dialog, setDialog] = useState(null);
  const [busy, setBusy] = useState(false);
  const [dialogError, setDialogError] = useState('');
  const [notice, setNotice] = useState('');

  const fetchProducts = useCallback(async () => {
    try {
      const { data } = await api.get('/admin/products');
      setProducts(data);
      setLoadError(false);
    } catch (err) {
      console.error('Error fetching products:', err);
      setLoadError(true);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  const openDialog = (next) => {
    setDialog(next);
    setDialogError('');
    setNotice('');
  };

  const closeDialog = () => {
    if (!busy) setDialog(null);
  };

  const handleDelete = async (product) => {
    setBusy(true);
    try {
      await api.delete(`/admin/products/${product.id}`);
      setDialog(null);
      setNotice(`"${product.name}" dihapus.`);
      fetchProducts();
    } catch (err) {
      setDialogError(err.response?.data?.error || 'Produk belum bisa dihapus. Coba lagi.');
    } finally {
      setBusy(false);
    }
  };

  const handleSubmit = async (formData) => {
    const editing = dialog?.product;
    setBusy(true);
    setDialogError('');
    try {
      if (editing) {
        await api.put(`/admin/products/${editing.id}`, formData);
      } else {
        await api.post('/admin/products', formData);
      }
      setDialog(null);
      setNotice(editing ? `"${formData.name}" diperbarui.` : `"${formData.name}" ditambahkan.`);
      fetchProducts();
    } catch (err) {
      setDialogError(err.response?.data?.error || 'Produk belum bisa disimpan. Coba lagi.');
    } finally {
      setBusy(false);
    }
  };

  const retry = () => {
    setLoading(true);
    fetchProducts();
  };

  const query = searchTerm.trim().toLowerCase();
  const filteredProducts = products.filter(
    (p) => p.name.toLowerCase().includes(query) || p.brand.toLowerCase().includes(query)
  );

  return (
    <div className="product-management">
      <header className="pm-header">
        <div>
          <h1>Produk</h1>
          {!loading && !loadError && <p className="pm-count">{products.length} produk di katalog</p>}
        </div>
        <button type="button" onClick={() => openDialog({ type: 'form', product: null })} className="btn-primary pm-button">
          Tambah produk
        </button>
      </header>

      <p className="pm-notice" aria-live="polite">{notice}</p>

      {loading && (
        <div className="pm-placeholder" role="status">
          <span className="pm-sr-only">Memuat produk…</span>
        </div>
      )}

      {!loading && loadError && (
        <div className="pm-message">
          <p>Daftar produk belum bisa dimuat. Periksa koneksi lalu coba lagi.</p>
          <button type="button" className="btn-secondary pm-button" onClick={retry}>Coba lagi</button>
        </div>
      )}

      {!loading && !loadError && (
        <>
          <div className="pm-search">
            <label htmlFor="pm-search" className="pm-sr-only">Cari produk</label>
            <input
              id="pm-search"
              type="search"
              placeholder="Cari nama atau merek"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          {filteredProducts.length === 0 ? (
            <p className="pm-empty">
              {products.length === 0
                ? 'Belum ada produk. Tambahkan produk pertama.'
                : `Tidak ada produk yang cocok dengan "${searchTerm.trim()}".`}
            </p>
          ) : (
            <div className="pm-table-wrap" tabIndex={0} role="region" aria-label="Tabel produk, bisa digeser">
              <table className="pm-table">
                <thead>
                  <tr>
                    <th scope="col">Produk</th>
                    <th scope="col">Kategori</th>
                    <th scope="col" className="is-number">Harga</th>
                    <th scope="col">BPOM</th>
                    <th scope="col" className="is-number">Ulasan</th>
                    <th scope="col"><span className="pm-sr-only">Aksi</span></th>
                  </tr>
                </thead>
                <tbody>
                  {filteredProducts.map((product) => (
                    <tr key={product.id}>
                      <td>
                        <strong>{product.name}</strong>
                        <span className="pm-brand">{product.brand}</span>
                      </td>
                      <td>{CATEGORIES[product.category] ?? product.category}</td>
                      <td className="is-number">{formatPrice.format(product.price)}</td>
                      <td><span className="pm-bpom">{product.bpom_number}</span></td>
                      <td className="is-number">{product.review_count}</td>
                      <td>
                        <div className="pm-actions">
                          <button
                            type="button"
                            onClick={() => openDialog({ type: 'form', product })}
                            className="pm-action"
                            aria-label={`Edit ${product.name}`}
                          >
                            Edit
                          </button>
                          <button
                            type="button"
                            onClick={() => openDialog({ type: 'delete', product })}
                            className="pm-action is-danger"
                            aria-label={`Hapus ${product.name}`}
                          >
                            Hapus
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}

      {dialog?.type === 'form' && (
        <ProductModal
          product={dialog.product}
          busy={busy}
          error={dialogError}
          onClose={closeDialog}
          onSubmit={handleSubmit}
        />
      )}

      {dialog?.type === 'delete' && (
        <Modal title="Hapus produk?" onClose={closeDialog}>
          <p className="pm-dialog-text">
            &ldquo;{dialog.product.name}&rdquo;
            {dialog.product.review_count > 0 && ` beserta ${dialog.product.review_count} ulasannya`} akan
            dihapus permanen dan tidak bisa dikembalikan.
          </p>
          <p className="pm-dialog-error" aria-live="polite">{dialogError}</p>
          <div className="pm-dialog-actions">
            <button type="button" onClick={closeDialog} className="btn-secondary pm-button" disabled={busy}>
              Batal
            </button>
            <button
              type="button"
              onClick={() => handleDelete(dialog.product)}
              className="pm-button pm-danger"
              disabled={busy}
            >
              {busy ? 'Menghapus…' : 'Hapus produk'}
            </button>
          </div>
        </Modal>
      )}
    </div>
  );
};

const ProductModal = ({ product, busy, error, onClose, onSubmit }) => {
  const id = useId();
  const [formData, setFormData] = useState({
    name: product?.name || '',
    brand: product?.brand || '',
    category: product?.category || 'cleanser',
    description: product?.description || '',
    price: product?.price || '',
    bpom_number: product?.bpom_number || '',
    active_ingredients: product?.active_ingredients || '',
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const field = (name) => ({ id: `${id}-${name}`, name, value: formData[name], onChange: handleChange });

  return (
    <Modal title={product ? 'Edit produk' : 'Tambah produk'} onClose={onClose}>
      <form onSubmit={handleSubmit} className="pm-form">
        <div className="form-group">
          <label htmlFor={`${id}-name`}>Nama produk</label>
          <input type="text" required {...field('name')} />
        </div>

        <div className="pm-form-row">
          <div className="form-group">
            <label htmlFor={`${id}-brand`}>Merek</label>
            <input type="text" required {...field('brand')} />
          </div>

          <div className="form-group">
            <label htmlFor={`${id}-category`}>Kategori</label>
            <select required {...field('category')}>
              {Object.entries(CATEGORIES).map(([value, text]) => (
                <option key={value} value={value}>{text}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor={`${id}-description`}>Deskripsi</label>
          <textarea rows="3" required {...field('description')} />
        </div>

        <div className="pm-form-row">
          <div className="form-group">
            <label htmlFor={`${id}-price`}>Harga (Rp)</label>
            <input type="number" min="0" inputMode="numeric" required {...field('price')} />
          </div>

          <div className="form-group">
            <label htmlFor={`${id}-bpom_number`}>Nomor BPOM</label>
            <input type="text" required {...field('bpom_number')} />
          </div>
        </div>

        <div className="form-group">
          <label htmlFor={`${id}-active_ingredients`}>Bahan aktif (opsional)</label>
          <input type="text" placeholder="Misalnya Niacinamide, Centella" {...field('active_ingredients')} />
        </div>

        <p className="pm-dialog-error" aria-live="polite">{error}</p>

        <div className="pm-dialog-actions">
          <button type="button" onClick={onClose} className="btn-secondary pm-button" disabled={busy}>
            Batal
          </button>
          <button type="submit" className="btn-primary pm-button" disabled={busy}>
            {busy ? 'Menyimpan…' : 'Simpan produk'}
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default ProductManagement;
