"""Uji simulasi kuesioner jenis kulit pada 200 foto berlabel (xlsx di datasets/skin_type_classification_dataset).

Belum ada data jawaban kuesioner dari orang sungguhan. Jadi jawaban disimulasikan dari skor 0-5 yang diberi anotator
untuk tiap foto (minyak berlebih, dehidrasi, pori terbuka), lalu hasil kuesioner dibandingkan dengan label jenis kulit foto.
Aturan pemetaan di bawah ditetapkan sebelum melihat hasil dan tidak disetel ulang.

Jalankan: python -m ml.eval_skin_quiz
"""
import glob, os, re, zipfile
from collections import Counter
from xml.etree import ElementTree as ET

from services.classifier import skin_type_from_quiz

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # root repo, skrip ini ada di ml/
NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
LABELS = {'oily': 'berminyak', 'dry': 'kering', 'normal': 'normal'}


def xlsx_rows(path):
    z = zipfile.ZipFile(path)
    shared = [''.join(t.text or '' for t in si.iter(NS + 't')) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).iter(NS + 'si')]
    rows = []
    for r in ET.fromstring(z.read('xl/worksheets/sheet1.xml')).iter(NS + 'row'):
        rows.append({re.match(r'[A-Z]+', c.get('r')).group(): shared[int(c.find(NS + 'v').text)] if c.get('t') == 's' else c.find(NS + 'v').text
                     for c in r.iter(NS + 'c') if c.find(NS + 'v') is not None})
    head = rows[0]
    return [{head[k]: v for k, v in r.items()} for r in rows[1:] if r.get('B')]


def simulated_answers(r):
    """Skor anotator 0-5 -> indeks pilihan di QUIZ (services/classifier.py)."""
    oil, dry, pores = (int(r[k]) for k in ('Excessive oil (0-5)', 'Dehydration (0-5)(5 very dehydrated)', 'Open pores (0-5)'))
    q1 = 3 if oil >= 4 else 2 if oil >= 2 else 0 if dry >= 4 else 1  # 2 jam setelah cuci muka
    q2 = 2 if oil >= 4 else 1 if oil >= 2 else 0                     # mengilap siang hari
    q3 = 0 if dry >= 4 else 1 if dry == 3 else 2                      # mengelupas
    q4 = 2 if pores >= 4 else 1 if pores >= 2 else 0                  # pori terlihat
    return [q1, q2, q3, q4]


if __name__ == '__main__':
    files = sorted(glob.glob(os.path.join(ROOT, 'datasets', 'skin_type_classification_dataset', '*.xlsx')))
    rows = [r for f in files for r in xlsx_rows(f)]
    pairs = [(LABELS[r['Image_ID'].split('_')[0]], skin_type_from_quiz(simulated_answers(r))) for r in rows]
    names = ['berminyak', 'kering', 'normal', 'kombinasi']
    print(f'{len(pairs)} foto | akurasi {sum(a == b for a, b in pairs) / len(pairs):.3f} | tebak kelas terbanyak '
          f'{max(Counter(a for a, _ in pairs).values()) / len(pairs):.3f}')
    for a in names[:3]:
        got = Counter(b for x, b in pairs if x == a)
        print(f'  label {a:9s} (n={sum(got.values())}) -> ' + ', '.join(f'{b} {got[b]}' for b in names) +
              f' | recall {got[a] / sum(got.values()):.2f}')
