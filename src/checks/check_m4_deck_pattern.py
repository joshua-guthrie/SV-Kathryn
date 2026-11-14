"""Permanent acceptance check for the M4 standard-lumber deck pattern."""
import json
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from parts import deck_planking
from parts.openings import framed_openings
from parts.params import (DECK_BUTT_EDGE_CLEARANCE_FT, DECK_BUTT_TOLERANCE_FT,
                          DECK_CENTRE_PLANK_WIDTH_FT, DECK_MAX_BOARD_LENGTH_FT,
                          DECK_PLANK_WIDTH_FT, DECK_STAGGER_FT)


def _run_order(runs):
    port = sorted(run for run in runs if run.startswith('Port'))
    starboard = sorted(run for run in runs if run.startswith('Starboard'))
    return ['Kingplank', *port, *starboard]


def _adjacent(runs):
    order = _run_order(runs)
    mapping = {}
    for side in ('Port', 'Starboard'):
        side_runs = sorted(run for run in order if run.startswith(side))
        mapping[side_runs[0]] = 'Kingplank'
        for aft, fore in zip(side_runs, side_runs[1:]):
            mapping[fore] = aft
    return mapping


def check():
    start = time.monotonic()
    boards = deck_planking.deck_boards()
    supports = {support.beam_set: support for support in deck_planking.pattern_supports()}
    scarfs = deck_planking.pattern_scarfs()
    runs = sorted({board['run'] for board in boards})
    order = _run_order(runs)
    adjacent = _adjacent(runs)
    by_run = {}
    for board in boards:
        by_run.setdefault(board['run'], []).append(board)
    for run in by_run:
        by_run[run].sort(key=lambda board: board['f0'])

    max_length = max(board['length'] for board in boards)
    assert max_length <= DECK_MAX_BOARD_LENGTH_FT + DECK_BUTT_TOLERANCE_FT, \
        ('Board exceeds 12 ft', max_length)
    assert all(board['shape'].isValid() and len(board['shape'].Solids()) == 1
               for board in boards), 'Invalid board solid'

    butt_count = 0
    butt_checks = []
    for run in order:
        rows = by_run.get(run, [])
        for upstream, downstream in zip(rows, rows[1:]):
            gap = downstream['f0'] - upstream['f1']
            if abs(gap) > .1:
                continue
            aft = upstream['butt_fore']
            fore = downstream['butt_aft']
            if aft is None and fore is None:
                continue
            assert aft is not None and fore is not None, \
                ('Unpaired internal deck butt', run, upstream['name'], downstream['name'])
            assert aft.beam_set == fore.beam_set, ('Butt beam mismatch', run)
            assert abs(aft.forward - fore.forward) <= DECK_BUTT_TOLERANCE_FT
            support = supports[aft.beam_set]
            assert abs(support.forward - aft.forward) <= DECK_BUTT_TOLERANCE_FT, \
                ('Butt not at beam centreline', run, aft.forward, support.forward)
            assert deck_planking._supported(support, upstream['x0'], upstream['x1']), \
                ('Upstream board not on beam', run, upstream['name'], support.beam_set)
            assert deck_planking._supported(support, downstream['x0'], downstream['x1']), \
                ('Downstream board not on beam', run, downstream['name'], support.beam_set)
            assert abs(upstream['f1'] - support.forward) <= DECK_BUTT_TOLERANCE_FT
            assert abs(downstream['f0'] - support.forward) <= DECK_BUTT_TOLERANCE_FT
            if any(opening.aft - DECK_BUTT_EDGE_CLEARANCE_FT < support.forward <
                   opening.fore + DECK_BUTT_EDGE_CLEARANCE_FT
                   for opening in framed_openings()):
                assert support.role in ('header_aft', 'header_fore', 'split'), \
                    ('Full field beam used as a coaming-line butt', run, support.beam_set)
            butt_count += 1
            butt_checks.append(dict(run=run, forward=support.forward,
                                    beam_set=support.beam_set,
                                    upstream=upstream['name'], downstream=downstream['name']))

    run_butts = {}
    for run in runs:
        values = set()
        for board in by_run[run]:
            for joint in (board['butt_aft'], board['butt_fore']):
                if joint is not None:
                    values.add((round(joint.forward, 6), joint.beam_set))
        run_butts[run] = values
    stagger = []
    pairs_under_four = 0
    for run in order:
        previous = adjacent.get(run)
        if previous is None or not run_butts[run] or not run_butts[previous]:
            continue
        minimum = min(abs(a[0] - b[0]) for a in run_butts[run]
                      for b in run_butts[previous])
        stagger.append(dict(aft=previous, fore=run, minimum_ft=minimum))
        assert minimum > DECK_BUTT_TOLERANCE_FT, \
            ('Adjacent planks share a beam', previous, run)
        assert minimum >= 2.0 - DECK_BUTT_TOLERANCE_FT, \
            ('Adjacent deck butts closer than the approved fallback', previous, run, minimum)
        if minimum < DECK_STAGGER_FT - DECK_BUTT_TOLERANCE_FT:
            pairs_under_four += 1

    for board in boards:
        centre = board['run'] == 'Kingplank'
        maximum_width = ((DECK_CENTRE_PLANK_WIDTH_FT if centre else DECK_PLANK_WIDTH_FT)
                         + .02)
        width = board['x1'] - board['x0']
        assert width <= maximum_width, ('Deck board wider than standard stock',
                                        board['name'], width, maximum_width)
        assert ('6-in' in board['stock']) if centre else ('4-in' in board['stock'])

    king = by_run['Kingplank']
    assert not any(board['butt_aft'] or board['butt_fore'] for board in king), \
        'Kingplank must be continuous/scarfed, not butt-jointed'
    assert len(scarfs) == 1, ('Kingplank scarf count changed', len(scarfs))
    assert scarfs[0]['shape'].isValid() and len(scarfs[0]['shape'].Solids()) == 1
    assert all(board['length'] <= DECK_MAX_BOARD_LENGTH_FT + DECK_BUTT_TOLERANCE_FT
               for board in king)

    field, margins, deck = deck_planking.pattern_waterway()
    board_volume = sum(board['shape'].Volume(1e-9) for board in boards)
    top_volume = sum(shape.Volume(1e-9) for shape in margins)
    deck_volume = deck.Volume(1e-9)
    assert abs(board_volume - field.Volume(1e-9)) < 1e-6 * max(1, field.Volume(1e-9))
    assert abs((board_volume + top_volume) - deck_volume) < 1e-6 * deck_volume
    waterway_parts = list(deck_planking.make_waterway_parts())
    assert len(waterway_parts) == 2
    waterway_volume = sum(shape.Volume(1e-9) for _, shape, _ in waterway_parts)
    assert waterway_volume > top_volume

    model = json.loads((ROOT / '.soma/model.map.json').read_text())['parts']
    build = json.loads((ROOT / '.soma/build.json').read_text())
    assert build['status'] == 'ok' and not build['warnings']
    registered = [part for part in model if part['group'].startswith('Deck/Planking/')]
    assert len(registered) == len(boards), ('Registered board count', len(registered), len(boards))
    assert sum(part['group'].startswith('Deck/Waterway') for part in model) == 4
    assert sum(part['group'].startswith('Deck/Scarfs/Kingplank') for part in model) == 1
    assert not any('Cambered deck' == part['name'] for part in model), 'Aggregate backing returned'
    assert not any(any(word in part['name'].lower() or word in part['group'].lower()
                       for word in ('ledger', 'butt block', 'backing'))
                   for part in model), 'A ledger/backing member is registered'

    boards_under_four = sum(board['length'] < 4.0 for board in boards)
    result = dict(
        status='passed', boards=len(boards), runs=len(runs),
        kingplank_boards=len(king), waterway_parts=len(waterway_parts),
        scarfs=len(scarfs), internal_butts=butt_count,
        max_board_ft=max_length,
        min_board_ft=min(board['length'] for board in boards),
        boards_under_4ft=boards_under_four,
        min_adjacent_stagger_ft=min(row['minimum_ft'] for row in stagger),
        adjacent_pairs_under_4ft=pairs_under_four,
        field_volume_ft3=board_volume, waterway_volume_ft3=waterway_volume,
        waterway_top_volume_ft3=top_volume,
        waterway_depth_volume_ft3=waterway_volume - top_volume,
        deck_volume_ft3=deck_volume,
        conservation_ppm=(board_volume + top_volume - deck_volume) / deck_volume * 1e6,
        seconds=time.monotonic() - start,
        remaining=['spiled/tapered edge treatment'])
    (ROOT / 'src/checks/m4_deck_pattern_acceptance.json').write_text(
        json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return result


if __name__ == '__main__':
    check()
