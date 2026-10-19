import os

from PIL import Image
from services.acne import analyze_acne, detect_acne, severity
from services.face import crop_face

FACE = os.environ.get('WAJAHKU_TEST_FACE', 'static/uploads/35815aad-fec2-4f7c-9861-bea675f4dea2.jpg')


def test_severity():
    assert [severity(n) for n in (0, 1, 10, 11, 40, 41, 100, 101)] == \
        ['tidak ada', 'ringan', 'ringan', 'sedang', 'sedang', 'berat', 'berat', 'sangat berat']


def test_plain_image_has_no_acne():
    assert detect_acne(Image.new('RGB', (500, 400), (200, 170, 150))) == []


def test_boxes_inside_face():
    face = crop_face(Image.open(FACE).convert('RGB'))
    for x0, y0, x1, y1, p in detect_acne(face):
        assert 0 <= x0 < x1 <= face.width + 1 and 0 <= y0 < y1 <= face.height + 1 and 0 < p <= 1


def test_analyze_acne_relative_boxes():
    r = analyze_acne(FACE)
    assert r['count'] == len(r['boxes']) and r['severity'] == severity(r['count'])
    assert all(0 <= x0 < x1 <= 1.001 and 0 <= y0 < y1 <= 1.001 for x0, y0, x1, y1, _ in r['boxes']), r


if __name__ == '__main__':
    test_severity(); test_plain_image_has_no_acne()
    if os.path.exists(FACE):
        test_boxes_inside_face(); test_analyze_acne_relative_boxes()
    else:
        print(f'Tes wajah dilewati: {FACE} tidak ada. Isi WAJAHKU_TEST_FACE dengan path foto wajah.')
    print('ok')
