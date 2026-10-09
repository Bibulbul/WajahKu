import os
import numpy as np
import onnxruntime as ort
from PIL import Image
from database.db import get_db
from services.face import crop_face

SKIN_CONDITIONS = {
    'jerawat': {
        'name': 'Jerawat (Acne)',
        'description': 'Terdapat peradangan dan komedo pada kulit wajah. Bisa disebabkan oleh produksi minyak berlebih, bakteri, atau hormon.'
    },
    'berminyak': {
        'name': 'Kulit Berminyak',
        'description': 'Produksi sebum berlebihan yang membuat wajah terlihat mengkilap dan pori-pori membesar.'
    },
    'kering': {
        'name': 'Kulit Kering',
        'description': 'Kulit terasa kencang, kasar, dan kusam karena kurangnya kelembaban alami.'
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
        'description': 'Kombinasi kulit berminyak di T-zone (dahi, hidung, dagu) dan normal/kering di area pipi.'
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
    }
}

# Urutan = id2label di models/.../config.json (acne, blackheades, dark spots, pores, wrinkles).
MODEL_LABELS = ['jerawat', 'komedo', 'flek', 'pori', 'kerutan']
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models', 'skin_efficientnet.onnx')
MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
STD = np.array([0.47853944, 0.4732864, 0.47434163], dtype=np.float32)
SECONDARY_MIN = 0.25  # ponytail: kondisi ke-2 dst tampil bila probabilitas softmax >= 25%; model single-label, bukan multi-label

_session = ort.InferenceSession(MODEL_PATH, providers=['CPUExecutionProvider'])

def analyze_skin_image(image_path):
    """Jalankan model EfficientNet-B0 (ONNX). Preprocessing sama dengan training di notebook."""
    img = crop_face(Image.open(image_path).convert('RGB')).resize((224, 224), Image.BILINEAR)
    x = ((np.asarray(img, dtype=np.float32) / 255 - MEAN) / STD).transpose(2, 0, 1)[None]
    logits = _session.run(None, {'pixel_values': x})[0][0]
    probs = np.exp(logits - logits.max())
    probs /= probs.sum()

    order = probs.argsort()[::-1]
    selected = [MODEL_LABELS[i] for i in order if i == order[0] or probs[i] >= SECONDARY_MIN]
    results = {
        c: {**SKIN_CONDITIONS[c], 'confidence': round(float(probs[MODEL_LABELS.index(c)]) * 100)}
        for c in selected
    }

    conn = get_db()
    recommendations = {}
    for condition in selected:
        rows = conn.execute(
            "SELECT step_number, step_title, step_description FROM skincare_routines WHERE condition_type = ? ORDER BY step_number",
            (condition,)
        ).fetchall()
        recommendations[condition] = [dict(row) for row in rows]
    conn.close()

    return results, recommendations
