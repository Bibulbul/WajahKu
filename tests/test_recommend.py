import os
import sqlite3

from services.recommend import reasons, recommend_products

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database')


def seed_products():
    """Produk seed_data.sql dengan avg_rating, dimuat ke database di memori."""
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    for name in ('schema.sql', 'seed_data.sql'):
        with open(os.path.join(DB_DIR, name), encoding='utf-8') as f:
            conn.executescript(f.read())
    rows = conn.execute("""
        SELECT p.*, COUNT(pr.id) as review_count, COALESCE(AVG(pr.rating), 0) as avg_rating
        FROM products p LEFT JOIN product_reviews pr ON p.id = pr.product_id
        GROUP BY p.id
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


PRODUCTS = seed_products()


def check(conditions):
    picked = recommend_products(PRODUCTS, conditions)
    assert len(picked) == 6 and len({p['id'] for p in picked}) == 6, conditions
    assert any(p['category'] == 'sunscreen' for p in picked), conditions
    return picked


def test_acne_first():
    top = check(['jerawat'])[0]
    assert 'jerawat' in [r['condition'] for r in top['reasons']], top


def test_scenarios():
    for conditions in (['berminyak', 'jerawat'], ['kering', 'kerutan', 'flek'], ['normal', 'kantung_mata'],
                       [], ['jenis_belum_pasti'], ['komedo', 'pori']):
        check(conditions)


def test_same_result_every_time():
    ids = lambda: [p['id'] for p in recommend_products(PRODUCTS, ['kering', 'flek'])]
    assert ids() == ids()


def test_word_match_only():
    # pha tidak boleh cocok dengan "alpha arbutin"
    assert reasons({'active_ingredients': 'Alpha Arbutin'}, {'kusam'}) == []
    assert reasons({'active_ingredients': 'PHA, Niacinamide'}, {'kusam'}) == \
        [{'condition': 'kusam', 'ingredient': 'PHA'}]


if __name__ == '__main__':
    test_acne_first(); test_scenarios(); test_same_result_every_time(); test_word_match_only()
    print('ok')
