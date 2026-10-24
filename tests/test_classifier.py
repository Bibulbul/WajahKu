import os

from PIL import Image
from services.classifier import ISSUE_LABELS, predict, skin_type_from_quiz
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


def test_predict_only_issues():
    assert set(predict(FACE)) <= set(ISSUE_LABELS)


def test_skin_quiz():
    assert skin_type_from_quiz([3, 2, 2, 2]) == 'berminyak'
    assert skin_type_from_quiz([2, 1, 1, 1]) == 'kombinasi'
    assert skin_type_from_quiz([0, 0, 2, 0]) == 'kering'
    assert skin_type_from_quiz([1, 0, 2, 0]) == 'normal'
    for bad in ([0, 0, 0], [0, 0, 0, 3], [0, 0, 0, -1], [True, 0, 0, 0], '0000', None):
        try:
            skin_type_from_quiz(bad)
        except ValueError:
            continue
        raise AssertionError(f'harus menolak {bad!r}')


if __name__ == '__main__':
    test_no_face_raises(); test_skin_quiz()
    if os.path.exists(FACE):
        test_face_is_cropped(); test_predict_only_issues()
    else:
        print(f'Tes wajah dilewati: {FACE} tidak ada. Isi WAJAHKU_TEST_FACE dengan path foto wajah.')
    print('ok')
