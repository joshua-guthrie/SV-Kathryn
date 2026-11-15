"""Build annotated evidence images for the lazyjack gap analysis.

Renders the current SOMA build from .soma/model.glb with the four lazyjack
parts highlighted, and annotates the renders and the source evidence
(S03 rigging sheet and LOC photographs) with the points the analysis
discusses.

    python src/checks/build_lazyjack_gap_assets.py

Requires a successful `soma build`. Writes PNGs to docs/images/lazyjack/.
VTK renders the model; Pillow draws the annotations.
"""
import json
import tempfile
from pathlib import Path

import numpy as np
import vtk
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/images/lazyjack'
FT = 304.8
SIZE = (1600, 1000)
FONT_PATH = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT_REG = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
RED = (0.80, 0.06, 0.05)
RED_PX = (204, 15, 13)
RED_INK = (160, 20, 15)
CYAN = (0.05, 0.42, 0.62)
CYAN_PX = (13, 107, 158)
CYAN_INK = (12, 82, 112)
INK = (25, 25, 25)
LAZY_NAMES = ('Port lazy jack 1', 'Port lazy jack 2',
              'Starboard lazy jack 1', 'Starboard lazy jack 2')
# Current lazyjack endpoints from the built part map (feet), see rigging.py.
TOP_FT = (0.16, -13.29, 17.24)
BOTTOM_FT = [(0.16, 37.80, 13.29), (0.16, 36.50, 13.27),
             (-0.16, 37.80, 13.29), (-0.16, 36.50, 13.27)]
BOOM_TIP_FT = (0, 37.15, 13.28)
# Design stations measured on S03, as fractions of the boom length from the
# aft end; converted to model Y with boom aft end Y=37.3 ft, length 49.33 ft.
BOOM_LENGTH_FT = 51.05
BOOM_AFT_FT = 37.3
S03_FRACTIONS = (.14, .39, .64, .83)


def _font(size, bold=True):
    return ImageFont.truetype(FONT_PATH if bold else FONT_REG, size)


def _hidden(part, prefixes):
    return any(part['name'] == item or part['group'].startswith(item)
               for item in prefixes)


class ModelScene:
    def __init__(self):
        build = json.loads((ROOT / '.soma/build.json').read_text())
        assert build['status'] == 'ok', 'Assets need a successful soma build'
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
        assert len(self.actors) == 2 * len(self.parts), 'Export actor/part count changed'
        self.overlays = []

    def apply_view(self, hide, highlight):
        for index, part in enumerate(reversed(self.parts)):
            pair = self.actors[2 * index:2 * index + 2]
            show = not _hidden(part, hide)
            for actor in pair:
                actor.SetVisibility(show)
                prop = actor.GetProperty()
                prop.SetInterpolationToPhong()
                prop.SetAmbient(.35)
                prop.SetDiffuse(.65)
                if highlight and part['name'] in LAZY_NAMES:
                    prop.SetColor(*RED)
                    prop.SetAmbient(.55)
                    prop.SetDiffuse(.45)

    def lazyjack_endpoints(self):
        by_name = {part['name']: part for part in self.parts}
        result = []
        for name in LAZY_NAMES:
            low, high = by_name[name]['bbox']
            result.append(((low[0], low[1], high[2]), (high[0], high[1], low[2])))
        return result

    def add_overlay(self, p0, p1, radius_ft=.2):
        line = vtk.vtkLineSource()
        line.SetPoint1(*p0)
        line.SetPoint2(*p1)
        tube = vtk.vtkTubeFilter()
        tube.SetInputConnection(line.GetOutputPort())
        tube.SetRadius(radius_ft * FT)
        tube.SetNumberOfSides(12)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(tube.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(*RED)
        actor.GetProperty().SetAmbient(.6)
        actor.GetProperty().SetDiffuse(.4)
        self.renderer.AddActor(actor)
        self.overlays.append(actor)
        for p in (p0, p1):
            sphere = vtk.vtkSphereSource()
            sphere.SetCenter(*p)
            sphere.SetRadius(radius_ft * 1.6 * FT)
            sphere.SetThetaResolution(16)
            sphere.SetPhiResolution(12)
            smapper = vtk.vtkPolyDataMapper()
            smapper.SetInputConnection(sphere.GetOutputPort())
            sactor = vtk.vtkActor()
            sactor.SetMapper(smapper)
            sactor.GetProperty().SetColor(*RED)
            sactor.GetProperty().SetAmbient(.6)
            sactor.GetProperty().SetDiffuse(.4)
            self.renderer.AddActor(sactor)
            self.overlays.append(sactor)

    def clear_overlays(self):
        for actor in self.overlays:
            self.renderer.RemoveActor(actor)
        self.overlays = []

    def render(self, direction, up, focus, scale, hide=(), highlight=True,
               overlay_lines=(), points=()):
        self.apply_view(hide, highlight)
        self.clear_overlays()
        for p0, p1 in overlay_lines:
            self.add_overlay(tuple(np.array(p0) * FT), tuple(np.array(p1) * FT))
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
        display = self.display_points(camera, points)
        window.Finalize()
        return image, display

    def display_points(self, camera, points):
        """World points (feet) to PIL pixel coordinates for the last render."""
        result = []
        for point in points:
            coord = vtk.vtkCoordinate()
            coord.SetCoordinateSystemToWorld()
            coord.SetValue(*[v * FT for v in point])
            x, y = coord.GetComputedDisplayValue(self.renderer)
            result.append((x, SIZE[1] - y))
        return result


def _label(draw, xy, text, font, fill=INK, anchor='la', pad=6):
    box = draw.textbbox((0, 0), text, font=font)
    w, h = box[2] - box[0], box[3] - box[1]
    x, y = xy
    if anchor[0] == 'r':
        x -= w
    elif anchor[0] == 'c':
        x -= w / 2
    if anchor[1] == 'b':
        y -= h
    rect = (x - pad, y - pad, x + w + pad, y + h + pad)
    draw.rounded_rectangle(rect, radius=6, fill=(255, 255, 255, 232),
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


def _dashed(draw, p0, p1, color, width=3, dash=12):
    p0 = np.array(p0, float)
    p1 = np.array(p1, float)
    span = np.linalg.norm(p1 - p0)
    if span < 1:
        return
    v = (p1 - p0) / span
    t = 0.0
    while t < span:
        end = min(t + dash, span)
        draw.line([tuple(p0 + v * t), tuple(p0 + v * end)], fill=color, width=width)
        t = end + dash


def annotate_profile(image, top_px, bottom_px, out_path):
    draw = ImageDraw.Draw(image, 'RGBA')
    _label(draw, (40, 40),
           'Current model — starboard profile, sails hidden (lazyjacks highlighted)',
           _font(26))
    # The design pendant starts at the hounds, far above this frame.
    _arrow(draw, (top_px[0] - 20, 140), (top_px[0] - 8, top_px[1] - 30), RED_PX)
    _label(draw, (top_px[0] - 470, 90),
           'Design pendant starts at the hounds,\nabout 47 ft above this point (off frame)',
           _font(21), fill=RED_INK)
    _arrow(draw, (top_px[0] - 4, top_px[1]),
           (top_px[0] - 330, top_px[1] - 80), RED_PX)
    _label(draw, (top_px[0] - 340, top_px[1] - 175),
           'All four legs start from one point inside the mast,\n'
           'only 5 ft above the boom', _font(21), fill=RED_INK, anchor='ra')
    _arrow(draw, (bottom_px[0] + 6, bottom_px[1] + 6),
           (bottom_px[0] + 260, bottom_px[1] + 140), RED_PX)
    _label(draw, (bottom_px[0] + 270, bottom_px[1] + 130),
           'Both lower ends sit within 1 ft 4 in of each other\nat the boom tip',
           _font(21), fill=RED_INK)
    _label(draw, (40, SIZE[1] - 120),
           'Two straight lines per side, on the centreline: no port/starboard cradle,\n'
           'no legs spread along the boom, and no jib lazyjacks.', _font(21))
    image.save(out_path)


def annotate_plan(image, tip_px, guide_lines_px, stations_px, out_path):
    draw = ImageDraw.Draw(image, 'RGBA')
    _label(draw, (40, 40),
           'Current model — plan over the boom (sails hidden)', _font(26))
    for p0, p1 in guide_lines_px:
        _dashed(draw, p0, p1, CYAN_PX + (215,))
    for point in stations_px:
        draw.ellipse((point[0] - 9, point[1] - 9, point[0] + 9, point[1] + 9),
                     outline=CYAN_PX + (235,), width=3)
    if guide_lines_px:
        _label(draw, (300, 300),
               'Proposed S03 pattern: a leg line each side (±0.8 ft)\n'
               'with four stations spread along the boom', _font(21), fill=CYAN_INK)
    draw.ellipse((tip_px[0] - 80, tip_px[1] - 24, tip_px[0] + 80, tip_px[1] + 24),
                 outline=RED_PX, width=4)
    _label(draw, (tip_px[0] + 100, tip_px[1] + 40),
           'Current: all four legs collapse onto the\ncentreline at the boom tip (±1.9 in)',
           _font(21), fill=RED_INK)
    _label(draw, (40, SIZE[1] - 110),
           'Fix direction: pendant from the hounds with legs to spread stations, port\n'
           'and starboard cradles, plus jib lazyjacks down to the club.', _font(21))
    image.save(out_path)


def annotate_s03(out_path):
    native = Image.open(ROOT / 'references/drawing_package/S03/S03-V01/native.png')
    crop = native.crop((400, 1900, 5900, 5950)).convert('RGB')
    crop = ImageOps.autocontrast(crop, cutoff=1)
    scale = 1700 / crop.width
    crop = crop.resize((1700, int(crop.height * scale)), Image.LANCZOS)
    draw = ImageDraw.Draw(crop, 'RGBA')
    _label(draw, (30, 24), 'S03 rigging sheet — the lazyjack arrangement to match',
           _font(24))

    def sx(x_native):
        return int((x_native - 400) * scale)

    def sy(y_native):
        return int((y_native - 1900) * scale)

    boom_y = sy(5240)
    stations = [1225, 2423, 3734, 4898]
    for x in stations:
        draw.ellipse((sx(x) - 22, boom_y - 22, sx(x) + 22, boom_y + 22),
                     outline=(0, 120, 40), width=4)
    _label(draw, (sx(stations[0]) - 6, boom_y - 105),
           'Legs to stations spread along the boom', _font(19), fill=(0, 105, 35))
    _label(draw, (sx(stations[0]) - 6, boom_y - 70),
           '≈14 / 38 / 65 / 89 % of boom length from the aft end', _font(19),
           fill=(0, 105, 35))
    block_y = sy(5100)
    for x in (1225, 2423):
        draw.ellipse((sx(x) - 26, block_y - 26, sx(x) + 26, block_y + 26),
                     outline=(150, 90, 0), width=4)
    _label(draw, (sx(2423) + 45, block_y - 120),
           'Adjuster blocks above the boom', _font(19), fill=(130, 75, 0))
    junction = (sx(4898), sy(2612))
    draw.ellipse((junction[0] - 34, junction[1] - 34,
                  junction[0] + 34, junction[1] + 34), outline=RED_PX, width=4)
    _label(draw, (junction[0] - 440, junction[1] - 30),
           'Pendant down from the hounds — callout (6)', _font(19), fill=RED_INK)
    draw.line([(sx(553), boom_y), (sx(5427), boom_y)], fill=(0, 0, 0), width=3)
    _label(draw, (sx(553) - 6, boom_y + 96), 'boom aft end', _font(18))
    _label(draw, (sx(5427) - 120, boom_y + 96), 'mast', _font(18))
    crop.save(out_path)


def annotate_photo(out_path):
    photo = Image.open(
        ROOT / 'references/loc_photos/LOC_Kathryn_photos/02-LOC-P01.jpg').convert('L')
    crop = photo.crop((180, 150, 700, 460)).convert('RGB')
    crop = ImageOps.autocontrast(crop, cutoff=1)
    crop = crop.resize((crop.width * 3, crop.height * 3), Image.LANCZOS)
    draw = ImageDraw.Draw(crop, 'RGBA')
    _label(draw, (22, 18),
           'LOC-P01 — the rig with the sails down (Lazyjacks guide the sails to the boom and club)',
           _font(22))
    callouts = [
        ((662, 362, 742, 442), 'Main pendant with adjuster loop', (330, 300)),
        ((560, 655, 640, 735), 'Lines hang outside the furled sail', (250, 590)),
        ((395, 712, 475, 792), 'Legs land at separate stations', (180, 805)),
        ((1090, 650, 1200, 760), 'Jib lazyjacks lead to the club', (1010, 600)),
    ]
    for box, text, label_xy in callouts:
        draw.ellipse(box, outline=RED_PX, width=4)
        _label(draw, label_xy, text, _font(19), fill=RED_INK)
    crop.save(out_path)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    scene = ModelScene()
    as_found = 'Port lazy jack 1' in {p['name'] for p in scene.parts}
    lazy_lines = scene.lazyjack_endpoints() if as_found else []

    if as_found:
        # 1. Starboard profile, sails hidden so the rig reads clearly.
        image, (top_px, bottom_px) = scene.render(
            direction=(-1, 0, .04), up=(0, 0, 1), focus=(0, 11.8, 15), scale=20,
            hide=('Sails',), overlay_lines=lazy_lines, points=(TOP_FT, BOOM_TIP_FT))
        annotate_profile(image, top_px, bottom_px,
                         OUT / 'model-lazyjacks-profile-annotated.png')

        # 2. Plan over the whole boom with the sails hidden.
        stations_ft = [(x, BOOM_AFT_FT - f * BOOM_LENGTH_FT, 12.8)
                       for x in (.8, -.8) for f in S03_FRACTIONS]
        guide_ft = [((x, -12, 12.8), (x, 37.3, 12.8)) for x in (.8, -.8)]
        image, display = scene.render(
            direction=(0, 0, 1), up=(1, 0, 0), focus=(0, 11.7, 16), scale=19,
            hide=('Sails', 'Rigging/Standing', 'Rigging/Fittings'),
            overlay_lines=lazy_lines,
            points=(BOOM_TIP_FT,
                    *[p for pair in guide_ft for p in pair],
                    *stations_ft))
        tip_px = display[0]
        guide_px = display[1:9]
        station_px = display[9:]
        annotate_plan(image, tip_px, [(guide_px[0], guide_px[1]),
                                      (guide_px[2], guide_px[3])],
                      station_px, OUT / 'model-lazyjacks-plan-annotated.png')
    else:
        print('As-found lazyjacks are no longer registered; keeping the '
              'committed as-found figures.')

    # 3. Design and photo evidence.
    annotate_s03(OUT / 'source-s03-lazyjacks-annotated.png')
    annotate_photo(OUT / 'source-loc-p01-lazyjacks-annotated.png')

    for path in sorted(OUT.glob('*.png')):
        print(path.relative_to(ROOT))



if __name__ == "__main__":
    main()
