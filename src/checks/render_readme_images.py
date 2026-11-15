"""Render the README gallery from the current SOMA export.

Run after `soma build`. Reads the viewer GLB and part map in .soma/, so the
pictures always match the built model. Exterior views show the whole vessel;
the section views clip the model to expose the hold, cabin and centreline.

    python src/checks/render_readme_images.py
    python src/checks/render_readme_images.py --only section-cabin

Requires VTK (the SOMA Python environment has it; otherwise `pip install vtk`).
"""
import argparse
import json
from pathlib import Path

import numpy as np
import vtk

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/images'
FT = 304.8
SIZE = (1600, 1000)
SAILS = ('Main sail (S08 demonstration)', 'Jib sail (S08 demonstration)')

VIEWS = (
    dict(name='bow', direction=(0, -1, 0), up=(0, 0, 1), hide=()),
    dict(name='stern', direction=(0, 1, 0), up=(0, 0, 1), hide=()),
    dict(name='port-side', direction=(1, 0, 0), up=(0, 0, 1), hide=()),
    dict(name='starboard-side', direction=(-1, 0, 0), up=(0, 0, 1), hide=()),
    dict(name='bow-quarter', direction=(1, -1, .45), up=(0, 0, 1), hide=()),
    dict(name='stern-quarter', direction=(1, 1, .45), up=(0, 0, 1), hide=()),
    dict(name='plan', direction=(0, 0, 1), up=(0, -1, 0),
         hide=('Rigging', 'Spars') + SAILS),
    dict(name='section-centreline', direction=(-1, 0, 0), up=(0, 0, 1),
         hide=('Rigging', 'Spars') + SAILS, clip=((0, 0, 0), (1, 0, 0))),
    dict(name='section-hold', direction=(0, 1, 0), up=(0, 0, 1),
         hide=('Rigging', 'Spars') + SAILS, clip=((0, -5 * FT, 0), (0, -1, 0))),
    dict(name='interior-cutaway', direction=(-1, -1, .55), up=(0, 0, 1),
         hide=('Rigging', 'Spars') + SAILS, clip=((0, 0, 0), (1, 0, 0))),
)


def _hidden(part, prefixes):
    return any(part['name'] == item or part['group'].startswith(item)
               for item in prefixes)


def _bounds(parts, clip):
    low = np.min([part['bbox'][0] for part in parts], axis=0)
    high = np.max([part['bbox'][1] for part in parts], axis=0)
    if clip:
        origin, normal = np.array(clip[0], float), np.array(clip[1], float)
        axis = int(np.argmax(np.abs(normal)))
        if normal[axis] > 0:
            low[axis] = max(low[axis], origin[axis])
        else:
            high[axis] = min(high[axis], origin[axis])
    return low, high


def render(view):
    build = json.loads((ROOT / '.soma/build.json').read_text())
    assert build['status'] == 'ok', 'Render needs a successful soma build'
    parts = json.loads((ROOT / '.soma/model.map.json').read_text())['parts']
    importer = vtk.vtkGLTFImporter()
    importer.SetFileName(str(ROOT / '.soma/model.glb'))
    importer.Update()
    renderer = importer.GetRenderer()
    renderer.SetBackground(.95, .96, .98)
    renderer.SetTwoSidedLighting(True)
    actors = renderer.GetActors()
    actors.InitTraversal()
    collection = [actors.GetNextActor() for _ in range(actors.GetNumberOfItems())]
    assert len(collection) == 2 * len(parts), 'Export actor/part count changed'

    plane = None
    if view.get('clip'):
        plane = vtk.vtkPlane()
        plane.SetOrigin(*view['clip'][0])
        plane.SetNormal(*view['clip'][1])

    visible = []
    for index, part in enumerate(reversed(parts)):
        pair = collection[2 * index:2 * index + 2]
        show = not _hidden(part, view['hide'])
        if show:
            visible.append(part)
        for actor in pair:
            actor.SetVisibility(show)
            prop = actor.GetProperty()
            prop.SetInterpolationToPhong()
            prop.SetAmbient(.35)
            prop.SetDiffuse(.65)
            if plane is not None:
                actor.GetMapper().AddClippingPlane(plane)
    assert visible, 'No visible parts'

    low, high = _bounds(visible, view.get('clip'))
    focus = (low + high) / 2
    direction = np.array(view['direction'], float)
    direction /= np.linalg.norm(direction)
    camera = renderer.GetActiveCamera()
    camera.ParallelProjectionOn()
    camera.SetFocalPoint(*focus)
    camera.SetPosition(*(focus + direction * np.linalg.norm(high - low) * 3))
    camera.SetViewUp(*view['up'])
    renderer.ResetCamera(low[0], high[0], low[1], high[1], low[2], high[2])
    camera.Zoom(1.06)
    renderer.ResetCameraClippingRange()

    window = vtk.vtkEGLRenderWindow()
    window.SetOffScreenRendering(True)
    window.SetSize(*SIZE)
    window.AddRenderer(renderer)
    vtk.vtkLightKit().AddLightsToRenderer(renderer)
    renderer.SetLightFollowCamera(True)
    window.Render()
    capture = vtk.vtkWindowToImageFilter()
    capture.SetInput(window)
    capture.Update()
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f'{view["name"]}.png'
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(path))
    writer.SetInputConnection(capture.GetOutputPort())
    writer.Write()
    window.Finalize()
    print(path.relative_to(ROOT), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only', action='append', default=[],
                        help='render only these view names (repeatable)')
    options = parser.parse_args()
    selected = [view for view in VIEWS
                if not options.only or view['name'] in options.only]
    assert selected, f'Unknown view(s): {options.only}'
    for view in selected:
        render(view)


if __name__ == '__main__':
    main()
