"""Preserve enlarged, unmodified-source evidence for the hatch/framing review."""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
Image.MAX_IMAGE_PIXELS = None


def crop(sheet, box, output, size):
    source = Image.open(ROOT / 'references/drawings' /
                        f'master-pnp-habshaer-md-md1400-md1454-sheet-{sheet:05d}a.tif')
    # Boxes are located on the existing 1440 x 960 review thumbnails.
    box = tuple(round(v * (source.width / 1440 if i % 2 == 0 else source.height / 960))
                for i, v in enumerate(box))
    detail = source.crop(box).convert('RGB')
    detail.thumbnail(size)
    detail.save(ROOT / 'renders' / output)
    print(output)


if __name__ == '__main__':
    crop(5, (125, 95, 970, 365), 'hatch-source-structural-plan.png', (2700, 1000))
    crop(5, (830, 650, 1085, 810), 'hatch-source-beam-notes.png', (1500, 1100))
    crop(5, (1090, 62, 1340, 165), 'hatch-source-deck-notes.png', (1500, 800))
    crop(4, (510, 570, 940, 705), 'hatch-source-deck-plan.png', (2400, 1000))
    crop(4, (500, 280, 950, 425), 'hatch-source-inboard-profile.png', (2400, 1000))
    crop(7, (260, 430, 550, 585), 'hatch-source-cabin-roof-support.png', (1800, 1100))
    crop(4, (135, 805, 1310, 875), 'hatch-source-scale-sheet4.png', (3500, 700))
    crop(5, (115, 805, 1085, 875), 'hatch-source-scale-sheet5.png', (3500, 700))
