"""Coordinate grids for checking the representative section traces."""
import json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'drawing_package'


def main():
    manifest = json.loads((PACKAGE / 'manifest.json').read_text())
    folder = PACKAGE / 'demos'
    folder.mkdir(exist_ok=True)
    for view_id in ('S06-V01', 'S07-V02'):
        view = next(v for v in manifest['views'] if v['id'] == view_id)
        image = Image.open(PACKAGE / view['preview']).convert('RGB')
        draw = ImageDraw.Draw(image)
        for x in range(0, image.width, 100):
            draw.line((x, 0, x, image.height), fill='#e5a2a2')
            draw.text((x + 2, 4), str(x), fill='#b00000', font_size=18)
        for y in range(0, image.height, 100):
            draw.line((0, y, image.width, y), fill='#a2bce5')
            draw.text((3, y + 4), str(y), fill='#004090', font_size=18)
        image.save(folder / f'{view_id}-pixel-grid.png')
        print(view_id, view['native_box'], view['preview_size'])


if __name__ == '__main__':
    main()
