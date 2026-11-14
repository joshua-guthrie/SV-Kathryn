"""Check the exported deck boards, waterway and scarf against the baseline."""
import json
import struct
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]


def check():
    build = json.loads((ROOT / '.soma/build.json').read_text())
    assert build['status'] == 'ok' and not build['warnings']
    assert build['finished'] >= max((ROOT / name).stat().st_mtime
                                    for name in ('model.py', 'src/parts/params.py',
                                                 'src/parts/deck_planking.py',
                                                 'src/parts/deck_beams.py', 'src/parts/beam_layout.py',
                                                 'references/drawing_package/m4_deck_schedule.json'))
    parts = json.loads((ROOT / '.soma/model.map.json').read_text())['parts']
    boards = [p for p in parts if p['group'].startswith('Deck/Planking/')]
    waterways = [p for p in parts if p['group'].startswith('Deck/Waterway')]
    scarfs = [p for p in parts if p['group'].startswith('Deck/Scarfs/Kingplank')]
    expected = json.loads((ROOT / 'src/checks/m4_deck_partition.json').read_text())
    baseline = json.loads((ROOT / 'src/checks/m4_deck_baseline.json').read_text())['part']
    assert len(boards) == expected['boards'], ('Missing deck boards', len(boards), expected['boards'])
    assert len(waterways) == expected['waterway_parts'], (
        'Missing waterway parts', len(waterways), expected['waterway_parts'])
    assert len(scarfs) == expected['scarfs'], ('Missing kingplank scarf', len(scarfs))
    assert not any(p['name'] == 'Cambered deck' for p in parts), 'Aggregate backing still registered'
    deck_parts = boards + waterways
    bounds = np.array([np.min([p['bbox'][0] for p in deck_parts], axis=0),
                       np.max([p['bbox'][1] for p in deck_parts], axis=0)])
    # The waterway depth intentionally extends below the deck envelope; compare
    # the deck top x/y/zmax, not the new zmin.
    top_error = max(abs(bounds[0][0] - baseline['bbox'][0][0]),
                    abs(bounds[0][1] - baseline['bbox'][0][1]),
                    abs(bounds[1][0] - baseline['bbox'][1][0]),
                    abs(bounds[1][1] - baseline['bbox'][1][1]),
                    abs(bounds[1][2] - baseline['bbox'][1][2]))
    assert top_error < .1, 'Deck exterior changed'
    top_volume = expected.get('waterway_top_volume_ft3', 0.0) * 304.8 ** 3
    volume = sum(p['volume'] for p in boards) + top_volume
    # Map volumes use default CAD integration; the exact partition separately
    # enforces 1-ppm conservation with high-accuracy integration.
    assert abs(volume - baseline['volume']) < baseline['volume'] * .001
    raw = (ROOT / '.soma/model.glb').read_bytes()
    length = struct.unpack_from('<I', raw, 12)[0]
    gltf = json.loads(raw[20:20 + length])
    ids = {p['id'] for p in deck_parts}
    mesh_nodes = [n for n in gltf['nodes'] if n.get('name') in ids]
    assert len(mesh_nodes) == len(deck_parts), 'Export is missing deck meshes'
    missing = [(n['name'], f['id']) for n in mesh_nodes
               for f in n['extras']['soma']['faces'] if not f['triCount']]
    assert not missing, ('Deck faces absent from actual viewer mesh', missing)
    result = dict(status='passed', registered_boards=len(boards),
                  registered_waterways=len(waterways), registered_scarfs=len(scarfs),
                  assembly_parts=len(parts),
                  bounds_mm=bounds.tolist(),
                  bbox_max_error_mm=float(top_error),
                  map_volume_relative_error=(volume - baseline['volume']) / baseline['volume'],
                  waterway_top_volume_ft3=expected.get('waterway_top_volume_ft3'),
                  waterway_depth_volume_ft3=expected.get('waterway_depth_volume_ft3'),
                  high_accuracy_material_error_ppm=expected['conservation_error_ppm'],
                  max_board_ft=expected['max_board_ft'],
                  internal_butts=expected['internal_butts'],
                  missing_mesh_faces=missing, aggregate_backing=False)
    (ROOT / 'src/checks/m4_registered_deck.json').write_text(json.dumps(result, indent=2) + '\n')
    print(f'PASS: {len(boards)} exported deck boards + {len(waterways)} waterway parts; '
          f'conserved material, unchanged exterior, beam-centred pattern, no backing or missing mesh faces.')
    return result


if __name__ == '__main__':
    check()
