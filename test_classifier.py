import os

from PIL import Image
from services.classifier import TYPE_LABELS, predict
from services.face import crop_face

# Foto wajah untuk uji. Foto pengguna tidak ikut di repo, jadi isi WAJAHKU_TEST_FACE dengan foto wajahmu sendiri.
FACE = os.environ.get('WAJAHKU_TEST_FACE', 'static/uploads/35815aad-fec2-4f7c-9861-bea675f4dea2.jpg')


def test_face_is_cropped():
    img = Image.open(FACE).convert('RGB')
    assert crop_face(img).width < img.width / 2


def test_no_face_raises():
    try:
        crop_face(Image.new('RGB', (600, 600), 'gray'))
    except ValueError:
        return
    raise AssertionError('harus menolak foto tanpa wajah')


def test_predict_has_skin_type():
    found = predict(FACE)
    assert any(k in found for k in TYPE_LABELS + ['jenis_belum_pasti']), found


if __name__ == '__main__':
    test_no_face_raises()
    if os.path.exists(FACE):
        test_face_is_cropped(); test_predict_has_skin_type()
    else:
        print(f'Tes wajah dilewati: {FACE} tidak ada. Isi WAJAHKU_TEST_FACE dengan path foto wajah.')
    print('ok')
