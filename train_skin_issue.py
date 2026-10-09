"""Latih Model B (masalah kulit: acne / blackheads / dark spots / pores / normal).

- acne, blackheads, dark spots, pores: close-up dari datasets/Skin v2 (wrinkles dibuang: isinya potret lansia utuh).
- normal: potongan area wajah (services.face.face_regions) dari foto berlabel 'normal' di dataset jenis kulit.
Jalankan: C:/wjx/Scripts/python train_skin_issue.py  (butuh cache dari train_skin_type.py)
"""
import glob, os, random, re
from collections import defaultdict

from PIL import Image
from torchvision import transforms as T

import train_skin_type as base
from services.face import face_regions

SKIN_V2 = os.path.join(base.ROOT, 'datasets', 'Skin v2')
PATCHES = os.path.join(base.ROOT, 'datasets', '_cache_normal_patches')
CLASSES = ['acne', 'blackheads', 'dark_spots', 'normal', 'pores']  # urutan = id label; salin ke classifier.py
FOLDERS = {'acne': 'acne', 'blackheades': 'blackheads', 'dark spots': 'dark_spots', 'pores': 'pores'}


def low_res(img):
    """Close-up dataset tajam, potongan wajah dari selfie buram: samakan supaya model tidak belajar 'tajam = masalah'."""
    s = random.randint(64, 160)
    return img.resize((s, s), Image.BILINEAR).resize(img.size, Image.BILINEAR)


def issue_items():
    groups = defaultdict(lambda: {'labels': set(), 'files': []})
    for folder, label in FOLDERS.items():
        for f in sorted(glob.glob(os.path.join(SKIN_V2, folder, '*'))):
            g = groups[re.sub(r'_(jpg|jpeg|png)\.rf\..*$', '', os.path.basename(f).lower())]
            g['labels'].add(label); g['files'].append(f)
    return [(sid, next(iter(g['labels'])), g['files']) for sid, g in groups.items() if len(g['labels']) == 1]


def normal_items():
    os.makedirs(PATCHES, exist_ok=True)
    rng = random.Random(base.SEED)
    items = []
    for sid, label, copies, has_face in base.build_cache():
        if label != 'normal' or not has_face:
            continue
        files = []
        for c in copies[:2]:
            for k, patch in enumerate(face_regions(Image.open(c).convert('RGB'))):
                out = os.path.join(PATCHES, f'{os.path.basename(c)[:-4]}_{k}.jpg')
                if not os.path.exists(out):
                    patch.save(out, quality=95)
                files.append(out)
        rng.shuffle(files)
        items.append((sid, 'normal', files))
    return items


if __name__ == '__main__':
    items = issue_items() + normal_items()
    print({c: sum(i[1] == c for i in items) for c in CLASSES}, 'foto asli per kelas')
    base.train(items, CLASSES, 'skin_issue', extra_tf=[T.RandomApply([T.Lambda(low_res)], p=0.5)])
