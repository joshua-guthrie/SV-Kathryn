"""M5 cabin fit-out acceptance: members, space, support and clearance."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from parts import hull, interior
from parts.deck import access_geometry
from parts.params import (CABIN_AFT_FT, CABIN_FORE_FT, INTERIOR_SKIN_FT,
                          ACCESS_CLEAR_WIDTH_FT, COMPANIONWAY_AFT_FT,
                          COMPANIONWAY_FORWARD_FT)


def check():
    parts = list(interior.make_cabin_fitout_parts())
    names = [name for name, _, _ in parts]
    assert len(parts) == 49, ('Cabin fit-out member count', len(parts))
    assert all(shape.isValid() and len(shape.Solids()) == 1 for _, shape, _ in parts)
    sole = [item for item in parts if item[0].startswith('Cabin sole board')]
    settees = [item for item in parts if 'cabin settee' in item[0]]
    lining = [item for item in parts if 'cabin lining board' in item[0]]
    stove = [item for item in parts if item[0].startswith('Cabin stove')]
    lockers = [item for item in parts if 'aft cabin locker' in item[0]]
    table = [item for item in parts if item[0].startswith('Cabin table')]
    assert len(sole) == 8 and len(settees) == 8 and len(lining) == 20
    assert len(stove) == 7 and len(lockers) == 4 and len(table) == 2

    sole_z = access_geometry().sole
    for name, shape, _ in parts:
        box = shape.BoundingBox()
        assert CABIN_AFT_FT - .1 <= 25 - box.ymax and 25 - box.ymin <= CABIN_FORE_FT + .1, (
            'Cabin member outside cabin fore-aft range', name)
        assert box.zmin >= sole_z - .16 and box.zmax <= hull.deck_height(
            (25 - box.ymax + 25 - box.ymin) / 2) + .02, ('Cabin member outside sole/deck range', name)
        mid_f = (25 - box.ymax + 25 - box.ymin) / 2
        half = hull.topside_halfwidth(mid_f, max(sole_z, box.zmax)) - INTERIOR_SKIN_FT
        assert abs(box.xmin) <= half + .12 and abs(box.xmax) <= half + .12, (
            'Cabin member outside hull width', name)

    for name, shape, _ in sole:
        assert abs(shape.BoundingBox().zmin - (sole_z - .14)) < 1e-6
    for name, shape, _ in settees:
        if name.endswith('top'):
            assert abs(shape.BoundingBox().zmax - (sole_z + 1.35)) < 1e-6
    for name, shape, _ in stove:
        assert shape.BoundingBox().zmin >= sole_z - 1e-6
    for name, shape, _ in lockers:
        assert shape.BoundingBox().zmin >= sole_z + 1.3

    # Companionway/door approach is forward of the fit-out except for the aft
    # lockers, which are above the settee backs and outboard of the well.
    for name, shape, _ in parts:
        if name.startswith('Cabin sole board'):
            continue
        box = shape.BoundingBox()
        f0, f1 = 25 - box.ymax, 25 - box.ymin
        if f1 > COMPANIONWAY_AFT_FT and f0 < COMPANIONWAY_FORWARD_FT:
            assert min(abs(box.xmin), abs(box.xmax)) > ACCESS_CLEAR_WIDTH_FT / 2 + .3, (
                'Cabin fit-out obstructs companionway', name)
    assert max(abs(shape.BoundingBox().xmin) for name, shape, _ in lockers) > 1.2

    evidence = dict(
        status='passed', source=['S07-V01 cabin section', 'S07-V02 cabin hatch section',
                                 'S04-V01 inboard profile', 'S04-V04 cabin profile aft'],
        members=dict(cabin_sole_boards=len(sole), settee_parts=len(settees),
                     lining_boards=len(lining), stove_parts=len(stove),
                     table_parts=len(table), aft_locker_parts=len(lockers)),
        basis='scale-measured cabin envelope; settee/stove/locker arrangement inferred from S07/S04',
        cabin_fore_aft_ft=[CABIN_AFT_FT, CABIN_FORE_FT], sole_ft=sole_z,
        unresolved=['exact historic settee/berth sections', 'stove model and flue route',
                    'individual locker door joinery', 'hold/forepeak loose fit-out absent per survey'])
    (ROOT / 'src/checks/m5_cabin_acceptance.json').write_text(
        json.dumps(evidence, indent=2) + '\n')
    print(json.dumps(evidence, indent=2))
    return evidence


if __name__ == '__main__':
    check()
