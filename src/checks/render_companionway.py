"""Closed/open/cutaway access evidence from the current SOMA assembly mesh."""
import json
import sys
from pathlib import Path

import vtk
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from parts import deck, hull
from parts.access import companionway_access
from parts.params import (
    boat_point, MODEL_MM_PER_FOOT, PORT_SIDE, COMPANIONWAY_AFT_FT,
    ACCESS_CLEAR_WIDTH_FT, ACCESS_DOOR_GAP_FT, ACCESS_DOOR_THICKNESS_FT,
)

PARTS = json.loads((ROOT / '.soma/model.map.json').read_text())['parts']


def render(path, opened=False, cutaway=False):
    imp = vtk.vtkGLTFImporter()
    imp.SetFileName(str(ROOT / '.soma/model.glb'))
    imp.Update()
    ren = imp.GetRenderer()
    ren.SetBackground(.92, .94, .97)
    actors = ren.GetActors()
    actors.InitTraversal()
    collection = [actors.GetNextActor() for _ in range(actors.GetNumberOfItems())]
    assert len(collection) == 2 * len(PARTS)
    clip = vtk.vtkPlane()
    clip.SetOrigin(0, 0, 0)
    clip.SetNormal(-1, 0, 0)
    access = companionway_access(hull.deck_height)
    posed = {n: s for n, s, _ in deck.make_companionway_doors(90)}
    for index, part in enumerate(reversed(PARTS)):
        name = part['name']
        pair = collection[2 * index:2 * index + 2]
        assert abs(pair[0].GetBounds()[2] - part['bbox'][0][1]) < .1, name
        for actor in pair:
            actor.GetProperty().SetAmbient(.4)
            actor.GetProperty().SetDiffuse(.6)
            if opened and name in posed:
                side = PORT_SIDE if name.startswith('Port ') else -PORT_SIDE
                pivot = boat_point(side * (ACCESS_CLEAR_WIDTH_FT / 2 - ACCESS_DOOR_GAP_FT),
                                   COMPANIONWAY_AFT_FT - .1 - ACCESS_DOOR_THICKNESS_FT / 2,
                                   access.sill + ACCESS_DOOR_GAP_FT)
                pivot = [v * MODEL_MM_PER_FOOT for v in pivot]
                transform = vtk.vtkTransform()
                transform.Translate(*pivot)
                transform.RotateZ(-side * 90)
                transform.Translate(*[-v for v in pivot])
                actor.SetUserTransform(transform)
            if cutaway:
                if part['group'].startswith('Deck/Planking') or name in {'Painted topsides', 'Underwater hull', 'Cambered deck',
                            'Main cabin', 'Main cabin roof', 'Raised companionway',
                            'Companionway roof', 'Companionway sill', 'Companionway lintel'}:
                    actor.GetMapper().AddClippingPlane(clip)
                if (part['group'].startswith('Spars') or 'stanchion' in name
                        or 'rail' in name or 'strake' in name
                        or name.startswith('Port ') and ('companionway' in name or 'cabin window' in name)):
                    actor.SetVisibility(False)
                if name.startswith('Companionway tread') or name == 'Companionway landing':
                    actor.GetProperty().SetColor(.75, .43, .14)
        if opened and name in posed:
            actual = pair[0].GetBounds()
            expected = posed[name].scale(MODEL_MM_PER_FOOT).BoundingBox()
            expected = (expected.xmin, expected.xmax, expected.ymin, expected.ymax,
                        expected.zmin, expected.zmax)
            assert max(abs(a - e) for a, e in zip(actual, expected)) < .1, name
    window = vtk.vtkEGLRenderWindow()
    window.SetOffScreenRendering(True)
    window.SetSize(1400, 1000)
    window.AddRenderer(ren)
    kit = vtk.vtkLightKit()
    kit.SetKeyLightIntensity(1.0)
    kit.AddLightsToRenderer(ren)
    cam = ren.GetActiveCamera()
    if cutaway:
        cam.SetPosition(450, 185, 117)
        cam.SetFocalPoint(0, 159, 68)
        cam.SetParallelScale(42)
    elif opened:
        cam.SetPosition(150, 410, 170)
        cam.SetFocalPoint(0, 163, 76)
        cam.SetParallelScale(46)
    else:
        cam.SetPosition(300, 360, 220)
        cam.SetFocalPoint(0, 145, 85)
        cam.SetParallelScale(55)
    cam.SetViewUp(0, 0, 1)
    cam.ParallelProjectionOn()
    ren.ResetCameraClippingRange()
    window.Render()
    capture = vtk.vtkWindowToImageFilter()
    capture.SetInput(window)
    capture.Update()
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(ROOT / path))
    writer.SetInputConnection(capture.GetOutputPort())
    writer.Write()
    window.Finalize()
    print(path)


def main():
    before = ROOT / 'renders/kathryn-companionway-before.png'
    if not before.exists():
        Image.open(ROOT / 'renders/kathryn-cabin-detail.png').save(before)
    render('renders/kathryn-cabin-detail.png')
    render('renders/kathryn-companionway-open.png', opened=True)
    render('renders/kathryn-companionway-cutaway.png', opened=True, cutaway=True)
    Image.MAX_IMAGE_PIXELS = None
    source = Image.open(ROOT / 'references/drawings/master-pnp-habshaer-md-md1400-md1454-sheet-00004a.tif')
    source.crop((3450, 2800, 5350, 4450)).save(ROOT / 'renders/kathryn-access-source-profile.png')
    source.crop((3400, 5600, 5300, 7150)).save(ROOT / 'renders/kathryn-access-source-plan.png')
    panels = [
        ('kathryn-companionway-before.png', 'Before: upper-only door, solid access path'),
        ('kathryn-cabin-detail.png', 'After: paired doors down to the low deck sill'),
        ('kathryn-companionway-open.png', 'Inspection pose: both leaves open 90 degrees'),
        ('kathryn-companionway-cutaway.png', 'Inspection cutaway: near-side shell removed; supported steps and landing'),
    ]
    sheet = Image.new('RGB', (1600, 1280), 'white')
    draw = ImageDraw.Draw(sheet)
    draw.text((24, 16), 'KATHRYN - COMPANIONWAY ACCESS CORRECTION', fill='black', font_size=26)
    for index, (file, caption) in enumerate(panels):
        x, y = (index % 2) * 800, 65 + (index // 2) * 600
        image = ImageOps.contain(Image.open(ROOT / 'renders' / file).convert('RGB'), (790, 555))
        sheet.paste(image, (x + (800 - image.width) // 2, y + 35))
        draw.text((x + 12, y + 4), caption, fill='black', font_size=17)
    sheet.save(ROOT / 'renders/kathryn-companionway-review.png')
    print('renders/kathryn-companionway-review.png')
    comparison = Image.new('RGB', (1500, 1700), 'white')
    draw = ImageDraw.Draw(comparison)
    for y, file, caption in (
        (0, 'kathryn-access-source-profile.png', 'Original sheet 4 - inboard profile and steep companion steps'),
        (850, 'kathryn-companionway-cutaway.png', 'Corrected CAD - inspection cutaway, paired doors open'),
    ):
        image = ImageOps.contain(Image.open(ROOT / 'renders' / file).convert('RGB'), (1480, 800))
        comparison.paste(image, ((1500 - image.width) // 2, y + 45))
        draw.text((20, y + 10), caption, fill='black', font_size=24)
    comparison.save(ROOT / 'renders/kathryn-companionway-source-comparison.png')
    print('renders/kathryn-companionway-source-comparison.png')


if __name__ == '__main__':
    main()
