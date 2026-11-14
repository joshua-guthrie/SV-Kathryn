"""Build a committed tree from scratch and verify the result.

The working tree can contain uncommitted fixes, app state and caches. This
check archives the requested commit to a temporary directory with no .soma,
output or rendered state, runs a full SOMA build there, and then runs the scale
and registered-deck checks against that clean build.
"""
import argparse
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GIT = ROOT / 'project-git'
EXPECTED_PARTS = 874


def git(*arguments):
    return subprocess.run([str(GIT), *arguments], cwd=ROOT, check=True,
                          text=True, capture_output=True).stdout.strip()


def export_tree(ref, destination):
    archive = destination.parent / f'{destination.name}.tar'
    git('archive', '--format=tar', '-o', str(archive), ref)
    with tarfile.open(archive) as handle:
        handle.extractall(destination, filter='data')
    archive.unlink()
    return git('rev-parse', '--short', ref)


def run(command, cwd, timeout):
    return subprocess.run(command, cwd=cwd, check=True, timeout=timeout)


def verify(tree, commit, expect_parts, timeout):
    started = time.monotonic()
    print(f'Building committed tree {commit} from scratch ...', flush=True)
    run([sys.executable, '-m', 'soma', 'build'], tree, timeout)
    build = json.loads((tree / '.soma/build.json').read_text())
    assert build['status'] == 'ok', ('Clean build failed', build.get('error'))
    assert not build['warnings'], ('Clean build warnings', build['warnings'])
    parts = len(build['parts'])
    assert parts == expect_parts, ('Part count changed', parts, expect_parts)
    assert (tree / 'output/model.step').is_file(), 'STEP export missing'
    for check in ('check_model_scale.py', 'check_registered_deck.py'):
        print(f'Running {check} in the clean tree ...', flush=True)
        run([sys.executable, f'src/checks/{check}'], tree, timeout)
    print(f'PASS: {commit} builds from scratch: {parts} parts, 0 warnings, '
          f'{time.monotonic() - started:.1f} s, scale and deck checks pass.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ref', default='HEAD', help='commit to verify')
    parser.add_argument('--expect-parts', type=int, default=EXPECTED_PARTS,
                        help='required registered part count')
    parser.add_argument('--timeout', type=float, default=1800,
                        help='seconds per build/check command')
    parser.add_argument('--keep', action='store_true',
                        help='keep the temporary tree')
    options = parser.parse_args()
    destination = Path(tempfile.mkdtemp(prefix='kathryn-committed-build-'))
    passed = False
    try:
        commit = export_tree(options.ref, destination)
        verify(destination, commit, options.expect_parts, options.timeout)
        passed = True
    finally:
        if options.keep or not passed:
            print(f'Clean tree: {destination}')
        else:
            shutil.rmtree(destination, ignore_errors=True)


if __name__ == '__main__':
    main()
