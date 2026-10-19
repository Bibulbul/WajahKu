"""Latih detektor jerawat (ML-06): YOLO26n satu kelas dari Skin-Problem-Detection-Relabel-Clean3.

Dataset: Parin Kittipongdaja, Roboflow Universe, CC BY 4.0
(https://universe.roboflow.com/parin-kittipongdaja-vwmn3/skin-problem-detection-relabel-clean3).
Ultralytics YOLO berlisensi AGPL-3.0: hanya dipakai saat training, aplikasi cukup onnxruntime.

Satu salinan per foto asli (Roboflow menyimpan foto yang sama di beberapa split), dibagi ulang 80/10/10
per foto asli. Foto yang dilabeli tapi tanpa kotak jerawat ikut sebagai contoh negatif.
Jalankan: C:/wjx/Scripts/python train_acne_yolo.py
Hasil: models/acne_yolo.onnx, models/acne_yolo.json (ambang), models/acne_yolo_report.txt
"""
import json, os, random, shutil
from collections import Counter, defaultdict

import numpy as np
from PIL import Image
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

from train_skin_issue_v2 import SRC, read_xlsx, source_id

ROOT = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(ROOT, 'datasets', '_yolo_acne')
OUT = os.path.join(ROOT, 'models')
SEED, IMGSZ = 42, 640


def build_dataset():
    """Hardlink foto ke WORK/images/<split> + label YOLO di WORK/labels/<split> (tanpa menyalin isi foto)."""
    best = {}
    for sp in ('train', 'valid', 'test'):
        js = json.load(open(os.path.join(SRC, sp, '_annotations.coco.json'), encoding='utf-8'))
        acne_id = next(c['id'] for c in js['categories'] if c['name'] == 'Acne')
        anns = defaultdict(list)
        for a in js['annotations']:
            anns[a['image_id']].append(a)
        for im in js['images']:
            if not anns[im['id']]:
                continue  # foto tanpa label sama sekali: belum tentu bersih
            boxes = [a['bbox'] for a in anns[im['id']] if a['category_id'] == acne_id]
            sid = source_id(im['file_name'])
            if sid not in best or len(boxes) > len(best[sid][2]):
                best[sid] = (os.path.join(SRC, sp, im['file_name']), (im['width'], im['height']), boxes)
    sources = sorted(best)
    random.Random(SEED).shuffle(sources)
    n = len(sources)
    for i, sid in enumerate(sources):
        sp = 'train' if i < 0.8 * n else 'val' if i < 0.9 * n else 'test'
        path, (W, H), boxes = best[sid]
        name = os.path.splitext(os.path.basename(path))[0]
        for d in ('images', 'labels'):
            os.makedirs(os.path.join(WORK, d, sp), exist_ok=True)
        img = os.path.join(WORK, 'images', sp, name + '.jpg')
        if not os.path.exists(img):
            os.link(path, img)
        with open(os.path.join(WORK, 'labels', sp, name + '.txt'), 'w') as f:
            f.writelines(f'0 {(x + w / 2) / W:.6f} {(y + h / 2) / H:.6f} {w / W:.6f} {h / H:.6f}\n' for x, y, w, h in boxes)
    yaml = os.path.join(WORK, 'data.yaml')
    open(yaml, 'w').write(f'path: {WORK}\ntrain: images/train\nval: images/val\ntest: images/test\nnames:\n  0: acne\n')
    return yaml


def iou(a, b):
    iw, ih = min(a[2], b[2]) - max(a[0], b[0]), min(a[3], b[3]) - max(a[1], b[1])
    inter = max(iw, 0) * max(ih, 0)
    return inter / ((a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter)


def evaluate(split, detect):
    """Presisi/recall (IoU >= 0.5, greedy) dan selisih jumlah per foto, memakai model ONNX yang dipasang di aplikasi."""
    tp = n_pred = n_true = 0
    counts = []
    for name in sorted(os.listdir(os.path.join(WORK, 'images', split))):
        img = Image.open(os.path.join(WORK, 'images', split, name)).convert('RGB')
        W, H = img.size
        rows = [list(map(float, l.split()[1:])) for l in open(os.path.join(WORK, 'labels', split, name[:-4] + '.txt'))]
        gt = [((cx - w / 2) * W, (cy - h / 2) * H, (cx + w / 2) * W, (cy + h / 2) * H) for cx, cy, w, h in rows]
        pred = detect(img)
        used = set()
        for p in sorted(pred, key=lambda b: -b[4]):
            j = max((j for j in range(len(gt)) if j not in used), key=lambda j: iou(p, gt[j]), default=None)
            if j is not None and iou(p, gt[j]) >= 0.5:
                used.add(j); tp += 1
        n_pred += len(pred); n_true += len(gt); counts.append((len(gt), len(pred)))
    P, R = tp / max(n_pred, 1), tp / max(n_true, 1)
    return P, R, 2 * P * R / max(P + R, 1e-9), np.array(counts)


def external_check(detect, crop_face):
    """Jumlah jerawat terdeteksi vs skor Acne 0-5 dari anotator di 200 foto skin_type_classification_dataset."""
    d = os.path.join(ROOT, 'datasets', 'skin_type_classification_dataset')
    n, score, skipped = [], [], 0
    for xlsx, sp in (('skinalaysis_labeling_train1.xlsx', 'train'), ('skinanalysis_valid1.xlsx', 'valid')):
        for r in read_xlsx(os.path.join(d, xlsx))[1:]:
            name = r['B'] if r['B'].endswith('.jpg') else r['B'] + '.jpg'
            if not r.get('C', '').isdigit() or int(r['C']) > 5:
                continue
            try:
                face = crop_face(Image.open(os.path.join(d, sp, name.split('_')[0], name)).convert('RGB'))
            except (ValueError, FileNotFoundError):
                skipped += 1
                continue
            n.append(len(detect(face))); score.append(int(r['C']))
    n, score = np.array(n), np.array(score)
    y = score >= 2
    return '\n'.join([
        f'Cek eksternal: {len(n)} foto skin_type_classification_dataset (dilewati, wajah tidak terdeteksi: {skipped})',
        f'  Spearman jumlah terdeteksi vs skor Acne 0-5: {spearmanr(n, score)[0]:.2f}',
        f'  AUC skor >= 2 (n positif {int(y.sum())}): {roc_auc_score(y, n):.2f} (0.5 = tebakan)',
        '  rata-rata jumlah terdeteksi per skor: ' + ', '.join(f'{s}: {n[score == s].mean():.1f} ({(score == s).sum()} foto)'
                                                          for s in sorted(set(score)))])


def main():
    from ultralytics import YOLO
    yaml = build_dataset()
    os.chdir(WORK)  # bobot awal yolo26n.pt diunduh ke folder kerja, bukan ke root repo
    weights = os.path.join(WORK, 'runs', 'acne', 'weights', 'best.pt')
    if not os.path.exists(weights):  # hapus folder runs/acne untuk melatih ulang
        YOLO('yolo26n.pt').train(data=yaml, imgsz=IMGSZ, epochs=100, patience=20, batch=16, seed=SEED, workers=1,  # RAM 12 GB: tiap worker Windows memuat torch sendiri
                                 project=os.path.join(WORK, 'runs'), name='acne', exist_ok=True)
    best = YOLO(weights)

    t = best.val(data=yaml, split='test', imgsz=IMGSZ)

    onnx = best.export(format='onnx', imgsz=IMGSZ, nms=False)  # keluaran end2end (1, 300, 6): server tidak perlu NMS
    shutil.copy(onnx, os.path.join(OUT, 'acne_yolo.onnx'))
    cfg = os.path.join(OUT, 'acne_yolo.json')
    json.dump({'conf': 0.01, 'imgsz': IMGSZ}, open(cfg, 'w'))

    from services import acne  # baca model yang baru disalin
    from services.face import crop_face

    def val_f1(conf):
        acne._cfg['conf'] = conf
        return evaluate('val', acne.detect_acne)[2]
    # ambang dipilih dari model ONNX (head end2end) di val, dinilai di test
    acne._cfg['conf'] = max(np.arange(0.04, 0.31, 0.02).round(2).tolist(), key=val_f1)
    json.dump(acne._cfg, open(cfg, 'w'), indent=1)
    conf = acne._cfg['conf']
    P, R, F1, c = evaluate('test', acne.detect_acne)
    sev = np.mean([acne.severity(a) == acne.severity(b) for a, b in c])
    (top, k), = Counter(acne.severity(a) for a in c[:, 0]).most_common(1)
    lines = [f'TEST: {len(c)} foto asli (tidak dilihat saat training), {int(c[:, 0].sum())} kotak jerawat',
             f'mAP50 {t.box.map50:.3f} | mAP50-95 {t.box.map:.3f} (ultralytics, .pt)',
             f'ambang skor {conf} (F1 terbaik di val) -> presisi {P:.3f} recall {R:.3f} F1 {F1:.3f} (IoU >= 0.5, model ONNX)',
             f'jumlah per foto: rata-rata selisih absolut {np.abs(c[:, 0] - c[:, 1]).mean():.1f} '
             f'(rata-rata benar {c[:, 0].mean():.1f}, terdeteksi {c[:, 1].mean():.1f})',
             f'tingkat keparahan sama dengan label: {sev:.1%} (selalu menebak "{top}": {k / len(c):.1%})', '', external_check(acne.detect_acne, crop_face)]
    report = '\n'.join(lines)
    print(report)
    open(os.path.join(OUT, 'acne_yolo_report.txt'), 'w', encoding='utf-8').write(report + '\n')


if __name__ == '__main__':
    main()
