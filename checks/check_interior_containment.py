"""Interior-vs-hull containment regression.

The cabin fit-out and transom framing must stay inside the actual interior
cavity. Structural members that intentionally bear on the shell (keelson,
frames, clamps) are outside this scope and are covered by M2/M3 checks.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from parts import hull, hull_frames, interior


def check():
    cavity = hull.continuous_interior()
    fitout = list(interior.make_cabin_fitout_parts())
    supports = {name: shape for name, shape, _ in hull_frames.make_support_parts()}
    transom = {name: shape for name, shape in supports.items()
               if 'transom' in name.lower()}
    assert len(fitout) == 49
    assert len(transom) == 6
    offenders = []
    for name, shape, _ in fitout:
        outside = shape.cut(cavity).Volume(1e-9)
        if outside > 1e-4:
            offenders.append((name, outside))
    for name, shape in transom.items():
        outside = shape.cut(cavity).Volume(1e-9)
        if outside > 1e-4:
            offenders.append((name, outside))
    assert not offenders, ('Interior material outside hull cavity', offenders)
    result = dict(status='passed', cabin_members=len(fitout),
                  transom_members=len(transom), outside_volume_ft3=0.0,
                  criterion='each member cut by continuous_interior has <=1e-4 ft3 outside',
                  source=['S07-V01/V02', 'S04-V01/V04', 'S05-27 transom framing'])
    (ROOT / 'checks/interior_containment_acceptance.json').write_text(
        json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return result


if __name__ == '__main__':
    check()
