"""Ambil data produk skincare wajah dari situs resmi merek ke ml/data/produk.csv (DB-03).

Izin dicek 30 Oktober dan 6 November 2026 (robots.txt + syarat penggunaan): Scarlett, Avoskin, Facetology, Npure,
MS Glow, dan Implora boleh. Wardah, Emina, Kahf, Garnier, Cetaphil hanya manual; Glad2Glow melarang scraping;
Azarine dan The Originote dilewati.
Yang diambil hanya fakta: nama, jenis produk, harga normal, nomor BPOM, nama bahan aktif. Deskripsi dan foto
tidak disalin. Satu permintaan tiap 10 detik; berhenti kalau situs menolak. Baris yang sudah ada tidak ditimpa.
Nomor BPOM tetap dicek manual di cekbpom.pom.go.id, lalu tanggalnya diisi di kolom bpom_dicek_tanggal.
Jalankan dari root repo: python -m ml.ambil_produk_merek scarlett|avoskin|facetology|npure|msglow|implora
Lanjutkan dengan: python -m ml.produk_skincare
"""
import csv, html, json, os, re, sys, time, urllib.error, urllib.request
from datetime import date

from ml.produk_skincare import COLUMNS, EXCLUDE, ROOT
from services.ingredients import INGREDIENT_CONDITIONS

OUT = os.path.join(ROOT, 'ml', 'data', 'produk.csv')
UA = 'WajahKu-student-project/1.0 (+https://github.com/Bibulbul/WajahKu)'
DELAY = 10
# Paket/set berisi produk satuan yang sudah ada di daftar
SKIP = re.compile(r'\bset\b|package|paket|combo|twin ?pack|triple ?pack|bundl|series|\bkit\b|\bbox\b|travel|deluxe|essentials', re.I)
NOT_FACE = re.compile(r'body|lip|parfum|perfume|fragrance|hair|shampoo|deodor|hand-|loofah|pouch|merch|tote|mirror|voucher', re.I)
ACID = re.compile(r'\s+acid\b', re.I)


def get(url):
    time.sleep(DELAY)
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=30) as r:  # 403/429/5xx -> HTTPError, skrip berhenti
        return r.read().decode('utf-8', errors='replace')


def text(fragment):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', fragment or ''))).strip()


def known_ingredients(txt):
    """Nama bahan aktif yang dikenal services/ingredients.py, dirapikan: 'salicylic' -> 'Salicylic Acid'."""
    found = []
    for pattern in INGREDIENT_CONDITIONS:
        m = re.search(pattern, txt, re.I)
        if not m:
            continue
        name = txt[m.start():m.end()]
        if ACID.match(txt, m.end()):
            name += ' Acid'
        name = ' '.join(w.upper() if len(w) <= 3 else w.capitalize() for w in name.split())
        name = 'Vitamin B5' if name == 'B5' else name
        if name.lower() not in (f.lower() for f in found):
            found.append(name)
    return ', '.join(found)


def bpom_in(txt):
    m = re.search(r'N[A-E]\s?\d{11}', txt)
    return m.group(0).replace(' ', '') if m else ''


def clean_name(name):
    """Judul gaya marketplace -> nama produk: tanpa [NEW]/NEW FORMULA, tanpa keterangan setelah ' - ', ' | ', atau '30ml-AHA'."""
    name = re.sub(r'\[[^\]]*\]|\bnew formula\b|^\s*formula\b|\bnew!?(?=\s)', ' ', name, flags=re.I)
    name = re.split(r'\s[-|]\s|(?<=\w)-(?=[A-Z])', name)[0]
    return re.sub(r'\b(SCARLETT|AVOSKIN|FACETOLOGY)\b', lambda m: m.group(0).capitalize(), re.sub(r'\s+', ' ', name)).strip(' ,')


def row(merek, nama, harga, bpom, bahan, jenis, url, catatan='nomor BPOM dari situs merek, belum dicek di cekbpom'):
    return {'nama': clean_name(nama), 'merek': merek, 'kategori': '', 'deskripsi': '', 'harga': str(harga),
            'nomor_bpom': bpom, 'bahan_aktif': bahan, 'jenis_bpom': jenis, 'bpom_dicek_tanggal': '',
            'sumber_url': url, 'diambil_tanggal': date.today().isoformat(), 'catatan': catatan if bpom else ''}


def sitemap_urls(sitemap, marker):
    urls = sorted(set(re.findall(rf'https?://[^<\s]+{marker}[^<\s]*', get(sitemap))))
    return [u for u in urls if not SKIP.search(u) and not NOT_FACE.search(u) and not EXCLUDE.search(u.replace('-', ' ').lower())]


def next_data(page):
    return json.loads(re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', page, re.S).group(1))['props']['pageProps']


def ld_product(page):
    """Data produk schema.org (ld+json) di halaman."""
    blocks = re.findall(r'<script[^>]*ld\+json[^>]*>(.*?)</script>', page, re.S)
    return next((d for d in map(json.loads, blocks) if d.get('@type') == 'Product'), {})


def scarlett(done):
    for url in sitemap_urls('https://scarlettofficial.id/sitemap.xml', '/product/'):
        if url in done:
            continue
        p = next_data(get(url))['data']
        if (p.get('productCategory') or {}).get('name') != 'Face' or SKIP.search(p['name']):
            yield url, None
            continue
        bahan = ', '.join(i['ingredient']['name'] for i in p.get('productIngredients') or [])
        jenis = ', '.join(t['productType']['name'] for t in p.get('productProductTypes') or [])
        yield url, row('Scarlett', p['name'], p['price'], bpom_in(text(p.get('description'))), bahan, jenis, url)


def avoskin(done):
    for url in sitemap_urls('https://www.avoskinbeauty.com/sitemap-0.xml', '/product/'):
        if url in done:
            continue
        d = (next_data(get(url)).get('dataProduct') or {}).get('data')
        if not d or not d.get('product'):  # produk sudah tidak dijual tapi masih ada di sitemap
            yield url, None
            continue
        p, info = d['product'], {i['title']: text(i['content']) for i in d['product_info']}
        if SKIP.search(p['name']) or NOT_FACE.search(p['name']):
            yield url, None
            continue
        # Bahan yang disorot di deskripsi; daftar komposisi lengkap hanya kalau deskripsi tidak menyebut apa pun
        bahan = known_ingredients(info.get('description', '')) or known_ingredients(info.get('ingredients', ''))
        yield url, row('Avoskin', p['name'], p['price'], bpom_in(' '.join(info.values())), bahan, p.get('categories') or '', url)


def facetology(done):
    for p in json.loads(get('https://facetology.id/wp-json/wc/store/v1/products?per_page=100')):
        url = p['permalink']
        if url in done:
            continue
        pr, txt = p['prices'], text((p.get('description') or '') + ' ' + (p.get('short_description') or ''))
        harga = int(pr['regular_price'] or 0) // 10 ** pr['currency_minor_unit']
        jenis = ', '.join(c['name'] for c in p['categories'])
        yield url, row('Facetology', html.unescape(p['name']), harga, bpom_in(txt), known_ingredients(txt), jenis, url)


def npure(done):
    for url in sitemap_urls('https://npure.co.id/sitemap-products.xml', '/products/'):
        if url in done:
            continue
        page = get(url)
        p, body = ld_product(page), text(page)
        jenis, _, nama = p['name'].rpartition('|')  # 'Facial Wash Anti Jerawat | NPURE Cica Cleanser'
        isi = body[body.find('Reviews'):body.find('Produk Terkait')]  # tanpa menu dan produk terkait
        yield url, row('Npure', nama, '', bpom_in(p.get('sku') or isi), known_ingredients(isi), jenis.strip(), url,
                       'nomor BPOM dari situs merek, belum dicek di cekbpom; harga di situs placeholder, isi manual')


def msglow(done):
    for url in sitemap_urls('https://msglowid.com/sitemap.xml', '/products/'):
        if url in done:
            continue
        p = ld_product(get(url))
        if not p:
            yield url, None
            continue
        desc = text(p.get('description'))
        yield url, row('MS Glow', p['name'], (p.get('offers') or {}).get('price') or '', bpom_in(desc),
                       known_ingredients(desc), '', url)


def implora(done):
    for url in sitemap_urls('https://implora.co.id/sitemap.xml', '/implora-'):
        if url in done or not url.endswith('-en'):  # versi -id isinya sama
            continue
        try:
            page = get(url)
        except urllib.error.HTTPError as e:  # sitemap Implora masih memuat halaman yang sudah dihapus
            if e.code != 404:
                raise
            yield url, None
            continue
        nama = text(re.search(r'<h1[^>]*>(.*?)</h1>', page, re.S).group(1))
        body = text(page)
        isi = body[body.find(nama, body.find('Share')):body.find('You Might Also Like')]
        harga = re.search(r'data-original="IDR ([\d.]+)', page)
        yield url, row('Implora', nama, harga.group(1).replace('.', '') if harga else '', bpom_in(isi),
                       known_ingredients(isi), '', url)


BRANDS = {'scarlett': scarlett, 'avoskin': avoskin, 'facetology': facetology,
          'npure': npure, 'msglow': msglow, 'implora': implora}


def main(brand):
    rows = []
    if os.path.exists(OUT):
        with open(OUT, encoding='utf-8-sig', newline='') as f:
            rows = list(csv.DictReader(f))
    done = {r['sumber_url'] for r in rows}
    added = 0
    for i, (url, r) in enumerate(BRANDS[brand](done), 1):
        if r:
            rows.append(r)
            added += 1
        print(f'{i} {"+ " + r["nama"] if r else "- dilewati (bukan wajah/paket)"}', flush=True)
        with open(OUT, 'w', encoding='utf-8-sig', newline='') as f:  # simpan tiap langkah, aman kalau berhenti
            w = csv.DictWriter(f, fieldnames=COLUMNS)
            w.writeheader()
            w.writerows(rows)
    print(f'selesai: {added} produk {brand} ditambahkan ke {OUT}')


if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] not in BRANDS:
        sys.exit(f'pakai: python -m ml.ambil_produk_merek {"|".join(BRANDS)}')
    main(sys.argv[1])
