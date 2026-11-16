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
EXPECTED_PARTS = 1025


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
    # Bound the OCCT pool before its first job. On this small workstation,
    # concurrent automatic builds otherwise push the CAD process into swap.
    # The official SOMA CLI still owns all output and registry operations.
    bootstrap = ("from OCP.OSD import OSD_Parallel,OSD_ThreadPool; "
                 "OSD_Parallel.SetUseOcctThreads_s(True); "
                 "p=OSD_ThreadPool.DefaultPool_s(2); "
                 "p.Init(2) if p.NbThreads()!=2 else None; "
                 "p.SetNbDefaultThreadsToLaunch(2); "
                 "import runpy,sys; sys.argv=['soma','build']; "
                 "runpy.run_module('soma',run_name='__main__')")
    run([sys.executable, '-c', bootstrap], tree, timeout)
    build = json.loads((tree / '.soma/build.json').read_text())
    assert build['status'] == 'ok', ('Clean build failed', build.get('error'))
    assert not build['warnings'], ('Clean build warnings', build['warnings'])
    parts = len(build['parts'])
    assert parts == expect_parts, ('Part count changed', parts, expect_parts)
    assert (tree / 'output/model.step').is_file(), 'STEP export missing'
    for check in ('check_model_scale.py', 'check_registered_deck.py', 'check_bow_attachment.py', 'check_trailboards.py', 'check_longhead_envelope.py'):
        print(f'Running {check} in the clean tree ...', flush=True)
        run([sys.executable, f'src/checks/{check}'], tree, timeout)
    print(f'PASS: {commit} builds from scratch: {parts} parts, 0 warnings, '
          f'{time.monotonic() - started:.1f} s, scale, deck, bow attachment and trailboard fidelity checks pass.')


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
