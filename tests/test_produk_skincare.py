import csv, os, tempfile

from ml.produk_skincare import check, detect_category, read_rows


def row(**kw):
    base = {'nama': 'Acne Face Wash', 'merek': 'Contoh', 'harga': 'Rp 35.000', 'nomor_bpom': 'NA18201299999',
            'bahan_aktif': 'Salicylic Acid, Tea Tree'}
    return {**base, **kw}


def test_rules():
    p, why = check(row(), set())
    assert why is None and p['category'] == 'cleanser' and p['price'] == 35000 and p['bpom_verified'] == 0, why
    assert check(row(nama='Matte Lip Cream'), set())[1].startswith('bukan skincare')
    assert check(row(nama='Volume Maskara'), set())[1].startswith('bukan skincare')  # bukan "mask"
    assert check(row(nama='Tea Tree Face Wash', merek='The Body Shop'), set())[1] is None  # merek tidak ikut dicek
    assert check(row(nama='Body Lotion SPF 30'), set())[1].startswith('bukan skincare')
    assert check(row(nomor_bpom='MD 123456789012'), set())[1].startswith('nomor BPOM')
    assert check(row(bahan_aktif=''), set())[1].startswith('bahan aktif kosong')
    assert check(row(bpom_dicek_tanggal='30/10/2026'), set())[1].startswith('bpom_dicek_tanggal')
    assert check(row(bpom_dicek_tanggal='2026-10-30'), set())[0]['bpom_verified'] == 1
    seen = set()
    check(row(), seen)
    assert check(row(nomor_bpom='NA 1820 1299 999'), seen)[1].startswith('nomor BPOM sudah ada')


def test_categories():
    assert detect_category('holyshield sunscreen serum spf 50') == 'sunscreen'
    assert detect_category('clear pore clay cleanser') == 'cleanser'
    assert detect_category('hydra bomb sleeping mask') == 'mask'
    assert detect_category('hydrating treatment essence') == 'toner'
    assert detect_category('acne spot treatment gel') == 'serum'
    assert detect_category('soothing aloe vera gel') == 'moisturizer'
    assert detect_category('eye cream caffeine') == 'moisturizer'


def test_excel_semicolon_csv():
    with tempfile.NamedTemporaryFile('w', suffix='.csv', delete=False, encoding='utf-8-sig', newline='') as f:
        f.write('nama;merek;harga;nomor_bpom;bahan_aktif\nAcne Face Wash;Contoh;35000;NA18201299999;Salicylic Acid\n')
    try:
        rows = read_rows(f.name)
        assert rows[0]['merek'] == 'Contoh' and check(rows[0], set())[1] is None
    finally:
        os.remove(f.name)


if __name__ == '__main__':
    test_rules(); test_categories(); test_excel_semicolon_csv()
    print('ok')
