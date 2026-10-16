import cv2
import numpy as np

FACE_MARGIN = 0.1  # tambahan di tiap sisi kotak wajah, proporsi lebar wajah
_face = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


def face_box(img):
    """Kotak (x0, y0, x1, y1) wajah terbesar di foto PIL, sudah ditambah margin.
    ponytail: Haar cascade hanya mengenali wajah menghadap depan; ganti detektor bila banyak penolakan."""
    faces = _face.detectMultiScale(np.asarray(img.convert('L')), 1.1, 5, minSize=(80, 80))
    if not len(faces):
        raise ValueError('Wajah tidak terdeteksi. Pastikan wajah menghadap kamera dan pencahayaan cukup.')
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    m = int(w * FACE_MARGIN)
    return max(x - m, 0), max(y - m, 0), min(x + w + m, img.width), min(y + h + m, img.height)


def crop_face(img):
    """Crop foto PIL ke wajah terbesar. Dipakai aplikasi dan training supaya input model sama."""
    return img.crop(face_box(img))


# Area wajah (proporsi kotak hasil crop_face): dahi, hidung, pipi kiri, pipi kanan, dagu.
# Model masalah kulit dilatih dengan foto close-up, jadi wajah dinilai per area lalu digabung.
REGIONS = [(.2, .05, .8, .3), (.35, .35, .65, .65), (.08, .45, .42, .8), (.58, .45, .92, .8), (.3, .78, .7, 1)]

# Model B v2: ditambah area bawah mata (kantung mata), pipi digeser sedikit ke bawah.
REGIONS_V2 = [(.2, .05, .8, .3), (.12, .38, .45, .58), (.55, .38, .88, .58), (.35, .35, .65, .65),
              (.08, .5, .42, .85), (.58, .5, .92, .85), (.3, .78, .7, 1)]
REGION_NAMES_V2 = ['dahi', 'bawah mata kiri', 'bawah mata kanan', 'hidung', 'pipi kiri', 'pipi kanan', 'dagu']


def face_regions(face, regions=REGIONS):
    W, H = face.size
    return [face.crop((int(a * W), int(b * H), int(c * W), int(d * H))) for a, b, c, d in regions]
