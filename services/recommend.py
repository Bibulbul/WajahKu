from services.ingredients import conditions_of

ISSUES = {'jerawat', 'komedo', 'pori', 'kerutan', 'kemerahan', 'flek', 'kantung_mata'}
SKIN_TYPES = {'berminyak', 'kering', 'kombinasi', 'normal'}
BASICS = ('cleanser', 'moisturizer', 'sunscreen')


def reasons(product, conditions):
    """[{'condition', 'ingredient'}] untuk kondisi scan yang cocok dengan bahan aktif produk."""
    found = {}
    for part in (product['active_ingredients'] or '').split(','):
        for c in conditions_of(part):
            if c in conditions:
                found.setdefault(c, part.strip())
    return [{'condition': c, 'ingredient': i} for c, i in found.items()]


def recommend_products(products, conditions, limit=6):
    """products: dict produk dengan avg_rating. conditions: conditions_detected scan.
    Skor = 2 x masalah kulit cocok + 1 x jenis kulit cocok; maks 2 per kategori; tabir surya wajib ada."""
    conditions = set(conditions) & (ISSUES | SKIN_TYPES)
    ranked = []
    for p in products:
        r = reasons(p, conditions)
        ranked.append({**p, 'reasons': r, 'score': sum(2 if x['condition'] in ISSUES else 1 for x in r)})
    ranked.sort(key=lambda p: (-p['score'], -p['avg_rating'], p['price']))

    picked, per_category = [], {}
    for p in ranked:
        if p['score'] > 0 and per_category.get(p['category'], 0) < 2 and len(picked) < limit:
            picked.append(p)
            per_category[p['category']] = per_category.get(p['category'], 0) + 1

    # Tabir surya wajib ada, sisa slot diisi pembersih/pelembap/tabir surya ber-rating tertinggi
    basics = sorted((p for p in ranked if p['category'] in BASICS and p not in picked),
                    key=lambda p: (-p['avg_rating'], p['price']))
    sunscreen = next((p for p in basics if p['category'] == 'sunscreen'), None)
    if sunscreen and not any(p['category'] == 'sunscreen' for p in picked):
        picked = picked[:limit - 1] + [sunscreen]
    for p in basics:
        if len(picked) >= limit:
            break
        if p not in picked:
            picked.append(p)
    return picked
