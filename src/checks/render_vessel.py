"""Render the actual SOMA export without the interior helpers' mast clipping.

This offline fallback does not change SOMA's viewer state or model geometry.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import vtk

ROOT = Path(__file__).resolve().parents[1]
DIRECTIONS = {"iso": (1, 1, .65), "side": (1, 0, 0),
              "aft": (0, 1, .25), "plan": (0, 0, 1)}


def render(out, view="iso", region="all", hide=()):
    build = json.loads((ROOT / ".soma/build.json").read_text())
    assert build["status"] == "ok", "Render requires a successful SOMA build"
    parts = json.loads((ROOT / ".soma/model.map.json").read_text())["parts"]
    importer = vtk.vtkGLTFImporter()
    importer.SetFileName(str(ROOT / ".soma/model.glb"))
    importer.Update()
    renderer = importer.GetRenderer()
    renderer.SetBackground(.94, .96, .98)
    actors = renderer.GetActors()
    actors.InitTraversal()
    collection = [actors.GetNextActor() for _ in range(actors.GetNumberOfItems())]
    assert len(collection) == 2 * len(parts), "Export actor/part count changed"
    visible = []
    for index, part in enumerate(reversed(parts)):
        pair = collection[2 * index:2 * index + 2]
        assert abs(pair[0].GetBounds()[2] - part["bbox"][0][1]) < .1, part["name"]
        show = not any(part["name"] == prefix or part["group"].startswith(prefix)
                       for prefix in hide)
        if show:
            visible.append(part)
        for actor in pair:
            actor.SetVisibility(show)
            prop = actor.GetProperty()
            prop.SetInterpolationToPhong()
            prop.SetAmbient(.35)
            prop.SetDiffuse(.65)
    assert visible, "No visible parts"
    low = np.min([part["bbox"][0] for part in visible], axis=0)
    high = np.max([part["bbox"][1] for part in visible], axis=0)
    if region == "stern":
        # Source coordinates: F=25-Y, converted to the exported mm scale.
        # The post's printed width is 14 in; use actual export dimensions.
        post = next(part for part in parts if part["name"] == "Samson post")
        units_per_ft = (post["bbox"][1][0] - post["bbox"][0][0]) / (14 / 12)
        low = np.array((-10, 11, -1)) * units_per_ft
        high = np.array((10, 29, 16)) * units_per_ft
    focus = (low + high) / 2
    distance = float(np.linalg.norm(high - low))
    camera = renderer.GetActiveCamera()
    camera.ParallelProjectionOn()
    direction = np.array(DIRECTIONS[view], dtype=float)
    direction /= np.linalg.norm(direction)
    camera.SetPosition(*(focus + direction * distance * 3))
    camera.SetFocalPoint(*focus)
    camera.SetViewUp(*((0, 1, 0) if view == "plan" else (0, 0, 1)))
    window = vtk.vtkEGLRenderWindow()
    window.SetOffScreenRendering(True)
    window.SetSize(1600, 1200)
    window.AddRenderer(renderer)
    lights = vtk.vtkLightKit()
    lights.SetKeyLightIntensity(1)
    lights.AddLightsToRenderer(renderer)
    renderer.ResetCamera(low[0], high[0], low[1], high[1], low[2], high[2])
    renderer.ResetCameraClippingRange()
    window.Render()
    capture = vtk.vtkWindowToImageFilter()
    capture.SetInput(window)
    capture.Update()
    path = ROOT / out
    path.parent.mkdir(parents=True, exist_ok=True)
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(path))
    writer.SetInputConnection(capture.GetOutputPort())
    writer.Write()
    window.Finalize()
    print(path, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--view", choices=DIRECTIONS, default="iso")
    parser.add_argument("--region", choices=("all", "stern"), default="all")
    parser.add_argument("--hide", action="append", default=[])
    parser.add_argument("--out", default="renders/current-full-vessel.png")
    args = parser.parse_args()
    render(args.out, args.view, args.region, args.hide)
