"""M4 source-beam integration: schedule, roles, opening splits and actual export."""
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from parts import deck_beams, hull_frames
from parts.beam_layout import (BEAMS, STERN_TIMBERS, beam_name, forward,
                               opening_splits, opening_support)
from parts.frame_layout import SOURCE as FRAME_SOURCE, source_plan_forward
from parts.openings import framed_openings

EXPECTED_BEAMS = 29
EXPECTED_SETS = 23


def check():
    build = json.loads((ROOT / '.soma/build.json').read_text())
    assert build['status'] == 'ok' and not build['warnings']
    assert build['finished'] >= max((ROOT / name).stat().st_mtime for name in (
        'model.py', 'src/parts/deck_beams.py', 'src/parts/beam_layout.py',
        'references/drawing_package/m4_deck_schedule.json'))
    schedule = json.loads((ROOT / 'references/drawing_package/m4_deck_schedule.json').read_text())
    assert len(schedule['members']) == EXPECTED_SETS
    assert len(BEAMS) == EXPECTED_SETS

    parts = {name: shape for name, shape, _ in deck_beams.make_deck_beam_parts()}
    assert len(parts) == EXPECTED_BEAMS, ('Beam count changed', len(parts))
    for name, shape in parts.items():
        assert shape.isValid() and len(shape.Solids()) == 1, name

    roles = {}
    for beam in BEAMS:
        roles[beam['role']] = roles.get(beam['role'], 0) + 1
        if beam['set'] <= 3:
            assert abs(beam['sided_ft'] - 4.75 / 12) < 1e-9
            assert abs(beam['molded_ft'] - 6 / 12) < 1e-9
        else:
            assert abs(beam['sided_ft'] - 5.5 / 12) < 1e-9
            assert abs(beam['molded_ft'] - 5.5 / 12) < 1e-9
        assert beam['material'] == ('oak' if 12 <= beam['set'] <= 15 else 'pine')
    assert roles == {'full': 10, 'split': 6, 'header_aft': 3, 'header_fore': 4}, roles

    openings = {opening.name: opening for opening in framed_openings()}
    for opening in openings.values():
        for end in ('aft', 'fore'):
            header = opening_support(opening.name, end)
            assert beam_name(header) in parts, (opening.name, end)
            assert abs(forward(header) - header['forward_ft']) <= .20 + 1e-9
            if end == 'aft':
                assert forward(header) + header['sided_ft'] / 2 <= opening.aft + 1e-6
            else:
                assert forward(header) - header['sided_ft'] / 2 >= opening.fore - 1e-6
        splits = opening_splits(opening.name)
        for beam in splits:
            assert opening.aft <= forward(beam) <= opening.fore
            for side, sign in (('port', 1), ('starboard', -1)):
                name = f'{opening.name} {side} half beam {beam["set"]}'
                assert name in parts, name
                box = parts[name].BoundingBox()
                if sign > 0:
                    assert box.xmin >= opening.across + opening.clear_width / 2 - 1e-6, \
                        ('Half beam enters clear opening', name)
                else:
                    assert box.xmax <= opening.across - opening.clear_width / 2 + 1e-6, \
                        ('Half beam enters clear opening', name)

    for beam in BEAMS:
        if beam['role'] != 'full':
            continue
        for opening in openings.values():
            assert not opening.aft < forward(beam) < opening.fore, \
                ('Full beam passes through opening', beam['set'], opening.name)

    for index, px in enumerate(FRAME_SOURCE['supports']['stanchion_plan_preview_x'], 1):
        name, station, new = hull_frames.stanchion_beam(index, source_plan_forward(px))
        assert not new, ('Stanchion needs an invented beam', index)
        assert name in parts, name
        assert abs(station - forward(next(b for b in BEAMS if beam_name(b) == name))) < 1e-9

    assert len(STERN_TIMBERS) == 1
    stern = [name for name, _, _ in hull_frames.make_support_parts()
             if name.startswith('Stern oak deck timber')]
    assert stern == [STERN_TIMBERS[0]['label']], stern
    assert STERN_TIMBERS[0]['material'] == 'oak'
    assert schedule['unresolved_stern_line']['status'].startswith('unresolved')

    exported = json.loads((ROOT / '.soma/model.map.json').read_text())['parts']
    exported_beams = [part for part in exported if part['group'] == 'Deck/Beams']
    assert len(exported_beams) == EXPECTED_BEAMS, len(exported_beams)
    raw = (ROOT / '.soma/model.glb').read_bytes()
    length = struct.unpack_from('<I', raw, 12)[0]
    gltf = json.loads(raw[20:20 + length])
    ids = {part['id'] for part in exported_beams}
    nodes = [node for node in gltf['nodes'] if node.get('name') in ids]
    assert len(nodes) == len(exported_beams), 'Export missing beam meshes'
    missing = [(node['name'], face['id']) for node in nodes
               for face in node['extras']['soma']['faces'] if not face['triCount']]
    assert not missing, ('Beam faces absent from viewer mesh', missing)

    result = dict(status='passed', measured_sets=EXPECTED_SETS, registered_beams=EXPECTED_BEAMS,
                  roles=roles, split_openings={opening.name: [b['set'] for b in opening_splits(opening.name)]
                                               for opening in openings.values()},
                  stern_timbers=[STERN_TIMBERS[0]['label']],
                  unresolved=['member d identity', '7c counter line F=-1.05'],
                  missing_mesh_faces=missing)
    (ROOT / 'src/checks/m4_beams_acceptance.json').write_text(json.dumps(result, indent=2) + '\n')
    print(f'PASS: {EXPECTED_SETS} measured sets -> {EXPECTED_BEAMS} registered beams; '
          'stock, opening splits, stanchions, stern timbers and actual export all agree.')
    return result


if __name__ == '__main__':
    check()
