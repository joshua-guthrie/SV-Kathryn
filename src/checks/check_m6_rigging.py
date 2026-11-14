"""M6 standing/running rig and S08 demonstration sails."""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from parts import rigging


def check():
    rig = list(rigging.make_rigging_parts())
    sails = list(rigging.make_sail_parts())
    assert len(rig) == 33 and len(sails) == 2
    assert all(shape.isValid() and len(shape.Solids()) == 1
               for _, shape, _, _ in (*rig, *sails))
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
    for required in ('Bobstay', 'Head stay', 'Jib stay', 'Main halyard',
                     'Jib halyard', 'Main sheet', 'Jib downhaul',
                     'Topping lift', 'Boom lift', 'Spectacle/jack iron'):
        assert required in names, required
    result = dict(status='passed', rigging_parts=len(rig), sail_parts=len(sails),
                  groups=sorted(groups),
                  main_plan_ft=dict(luff=45.5, foot=49.333, leech_s08=68.0,
                                    straight_leech=round(main_leech, 3),
                                    roach_unmodelled=round(68.0 - main_leech, 3)),
                  jib_plan_ft=dict(luff=round(jib_luff, 3), foot=round(jib_foot, 3),
                                   leech=round(jib_leech, 3)),
                  source=['S03-V01 hull profile and rigging',
                          'S03-N02 rigging/running-gear key', 'S08-V01 sail plan'],
                  unresolved=['main-sail roached leech not modelled',
                              'exact cleat/pin-rail positions',
                              'hoops/hanks intentionally omitted per S08 note'])
    (ROOT / 'checks/m6_rigging_acceptance.json').write_text(
        json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return result


if __name__ == '__main__':
    check()
