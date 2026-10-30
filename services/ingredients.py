"""Pemetaan bahan aktif skincare wajah -> kondisi kulit WajahKu. Dirawat ML Engineer.

Dipakai rekomendasi produk (BE-07) dan validasi data produk (ml/produk_skincare.py).
Kunci = pola regex, dicocokkan ke tiap bahan di kolom active_ingredients (huruf kecil). Pakai \\b untuk
singkatan pendek: tanpa itu `pha` ikut cocok dengan "alpha arbutin".
Sumber: pengetahuan umum kandungan kosmetik, belum ditinjau ahli. Bukan saran medis.
"""
import re

INGREDIENT_CONDITIONS = {
    # Jerawat, komedo, minyak
    r'salicylic|\bbha\b|beta hydroxy': ['jerawat', 'komedo', 'pori', 'berminyak'],
    r'tea tree|melaleuca': ['jerawat', 'berminyak'],
    r'azelaic': ['jerawat', 'kemerahan', 'flek'],
    r'sulfur|sulphur': ['jerawat', 'berminyak'],
    r'zinc pca|zinc gluconate': ['berminyak', 'jerawat'],
    r'propolis': ['jerawat', 'kemerahan'],
    r'witch hazel|hamamelis': ['berminyak', 'pori'],
    r'clay|kaolin|bentonite|charcoal': ['berminyak', 'pori', 'komedo'],
    r'green tea|camellia sinensis': ['berminyak', 'kemerahan'],
    # Pori, kusam, eksfoliasi
    r'niacinamide': ['pori', 'kemerahan', 'flek', 'berminyak', 'kombinasi'],
    r'\baha\b|glycolic|lactic|mandelic': ['kusam', 'komedo', 'flek'],
    r'\bpha\b|gluconolactone|lactobionic': ['kusam'],
    r'galactomyces|ferment': ['kusam'],
    # Flek dan warna kulit
    r'vitamin c|ascorbic|ascorbyl': ['flek', 'kusam'],
    r'arbutin': ['flek'],
    r'tranexamic': ['flek'],
    r'kojic': ['flek'],
    r'licorice|glycyrrhiza': ['flek', 'kemerahan'],
    # Kerutan
    r'retinol|retinal|retinoid|retinyl': ['kerutan', 'flek'],
    r'bakuchiol': ['kerutan'],
    r'peptide': ['kerutan'],
    r'adenosine': ['kerutan'],
    # Kantung mata
    r'caffeine|kafein': ['kantung_mata'],
    # Kemerahan dan skin barrier
    r'centella|cica|madecassoside|asiaticoside': ['kemerahan', 'jerawat'],
    r'ceramide': ['kering', 'kemerahan'],
    r'panthenol|vitamin b5|\bb5\b': ['kering', 'kemerahan'],
    r'allantoin': ['kemerahan', 'kering'],
    r'aloe': ['kemerahan', 'kering'],
    r'mugwort|artemisia': ['kemerahan'],
    r'snail': ['kering', 'kemerahan'],
    # Hidrasi
    r'hyaluronic|hyaluronate': ['kering', 'normal', 'kombinasi'],
    r'squalane': ['kering'],
    r'urea': ['kering'],
}


def conditions_of(ingredient):
    """Kondisi yang cocok untuk satu nama bahan, mis. 'Salicylic Acid 2%' -> ['jerawat', ...]."""
    text = ingredient.lower()
    found = []
    for pattern, conds in INGREDIENT_CONDITIONS.items():
        if re.search(pattern, text):
            found += [c for c in conds if c not in found]
    return found


if __name__ == '__main__':
    assert conditions_of('Salicylic Acid 2%')[0] == 'jerawat'
    assert conditions_of('Alpha Arbutin') == ['flek']  # bukan 'kusam' dari \bpha\b
    assert conditions_of('Zinc Oxide') == []  # tabir surya, bukan zinc PCA
    assert conditions_of('Caffeine') == ['kantung_mata']
    assert conditions_of('Glycerin') == []
    print('ok')
