"""Check the expanded S04 outer longhead/trailboard timber envelope.

Run after the official `soma build`. The check uses the completed exported
BREPs, not a rebuilt approximation. Source picks and the held-out S04 stations
remain separate from CAD contact tolerances.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
import cadquery as cq

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from soma.measure import Model
from parts.trailboard_layout import (ENVELOPE, ENVELOPE_PATH, outer_top, outer_bottom,
                                     panel_top, panel_bottom)
from solid_contacts import contact_distance

CAD_TOL_FT = 1 / 304.8
SOURCE_LIMIT_FT = 0.20


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check(project=ROOT, out=None, strict=True):
    project = Path(project)
    ledger = json.loads(ENVELOPE_PATH.read_text())
    source = ROOT / ledger['source']['file']
    assert sha(source) == ledger['source']['sha256'], 'S04 source changed'
    assert sha(ROOT / 'references/drawing_package/bow_remedy_registration.json') == \
        ledger['registration']['source_registration_sha256'], 'Bow registration changed'

    build = json.loads((project / '.soma/build.json').read_text())
    assert build['status'] == 'ok' and not build['warnings'], build.get('error')
    model = Model(project / '.soma')
    records = {p['name']: p for p in model.map['parts']}
    cache = {}

    def part(name):
        if name not in cache:
            cache[name] = model.shape(records[name]['id']).scale(1 / 304.8)
        return cache[name]

    checks = []

    def result(cid, status, actual, limit, units, method, evidence=None):
        checks.append(dict(id=cid, status='pass' if status else 'fail', actual=actual,
                           limit=limit, units=units, method=method,
                           evidence_paths=evidence or []))

    backing = part('Longhead trailboard backing')
    upper_shoulder = part('Longhead upper shoulder')
    boards = {label: part(label + ' trailboard board') for label in ('Port', 'Starboard')}
    spar = part('Bowsprit')
    stem = part('Painted stem and cutwater')
    cross = part('Bowsprit heel bearing cross-timber')
    extension = part('Bowsprit stem-head extension')
    headrails = {label: part(label + ' projecting headrail') for label in ('Port', 'Starboard')}

    for name, shape in [('Longhead trailboard backing', backing),
                        ('Longhead upper shoulder', upper_shoulder),
                        *((label + ' trailboard board', board) for label, board in boards.items())]:
        assert shape.isValid() and len(shape.Solids()) == 1, name

    # Held-out S04 stations: not used to fit the envelope curves.
    held = []
    for row in ledger['held_out_outer']:
        f, z = row['fz']
        expected = outer_top(f) if row['role'] == 'upper' else outer_bottom(f)
        held.append(dict(role=row['role'], grid_x=row['grid_x'], f_ft=f,
                         source_z_ft=z, model_z_ft=expected,
                         residual_ft=abs(expected - z)))
    max_held = max(row['residual_ft'] for row in held)
    result('LE-01', max_held <= SOURCE_LIMIT_FT,
           {'maximum_residual_ft': max_held, 'held_out': held}, SOURCE_LIMIT_FT, 'ft',
           'Compare the declared envelope curve with independent S04-V01 picks not used in the fit')

    # Actual exported envelope at profile sections away from fitted seats.
    profile = []
    for f in (53.0, 56.0, 60.0, 62.5):
        plane = cq.Face.makeFromWires(
            cq.Workplane(cq.Plane(origin=(0, 25 - f, 0), xDir=(1, 0, 0),
                                  normal=(0, 1, 0))).rect(10, 30).val())
        section = backing.intersect(plane)
        assert section.Volume() > 1e-9, f'empty envelope section at F={f}'
        bounds = section.BoundingBox()
        profile.append(dict(forward_ft=f, actual_lower_ft=bounds.zmin,
                            actual_upper_ft=bounds.zmax,
                            source_lower_ft=outer_bottom(f),
                            source_upper_ft=outer_top(f),
                            lower_residual_ft=abs(bounds.zmin - outer_bottom(f)),
                            upper_residual_ft=abs(bounds.zmax - outer_top(f))))
    max_profile = max(max(r['lower_residual_ft'], r['upper_residual_ft']) for r in profile)
    result('LE-02', max_profile <= 0.05,
           {'maximum_profile_residual_ft': max_profile, 'sections': profile}, 0.05, 'ft',
           'Intersect the exported backing at four stations and compare its actual outer bounds with the ledger')

    # Cross-sections must retain timber above and below the decorated fascia.
    occupancy = []
    for f in (53.0, 56.0, 60.0):
        plane = cq.Face.makeFromWires(
            cq.Workplane(cq.Plane(origin=(0, 25 - f, 0), xDir=(1, 0, 0),
                                  normal=(0, 1, 0))).rect(10, 30).val())
        bounds = backing.intersect(plane).BoundingBox()
        occupancy.append(dict(forward_ft=f, face_top_ft=panel_top(f),
                              face_bottom_ft=panel_bottom(f),
                              timber_top_ft=bounds.zmax, timber_bottom_ft=bounds.zmin,
                              upper_margin_ft=bounds.zmax - panel_top(f),
                              lower_margin_ft=panel_bottom(f) - bounds.zmin))
    min_margin = min(min(r['upper_margin_ft'], r['lower_margin_ft']) for r in occupancy)
    result('LE-03', min_margin >= 0.05,
           {'minimum_timber_margin_ft': min_margin, 'sections': occupancy}, 0.05, 'ft',
           'Section the exported backing above and below the existing S01 fascia at aft, middle and forward stations')

    clearance = min(backing.distance(spar), upper_shoulder.distance(spar))
    nominal = ledger['clearance']['nominal_min_ft']
    band = ledger['clearance']['acceptance_band_ft']
    no_common = backing.intersect(spar).Volume() + upper_shoulder.intersect(spar).Volume()
    result('LE-04', no_common <= 1e-7 and band[0] <= clearance <= band[1],
           {'minimum_clearance_ft': clearance, 'minimum_clearance_in': clearance * 12,
            'nominal_ft': nominal, 'acceptance_band_ft': band,
            'common_volume_ft3': no_common}, band, 'ft',
           'Exact exported solids: positive nearest-parallel span beneath the bowsprit with no contact or common volume')

    contacts = {}
    for name, shape in [('Backing / painted stem', stem),
                        ('Backing / stem-head extension', extension),
                        ('Backing / heel cross-timber', cross),
                        ('Upper shoulder / stem-head extension', extension),
                        ('Upper shoulder / painted stem', stem),
                        ('Upper shoulder / heel cross-timber', cross)]:
        wood = backing if name.startswith('Backing') else upper_shoulder
        contacts[name] = dict(distance_mm=wood.distance(shape) * 304.8,
                              common_ft3=wood.intersect(shape).Volume())
    seat_contacts=('Backing / painted stem','Backing / stem-head extension',
                   'Backing / heel cross-timber','Upper shoulder / stem-head extension')
    result('LE-05', all(contacts[k]['distance_mm'] <= 1.0 and contacts[k]['common_ft3'] <= 1e-7
                        for k in seat_contacts)
           and all(v['common_ft3'] <= 1e-7 for v in contacts.values()),
           contacts, {'distance_mm': 1.0, 'common_ft3': 1e-7}, 'mixed',
           'Fitted seats against the unchanged stem, cross-timber and stem-head extension')

    support = {}
    for label, board in boards.items():
        support[label + ' / backing'] = dict(distance_mm=board.distance(backing) * 304.8,
                                             common_ft3=board.intersect(backing).Volume())
        support[label + ' / headrail'] = dict(distance_mm=board.distance(headrails[label]) * 304.8,
                                              common_ft3=board.intersect(headrails[label]).Volume())
    result('LE-06', all(v['distance_mm'] <= 1.0 and v['common_ft3'] <= 1e-7
                        for k, v in support.items() if 'backing' in k),
           support, {'distance_mm': 1.0, 'common_ft3': 1e-7}, 'mixed',
           'Seat both S01 faces on the enlarged timber; retain the separate headrails without interpenetration')

    asymmetry = {}
    for key, a, b in [('board_bounds', boards['Port'].BoundingBox(), boards['Starboard'].BoundingBox()),
                      ('headrail_bounds', headrails['Port'].BoundingBox(), headrails['Starboard'].BoundingBox())]:
        asymmetry[key] = dict(x_mirror_mm=abs(a.xmin + b.xmax) * 304.8,
                              y_mm=abs(a.ymin - b.ymin) * 304.8,
                              z_mm=max(abs(a.zmin - b.zmin), abs(a.zmax - b.zmax)) * 304.8)
    backing_bounds = backing.BoundingBox()
    asymmetry['backing_centre_mm'] = abs(backing_bounds.xmin + backing_bounds.xmax) * 304.8
    max_asym = max([v for row in asymmetry.values() if isinstance(row, dict) for v in row.values()] + [asymmetry['backing_centre_mm']])
    result('LE-07', max_asym <= 0.1, {'maximum_mm': max_asym, 'components': asymmetry}, 0.1, 'mm',
           'Mirror-consistency of exported port/starboard bounds and the common backing centre')

    unintended = {}
    for name, shape in [('Bowsprit', spar), ('Port headrail', headrails['Port']),
                        ('Starboard headrail', headrails['Starboard']),
                        ('Port board', boards['Port']), ('Starboard board', boards['Starboard']),
                        ('Painted topsides', part('Painted topsides')), ('Keel', part('Keel')),
                        ('Painted stem and cutwater', stem), ('Stem-head extension', extension),
                        ('Heel cross-timber', cross)]:
        unintended['Backing / ' + name] = backing.intersect(shape).Volume()
        unintended['Upper shoulder / ' + name] = upper_shoulder.intersect(shape).Volume()
    result('LE-08', max(unintended.values()) <= 1e-7,
           {'unintended_common_ft3': unintended}, 1e-7, 'ft3',
           'Exported solids checked for unintended common volume after fitted-seat cuts')

    paths = [ROOT / 'model.py', *sorted((ROOT / 'src/parts').glob('*.py')),
             ROOT / 'references/drawing_package/longhead_envelope.json',
             ROOT / 'references/drawing_package/bow_remedy_registration.json',
             ROOT / 'references/drawing_package/jib_club.json']
    record = dict(schema_version=1,
                  status='passed' if all(c['status'] == 'pass' for c in checks) else 'failed',
                  part_count=len(records),
                  model_source_hashes={str(p.relative_to(ROOT)): sha(p) for p in paths},
                  build_hashes={str(p.relative_to(project)): sha(p) for p in
                                [project / '.soma/build.json', project / '.soma/model.glb',
                                 project / '.soma/model.map.json', project / 'output/model.step']},
                  source_hashes={'S04-V01': sha(source)},
                  checks=checks,
                  ledger=ledger)
    if out:
        out = Path(out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({'status': record['status'], 'parts': len(records),
                      'checks': [{k: c[k] for k in ('id', 'status')} for c in checks],
                      'max_held_residual_ft': max_held,
                      'min_clearance_ft': clearance,
                      'min_timber_margin_ft': min_margin}, indent=2), flush=True)
    if strict:
        assert record['status'] == 'passed', [(c['id'], c['actual']) for c in checks if c['status'] == 'fail']
    return record


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, default=ROOT)
    parser.add_argument('--out', type=Path,
                        default=ROOT / 'docs/images/trailboard_envelope_gap/acceptance.json')
    parser.add_argument('--report-only', action='store_true')
    args = parser.parse_args()
    check(args.project, args.out, strict=not args.report_only)
