import { useEffect, useState, useCallback } from 'react';
import api from '../../services/api';
import Modal from '../../components/common/Modal';
import './ProductManagement.css';

const ProductManagement = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  const fetchProducts = useCallback(async () => {
    try {
      const { data } = await api.get('/admin/products');
      setProducts(data);
    } catch (err) {
      console.error('Error fetching products:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  const handleEdit = (product) => {
    setEditingProduct(product);
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (!confirm('Yakin ingin menghapus produk ini?')) return;

    try {
      await api.delete(`/admin/products/${id}`);
      fetchProducts();
    } catch {
      alert('Gagal menghapus produk');
    }
  };

  const handleSubmit = async (formData) => {
    try {
      if (editingProduct) {
        await api.put(`/admin/products/${editingProduct.id}`, formData);
      } else {
        await api.post('/admin/products', formData);
      }
      setShowModal(false);
      setEditingProduct(null);
      fetchProducts();
    } catch {
      alert('Gagal menyimpan produk');
    }
  };

  const filteredProducts = products.filter(p =>
    p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.brand.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return <div className="loading-container"><div className="spinner"></div></div>;
  }

  return (
    <div className="product-management">
      <div className="page-header">
        <h1>Manajemen Produk</h1>
        <button
          onClick={() => {
            setEditingProduct(null);
            setShowModal(true);
          }}
          className="btn-primary"
        >
          + Tambah Produk
        </button>
      </div>

      <div className="search-bar">
        <input
          type="text"
          placeholder="Cari produk..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      <div className="products-table">
        <table>
          <thead>
            <tr>
              <th>Nama Produk</th>
              <th>Brand</th>
              <th>Kategori</th>
              <th>Harga</th>
              <th>BPOM</th>
              <th>Review</th>
              <th>Aksi</th>
            </tr>
          </thead>
          <tbody>
            {filteredProducts.map((product) => (
              <tr key={product.id}>
                <td><strong>{product.name}</strong></td>
                <td>{product.brand}</td>
                <td>{product.category}</td>
                <td>Rp {product.price.toLocaleString('id-ID')}</td>
                <td><span className="bpom-badge">{product.bpom_number}</span></td>
                <td>{product.review_count} review</td>
                <td>
                  <div className="action-buttons">
                    <button onClick={() => handleEdit(product)} className="btn-edit">Edit</button>
                    <button onClick={() => handleDelete(product.id)} className="btn-delete">Hapus</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <ProductModal
          product={editingProduct}
          onClose={() => {
            setShowModal(false);
            setEditingProduct(null);
          }}
          onSubmit={handleSubmit}
        />
      )}
    </div>
  );
};

const ProductModal = ({ product, onClose, onSubmit }) => {
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

  return (
    <Modal onClose={onClose}>
      <h2>{product ? 'Edit Produk' : 'Tambah Produk'}</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Nama Produk</label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label>Brand</label>
          <input
            type="text"
            name="brand"
            value={formData.brand}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label>Kategori</label>
          <select name="category" value={formData.category} onChange={handleChange} required>
            <option value="cleanser">Cleanser</option>
            <option value="toner">Toner</option>
            <option value="serum">Serum</option>
            <option value="moisturizer">Moisturizer</option>
            <option value="sunscreen">Sunscreen</option>
            <option value="mask">Mask</option>
            <option value="exfoliant">Exfoliant</option>
          </select>
        </div>

        <div className="form-group">
          <label>Deskripsi</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            rows="3"
            required
          />
        </div>

        <div className="form-group">
          <label>Harga</label>
          <input
            type="number"
            name="price"
            value={formData.price}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label>Nomor BPOM</label>
          <input
            type="text"
            name="bpom_number"
            value={formData.bpom_number}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label>Bahan Aktif</label>
          <input
            type="text"
            name="active_ingredients"
            value={formData.active_ingredients}
            onChange={handleChange}
          />
        </div>

        <div className="modal-actions">
          <button type="button" onClick={onClose} className="btn-secondary">
            Batal
          </button>
          <button type="submit" className="btn-primary">
            Simpan
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default ProductManagement;
