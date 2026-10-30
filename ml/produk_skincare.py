"""Saring dan validasi data produk skincare wajah (DB-03/DB-04) dari CSV kurasi tim, lalu siapkan impor.

Isi ml/data/produk.csv mengikuti ml/data/produk_template.csv (pemisah koma atau titik koma, dari Excel juga bisa).
Jalankan dari root repo: python -m ml.produk_skincare [ml/data/produk.csv]
Hasil di folder yang sama: produk_bersih.csv, produk_ditolak.csv (dengan alasan), produk_tambahan.sql (untuk Backend).

Yang diterima hanya skincare wajah: nomor notifikasi kosmetik BPOM (N + A-E + 11 angka), bukan riasan/rambut/
tubuh/parfum/kuku/mulut, kategori salah satu dari CATEGORIES, dan bahan aktif terisi (dipakai rekomendasi produk).
"""
import csv, os, re, sqlite3, sys
from collections import Counter
from datetime import date

from services.ingredients import conditions_of

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLUMNS = ['nama', 'merek', 'kategori', 'deskripsi', 'harga', 'nomor_bpom', 'bahan_aktif',
           'jenis_bpom', 'bpom_dicek_tanggal', 'sumber_url', 'diambil_tanggal', 'catatan']
CONDITIONS = ['jerawat', 'komedo', 'pori', 'kerutan', 'kemerahan', 'flek', 'kantung_mata',
              'kusam', 'berminyak', 'kering', 'kombinasi', 'normal']

# Bukan skincare wajah. Dicek lebih dulu: "maskara" jangan sampai terbaca "mask".
EXCLUDE = re.compile(r'\b(' + '|'.join([
    r'lip ?(stick|tint|cream|matte|gloss|liner)', r'lipstik', r'bedak', r'(loose|compact|two way) powder', r'foundation',
    r'cushion', r'\b[bc]c cream', r'concealer', r'primer', r'mas[ck]ara', r'eye ?liner', r'eye ?shadow', r'pensil alis',
    r'eyebrow', r'blush', r'perona', r'highlighter', r'contour', r'setting spray',
    r'shampoo', r'sampo', r'hair', r'rambut', r'conditioner',
    r'body (lotion|wash|serum|scrub|butter|cream|mist|oil|spray)', r'sabun mandi', r'lulur', r'hand (cream|& body|and body)',
    r'deodoran', r'deodorant', r'antiperspirant', r'parfum', r'perfume', r'eau de', r'cologne',
    r'kuku', r'nail', r'kutek', r'pasta gigi', r'toothpaste', r'mouthwash', r'obat kumur', r'foot', r'kaki', r'kewanitaan',
]) + r')')

# Urutan penting: yang lebih spesifik dulu ("Sunscreen Serum" = sunscreen, "Clay Cleanser" = cleanser)
CATEGORIES = {
    'sunscreen': r'sunscreen|sunblock|sun screen|tabir surya|\bspf\b|\buv\b',
    'cleanser': r'cleans|face wash|facial wash|facial foam|pembersih|sabun (wajah|muka)|micellar|foaming',
    'exfoliant': r'exfoliat|peeling|scrub|gommage',
    'mask': r'mask|masker',
    'toner': r'toner|essence|face mist|facial mist|facial spray',
    'serum': r'serum|ampoule|ampul|booster|spot|concentrate',
    'moisturizer': r'moisturi[sz]er|pelemba[bp]|cream|krim|\bgel\b|lotion|emulsion',
}
BPOM = re.compile(r'N[A-E]\d{11}')


def detect_category(text):
    return next((cat for cat, pat in CATEGORIES.items() if re.search(pat, text)), None)


def read_rows(path):
    with open(path, encoding='utf-8-sig', newline='') as f:
        sample = f.read(4096)
        f.seek(0)
        dialect = csv.Sniffer().sniff(sample, delimiters=',;')
        return list(csv.DictReader(f, dialect=dialect))


def existing_bpom():
    """Nomor BPOM yang sudah ada di seed_data.sql, supaya tidak dobel."""
    db = sqlite3.connect(':memory:')
    for name in ('schema.sql', 'seed_data.sql'):
        db.executescript(open(os.path.join(ROOT, 'database', name), encoding='utf-8').read())
    return {n for (n,) in db.execute('SELECT bpom_number FROM products')}


def check(row, seen):
    """(produk siap impor, None) atau (None, alasan ditolak)."""
    r = {k: (row.get(k) or '').strip() for k in COLUMNS}
    text = f"{r['nama']} {r['jenis_bpom']}".lower()
    nomor = re.sub(r'[\s.\-]', '', r['nomor_bpom']).upper()
    if not BPOM.fullmatch(nomor):
        return None, f'nomor BPOM "{r["nomor_bpom"]}" bukan notifikasi kosmetik (N + A-E + 11 angka)'
    if nomor in seen:
        return None, 'nomor BPOM sudah ada (dobel atau sudah di seed_data.sql)'
    if m := EXCLUDE.search(text):
        return None, f'bukan skincare wajah ("{m.group(0)}")'
    kategori = r['kategori'].lower() or detect_category(text)
    if kategori not in CATEGORIES:
        return None, f'kategori "{r["kategori"] or "?"}" tidak dikenal; isi salah satu: {", ".join(CATEGORIES)}'
    if not r['nama'] or not r['merek']:
        return None, 'nama atau merek kosong'
    bahan = [b.strip() for b in r['bahan_aktif'].replace(';', ',').split(',') if b.strip()]
    if not bahan:
        return None, 'bahan aktif kosong (wajib untuk rekomendasi produk)'
    harga = re.sub(r'\D', '', r['harga'].split(',')[0])
    if not harga or int(harga) <= 0:
        return None, f'harga "{r["harga"]}" tidak valid'
    dicek = r['bpom_dicek_tanggal']
    if dicek:
        try:
            date.fromisoformat(dicek)
        except ValueError:
            return None, f'bpom_dicek_tanggal "{dicek}" harus YYYY-MM-DD'
    seen.add(nomor)
    return {'name': r['nama'], 'brand': r['merek'], 'category': kategori,
            'description': r['deskripsi'] or r['nama'], 'price': int(harga), 'bpom_number': nomor,
            'bpom_verified': int(bool(dicek)), 'active_ingredients': ', '.join(bahan)}, None


def sql_value(v):
    return str(v) if isinstance(v, int) else "'" + v.replace("'", "''") + "'"


def main(path):
    rows = read_rows(path)
    seen = existing_bpom()
    ok, rejected = [], []
    for i, row in enumerate(rows, start=2):  # baris 1 = header
        product, why = check(row, seen)
        if product:
            ok.append(product)
        else:
            rejected.append({**row, 'baris': i, 'alasan': why})

    out = os.path.dirname(os.path.abspath(path))
    if ok:
        with open(os.path.join(out, 'produk_bersih.csv'), 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(ok[0]))
            w.writeheader()
            w.writerows(ok)
        cols = list(ok[0])
        with open(os.path.join(out, 'produk_tambahan.sql'), 'w', encoding='utf-8') as f:
            f.write(f'-- Dibuat ml/produk_skincare.py dari {os.path.basename(path)}, {date.today()}\n')
            f.write(f'INSERT INTO products ({", ".join(cols)}) VALUES\n')
            f.write(',\n'.join('(' + ', '.join(sql_value(p[c]) for c in cols) + ')' for p in ok) + ';\n')
    with open(os.path.join(out, 'produk_ditolak.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['baris', 'alasan'] + COLUMNS, extrasaction='ignore')
        w.writeheader()
        w.writerows(rejected)

    print(f'{len(rows)} baris: {len(ok)} diterima, {len(rejected)} ditolak')
    for why, n in Counter(r['alasan'].split(' (')[0].split('"')[0] for r in rejected).most_common():
        print(f'  ditolak {n}x: {why}')
    print('per kategori:', dict(Counter(p['category'] for p in ok)))
    print(f"BPOM sudah dicek: {sum(p['bpom_verified'] for p in ok)}/{len(ok)}")
    cover = Counter(c for p in ok for c in {c for b in p['active_ingredients'].split(', ') for c in conditions_of(b)})
    print('produk per kondisi:', ', '.join(f'{c} {cover[c]}' for c in CONDITIONS))
    if thin := [c for c in CONDITIONS if cover[c] < 3]:
        print('  kurang dari 3 produk, cari lagi:', ', '.join(thin))
    unknown = Counter(b for p in ok for b in p['active_ingredients'].split(', ') if not conditions_of(b))
    if unknown:
        print('bahan belum ada di services/ingredients.py (tambahkan kalau relevan):',
              ', '.join(f'{b} ({n})' for b, n in unknown.most_common(15)))
    print(f'hasil: {out}')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'ml', 'data', 'produk.csv'))
