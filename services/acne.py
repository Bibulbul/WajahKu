import json
import os

import numpy as np
import onnxruntime as ort
from PIL import Image

from services.face import face_box

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_cfg = json.load(open(os.path.join(ROOT, 'models', 'acne_yolo.json')))
_sess = ort.InferenceSession(os.path.join(ROOT, 'models', 'acne_yolo.onnx'), providers=['CPUExecutionProvider'])

# Kriteria Hayashi (2008) menghitung lesi meradang di separuh wajah: ringan 0-5, sedang 6-20, berat 21-50, sangat berat > 50.
# Model menghitung seluruh wajah, jadi batasnya dikali dua.
SEVERITY = [(0, 'tidak ada'), (10, 'ringan'), (40, 'sedang'), (100, 'berat')]


def detect_acne(img):
    """Kotak jerawat [(x0, y0, x1, y1, skor)] di koordinat foto PIL RGB (biasanya hasil crop_face).
    Foto ditarik ke persegi seperti data training (Roboflow: resize stretch 640x640)."""
    s = _cfg['imgsz']
    x = (np.asarray(img.resize((s, s), Image.BILINEAR), dtype=np.float32) / 255).transpose(2, 0, 1)[None]
    out = _sess.run(None, {_sess.get_inputs()[0].name: x})[0][0]  # (maks deteksi, 6): x0 y0 x1 y1 skor kelas, tanpa NMS lagi
    out = out[out[:, 4] >= _cfg['conf']]
    sx, sy = img.width / s, img.height / s
    return [(x0 * sx, y0 * sy, x1 * sx, y1 * sy, float(p)) for x0, y0, x1, y1, p, _ in out]


def severity(count):
    return next((name for limit, name in SEVERITY if count <= limit), 'sangat berat')


def analyze_acne(image_path):
    """{'count', 'severity', 'boxes': [[x0, y0, x1, y1, skor]]}, koordinat 0-1 terhadap seluruh foto (siap digambar di atas <img>).
    ValueError bila wajah tidak terdeteksi, sama seperti crop_face."""
    img = Image.open(image_path).convert('RGB')
    fx, fy, fx1, fy1 = face_box(img)
    boxes = detect_acne(img.crop((fx, fy, fx1, fy1)))
    W, H = img.size
    return {'count': len(boxes), 'severity': severity(len(boxes)),
            'boxes': [[round((x0 + fx) / W, 4), round((y0 + fy) / H, 4), round((x1 + fx) / W, 4), round((y1 + fy) / H, 4), round(p, 2)]
                      for x0, y0, x1, y1, p in boxes]}


if __name__ == '__main__':
    # Coba cepat tanpa aplikasi: python -m services.acne foto.jpg -> foto_jerawat.jpg dengan kotak jerawat
    import sys
    from PIL import ImageDraw
    src = sys.argv[1]
    r = analyze_acne(src)
    img = Image.open(src).convert('RGB')
    draw = ImageDraw.Draw(img)
    for x0, y0, x1, y1, _ in r['boxes']:
        draw.ellipse((x0 * img.width, y0 * img.height, x1 * img.width, y1 * img.height), outline=(255, 60, 0), width=3)
    out = os.path.splitext(src)[0] + '_jerawat.jpg'
    img.save(out)
    print(f"{r['count']} jerawat terdeteksi, tingkat {r['severity']} -> {out}")
