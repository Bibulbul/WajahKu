"""Latih Model A (jenis kulit: dry / normal / oily / combination) dari dua dataset Roboflow di datasets/.

Jalankan: C:/wjx/Scripts/python train_skin_type.py
Hasil: models/skin_type.onnx + models/skin_type_report.txt
"""
import glob, hashlib, os, random, re
from collections import defaultdict

import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Dataset, WeightedRandomSampler
from torchvision import models, transforms as T

from services.face import crop_face

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIRS = [os.path.join(ROOT, 'datasets', d) for d in ('Oily-Dry-Skin-Types', 'skin_type_classification_dataset')]
CACHE = os.path.join(ROOT, 'datasets', '_cache_skin_type')
OUT = os.path.join(ROOT, 'models')
CLASSES = ['combination', 'dry', 'normal', 'oily']  # urutan = id label; salin ke classifier.py
EPOCHS, BATCH, LR, SEED, MAX_COPIES, PATIENCE = 15, 32, 3e-4, 42, 4, 4
MEAN, STD = [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]

random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)


def source_id(path):
    """Roboflow membuat beberapa salinan augmentasi per foto: nama sama sebelum '.rf.<hash>'."""
    name = re.sub(r'_(jpg|jpeg|png)\.rf\..*$', '', os.path.basename(path).lower())
    return re.sub(r'^(combination|dry|normal|oily)[_-]*', '', name)


def black_fraction(img):
    return float((np.asarray(img).max(axis=2) < 8).mean())


def build_cache():
    """Gabung kedua dataset per foto asli, crop wajah (sama seperti aplikasi), simpan ke cache.
    Foto tanpa wajah terdeteksi (banyak close-up pipi/mata) disimpan utuh tapi tidak dipakai:
    dicoba sebagai data train tambahan, hasil val turun (0.473 -> 0.391)."""
    groups = defaultdict(lambda: {'labels': set(), 'files': set()})
    for d in SRC_DIRS:
        for f in glob.glob(os.path.join(d, '*', '*', '*')):
            label = os.path.basename(os.path.dirname(f))
            g = groups[source_id(f)]
            g['labels'].add(label); g['files'].add(f)
    os.makedirs(CACHE, exist_ok=True)
    items, dropped = [], defaultdict(int)
    for sid, g in groups.items():
        if len(g['labels']) != 1:
            dropped['label_bentrok'] += 1; continue
        label = next(iter(g['labels']))
        face, whole = [], []
        for f in sorted(g['files']):
            h = hashlib.md5(f.encode()).hexdigest()[:16]
            out, out_nf = os.path.join(CACHE, h + '.jpg'), os.path.join(CACHE, 'nf_' + h + '.jpg')
            if not os.path.exists(out) and not os.path.exists(out_nf):
                img = Image.open(f).convert('RGB')
                try:
                    crop_face(img).resize((256, 256), Image.BILINEAR).save(out, quality=95)
                except ValueError:
                    img.resize((256, 256), Image.BILINEAR).save(out_nf, quality=95)
            (face if os.path.exists(out) else whole).append(out if os.path.exists(out) else out_nf)
        items.append((sid, label, face or whole, bool(face)))
    print('foto asli:', len(items), '| dengan wajah:', sum(i[3] for i in items), '| dibuang:', dict(dropped))
    return items


class Data(Dataset):
    def __init__(self, files, labels, tf):
        self.files, self.labels, self.tf = files, labels, tf
    def __len__(self): return len(self.files)
    def __getitem__(self, i):
        return self.tf(Image.open(self.files[i]).convert('RGB')), self.labels[i]


def train(items, classes, name, extra_tf=()):
    """items: [(source_id, label, [file salinan...]), ...]. Split per foto asli supaya salinan augmentasi
    tidak bocor ke val/test. Simpan models/<name>.onnx dan models/<name>_report.txt."""
    ids = [classes.index(i[1]) for i in items]
    tr, rest = train_test_split(range(len(items)), test_size=0.2, stratify=ids, random_state=SEED)
    va, te = train_test_split(rest, test_size=0.5, stratify=[ids[i] for i in rest], random_state=SEED)

    def cleanest(copies):  # eval: satu salinan per foto, pilih yang paling sedikit border hitam hasil rotasi
        return min(copies, key=lambda c: black_fraction(Image.open(c).convert('RGB')))

    train_items = [items[i] for i in tr]
    tr_f = [c for it in train_items for c in it[2][:MAX_COPIES]]
    tr_y = [classes.index(it[1]) for it in train_items for _ in it[2][:MAX_COPIES]]
    va_f = [cleanest(items[i][2]) for i in va]; va_y = [ids[i] for i in va]
    te_f = [cleanest(items[i][2]) for i in te]; te_y = [ids[i] for i in te]
    print('train', len(tr_f), 'file dari', len(train_items), 'foto | val', len(va_f), '| test', len(te_f))

    train_tf = T.Compose([*extra_tf, T.RandomResizedCrop(224, scale=(0.7, 1)), T.RandomHorizontalFlip(), T.RandomRotation(10),
                          T.ColorJitter(0.2, 0.2, 0.1), T.ToTensor(), T.Normalize(MEAN, STD)])
    eval_tf = T.Compose([T.Resize((224, 224)), T.ToTensor(), T.Normalize(MEAN, STD)])
    w = 1 / np.bincount(tr_y)
    sampler = WeightedRandomSampler([w[y] for y in tr_y], len(tr_y))  # kelas kecil lebih sering muncul
    mk = lambda f, y, tf, **kw: DataLoader(Data(f, y, tf), BATCH, num_workers=3, **kw)
    dl_tr, dl_va, dl_te = mk(tr_f, tr_y, train_tf, sampler=sampler), mk(va_f, va_y, eval_tf), mk(te_f, te_y, eval_tf)

    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    net = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)
    net.classifier[1] = nn.Linear(net.classifier[1].in_features, len(classes))
    net.to(dev)
    opt = torch.optim.AdamW(net.parameters(), lr=LR, weight_decay=0.01)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, LR, total_steps=EPOCHS * len(dl_tr))
    loss_fn = nn.CrossEntropyLoss(label_smoothing=0.1)
    scaler = torch.amp.GradScaler(enabled=dev == 'cuda')

    def predict(dl):
        net.eval(); ys, ps = [], []
        with torch.no_grad(), torch.autocast(dev, enabled=dev == 'cuda'):
            for x, y in dl:
                ps += net(x.to(dev)).argmax(1).cpu().tolist(); ys += y.tolist()
        return ys, ps

    best, best_state, bad = -1, None, 0
    for ep in range(EPOCHS):
        net.train(); tot = 0
        for x, y in dl_tr:
            x, y = x.to(dev), y.to(dev)
            with torch.autocast(dev, enabled=dev == 'cuda'):
                loss = loss_fn(net(x), y)
            opt.zero_grad(); scaler.scale(loss).backward(); scaler.step(opt); scaler.update(); sched.step()
            tot += loss.item()
        ys, ps = predict(dl_va); f1 = f1_score(ys, ps, average='macro')
        print(f'epoch {ep + 1:2d} loss {tot / len(dl_tr):.3f} val macroF1 {f1:.3f} acc {np.mean(np.array(ys) == ps):.3f}', flush=True)
        if f1 > best: best, bad, best_state = f1, 0, {k: v.clone() for k, v in net.state_dict().items()}
        else:
            bad += 1
            if bad >= PATIENCE: break
    net.load_state_dict(best_state)

    ys, ps = predict(dl_te)
    majority = max(np.bincount(te_y)) / len(te_y)
    report = (f'TEST (foto asli yang tidak pernah dilihat saat training, {len(te_y)} foto)\n'
              f'accuracy {np.mean(np.array(ys) == ps):.3f} | macroF1 {f1_score(ys, ps, average="macro"):.3f} | tebak kelas terbanyak {majority:.3f}\n'
              f'{classification_report(ys, ps, target_names=classes, zero_division=0)}\n'
              f'confusion (baris=asli, kolom={classes}):\n{confusion_matrix(ys, ps)}\n')
    print(report)
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, f'{name}_report.txt'), 'w', encoding='utf-8').write(report)

    net.eval().cpu()
    torch.onnx.export(net, (torch.randn(1, 3, 224, 224),), os.path.join(OUT, f'{name}.onnx'), input_names=['pixel_values'],
                      output_names=['logits'], dynamic_axes={'pixel_values': {0: 'b'}, 'logits': {0: 'b'}}, dynamo=False, opset_version=17)
    print(f'tersimpan: models/{name}.onnx')


if __name__ == '__main__':
    every = build_cache()
    train([i[:3] for i in every if i[3]], CLASSES, 'skin_type')  # hanya foto berwajah, seperti input aplikasi
