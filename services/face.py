import cv2
import numpy as np

FACE_MARGIN = 0.1  # tambahan di tiap sisi kotak wajah, proporsi lebar wajah
_face = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


def crop_face(img):
    """Crop foto PIL ke wajah terbesar. Dipakai aplikasi dan training supaya input model sama.
    ponytail: Haar cascade hanya mengenali wajah menghadap depan; ganti detektor bila banyak penolakan."""
    faces = _face.detectMultiScale(np.asarray(img.convert('L')), 1.1, 5, minSize=(80, 80))
    if not len(faces):
        raise ValueError('Wajah tidak terdeteksi. Pastikan wajah menghadap kamera dan pencahayaan cukup.')
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    m = int(w * FACE_MARGIN)
    return img.crop((max(x - m, 0), max(y - m, 0), min(x + w + m, img.width), min(y + h + m, img.height)))


# Area wajah (proporsi kotak hasil crop_face): dahi, hidung, pipi kiri, pipi kanan, dagu.
# Model masalah kulit dilatih dengan foto close-up, jadi wajah dinilai per area lalu digabung.
REGIONS = [(.2, .05, .8, .3), (.35, .35, .65, .65), (.08, .45, .42, .8), (.58, .45, .92, .8), (.3, .78, .7, 1)]


def face_regions(face):
    W, H = face.size
    return [face.crop((int(a * W), int(b * H), int(c * W), int(d * H))) for a, b, c, d in REGIONS]
