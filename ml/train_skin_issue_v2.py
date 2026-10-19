"""Latih Model B v2 (masalah kulit, multi-label) dari Skin-Problem-Detection-Relabel-Clean3.

Dataset: Parin Kittipongdaja, Roboflow Universe, CC BY 4.0
(https://universe.roboflow.com/parin-kittipongdaja-vwmn3/skin-problem-detection-relabel-clean3).

Patch dibuat dari foto yang sama: area yang bertanda kotak = positif, area tanpa kotak = negatif,
supaya model tidak bisa menebak dari gaya foto (masalah Model B v1). Foto berwajah dipotong per area
dengan REGIONS_V2 (sama dengan aplikasi); close-up tanpa wajah terdeteksi dipotong per kuadran.
Jalankan: C:/wjx/Scripts/python -m ml.train_skin_issue_v2
Hasil: models/skin_issue_v2.onnx, models/skin_issue_v2.json (kelas + ambang), models/skin_issue_v2_report.txt
"""
import csv, hashlib, json, os, random, re, zipfile
from collections import Counter, defaultdict
from xml.etree import ElementTree as ET

import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from sklearn.metrics import average_precision_score, f1_score, precision_score, recall_score, roc_auc_score
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms as T

from services.face import REGIONS_V2, crop_face, face_box, face_regions
from ml.train_skin_issue import low_res

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # root repo, skrip ini ada di ml/
SRC = os.path.join(ROOT, 'datasets', 'Skin-Problem-Detection-Relabel-Clean3.v2i.coco')
CACHE = os.path.join(ROOT, 'datasets', '_cache_issue_v2')
OUT = os.path.join(ROOT, 'models')
# urutan = indeks output model; salin ke services/classifier.py
CLASSES = ['acne', 'comedo', 'pores', 'wrinkles', 'redness', 'dark_spots', 'eye_bags']
MAP = {'Acne': 'acne', 'Blackheads': 'comedo', 'Whiteheads': 'comedo', 'Englarged-Pores': 'pores', 'Wrinkles': 'wrinkles',
       'Skin-Redness': 'redness', 'Dark-Spots': 'dark_spots', 'Eyebags': 'eye_bags'}  # Dry/Oily-Skin tidak dipakai: label paling berantakan
EPOCHS, BATCH, LR, SEED, PATIENCE = 15, 32, 3e-4, 42, 4
MEAN, STD = [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]
random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)


def source_id(name):
    return re.sub(r'_(jpg|jpeg|png|webp)\.rf\..*$', '', os.path.basename(name).lower())


def labels_for(patch, boxes):
    """Kelas yang kotaknya cukup masuk ke patch: >=50% luas kotak, atau kotak menutupi >=25% patch."""
    px0, py0, px1, py1 = patch
    parea = (px1 - px0) * (py1 - py0)
    found = set()
    for (x0, y0, x1, y1), c in boxes:
        iw, ih = min(x1, px1) - max(x0, px0), min(y1, py1) - max(y0, py0)
        if iw <= 0 or ih <= 0:
            continue
        inter = iw * ih
        if inter / ((x1 - x0) * (y1 - y0)) >= 0.5 or inter / parea >= 0.25:
            found.add(c)
    return found


def build_cache():
    """Satu salinan per foto asli (Roboflow menyimpan salinan sama di beberapa split), lalu potong patch."""
    best = {}
    for sp in ('train', 'valid', 'test'):
        js = json.load(open(os.path.join(SRC, sp, '_annotations.coco.json'), encoding='utf-8'))
        cats = {c['id']: c['name'] for c in js['categories']}
        anns = defaultdict(list)
        for a in js['annotations']:
            if cats[a['category_id']] in MAP:
                x, y, w, h = a['bbox']
                anns[a['image_id']].append(((x, y, x + w, y + h), MAP[cats[a['category_id']]]))
        for im in js['images']:
            sid = source_id(im['file_name'])
            if anns[im['id']] and len(anns[im['id']]) > len(best.get(sid, (None, []))[1]):
                best[sid] = (os.path.join(SRC, sp, im['file_name']), anns[im['id']])
    os.makedirs(CACHE, exist_ok=True)
    manifest = os.path.join(CACHE, 'manifest.json')
    if os.path.exists(manifest):
        return json.load(open(manifest, encoding='utf-8'))
    items, faces = [], 0
    for sid, (path, boxes) in sorted(best.items()):
        img = Image.open(path).convert('RGB')
        W, H = img.size
        try:
            fx0, fy0, fx1, fy1 = face_box(img)
            fw, fh = fx1 - fx0, fy1 - fy0
            patches = [(fx0 + a * fw, fy0 + b * fh, fx0 + c * fw, fy0 + d * fh) for a, b, c, d in REGIONS_V2]
            faces += 1
        except ValueError:
            patches = [(0, 0, W, H), (0, 0, W / 2, H / 2), (W / 2, 0, W, H / 2), (0, H / 2, W / 2, H), (W / 2, H / 2, W, H)]
        for k, p in enumerate(patches):
            out = os.path.join(CACHE, f'{hashlib.md5(sid.encode()).hexdigest()[:12]}_{k}.jpg')
            img.crop(tuple(int(v) for v in p)).resize((256, 256), Image.BILINEAR).save(out, quality=92)
            items.append({'source': sid, 'file': out, 'labels': sorted(labels_for(p, boxes))})
    print(f'foto asli: {len(best)} | berwajah (dipotong per area): {faces} | patch: {len(items)}')
    json.dump(items, open(manifest, 'w', encoding='utf-8'))
    return items


class Data(Dataset):
    def __init__(self, items, tf):
        self.items, self.tf = items, tf
    def __len__(self): return len(self.items)
    def __getitem__(self, i):
        it = self.items[i]
        y = torch.tensor([float(c in it['labels']) for c in CLASSES])
        return self.tf(Image.open(it['file']).convert('RGB')), y


def split(items):
    """80/10/10 per foto asli: semua patch dari satu foto masuk split yang sama."""
    sources = sorted({it['source'] for it in items})
    random.Random(SEED).shuffle(sources)
    n = len(sources)
    part = {s: ('train' if i < 0.8 * n else 'val' if i < 0.9 * n else 'test') for i, s in enumerate(sources)}
    return [[it for it in items if part[it['source']] == p] for p in ('train', 'val', 'test')]


def count(items):
    c = Counter(l for it in items for l in it['labels'])
    return {k: c[k] for k in CLASSES} | {'tanpa label': sum(not it['labels'] for it in items)}


def best_thresholds(y, p):
    th = []
    for j in range(len(CLASSES)):
        cand = [(f1_score(y[:, j], p[:, j] >= t, zero_division=0), t) for t in np.arange(0.1, 0.91, 0.05)]
        th.append(round(float(max(cand)[1]), 2))
    return np.array(th)


def read_xlsx(path):
    """Baca sheet pertama .xlsx tanpa dependensi tambahan -> list baris (list string)."""
    ns = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    z = zipfile.ZipFile(path)
    shared = [''.join(t.text or '' for t in si.iter('{%s}t' % ns['m'])) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si', ns)]
    rows = []
    for r in ET.fromstring(z.read('xl/worksheets/sheet1.xml')).find('m:sheetData', ns).findall('m:row', ns):
        row = {}
        for c in r.findall('m:c', ns):
            v = c.find('m:v', ns)
            if v is not None:
                row[re.match(r'[A-Z]+', c.get('r')).group()] = shared[int(v.text)] if c.get('t') == 's' else v.text
        rows.append(row)
    return rows


def external_check(predict_face):
    """Bandingkan skor model (maks per area wajah) dengan skor 0-5 dari 200 foto berlabel di skin_type_classification_dataset."""
    d = os.path.join(ROOT, 'datasets', 'skin_type_classification_dataset')
    cols = {'acne': ['C'], 'comedo': ['D', 'E'], 'pores': ['F'], 'redness': ['J'], 'wrinkles': ['N'], 'dark_spots': ['Q'], 'eye_bags': ['L']}
    scores, truth, skipped = defaultdict(list), defaultdict(list), 0
    for xlsx, sp in (('skinalaysis_labeling_train1.xlsx', 'train'), ('skinanalysis_valid1.xlsx', 'valid')):
        for r in read_xlsx(os.path.join(d, xlsx))[1:]:
            name = r['B'] if r['B'].endswith('.jpg') else r['B'] + '.jpg'
            folder = name.split('_')[0]
            try:
                p = predict_face(Image.open(os.path.join(d, sp, folder, name)).convert('RGB'))
            except (ValueError, FileNotFoundError):
                skipped += 1
                continue
            for c, cs in cols.items():
                vals = [int(r[k]) for k in cs if r.get(k, '').isdigit() and int(r[k]) <= 5]
                if vals:
                    scores[c].append(p[CLASSES.index(c)]); truth[c].append(max(vals))
    lines = [f'Cek eksternal: 200 foto skin_type_classification_dataset (dilewati, wajah tidak terdeteksi: {skipped})',
             'AUC = peluang foto dengan skor >= 2 mendapat nilai model lebih tinggi daripada foto skor < 2 (0.5 = tebakan)']
    for c in CLASSES:
        y = np.array(truth[c]) >= 2
        auc = roc_auc_score(y, scores[c]) if 0 < y.sum() < len(y) else float('nan')
        lines.append(f'  {c:11s} n={len(y):3d} positif={int(y.sum()):3d} AUC={auc:.2f}')
    return '\n'.join(lines)


def main():
    items = build_cache()
    tr, va, te = split(items)
    print('patch train', len(tr), count(tr)); print('patch val', len(va), count(va)); print('patch test', len(te), count(te))

    train_tf = T.Compose([T.RandomApply([T.Lambda(low_res)], p=0.5), T.RandomResizedCrop(224, scale=(0.7, 1)), T.RandomHorizontalFlip(),
                          T.RandomRotation(10), T.ColorJitter(0.2, 0.2, 0.1), T.ToTensor(), T.Normalize(MEAN, STD)])
    eval_tf = T.Compose([T.Resize((224, 224)), T.ToTensor(), T.Normalize(MEAN, STD)])
    mk = lambda its, tf, shuffle: DataLoader(Data(its, tf), BATCH, shuffle=shuffle, num_workers=3)
    dl_tr, dl_va, dl_te = mk(tr, train_tf, True), mk(va, eval_tf, False), mk(te, eval_tf, False)

    y_tr = np.array([[c in it['labels'] for c in CLASSES] for it in tr], dtype=np.float32)
    pos = y_tr.sum(0)
    pos_weight = torch.tensor(np.clip((len(y_tr) - pos) / np.maximum(pos, 1), 1, 10), dtype=torch.float32)  # kelas langka diberi bobot lebih

    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    net = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)
    net.classifier[1] = nn.Linear(net.classifier[1].in_features, len(CLASSES))
    net.to(dev)
    opt = torch.optim.AdamW(net.parameters(), lr=LR, weight_decay=0.01)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, LR, total_steps=EPOCHS * len(dl_tr))
    loss_fn = nn.BCEWithLogitsLoss(pos_weight=pos_weight.to(dev))
    scaler = torch.amp.GradScaler(enabled=dev == 'cuda')

    def predict(dl):
        net.eval(); ys, ps = [], []
        with torch.no_grad(), torch.autocast(dev, enabled=dev == 'cuda'):
            for x, y in dl:
                ps.append(torch.sigmoid(net(x.to(dev)).float()).cpu().numpy()); ys.append(y.numpy())
        return np.concatenate(ys), np.concatenate(ps)

    def mean_ap(y, p):
        return float(np.mean([average_precision_score(y[:, j], p[:, j]) for j in range(len(CLASSES)) if y[:, j].sum()]))

    best, best_state, bad = -1, None, 0
    for ep in range(EPOCHS):
        net.train(); tot = 0
        for x, y in dl_tr:
            x, y = x.to(dev), y.to(dev)
            with torch.autocast(dev, enabled=dev == 'cuda'):
                loss = loss_fn(net(x).float(), y)
            opt.zero_grad(); scaler.scale(loss).backward(); scaler.step(opt); scaler.update(); sched.step()
            tot += loss.item()
        m = mean_ap(*predict(dl_va))
        print(f'epoch {ep + 1:2d} loss {tot / len(dl_tr):.3f} val mAP {m:.3f}', flush=True)
        if m > best:
            best, bad, best_state = m, 0, {k: v.clone() for k, v in net.state_dict().items()}
        else:
            bad += 1
            if bad >= PATIENCE:
                break
    net.load_state_dict(best_state)

    th = best_thresholds(*predict(dl_va))  # ambang per kelas dipilih di val, dinilai di test
    y, p = predict(dl_te)
    pred = p >= th
    lines = [f'val mAP terbaik {best:.3f}', f'TEST: {len(te)} patch dari {len({it["source"] for it in te})} foto asli (tidak dilihat saat training)',
             f'mAP {mean_ap(y, p):.3f} | macro F1 {f1_score(y, pred, average="macro", zero_division=0):.3f}',
             'kelas        ambang  AP     F1     presisi recall  jumlah positif']
    for j, c in enumerate(CLASSES):
        ap = average_precision_score(y[:, j], p[:, j]) if y[:, j].sum() else float('nan')
        lines.append(f'{c:12s} {th[j]:.2f}   {ap:.3f}  {f1_score(y[:, j], pred[:, j], zero_division=0):.3f}  '
                     f'{precision_score(y[:, j], pred[:, j], zero_division=0):.3f}   {recall_score(y[:, j], pred[:, j], zero_division=0):.3f}   {int(y[:, j].sum())}')
    neg = ~y.any(1)
    lines.append(f'patch tanpa masalah: {int(neg.sum())}, yang tetap tanpa deteksi: {float((~pred[neg].any(1)).mean()):.1%}')

    net.eval().cpu()
    os.makedirs(OUT, exist_ok=True)
    onnx_path = os.path.join(OUT, 'skin_issue_v2.onnx')
    torch.onnx.export(net, (torch.randn(1, 3, 224, 224),), onnx_path, input_names=['pixel_values'], output_names=['logits'],
                      dynamic_axes={'pixel_values': {0: 'b'}, 'logits': {0: 'b'}}, dynamo=False, opset_version=17)
    json.dump({'classes': CLASSES, 'thresholds': th.tolist(), 'mean': MEAN, 'std': STD}, open(os.path.join(OUT, 'skin_issue_v2.json'), 'w'), indent=1)

    import onnxruntime as ort
    sess = ort.InferenceSession(onnx_path, providers=['CPUExecutionProvider'])
    M, S = np.array(MEAN, np.float32), np.array(STD, np.float32)
    def predict_face(img):
        x = np.stack([((np.asarray(r.resize((224, 224), Image.BILINEAR), np.float32) / 255 - M) / S).transpose(2, 0, 1)
                      for r in face_regions(crop_face(img), REGIONS_V2)])
        return (1 / (1 + np.exp(-sess.run(None, {'pixel_values': x})[0]))).max(0)
    lines.append(''); lines.append(external_check(predict_face))

    report = '\n'.join(lines)
    print(report)
    open(os.path.join(OUT, 'skin_issue_v2_report.txt'), 'w', encoding='utf-8').write(report + '\n')
    print('tersimpan: models/skin_issue_v2.onnx')


if __name__ == '__main__':
    main()
