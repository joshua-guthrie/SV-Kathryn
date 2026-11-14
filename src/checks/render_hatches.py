"""Actual SOMA mesh views of closed/open hatches and opening-support timberwork."""
import json
from pathlib import Path
import vtk
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[2]


def render(filename, mode='closed'):
    parts = json.loads((ROOT / '.soma/model.map.json').read_text())['parts']
    imp = vtk.vtkGLTFImporter()
    imp.SetFileName(str(ROOT / '.soma/model.glb'))
    imp.Update()
    ren = imp.GetRenderer()
    ren.SetBackground(.92, .94, .97)
    actors = ren.GetActors()
    actors.InitTraversal()
    collection = [actors.GetNextActor() for _ in range(actors.GetNumberOfItems())]
    assert len(collection) == 2 * len(parts)
    clip = vtk.vtkPlane()
    clip.SetOrigin(0, 0, 0)
    clip.SetNormal(-1, 0, 0)
    for index, part in enumerate(reversed(parts)):
        name, group = part['name'], part['group']
        pair = collection[2 * index:2 * index + 2]
        assert abs(pair[0].GetBounds()[2] - part['bbox'][0][1]) < .1, name
        for actor in pair:
            actor.GetProperty().SetAmbient(.45)
            actor.GetProperty().SetDiffuse(.55)
            if mode != 'closed' and 'hatch cover' in name:
                actor.SetVisibility(False)
            if group.startswith('Spars'):
                actor.SetVisibility(False)
            if mode == 'frame-plan':
                keep = group == 'Interior/Opening framing' or group == 'Deck/Hatches'
                if 'cover' in name or 'roof' in name:
                    keep = False
                actor.SetVisibility(keep)
            elif mode == 'section':
                if part['group'].startswith('Deck/Planking') or name in ('Painted topsides', 'Underwater hull', 'Cambered deck',
                            'Main hold hatch'):
                    actor.GetMapper().AddClippingPlane(clip)
                if group.startswith('Deck/Rails'):
                    actor.SetVisibility(False)
                if 'Main hold hatch port' in name or 'Forebody port' in name:
                    actor.SetVisibility(False)
            if group == 'Interior/Opening framing':
                actor.GetProperty().SetColor(.67, .40, .18)
    win = vtk.vtkEGLRenderWindow()
    win.SetOffScreenRendering(True)
    win.SetSize(*( (2000, 700) if mode == 'frame-plan' else (1500, 1050) ))
    win.AddRenderer(ren)
    kit = vtk.vtkLightKit()
    kit.SetKeyLightIntensity(1)
    kit.AddLightsToRenderer(ren)
    cam = ren.GetActiveCamera()
    cam.ParallelProjectionOn()
    if mode == 'frame-plan':
        cam.SetPosition(0, 0, 1000)
        cam.SetFocalPoint(0, 0, 0)
        cam.SetViewUp(1, 0, 0)
        cam.SetParallelScale(92)
    elif mode == 'section':
        cam.SetPosition(450, -42, 115)
        cam.SetFocalPoint(0, -57, 45)
        cam.SetViewUp(0, 0, 1)
        cam.SetParallelScale(48)
    else:
        cam.SetPosition(260, 230, 330)
        cam.SetFocalPoint(0, -5, 65)
        cam.SetViewUp(0, 0, 1)
        cam.SetParallelScale(115)
    ren.ResetCameraClippingRange()
    win.Render()
    image = vtk.vtkWindowToImageFilter()
    image.SetInput(win)
    image.Update()
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(ROOT / 'renders' / filename))
    writer.SetInputConnection(image.GetOutputPort())
    writer.Write()
    win.Finalize()
    print(filename)


def main():
    panels = [('hatch-deck-closed.png', 'closed', 'Normal assembly: separate removable hatch boards'),
              ('hatch-deck-open.png', 'open', 'Inspection: covers removed to show the three passages'),
              ('hatch-hold-section.png', 'section', 'Main hold inspection cutaway: shell, opening and support beams'),
              ('hatch-framing-plan.png', 'frame-plan', 'Opening-support subset: hull, deck and covers hidden')]
    for file, mode, _ in panels:
        render(file, mode)
    sheet = Image.new('RGB', (1800, 1360), 'white')
    draw = ImageDraw.Draw(sheet)
    draw.text((20, 15), 'KATHRYN - HATCH OPENINGS AND INDIVIDUAL SUPPORT TIMBERS', fill='black', font_size=25)
    for i, (file, _, caption) in enumerate(panels):
        x, y = i % 2 * 900, 65 + i // 2 * 640
        image = ImageOps.contain(Image.open(ROOT / 'renders' / file).convert('RGB'), (880, 590))
        sheet.paste(image, (x + (900 - image.width) // 2, y + 40 + (590 - image.height) // 2))
        draw.text((x + 12, y + 8), caption, fill='black', font_size=17)
    sheet.save(ROOT / 'renders/hatch-review.png')
    comparison = Image.new('RGB', (2000, 1450), 'white')
    draw = ImageDraw.Draw(comparison)
    for y, file, caption in (
        (0, 'hatch-source-structural-plan.png', 'Original sheet 5 - structural plan'),
        (725, 'hatch-framing-plan.png', 'M1 source-registered opening-support subset - full hull framing belongs to M3'),
    ):
        image = ImageOps.contain(Image.open(ROOT / 'renders' / file).convert('RGB'), (1980, 665))
        comparison.paste(image, ((2000 - image.width) // 2, y + 55 + (665 - image.height) // 2))
        draw.text((20, y + 15), caption, fill='black', font_size=23)
    comparison.save(ROOT / 'renders/hatch-source-comparison.png')
    print('hatch-review.png; hatch-source-comparison.png')


if __name__ == '__main__':
    main()
