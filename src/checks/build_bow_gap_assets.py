"""Build annotated evidence images for the bowsprit/trailboard/jib gap analysis.

Renders the current SOMA build from .soma/model.glb with the bowsprit, jib,
jib club, trailboards and heel fittings highlighted, and annotates the renders
and the source evidence (S01-V03, S03-V01, S04-V01, LOC-P22).

    python src/checks/build_bow_gap_assets.py

Requires a successful `soma build`. Writes PNGs to docs/images/bowsprit/.
"""
import json
import tempfile
from pathlib import Path

import numpy as np
import vtk
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/images/bowsprit'
FT = 304.8
SIZE = (1600, 1000)
FONT_PATH = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT_REG = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
RED = (0.82, 0.08, 0.05)
RED_PX = (201, 18, 12)
RED_INK = (160, 20, 15)
BLUE_PX = (8, 92, 158)
BLUE_INK = (8, 82, 140)
GREEN_PX = (16, 120, 55)
GREEN_INK = (10, 100, 45)
PURPLE_PX = (112, 40, 150)
PURPLE_INK = (95, 30, 130)
ORANGE_PX = (196, 102, 0)
ORANGE_INK = (150, 80, 0)
INK = (25, 25, 25)

HILITE = {
    'Bowsprit': RED,
    'Jib sail (S08 demonstration)': (0.05, 0.45, 0.75),
    'Jib club': (0.45, 0.12, 0.60),
    'Centreline carved trailboard': (0.08, 0.55, 0.18),
    'Port projecting headrail': (0.95, 0.55, 0.10),
    'Starboard projecting headrail': (0.95, 0.55, 0.10),
    'Samson post': (0.60, 0.15, 0.65),
    'Bowsprit heel saddle': (0.10, 0.45, 0.85),
    'Bowsprit heel bearing cross-timber': (0.10, 0.65, 0.80),
    'Bowsprit cross-bearer 1': (0.10, 0.75, 0.35),
    'Oak stem knee with Samson-post mortise': (0.35, 0.35, 0.35),
    'Painted stem and cutwater': (0.45, 0.45, 0.45),
}

# Bow geometry, feet and model Y (bow -Y).
BOWSPRIT_TIP_FT = (0, -39.24, 11.26)
BOWSPRIT_HEEL_FT = (0, -27.75, 10.57)
JIB_TACK_FT = (0, -39.23, 11.26)
JIB_CLEW_FT = (0, -13.59, 10.22)
CLUB_AFT_FT = (0, -16.61, 11.96)
CLUB_FORE_FT = (0, -24.97, 12.76)
TRAILBOARD_FT = (0, -30.0, 9.4)
SAMSON_FT = (0, -20.72, 10.79)
STEM_HEAD_FT = (0, -24.6, 8.15)
SADDLE_FT = (0, -27.77, 10.17)
CROSS_BEARER_FT = (0, -27.77, 10.4)
HEEL_RAIL_FT = (1.51, -27.77, 9.91)
JIB_INTERSECTION_FT = (0, -33.0, 10.97)
TRAVELLER_FT = (0, -16.6, 8.7)


def _font(size, bold=True):
    return ImageFont.truetype(FONT_PATH if bold else FONT_REG, size)


def _hidden(part, prefixes):
    return any(part['name'] == item or part['group'].startswith(item)
               for item in prefixes)


class ModelScene:
    def __init__(self):
        build = json.loads((ROOT / '.soma/build.json').read_text())
        assert build['status'] == 'ok'
        self.parts = json.loads((ROOT / '.soma/model.map.json').read_text())['parts']
        importer = vtk.vtkGLTFImporter()
        importer.SetFileName(str(ROOT / '.soma/model.glb'))
        importer.Update()
        self.renderer = importer.GetRenderer()
        self.renderer.SetBackground(.95, .96, .98)
        self.renderer.SetTwoSidedLighting(True)
        actors = self.renderer.GetActors()
        actors.InitTraversal()
        self.actors = [actors.GetNextActor() for _ in range(actors.GetNumberOfItems())]
        assert len(self.actors) == 2 * len(self.parts)

    def apply(self, hide=(), jib_opacity=1.0):
        for index, part in enumerate(reversed(self.parts)):
            pair = self.actors[2 * index:2 * index + 2]
            show = not _hidden(part, hide)
            for actor in pair:
                actor.SetVisibility(show)
                prop = actor.GetProperty()
                prop.SetInterpolationToPhong()
                prop.SetAmbient(.38)
                prop.SetDiffuse(.62)
                prop.SetOpacity(1.0)
                if part['name'] in HILITE:
                    prop.SetColor(*HILITE[part['name']])
                    prop.SetAmbient(.60)
                if part['name'] == 'Jib sail (S08 demonstration)':
                    prop.SetOpacity(jib_opacity)

    def render(self, direction, up, focus, scale, hide=(), jib_opacity=1.0,
               points=()):
        self.apply(hide, jib_opacity)
        camera = self.renderer.GetActiveCamera()
        camera.ParallelProjectionOn()
        direction = np.array(direction, float)
        direction /= np.linalg.norm(direction)
        focus = np.array(focus, float) * FT
        camera.SetFocalPoint(*focus)
        camera.SetPosition(*(focus + direction * 200000))
        camera.SetViewUp(*up)
        camera.SetParallelScale(scale * FT)
        self.renderer.ResetCameraClippingRange()
        window = vtk.vtkEGLRenderWindow()
        window.SetOffScreenRendering(True)
        window.SetSize(*SIZE)
        window.AddRenderer(self.renderer)
        vtk.vtkLightKit().AddLightsToRenderer(self.renderer)
        self.renderer.SetLightFollowCamera(True)
        window.Render()
        tmp = Path(tempfile.mkstemp(suffix='.png')[1])
        capture = vtk.vtkWindowToImageFilter()
        capture.SetInput(window)
        capture.Update()
        writer = vtk.vtkPNGWriter()
        writer.SetFileName(str(tmp))
        writer.SetInputConnection(capture.GetOutputPort())
        writer.Write()
        image = Image.open(tmp).convert('RGB')
        image.load()
        tmp.unlink()
        display = []
        for point in points:
            coord = vtk.vtkCoordinate()
            coord.SetCoordinateSystemToWorld()
            coord.SetValue(*[v * FT for v in point])
            x, y = coord.GetComputedDisplayValue(self.renderer)
            display.append((x, SIZE[1] - y))
        window.Finalize()
        return image, display


def _label(draw, xy, text, font, fill=INK, pad=6):
    box = draw.textbbox((0, 0), text, font=font)
    w, h = box[2] - box[0], box[3] - box[1]
    x, y = xy
    if x + w + 2 * pad > SIZE[0]:
        x = SIZE[0] - w - 2 * pad
    if x < pad:
        x = pad
    if y < pad:
        y = pad
    rect = (x - pad, y - pad, x + w + pad, y + h + pad)
    draw.rounded_rectangle(rect, radius=6, fill=(255, 255, 255, 235),
                           outline=fill, width=2)
    draw.text((x, y), text, font=font, fill=fill)


def _arrow(draw, tip, tail, color, width=4):
    draw.line([tail, tip], fill=color, width=width)
    v = np.array(tip, float) - np.array(tail, float)
    if np.linalg.norm(v) < 1:
        return
    v /= np.linalg.norm(v)
    n = np.array([-v[1], v[0]])
    base = np.array(tip, float) - v * 16
    for sign in (-1, 1):
        draw.line([tip, tuple(base + n * 9 * sign)], fill=color, width=width)


def annotate_model_profile(image, px, out_path):
    draw = ImageDraw.Draw(image, 'RGBA')
    title = _font(25)
    body = _font(20)
    _label(draw, (36, 34),
           'Current model — bow, starboard profile (jib shown semi-transparent)', title)
    _arrow(draw, px['intersection'], (px['intersection'][0] + 150, px['intersection'][1] - 90), RED_PX)
    _label(draw, (px['intersection'][0] + 160, px['intersection'][1] - 150),
           'The jib plate is on the centreline; its foot passes\n'
           'through the bowsprit along almost the whole spar.', body, fill=RED_INK)
    club_mid = ((px['club_aft'][0] + px['club_fore'][0]) / 2,
                (px['club_aft'][1] + px['club_fore'][1]) / 2)
    _arrow(draw, club_mid, (260, 470), PURPLE_PX)
    _label(draw, (40, 480),
           'Jib club floats 1.6–2.1 ft above the sail foot\nand has no sail attached to it.', body,
           fill=PURPLE_INK)
    _arrow(draw, px['trailboard'], (px['trailboard'][0] - 60, px['trailboard'][1] + 130), GREEN_PX)
    _label(draw, (px['trailboard'][0] - 80, px['trailboard'][1] + 140),
           'One centreline trailboard, 11.9 ft long,\nunder the bowsprit like a shelf.', body,
           fill=GREEN_INK)
    _arrow(draw, px['samson'], (px['samson'][0] + 40, px['samson'][1] - 110), ORANGE_PX)
    _label(draw, (px['samson'][0] - 30, px['samson'][1] - 190),
           'Samson post is about 7 ft aft of the heel;\n'
           'the drawing and photo put it beside the heel.', body, fill=ORANGE_INK)
    image.save(out_path)


def annotate_model_nojib(image, px, out_path):
    draw = ImageDraw.Draw(image, 'RGBA')
    title = _font(25)
    body = _font(20)
    _label(draw, (36, 34), 'Current model — bow, jib hidden, attachment details', title)
    _arrow(draw, px['saddle'], (px['saddle'][0] + 170, px['saddle'][1] - 140), BLUE_PX)
    _label(draw, (px['saddle'][0] + 180, px['saddle'][1] - 190),
           'Heel saddle, cross-timber and cross-bearer\n'
           'bear on the headrails, not on the stem head', body, fill=BLUE_INK)
    _arrow(draw, px['stem_head'], (px['stem_head'][0] - 90, px['stem_head'][1] + 100), (70, 70, 70))
    _label(draw, (px['stem_head'][0] - 360, px['stem_head'][1] + 110),
           'Stem head/knee tops out about 1.5 ft below\nthe heel saddle (model gap)', body,
           fill=(60, 60, 60))
    _arrow(draw, px['heel'], (px['heel'][0] + 120, px['heel'][1] + 170), RED_PX)
    _label(draw, (px['heel'][0] + 130, px['heel'][1] + 180),
           'No fid through the heel mortise; the photo\nshows a pin through the bowsprit heel', body,
           fill=RED_INK)
    _label(draw, (36, SIZE[1] - 120),
           'Attachment parts that do exist: walking boards, three cross-bearers,\n'
           'heel/stem-head bands, bobstays and side shrouds. See LOC-P22.', body)
    image.save(out_path)


def annotate_model_top(image, px, out_path):
    draw = ImageDraw.Draw(image, 'RGBA')
    title = _font(25)
    body = _font(20)
    _label(draw, (36, 34), 'Current model — plan over the bowsprit', title)
    _arrow(draw, px['trailboard'], (px['trailboard'][0] - 180, px['trailboard'][1] + 170), GREEN_PX)
    _label(draw, (px['trailboard'][0] - 450, px['trailboard'][1] + 180),
           'The trailboard is one thin centreline fin;\n'
           'it should be port/starboard boards on the bow faces', body, fill=GREEN_INK)
    _arrow(draw, px['traveller'], (px['traveller'][0] + 220, px['traveller'][1] + 120), PURPLE_PX)
    _label(draw, (px['traveller'][0] + 230, px['traveller'][1] + 130),
           'Jib sheet traveller and jib club are on the\n'
           'centreline aft of the stem (club not in this crop)', body, fill=PURPLE_INK)
    image.save(out_path)


def annotate_floating(image, px, out_path):
    draw = ImageDraw.Draw(image, 'RGBA')
    title = _font(25)
    body = _font(20)
    _label(draw, (36, 34),
           'Current model — why the bowsprit looks unsupported at the heel', title)
    _arrow(draw, px['saddle'], (px['saddle'][0] - 60, px['saddle'][1] - 150), RED_PX)
    _label(draw, (px['saddle'][0] - 330, px['saddle'][1] - 260),
           'Heel saddle sits 3.2 ft forward of the stem head\n'
           'and 1.5 ft above the stem knee; no stem-head timber is beneath it', body, fill=RED_INK)
    _arrow(draw, px['stem_head'], (px['stem_head'][0] - 140, px['stem_head'][1] + 80), (80, 80, 80))
    _label(draw, (px['stem_head'][0] - 470, px['stem_head'][1] + 90),
           'Stem head/knee ends here', body, fill=(60, 60, 60))
    _arrow(draw, px['trailboard'], (px['trailboard'][0] + 120, px['trailboard'][1] + 160), GREEN_PX)
    _label(draw, (px['trailboard'][0] + 130, px['trailboard'][1] + 170),
           'The only trailboard is this centreline shelf under the\n'
           'bowsprit; it bridges the gap and hides the missing support.', body, fill=GREEN_INK)
    _arrow(draw, px['samson'], (px['samson'][0] + 130, px['samson'][1] + 170), PURPLE_PX)
    _label(draw, (px['samson'][0] + 140, px['samson'][1] + 180),
           'Samson post 7 ft aft of the heel;\nthe photo puts it beside the heel', body, fill=PURPLE_INK)
    _label(draw, (36, SIZE[1] - 110),
           'Support path: heel saddle -> cross-bearer -> headrails. There is no knee or\n'
           'stem-head timber under the heel, so the platform reads as floating.', body)
    image.save(out_path)


def annotate_s01(out_path):
    native = Image.open(ROOT / 'references/drawing_package/S01/S01-V03/native.png')
    crop = native.crop((0, 0, 3400, 2050)).convert('RGB')
    crop = ImageOps.autocontrast(crop, cutoff=1)
    crop = crop.resize((1500, int(crop.height * 1500 / crop.width)), Image.LANCZOS)
    draw = ImageDraw.Draw(crop, 'RGBA')
    title = _font(23)
    body = _font(19)
    _label(draw, (20, 14),
           'S01-V03 — trailboard, headrail and chains, bow ornament detail', title)
    calls = [
        ((520, 85, 1480, 215), 'Bowsprit', RED_INK, (930, 20)),
        ((385, 145, 425, 350), 'Fid/pin through the heel', GREEN_INK, (30, 55)),
        ((0, 205, 1455, 285), 'Headrail above the trailboard', ORANGE_INK, (30, 300)),
        ((140, 355, 1160, 475), 'Carved trailboard and KATHRYN on the bow side',
         GREEN_INK, (140, 490)),
        ((100, 480, 1495, 820), 'Bowsprit shroud chains below the headrail', BLUE_INK, (760, 845)),
    ]
    for (x0, y0, x1, y1), text, color, label_xy in calls:
        draw.rectangle((x0, y0, x1, y1), outline=color, width=4)
        _label(draw, label_xy, text, body, fill=color)
    crop.save(out_path)


def annotate_s03(out_path):
    native = Image.open(ROOT / 'references/drawing_package/S03/S03-V01/native.png')
    crop = native.crop((6700, 4200, 9500, 6300)).convert('RGB')
    crop = ImageOps.autocontrast(crop, cutoff=1)
    crop = crop.resize((1400, int(crop.height * 1400 / crop.width)), Image.LANCZOS)
    draw = ImageDraw.Draw(crop, 'RGBA')
    title = _font(23)
    body = _font(19)
    _label(draw, (20, 18), 'S03-V01 — bowsprit, headrails and stays at the bow', title)
    calls = [
        ((20, 540, 360, 700), 'Heel extends inboard of the stem head', RED_INK),
        ((450, 620, 1350, 800), 'Headrails run out under the spar', ORANGE_INK),
        ((700, 300, 1350, 620), 'Jib stay and bobstay to the tip', BLUE_INK),
    ]
    label_pos = [(30, 760), (470, 820), (760, 250)]
    for (box, text, color), xy in zip(calls, label_pos):
        draw.rectangle(box, outline=color, width=4)
        _label(draw, xy, text, body, fill=color)
    crop.save(out_path)


def annotate_p22(out_path):
    photo = Image.open(
        ROOT / 'references/loc_photos/LOC_Kathryn_photos/23-LOC-P22.jpg').convert('L')
    crop = photo.crop((60, 250, 560, 830)).convert('RGB')
    crop = ImageOps.autocontrast(crop, cutoff=1)
    crop = crop.resize((crop.width * 3, crop.height * 3), Image.LANCZOS)
    draw = ImageDraw.Draw(crop, 'RGBA')
    title = _font(24)
    body = _font(19)
    _label(draw, (16, 14), 'LOC-P22 — bowsprit heel, cross-timber and Samson post', title)
    calls = [
        ((120, 40, 750, 260), 'Bowsprit', RED_INK, (900, 60)),
        ((360, 430, 1060, 690), 'Cross-timber bed under the heel', ORANGE_INK, (60, 760)),
        ((420, 500, 620, 610), 'Mortise/fid through the heel', GREEN_INK, (700, 1050)),
        ((1130, 800, 1500, 1600), 'Samson post beside the heel', PURPLE_INK, (760, 1250)),
        ((150, 280, 420, 820), 'Walking boards and headrail', BLUE_INK, (30, 1350)),
    ]
    for (x0, y0, x1, y1), text, color, label_xy in calls:
        draw.rectangle((x0, y0, x1, y1), outline=color, width=4)
        _label(draw, label_xy, text, body, fill=color)
    crop.save(out_path)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    scene = ModelScene()
    points = (BOWSPRIT_TIP_FT, BOWSPRIT_HEEL_FT, JIB_TACK_FT, JIB_CLEW_FT,
              CLUB_AFT_FT, CLUB_FORE_FT, TRAILBOARD_FT, SAMSON_FT,
              STEM_HEAD_FT, SADDLE_FT, CROSS_BEARER_FT, HEEL_RAIL_FT,
              JIB_INTERSECTION_FT, TRAVELLER_FT)
    names = ('tip', 'heel', 'tack', 'clew', 'club_aft', 'club_fore',
             'trailboard', 'samson', 'stem_head', 'saddle', 'cross_bearer',
             'heel_rail', 'intersection', 'traveller')
    image, display = scene.render(
        direction=(-1, 0, .03), up=(0, 0, 1), focus=(0, -30, 9.0), scale=8.5,
        jib_opacity=.30, points=points)
    px = dict(zip(names, display))
    annotate_model_profile(image, px, OUT / 'model-bow-profile-annotated.png')

    image, display = scene.render(
        direction=(-1, 0, .03), up=(0, 0, 1), focus=(0, -30, 9.0), scale=8.5,
        hide=('Jib sail (S08 demonstration)',), jib_opacity=1.0, points=points)
    px = dict(zip(names, display))
    annotate_model_nojib(image, px, OUT / 'model-bow-nojib-annotated.png')

    image, display = scene.render(
        direction=(0, -.05, 1), up=(0, 1, 0), focus=(0, -32, 10.5), scale=7.0,
        hide=('Jib sail (S08 demonstration)',), points=points)
    px = dict(zip(names, display))
    annotate_model_top(image, px, OUT / 'model-bow-top-annotated.png')

    image, display = scene.render(
        direction=(-.9, .5, .55), up=(0, 0, 1), focus=(0, -27, 9.8), scale=6.0,
        hide=('Jib sail (S08 demonstration)',), points=points)
    px = dict(zip(names, display))
    annotate_floating(image, px, OUT / 'model-bow-floating-annotated.png')

    annotate_s01(OUT / 'source-s01-trailboard-annotated.png')
    annotate_s03(OUT / 'source-s03-bow-annotated.png')
    annotate_p22(OUT / 'source-loc-p22-heel-annotated.png')
    # Side-by-side trailboard comparison.
    top = Image.open(OUT / 'source-s01-trailboard-annotated.png').convert('RGB')
    bottom = Image.open(OUT / 'model-bow-floating-annotated.png').convert('RGB')
    width = 1500
    top = top.resize((width, int(top.height * width / top.width)), Image.LANCZOS)
    bottom = bottom.resize((width, int(bottom.height * width / bottom.width)),
                           Image.LANCZOS)
    header = 46
    gap = 16
    canvas = Image.new('RGB', (width + 40, header + top.height + gap + header
                               + bottom.height + 20), (245, 245, 245))
    cdraw = ImageDraw.Draw(canvas)
    cdraw.text((20, 10), 'DRAWING — S01-V03: carved trailboard on the bow side',
               font=_font(26), fill=GREEN_INK)
    canvas.paste(top, (20, header))
    y2 = header + top.height + gap
    cdraw.text((20, y2 + 8),
               'MODEL — one centreline trailboard under the bowsprit',
               font=_font(26), fill=GREEN_INK)
    canvas.paste(bottom, (20, y2 + header))
    canvas.save(OUT / 'trailboard-comparison-annotated.png')


    for path in sorted(OUT.glob('*.png')):
        print(path.relative_to(ROOT))


if __name__ == '__main__':
    main()
