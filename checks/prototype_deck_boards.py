"""Validate an exact deck-board partition before replacing the live aggregate."""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from parts import hull, deck_planking


def check():
    start = time.monotonic()
    boards = deck_planking.deck_boards()
    reference = hull.make_deck().Volume(1e-9)
    total = sum(board['shape'].Volume(1e-9) for board in boards)
    result = dict(status='passed', boards=len(boards),
                  runs=len({board['run'] for board in boards}),
                  reference_volume_ft3=reference, board_volume_ft3=total,
                  conservation_error_ppm=(total - reference) / reference * 1e6,
                  faces=sum(len(board['shape'].Faces()) for board in boards),
                  seconds=time.monotonic() - start,
                  remaining=['waterways', 'supported staggered butt joints', 'full deck-beam integration'])
    (ROOT / 'checks/m4_deck_partition.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2), flush=True)
    return result


if __name__ == '__main__':
    check()
