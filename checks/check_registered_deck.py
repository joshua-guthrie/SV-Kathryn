"""Check the actual exported deck boards against the pre-partition assembly."""
import json
import struct
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def check():
    build = json.loads((ROOT / '.soma/build.json').read_text())
    assert build['status'] == 'ok' and not build['warnings']
    assert build['finished'] >= max((ROOT / name).stat().st_mtime
                                    for name in ('model.py', 'parts/deck_planking.py', 'parts/params.py'))
    parts = json.loads((ROOT / '.soma/model.map.json').read_text())['parts']
    boards = [p for p in parts if p['group'].startswith('Deck/Planking/')]
    expected = json.loads((ROOT / 'checks/m4_deck_partition.json').read_text())
    baseline = json.loads((ROOT / 'checks/m4_deck_baseline.json').read_text())['part']
    assert len(boards) == expected['boards'], ('Missing deck boards', len(boards), expected['boards'])
    assert not any(p['name'] == 'Cambered deck' for p in parts), 'Aggregate backing still registered'
    bounds = np.array([np.min([p['bbox'][0] for p in boards], axis=0),
                       np.max([p['bbox'][1] for p in boards], axis=0)])
    assert np.max(abs(bounds - np.array(baseline['bbox']))) < .1, 'Deck exterior changed'
    volume = sum(p['volume'] for p in boards)
    # Map volumes use default CAD integration; the exact partition separately
    # enforces 1-ppm conservation with high-accuracy integration.
    assert abs(volume - baseline['volume']) < baseline['volume'] * .001
    raw = (ROOT / '.soma/model.glb').read_bytes()
    length = struct.unpack_from('<I', raw, 12)[0]
    gltf = json.loads(raw[20:20 + length])
    ids = {p['id'] for p in boards}
    mesh_nodes = [n for n in gltf['nodes'] if n.get('name') in ids]
    assert len(mesh_nodes) == len(boards), 'Export is missing board meshes'
    missing = [(n['name'], f['id']) for n in mesh_nodes
               for f in n['extras']['soma']['faces'] if not f['triCount']]
    assert not missing, ('Deck faces absent from actual viewer mesh', missing)
    result = dict(status='passed', registered_boards=len(boards), assembly_parts=len(parts),
                  bounds_mm=bounds.tolist(), bbox_max_error_mm=float(np.max(abs(bounds - np.array(baseline['bbox'])))),
                  map_volume_relative_error=(volume - baseline['volume']) / baseline['volume'],
                  high_accuracy_material_error_ppm=expected['conservation_error_ppm'],
                  missing_mesh_faces=missing, aggregate_backing=False)
    (ROOT / 'checks/m4_registered_deck.json').write_text(json.dumps(result, indent=2) + '\n')
    print(f'PASS: {len(boards)} exported deck-board solids; conserved material, unchanged exterior, no backing or missing mesh faces.')
    return result


if __name__ == '__main__':
    check()
