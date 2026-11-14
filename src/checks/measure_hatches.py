"""Reproducible sheet-4 ruler/footprint measurements on original TIFF geometry."""
import json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
Image.MAX_IMAGE_PIXELS = None


def main():
    path = ROOT / 'references/drawings/master-pnp-habshaer-md-md1400-md1454-sheet-00004a.tif'
    source = Image.open(path)
    sx, sy = source.width / 1440, source.height / 960
    # Coordinates locate native scan points through a documented proportional
    # grid. Conversion uses original pixels, not the resolution of review PNGs.
    zero, ten, fifty = 164.5 * sx, 314.5 * sx, 914.5 * sx
    pixels_per_ft = (fifty - zero) / 50
    assert abs((ten - zero) / pixels_per_ft - 10) < .02
    dpi_check = float(source.info['dpi'][0]) * 3 / 8
    assert abs(pixels_per_ft / dpi_check - 1) < .02
    boxes = {'After deck hatch': (537, 615, 588, 663),
             'Main hold hatch': (754, 590, 837, 688),
             'Forepeak hatch': (861, 585, 891, 616)}
    ledger = {'source': str(path.relative_to(ROOT)), 'view': 'sheet 4 deck plan',
              'native_pixels_per_ft': pixels_per_ft,
              'ruler_0_10_50_native_x': [zero, ten, fifty],
              'dpi_and_printed_scale_check_pixels_per_ft': dpi_check,
              'footprint_pick_uncertainty_ft': .15,
              'longitudinal_registration': 'Existing normalized arrangement centres retained; '
              'raw scaled longitudinal positions are not yet reconciled across all assemblies.',
              'measurements': {}}
    view = source.convert('RGB').resize((1440, 960))
    draw = ImageDraw.Draw(view)
    for name, (x0, y0, x1, y1) in boxes.items():
        length = (x1 - x0) * sx / pixels_per_ft
        width = (y1 - y0) * sy / pixels_per_ft
        ledger['measurements'][name] = {
            'native_box': [x0 * sx, y0 * sy, x1 * sx, y1 * sy],
            'outer_length_ft': length, 'outer_width_ft': width}
        draw.rectangle((x0, y0, x1, y1), outline='red', width=2)
        draw.text((x0, y1 + 5), f'{width:.2f} W x {length:.2f} L ft', fill='red', font_size=13)
        print(f'{name}: {width:.3f} ft across x {length:.3f} ft fore/aft')
    draw.line((164.5, 835, 914.5, 835), fill='red', width=3)
    view.save(ROOT / 'renders/hatch-scale-measurements.png')
    (ROOT / 'src/checks/hatch_measurements.json').write_text(json.dumps(ledger, indent=2) + '\n')
    print('Native ruler calibration:', pixels_per_ft, 'px/ft; printed-scale check:', dpi_check)


if __name__ == '__main__':
    main()
