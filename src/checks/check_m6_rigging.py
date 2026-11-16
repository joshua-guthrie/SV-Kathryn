"""M6 standing/running rig and S08 demonstration sails."""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from parts import rigging

def _box(shape):
    return shape.BoundingBox()


def _contains(box, point, tol=.05):
    return (box.xmin - tol <= point[0] <= box.xmax + tol and
            box.ymin - tol <= point[1] <= box.ymax + tol and
            box.zmin - tol <= point[2] <= box.zmax + tol)


def _check_lazyjack_geometry(rig):
    shapes = {name: shape for name, shape, _, _ in rig}
    top_z = rigging.HOUNDS_Z - .3
    mast_r = rigging.mast_radius_at(top_z)
    for side, label in ((1, 'Port'), (-1, 'Starboard')):
        pendant = _box(shapes[f'{label} main lazyjack pendant'])
        if side > 0:
            assert pendant.xmin > mast_r + .02, 'main pendant starts inside the mast'
        else:
            assert pendant.xmax < -mast_r - .02, 'main pendant starts inside the mast'
        for i, y in enumerate(rigging.MAIN_LAZYJACK_STATIONS_Y_FT, 1):
            point = rigging._main_lazyjack_station(side, y)
            box = _box(shapes[f'{label} main lazyjack leg {i}'])
            assert _contains(box, point), f'main leg {i} misses its boom station'
            assert abs(point[0]) > .25, f'main leg {i} is not outboard of the boom'
            assert box.ymax <= 37.50, f'main leg {i} runs past the boom tip'
        club_low = min(rigging.JIB_TACK[1], rigging.JIB_CLEW[1])
        club_high = max(rigging.JIB_TACK[1], rigging.JIB_CLEW[1])
        for i, t in enumerate((1 / 3, 2 / 3), 1):
            point = rigging._jib_club_point(t, side)
            box = _box(shapes[f'{label} jib lazyjack leg {i}'])
            assert _contains(box, point), f'jib leg {i} misses the club'
            assert club_low - .1 <= box.ymin and box.ymax <= club_high + .1, \
                f'jib leg {i} runs outside the club'
    return dict(
        main_stations_y_ft=list(rigging.MAIN_LAZYJACK_STATIONS_Y_FT),
        main_junctions_y_z_ft=[list(rigging.MAIN_LAZYJACK_J1_Y_Z_FT),
                               list(rigging.MAIN_LAZYJACK_J2_Y_Z_FT)],
        outboard_x_ft=rigging.LAZYJACK_X_FT,
        jib_junction_z_ft=rigging.JIB_LAZYJACK_JUNCTION_Z_FT,
        jib_legs=2,
        sources=['S03-V01 callout (6)',
                 'LOC-C01/P01 caption: gear to the boom and club'],
    )


def check():
    rig = list(rigging.make_rigging_parts())
    sails = list(rigging.make_sail_parts())
    sail_spars = list(rigging.make_sail_spars())
    assert len(rig) == 60 and len(sails) == 2 and len(sail_spars) == 1
    assert all(shape.isValid() and len(shape.Solids()) == 1
               for _, shape, _, _ in (*rig, *sails))
    assert sail_spars[0][0] == 'Jib club'
    assert sail_spars[0][1].isValid() and len(sail_spars[0][1].Solids()) == 1
    groups = {group for _, _, _, group in rig}
    assert groups == {'Rigging/Standing', 'Rigging/Running', 'Rigging/Fittings'}
    main = math.dist(rigging.MAIN_TACK, rigging.MAIN_HEAD)
    main_foot = math.dist(rigging.MAIN_TACK, rigging.MAIN_CLEW)
    main_leech = math.dist(rigging.MAIN_HEAD, rigging.MAIN_CLEW)
    jib_luff = math.dist(rigging.JIB_TACK, rigging.JIB_HEAD)
    jib_foot = math.dist(rigging.JIB_TACK, rigging.JIB_CLEW)
    jib_leech = math.dist(rigging.JIB_HEAD, rigging.JIB_CLEW)
    assert abs(main - 45.5) < .01 and abs(main_foot - 49.333) < .01
    assert abs(jib_luff - 49.5) < .01 and abs(jib_foot - 25.667) < .01
    assert abs(jib_leech - 42.0) < .01
    names = {name for name, _, _, _ in rig}
    for required in ('Head stay', 'Jib stay', 'Main halyard',
                     'Jib halyard', 'Main sheet', 'Jib downhaul',
                     'Topping lift', 'Boom lift', 'Spectacle/jack iron'):
        assert required in names, required
    lazy_required = []
    for label in ('Port', 'Starboard'):
        lazy_required += [f'{label} main lazyjack pendant',
                          f'{label} main lazyjack branch']
        lazy_required += [f'{label} main lazyjack leg {i}' for i in range(1, 5)]
        lazy_required += [f'{label} main lazyjack tail {i}' for i in (1, 2)]
        lazy_required += [f'{label} main lazyjack junction {i}' for i in (1, 2)]
        lazy_required += [f'{label} jib lazyjack pendant',
                          f'{label} jib lazyjack leg 1',
                          f'{label} jib lazyjack leg 2',
                          f'{label} jib lazyjack tail',
                          f'{label} jib lazyjack junction']
    for required in lazy_required:
        assert required in names, required
    import numpy as np
    h=np.array(rigging.JIB_HEAD);t=np.array(rigging.JIB_TACK);m=np.array(rigging.HEAD)
    assert np.linalg.norm(np.cross(h-t,m-t))/np.linalg.norm(m-t)<1e-7,'Jib head is off its actual stay'
    lazyjacks = _check_lazyjack_geometry(rig)
    sheet = next(shape for name, shape, _, _ in rig if name == 'Main sheet')
    box = sheet.BoundingBox()
    assert box.xlen < .05 and box.ylen < .05, 'Main sheet must hang vertically'
    traveller = rigging.boat_point(0, rigging.STERN_REMEDY_SOURCE['traveller']['forward_ft'],
                                   rigging.deck_height(rigging.STERN_REMEDY_SOURCE['traveller']['forward_ft'])
                                   + rigging.STERN_REMEDY_SOURCE['traveller']['height_above_deck_ft'])
    assert abs((box.ymin + box.ymax) / 2 - traveller[1]) < .05, 'Main sheet is not above the traveller'
    assert box.zmin >= traveller[2], 'Main sheet must rise from the traveller'
    result = dict(status='passed', rigging_parts=len(rig), sail_parts=len(sails),
                  groups=sorted(groups),
                  lazyjacks=lazyjacks,
                  jib_club_ft=dict(fore=[round(v, 3) for v in rigging.JIB_TACK],
                                   aft=[round(v, 3) for v in rigging.JIB_CLEW],
                                   foot_raise_ft=rigging.JIB_FOOT_RAISE_FT),
                  main_plan_ft=dict(luff=45.5, foot=49.333, leech_s08=68.0,
                                    straight_leech=round(main_leech, 3),
                                    roach_unmodelled=round(68.0 - main_leech, 3)),
                  jib_plan_ft=dict(luff=round(jib_luff, 3), foot=round(jib_foot, 3),
                                   leech=round(jib_leech, 3)),
                  source=['S03-V01 hull profile and rigging',
                          'S03-N02 rigging/running-gear key', 'S08-V01 sail plan'],
                  unresolved=['main-sail roached leech not modelled',
                              'exact cleat/pin-rail positions',
                              'hoops/hanks intentionally omitted per S08 note',
                              'lazyjack junction heights and leg split inferred '
                              'from the S03 profile'])
    (ROOT / 'src/checks/m6_rigging_acceptance.json').write_text(
        json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return result


if __name__ == '__main__':
    check()
