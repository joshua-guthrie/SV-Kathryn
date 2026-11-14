"""Validate the standard-lumber deck partition before registration."""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from parts import deck_planking


def check():
    start = time.monotonic()
    boards = deck_planking.deck_boards()
    field, margins, deck = deck_planking.pattern_waterway()
    waterway = list(deck_planking.make_waterway_parts())
    scarfs = list(deck_planking.make_kingplank_scarf_parts())
    board_volume = sum(board['shape'].Volume(1e-9) for board in boards)
    waterway_volume = sum(shape.Volume(1e-9) for _, shape, _ in waterway)
    top_volume = sum(shape.Volume(1e-9) for shape in margins)
    depth_volume = waterway_volume - top_volume
    field_volume = field.Volume(1e-9)
    deck_volume = deck.Volume(1e-9)
    assert abs(board_volume - field_volume) < max(1e-6, field_volume * 1e-6)
    assert abs(board_volume + top_volume - deck_volume) < deck_volume * 1e-6
    assert depth_volume > 0
    internal = sum(bool(board['butt_aft']) for board in boards)
    schedule = []
    for board in sorted(boards, key=lambda item: (item['run'], item['f0'])):
        schedule.append(dict(
            id=board['name'], run=board['run'], stock=board['stock'],
            finished_length_ft=round(board['length'], 4),
            max_width_in=round((board['x1'] - board['x0']) * 12, 3),
            f_aft_ft=round(board['f0'], 4), f_fore_ft=round(board['f1'], 4),
            butt_aft_beam=(board['butt_aft'].beam_set
                           if board['butt_aft'] else None),
            butt_fore_beam=(board['butt_fore'].beam_set
                            if board['butt_fore'] else None),
            scarf=bool(board.get('scarf')),
            material=board['material']))
    result = dict(
        status='passed', boards=len(boards),
        runs=len({board['run'] for board in boards}),
        kingplank_boards=sum(board['run'] == 'Kingplank' for board in boards),
        waterway_parts=len(waterway), scarfs=len(scarfs),
        internal_butts=internal,
        max_board_ft=max(board['length'] for board in boards),
        min_board_ft=min(board['length'] for board in boards),
        boards_under_4ft=sum(board['length'] < 4 for board in boards),
        field_volume_ft3=field_volume,
        waterway_volume_ft3=waterway_volume,
        waterway_top_volume_ft3=top_volume,
        waterway_depth_volume_ft3=depth_volume,
        deck_volume_ft3=deck_volume,
        board_volume_ft3=board_volume,
        conservation_error_ppm=(board_volume + top_volume - deck_volume)
        / deck_volume * 1e6,
        faces=sum(len(board['shape'].Faces()) for board in boards),
        seconds=time.monotonic() - start,
        schedule_file='src/checks/m4_deck_board_schedule.json',
        remaining=['spiled/tapered edge treatment'])
    (ROOT / 'src/checks/m4_deck_partition.json').write_text(
        json.dumps(result, indent=2) + '\n')
    (ROOT / 'src/checks/m4_deck_board_schedule.json').write_text(
        json.dumps(schedule, indent=2) + '\n')
    print(json.dumps(result, indent=2), flush=True)
    return result


if __name__ == '__main__':
    check()
