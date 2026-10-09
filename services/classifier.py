import os
import numpy as np
import onnxruntime as ort
from PIL import Image
from database.db import get_db
from services.face import crop_face, face_regions

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
        'name': 'Komedo Hitam',
        'description': 'Pori-pori tersumbat sebum dan sel kulit mati yang teroksidasi sehingga tampak sebagai titik hitam, biasanya di hidung dan dagu.'
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

# Urutan = CLASSES di train_skin_type.py / train_skin_issue.py.
TYPE_LABELS = ['kombinasi', 'kering', 'normal', 'berminyak']
ISSUE_LABELS = ['jerawat', 'komedo', 'flek', None, 'pori']  # None = kelas normal (tidak ada masalah)
TYPE_MIN = 0.6   # di test set: 58% foto lolos, 53% benar. Di bawahnya tampil "belum pasti"
ISSUE_MIN = 0.5  # masalah dianggap ada bila di salah satu area wajah probabilitasnya >= 50%

_type = ort.InferenceSession(os.path.join(ROOT, 'models', 'skin_type.onnx'), providers=['CPUExecutionProvider'])
_issue = ort.InferenceSession(os.path.join(ROOT, 'models', 'skin_issue.onnx'), providers=['CPUExecutionProvider'])


def _probs(session, images):
    x = np.stack([((np.asarray(im.resize((224, 224), Image.BILINEAR), dtype=np.float32) / 255 - MEAN) / STD).transpose(2, 0, 1)
                  for im in images])
    logits = session.run(None, {'pixel_values': x})[0]
    e = np.exp(logits - logits.max(1, keepdims=True))
    return e / e.sum(1, keepdims=True)


def predict(image_path):
    """{kondisi: probabilitas 0-1}. Jenis kulit dari seluruh wajah, masalah kulit dari tiap area wajah."""
    face = crop_face(Image.open(image_path).convert('RGB'))
    p = _probs(_type, [face])[0]
    found = {TYPE_LABELS[p.argmax()] if p.max() >= TYPE_MIN else 'jenis_belum_pasti': float(p.max())}
    worst = _probs(_issue, face_regions(face)).max(0)  # skor tertinggi per masalah di antara semua area
    for label, score in zip(ISSUE_LABELS, worst):
        if label and score >= ISSUE_MIN:
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
