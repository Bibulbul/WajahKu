import json
import os
import numpy as np
import onnxruntime as ort
from PIL import Image
from database.db import get_db
from services.face import REGIONS_V2, crop_face, face_regions

SKIN_CONDITIONS = {
    'jerawat': {
        'name': 'Jerawat (Acne)',
        'description': 'Terdapat peradangan dan komedo pada kulit wajah. Bisa disebabkan oleh produksi minyak berlebih, bakteri, atau hormon.'
    },
    'berminyak': {
        'name': 'Kulit Berminyak',
        'description': 'Produksi sebum berlebihan yang membuat wajah terlihat mengkilap dan pori-pori membesar. (Perkiraan AI)'
    },
    'kering': {
        'name': 'Kulit Kering',
        'description': 'Kulit terasa kencang, kasar, dan kusam karena kurangnya kelembaban alami. (Perkiraan AI)'
    },
    'kusam': {
        'name': 'Kulit Kusam',
        'description': 'Warna kulit tidak merata dan terlihat tidak bercahaya, biasanya karena sel kulit mati menumpuk.'
    },
    'kemerahan': {
        'name': 'Kemerahan (Redness)',
        'description': 'Area kulit yang memerah, bisa karena iritasi, sensitivitas, atau peradangan.'
    },
    'kombinasi': {
        'name': 'Kulit Kombinasi',
        'description': 'Kombinasi kulit berminyak di T-zone (dahi, hidung, dagu) dan normal/kering di area pipi. (Perkiraan AI)'
    },
    'komedo': {
        'name': 'Komedo',
        'description': 'Pori-pori tersumbat sebum dan sel kulit mati. Tampak sebagai titik hitam (blackhead) atau bintik putih kecil (whitehead), biasanya di hidung, dahi, dan dagu.'
    },
    'kantung_mata': {
        'name': 'Kantung Mata',
        'description': 'Area bawah mata tampak bengkak atau menggantung. Sering dipengaruhi kurang tidur, retensi cairan, faktor keturunan, dan usia.'
    },
    'flek': {
        'name': 'Flek Hitam',
        'description': 'Bercak gelap akibat produksi melanin berlebih, biasanya karena paparan sinar matahari, bekas jerawat, atau perubahan hormon.'
    },
    'pori': {
        'name': 'Pori-pori Besar',
        'description': 'Pori-pori tampak membesar, sering terkait produksi minyak berlebih, kulit kurang elastis, dan penumpukan kotoran.'
    },
    'kerutan': {
        'name': 'Kerutan',
        'description': 'Garis halus dan kerutan akibat berkurangnya kolagen dan elastin, dipercepat oleh paparan UV dan kurangnya hidrasi.'
    },
    'normal': {
        'name': 'Kulit Normal',
        'description': 'Produksi minyak dan kelembaban seimbang, tidak terlalu berminyak maupun kering. (Perkiraan AI)'
    },
    'jenis_belum_pasti': {
        'name': 'Jenis Kulit Belum Pasti',
        'description': 'AI belum cukup yakin menentukan jenis kulit dari foto ini. Coba foto ulang dengan cahaya alami, tanpa makeup, wajah menghadap kamera.'
    }
}

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)

# Urutan = CLASSES di train_skin_type.py.
TYPE_LABELS = ['kombinasi', 'kering', 'normal', 'berminyak']
TYPE_MIN = 0.6   # di test set: 58% foto lolos, 53% benar. Di bawahnya tampil "belum pasti"

# Model B v2 (multi-label, train_skin_issue_v2.py): kelas dan ambang per kelas dari models/skin_issue_v2.json.
ISSUE_NAMES = {'acne': 'jerawat', 'comedo': 'komedo', 'pores': 'pori', 'wrinkles': 'kerutan',
               'redness': 'kemerahan', 'dark_spots': 'flek', 'eye_bags': 'kantung_mata'}
_issue_cfg = json.load(open(os.path.join(ROOT, 'models', 'skin_issue_v2.json'), encoding='utf-8'))
ISSUE_LABELS = [ISSUE_NAMES[c] for c in _issue_cfg['classes']]
ISSUE_MIN = np.array(_issue_cfg['face_thresholds'])  # ambang level wajah (maks 7 area), dari tune_face_thresholds_v2.py

_type = ort.InferenceSession(os.path.join(ROOT, 'models', 'skin_type.onnx'), providers=['CPUExecutionProvider'])
_issue = ort.InferenceSession(os.path.join(ROOT, 'models', 'skin_issue_v2.onnx'), providers=['CPUExecutionProvider'])


def _logits(session, images):
    x = np.stack([((np.asarray(im.resize((224, 224), Image.BILINEAR), dtype=np.float32) / 255 - MEAN) / STD).transpose(2, 0, 1)
                  for im in images])
    return session.run(None, {'pixel_values': x})[0]


def _softmax(logits):
    e = np.exp(logits - logits.max(1, keepdims=True))
    return e / e.sum(1, keepdims=True)


def predict(image_path):
    """{kondisi: probabilitas 0-1}. Jenis kulit dari seluruh wajah, masalah kulit dari tiap area wajah."""
    face = crop_face(Image.open(image_path).convert('RGB'))
    p = _softmax(_logits(_type, [face]))[0]
    found = {TYPE_LABELS[p.argmax()] if p.max() >= TYPE_MIN else 'jenis_belum_pasti': float(p.max())}
    worst = (1 / (1 + np.exp(-_logits(_issue, face_regions(face, REGIONS_V2))))).max(0)  # skor tertinggi per masalah di antara 7 area
    for label, score, th in zip(ISSUE_LABELS, worst, ISSUE_MIN):
        if score >= th:
            found[label] = float(score)
    return found


def analyze_skin_image(image_path):
    found = predict(image_path)
    results = {c: {**SKIN_CONDITIONS[c], 'confidence': round(p * 100)} for c, p in found.items()}

    conn = get_db()
    recommendations = {}
    for condition in found:
        rows = conn.execute(
            "SELECT step_number, step_title, step_description FROM skincare_routines WHERE condition_type = ? ORDER BY step_number",
            (condition,)
        ).fetchall()
        if rows:
            recommendations[condition] = [dict(row) for row in rows]
    conn.close()

    return results, recommendations
