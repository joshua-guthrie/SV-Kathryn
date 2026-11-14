"""Catch a valid mast solid whose side surface disappears during tessellation."""
import json
import struct
import sys
from pathlib import Path

import numpy as np
from OCP.BRepTools import BRepTools

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from parts.spars import make_mast
from soma.mesher import mesh_shape


def exported_mast_mesh():
    """Inspect the actual full-size viewer mesh, avoiding an expensive remesh."""
    build = json.loads((ROOT / '.soma/build.json').read_text())
    assert build['status'] == 'ok'
    assert build['finished'] >= (ROOT / 'src/parts/spars.py').stat().st_mtime
    raw = (ROOT / '.soma/model.glb').read_bytes()
    json_size = struct.unpack_from('<I', raw, 12)[0]
    document = json.loads(raw[20:20 + json_size])
    binary_start = 20 + json_size + 8
    node = next(n for n in document['nodes'] if n.get('name', '').endswith(':Mast'))
    primitive = next(p for p in document['meshes'][node['mesh']]['primitives'] if p.get('mode', 4) == 4)

    def array(index, components, dtype):
        accessor = document['accessors'][index]
        view = document['bufferViews'][accessor['bufferView']]
        return np.frombuffer(raw, dtype=dtype, count=accessor['count'] * components,
                             offset=binary_start + view.get('byteOffset', 0) + accessor.get('byteOffset', 0))

    positions = array(primitive['attributes']['POSITION'], 3, '<f4').reshape(-1, 3)
    indices = array(primitive['indices'], 1, '<u4').reshape(-1, 3)
    return dict(positions=positions, indices=indices, faces=node['extras']['soma']['faces'])


def check():
    mast = make_mast()
    assert mast.isValid() and len(mast.Solids()) == 1
    # Captured before repair with high-accuracy integration. Default GProp
    # integration differs for analytic and rational representations.
    before_volume = 27.97272912589371
    assert abs(mast.Volume(1e-9) - before_volume) < before_volume * 1e-6
    results = []
    for denominator in (1, 32, 64):
        print(f'Checking mast viewer mesh at 1:{denominator} ...', flush=True)
        shape = mast.scale(304.8 / denominator)
        if denominator == 1:
            mesh = exported_mast_mesh()
        else:
            BRepTools.Clean_s(shape.wrapped)
            mesh = mesh_shape(shape)
        points, indices = mesh['positions'], mesh['indices']
        triangles = points[indices].astype(float)
        area = np.linalg.norm(np.cross(triangles[:, 1] - triangles[:, 0],
                                       triangles[:, 2] - triangles[:, 0]), axis=1).sum() / 2
        missing = [i for i, face in enumerate(mesh['faces']) if not face['triCount']]
        ratio = float(area / shape.Area())
        assert not missing, ('Mast faces absent from viewer mesh', denominator, missing)
        assert .98 < ratio < 1.02, ('Incomplete mast surface', denominator, ratio)
        results.append(dict(scale_denominator=denominator, triangles=len(indices),
                            meshed_to_CAD_area_ratio=ratio, missing_faces=missing))
    result = dict(status='passed', accurate_volume_ft3=mast.Volume(1e-9),
                  original_accurate_volume_ft3=before_volume, scales=results)
    (ROOT / 'src/checks/mast_mesh_acceptance.json').write_text(json.dumps(result, indent=2) + '\n')
    print('PASS: complete mast viewer surfaces at 1:1, 1:32 and 1:64; original material conserved.', flush=True)
    return result


if __name__ == '__main__':
    check()
