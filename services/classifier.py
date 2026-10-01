import time
import random
from database.db import get_db

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
    }
}

def analyze_skin_image(image_path):
    """
    Sistem analisis kulit wajah.
    Saat ini menggunakan simulasi (mock) sebelum dihubungkan ke model PyTorch EfficientNet-B0.
    """
    time.sleep(random.uniform(1.5, 2.5))
    
    all_conditions = list(SKIN_CONDITIONS.keys())
    num_conditions = random.randint(1, 3)
    
    selected = []
    if random.random() > 0.6 and 'kemerahan' not in selected:
        selected.append('kemerahan')
        if random.random() > 0.5:
            selected.append(random.choice(['jerawat', 'kering']))
    
    while len(selected) < num_conditions:
        cond = random.choice(all_conditions)
        if cond not in selected:
            selected.append(cond)
    
    results = {}
    for condition in selected:
        confidence = random.randint(65, 98)
        results[condition] = {
            'name': SKIN_CONDITIONS[condition]['name'],
            'description': SKIN_CONDITIONS[condition]['description'],
            'confidence': confidence
        }
    
    recommendations = {}
    conn = get_db()
    for condition in selected:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT step_number, step_title, step_description FROM skincare_routines WHERE condition_type = ? ORDER BY step_number",
            (condition,)
        )
        steps = [dict(row) for row in cursor.fetchall()]
        recommendations[condition] = steps
    conn.close()
    
    return results, recommendations
