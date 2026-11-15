#!/usr/bin/env python3
"""Build the Kathryn model with plain CadQuery, without the SOMA app.

The model is a SOMA project: model.py imports `add_part`, `param`,
`import_step` and `import_assembly` from `soma`. This script installs a small
stand-in for those four functions before running model.py, collects the parts,
and writes a STEP assembly (and optionally a whole-model STL).

    pip install cadquery numpy scipy
    python build_without_soma.py
    python build_without_soma.py --stl
    python build_without_soma.py --out output/kathryn.step

SOMA-only features are not reproduced: the Parameters panel writes
parameters.json, the viewer cache and the GLB export. Values in parameters.json
are still applied by name when present. The deck-board cache in output/ is
reused when it is valid, as it is for `soma build`.
"""
import argparse
import inspect
import json
import re
import sys
import time
import types
from pathlib import Path

import cadquery as cq

ROOT = Path(__file__).resolve().parent
PARAMS_FILE = ROOT / 'parameters.json'
_ASSIGNMENT = re.compile(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*param\(')

PARTS = []


def _user_values():
    if not PARAMS_FILE.is_file():
        return {}
    try:
        data = json.loads(PARAMS_FILE.read_text(encoding='utf-8-sig'))
    except (OSError, ValueError) as error:
        print(f'{PARAMS_FILE.name}: ignored ({error}); code defaults apply.')
        return {}
    values = data.get('values') if isinstance(data, dict) else None
    if not isinstance(values, dict):
        print(f'{PARAMS_FILE.name}: no "values" object; code defaults apply.')
        return {}
    return {str(key): value for key, value in values.items()}


def param(default, label=None, *, min=None, max=None, step=None, unit=None,
          options=None, group=None, help=None, name=None):
    """Return the value from parameters.json by constant name, or the default."""
    user = _user_values()
    if name is None:
        frame = inspect.currentframe().f_back
        line = inspect.getframeinfo(frame, context=0).code_context or ['']
        match = _ASSIGNMENT.match(line[0])
        name = match.group(1) if match else None
    value = user.get(name, default)
    if name is not None and name in user:
        if options is not None and value not in options:
            print(f'parameters.json: {name}={value!r} is not in {options}; default applies.')
            value = default
        elif isinstance(default, bool):
            value = bool(value)
        elif isinstance(default, int) and not isinstance(default, bool):
            value = int(value)
        elif isinstance(default, float):
            value = float(value)
        print(f'Parameter {name} = {value!r} (set in parameters.json)')
    return value


def import_step(path):
    return cq.importers.importStep(str(ROOT / path)).val()


def import_assembly(path):
    raise NotImplementedError(
        f'import_assembly({path!r}) needs SOMA; this model does not use it. '
        'Open the project in SOMA for imported sub-assemblies.')


def add_part(name, shape, role=None, color=None, group=None, alpha=None):
    if shape is None or not shape.isValid():
        raise ValueError(f'Invalid part: {name}')
    if any(part['name'] == name for part in PARTS):
        raise ValueError(f'Duplicate part name: {name}')
    PARTS.append(dict(name=name, shape=shape, role=role, group=group,
                      color=color, alpha=alpha))


def soma_shim():
    module = types.ModuleType('soma')
    module.__all__ = ['add_part', 'param', 'import_step', 'import_assembly']
    module.add_part = add_part
    module.param = param
    module.import_step = import_step
    module.import_assembly = import_assembly
    return module


def assembly():
    root = cq.Assembly(name='Kathryn')
    groups = {}

    def group_assembly(path):
        if path not in groups:
            groups[path] = cq.Assembly(name=path.rpartition('/')[2])
        return groups[path]

    for part in PARTS:
        target = group_assembly(part['group']) if part['group'] else root
        color = cq.Color(*part['color']) if part['color'] else None
        target.add(part['shape'], name=part['name'], color=color)
    # CadQuery 2.8 snapshots a sub-assembly when it is added, so link the tree
    # only after every group is full: deepest first, parents last.
    for path in sorted(groups, key=lambda item: item.count('/'), reverse=True):
        parent_path, _, leaf = path.rpartition('/')
        parent = groups[parent_path] if parent_path else root
        parent.add(groups[path], name=leaf)
    return root


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', default='output/model_standalone.step',
                        help='STEP output path (default: %(default)s)')
    parser.add_argument('--stl', nargs='?', const=True,
                        help='also write an STL; optional path')
    args = parser.parse_args()

    sys.path.insert(0, str(ROOT / 'src'))
    sys.modules['soma'] = soma_shim()
    started = time.monotonic()
    print('Building model.py with plain CadQuery ...', flush=True)
    exec(compile((ROOT / 'model.py').read_text(), str(ROOT / 'model.py'), 'exec'),
         {'__name__': '__main__', '__file__': str(ROOT / 'model.py')})
    print(f'{len(PARTS)} parts registered in {time.monotonic() - started:.1f} s',
          flush=True)

    out = (ROOT / args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    assembly().save(str(out))
    print(f'STEP: {out}', flush=True)

    if args.stl:
        stl = Path(args.stl) if isinstance(args.stl, str) else out.with_suffix('.stl')
        stl = (ROOT / stl).resolve() if not stl.is_absolute() else stl
        shapes = [part['shape'] for part in PARTS if part['shape'].Solids()]
        cq.exporters.export(cq.Compound.makeCompound(shapes), str(stl))
        print(f'STL:  {stl}', flush=True)
    print(f'Done in {time.monotonic() - started:.1f} s', flush=True)


if __name__ == '__main__':
    main()
