"""Pilih ambang Model B v2 di level WAJAH (aplikasi mengambil skor tertinggi dari 7 area, bukan satu patch).

Label wajah = kelas yang ada di salah satu dari 7 patch-nya. Ambang dipilih di wajah validasi (F1 terbaik),
lalu dinilai di wajah test. Hasil ditambahkan ke models/skin_issue_v2.json ("face_thresholds") dan laporan.
Jalankan: C:/wjx/Scripts/python tune_face_thresholds_v2.py   (setelah train_skin_issue_v2.py)
"""
import json, os
from collections import defaultdict

import numpy as np
import onnxruntime as ort
from PIL import Image
from sklearn.metrics import f1_score, precision_score, recall_score

from services.face import REGIONS_V2
from train_skin_issue_v2 import CLASSES, OUT, build_cache, split

cfg_path = os.path.join(OUT, 'skin_issue_v2.json')
cfg = json.load(open(cfg_path, encoding='utf-8'))
sess = ort.InferenceSession(os.path.join(OUT, 'skin_issue_v2.onnx'), providers=['CPUExecutionProvider'])
M, S = np.array(cfg['mean'], np.float32), np.array(cfg['std'], np.float32)


def faces(items):
    """Skor (maks 7 area) dan label per wajah, hanya foto yang dipotong per area wajah."""
    by = defaultdict(list)
    for it in items:
        by[it['source']].append(it)
    ys, ps = [], []
    for patches in by.values():
        if len(patches) != len(REGIONS_V2):
            continue  # close-up tanpa wajah terdeteksi
        x = np.stack([((np.asarray(Image.open(p['file']).convert('RGB').resize((224, 224), Image.BILINEAR), np.float32) / 255 - M) / S)
                      .transpose(2, 0, 1) for p in patches])
        ps.append((1 / (1 + np.exp(-sess.run(None, {'pixel_values': x})[0]))).max(0))
        ys.append([any(c in p['labels'] for p in patches) for c in CLASSES])
    return np.array(ys), np.array(ps)


_, va, te = split(build_cache())
yv, pv = faces(va)
yt, pt = faces(te)
MIN_POS = 5      # kelas dengan < 5 wajah positif di validasi: F1 tidak bisa dipercaya
MAX_FALSE = 0.10  # untuk kelas itu: ambang terendah yang membuat <= 10% wajah tanpa kondisi tersebut salah terdeteksi
th, rule = [], []
for j in range(len(CLASSES)):
    grid = np.arange(0.3, 0.991, 0.01)
    if yv[:, j].sum() >= MIN_POS:
        th.append(round(float(max((f1_score(yv[:, j], pv[:, j] >= t, zero_division=0), t) for t in grid)[1]), 2)); rule.append('F1')
    else:
        neg = pv[~yv[:, j], j]
        t = float(next(t for t in grid if (neg >= t).mean() <= MAX_FALSE))
        th.append(round(max(t, cfg['thresholds'][j]), 2)); rule.append('maks 10% salah')  # tidak lebih longgar dari ambang patch
th = np.array(th)
pred = pt >= th

lines = ['', f'AMBANG LEVEL WAJAH (maks 7 area): dipilih di {len(yv)} wajah validasi, dinilai di {len(yt)} wajah test',
         'kelas        ambang  aturan          F1     presisi recall  wajah positif (test)']
for j, c in enumerate(CLASSES):
    lines.append(f'{c:12s} {th[j]:.2f}   {rule[j]:15s} {f1_score(yt[:, j], pred[:, j], zero_division=0):.3f}  '
                 f'{precision_score(yt[:, j], pred[:, j], zero_division=0):.3f}   {recall_score(yt[:, j], pred[:, j], zero_division=0):.3f}   {int(yt[:, j].sum())}')
before = (pt >= np.array(cfg['thresholds'])).sum(1).mean()
lines.append(f'rata-rata kondisi terdeteksi per wajah test: {before:.2f} (ambang patch) -> {pred.sum(1).mean():.2f} (ambang wajah); '
             f'label sebenarnya {yt.sum(1).mean():.2f}')
report = '\n'.join(lines)
print(report)

cfg['face_thresholds'] = th.tolist()
json.dump(cfg, open(cfg_path, 'w'), indent=1)
open(os.path.join(OUT, 'skin_issue_v2_report.txt'), 'a', encoding='utf-8').write(report + '\n')
