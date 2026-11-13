"""M4 standard-lumber deck planking.

Deck boards are standard 4-in/6-in nominal stock, no longer than 12 ft. Every
internal butt terminates at the centreline of a measured S05-07 deck beam so
the two adjoining boards share that beam, each covering half its sided width.
There are no ledgers or unsupported butts. The kingplank is continuous per
continuous deck piece; a visible scarf is cut where a stock joint is modelled.
"""
from bisect import bisect_right
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path

import cadquery as cq
import numpy as np

from . import centreline_layout, framing, hull
from .beam_layout import BEAMS, forward as beam_forward
from .board_tools import plane_f, plane_x, segmented_loft, split_material
from .openings import framed_openings
from .params import (
    DECK_BUTT_EDGE_CLEARANCE_FT, DECK_BUTT_TOLERANCE_FT,
    DECK_CENTRE_PLANK_WIDTH_FT, DECK_KINGPLANK_NOMINAL_IN,
    DECK_MAX_BOARD_LENGTH_FT, DECK_MIN_BOARD_LENGTH_FT,
    DECK_PLANK_NOMINAL_IN, DECK_PLANK_WIDTH_FT, DECK_SCARF_LENGTH_FT,
    DECK_SCARF_MIN_BOARD_FT, DECK_STAGGER_FT, BOW_POST_FORWARD_FT, PORT_SIDE,
    TRUNK_AFT_FT, TRUNK_FORE_FT, TRUNK_GAP_FT,
)
from .primitives import block


@dataclass(frozen=True)
class RawPiece:
    run: str
    run_index: int
    side: int
    x0: float
    x1: float
    f0: float
    f1: float
    shape: object = None


@dataclass(frozen=True)
class BeamSupport:
    beam_set: int
    role: str
    forward: float
    sided_ft: float
    intervals: tuple


@dataclass(frozen=True)
class Joint:
    forward: float
    beam_set: int | None
    sided_ft: float | None
    kind: str = 'butt'


@lru_cache(maxsize=1)
def _waterway_split():
    """Separate the deck margin outboard of the clamp from the plank field.

    The margin is a provisional oak waterway, following the accepted clamp
    curve. Its exact section is still to be measured; this split only removes
    the unbraced edge from the standard-lumber plank field.
    """
    deck = hull.make_deck()
    aft, fore = hull.SECTIONS[0][0] - .5, hull.SECTIONS[-1][0] + .5
    positions = np.linspace(aft, fore, max(24, int((fore - aft) / .25) + 2))
    tools = []
    for sign in (1, -1):
        inner = [(sign * max(.02, framing.clamp_outer(float(forward))), 25 - forward)
                 for forward in positions]
        outer = [(sign * 12.0, 25 - positions[-1]), (sign * 12.0, 25 - positions[0])]
        tool = cq.Workplane('XY').polyline([*inner, *outer]).close().extrude(20).val()
        assert tool.isValid() and len(tool.Solids()) == 1, 'Invalid waterway tool'
        tools.append(tool)
    margins = tuple(deck.intersect(tool) for tool in tools)
    field = deck.cut(*tools)
    total = sum(shape.Volume(1e-9) for shape in (field, *margins))
    expected = deck.Volume(1e-9)
    assert abs(total - expected) < expected * 1e-6, 'Waterway/field split lost material'
    assert field.isValid() and all(shape.isValid() for shape in margins)
    return field, margins, deck


def _course_edges():
    source = hull.make_deck()
    maximum = max(abs(source.BoundingBox().xmin), abs(source.BoundingBox().xmax))
    positive = []
    edge = DECK_CENTRE_PLANK_WIDTH_FT / 2
    while edge < maximum:
        positive.append(edge)
        edge += DECK_PLANK_WIDTH_FT
    return tuple(positive)


def _label(x, positive):
    course = bisect_right(positive, abs(x))
    if course == 0:
        return 'Kingplank'
    return f'{"Port" if x > 0 else "Starboard"} deck plank {course:02d}'


@lru_cache(maxsize=1)
def _deck_cuts():
    stock = hull.rudder_stock_passage().BoundingBox()
    bow = block(0, BOW_POST_FORWARD_FT, -5, 5 / 12 + .012, 5 / 12 + .012, 25).BoundingBox()
    mast = centreline_layout.mast_chock_envelope(hull.deck_height, .006).BoundingBox()
    return tuple((25 - box.ymax, 25 - box.ymin, box.xmin, box.xmax)
                 for box in (stock, bow, mast))


@lru_cache(maxsize=1)
def _f_grid():
    field = _waterway_split()[0]
    box = field.BoundingBox()
    fmin, fmax = 25 - box.ymax, 25 - box.ymin
    positions = np.arange(fmin, fmax, .02)
    clamps = np.array([framing.clamp_outer(float(f)) for f in positions])
    return tuple(positions), tuple(clamps), fmin, fmax


def _section_intervals(x0, x1):
    section = _waterway_split()[0].intersect(plane_x((x0 + x1) / 2))
    cuts = []
    for face in section.Faces():
        box = face.BoundingBox()
        if face.Area() > 1e-5:
            cuts.append((25 - box.ymax, 25 - box.ymin))
    cuts.sort()
    merged = []
    for f0, f1 in cuts:
        if merged and f0 <= merged[-1][1] + .05:
            merged[-1] = (merged[-1][0], max(merged[-1][1], f1))
        else:
            merged.append((f0, f1))
    return tuple(merged)


def _f_intervals(x0, x1, use_section=False):
    if use_section:
        return _section_intervals(x0, x1)
    positions, clamps, _, fmax = _f_grid()
    inner = max(.02, min(abs(x0), abs(x1)))
    cuts = []
    for opening in framed_openings():
        if x1 > opening.across - opening.clear_width / 2 and \
                x0 < opening.across + opening.clear_width / 2:
            cuts.append((opening.aft, opening.fore))
    intervals = []
    start = None
    for f, clamp in zip(positions, clamps):
        blocked = any(a - .02 < f < b + .02 for a, b in cuts)
        present = clamp >= inner - .01 and not blocked
        if present and start is None:
            start = f
        elif start is not None and not present:
            intervals.append((start, f))
            start = None
    if start is not None:
        intervals.append((start, fmax))
    return tuple((a, b) for a, b in intervals if b - a > .05)


@lru_cache(maxsize=1)
def _raw_pieces():
    field = _waterway_split()[0]
    box = field.BoundingBox()
    field_max = max(abs(box.xmin), abs(box.xmax))
    positive = _course_edges()
    runs = [('Kingplank', -DECK_CENTRE_PLANK_WIDTH_FT / 2,
             DECK_CENTRE_PLANK_WIDTH_FT / 2)]
    for index, left in enumerate(positive, 1):
        right = min(positive[index] if index < len(positive) else field_max,
                    field_max)
        if left >= field_max - .01:
            break
        if right - left < .02:
            continue
        runs.append((f'Port deck plank {index:02d}', left, right))
        runs.append((f'Starboard deck plank {index:02d}', -right, -left))
    order = ('Kingplank', *[run for run, _, _ in runs if run.startswith('Port')],
             *[run for run, _, _ in runs if run.startswith('Starboard')])
    lookup = {run: (x0, x1) for run, x0, x1 in runs}
    result = []
    for run_index, run in enumerate(order):
        x0, x1 = lookup[run]
        side = 0 if run == 'Kingplank' else (1 if run.startswith('Port') else -1)
        cut_x = _deck_cuts()
        use_section = run == 'Kingplank' or any(
            x1 > a and x0 < b for _, _, a, b in cut_x)
        for f0, f1 in _f_intervals(x0, x1, use_section):
            result.append(RawPiece(run, run_index, side, x0, x1, f0, f1))
    return tuple(result), order


@lru_cache(maxsize=1)
def _beam_supports():
    openings = {opening.name: opening for opening in framed_openings()}
    stock = hull.rudder_stock_passage().BoundingBox()
    stock_f0, stock_f1 = 25 - stock.ymax, 25 - stock.ymin
    supports = []
    for beam in BEAMS:
        f = beam_forward(beam)
        span = framing.clamp_outer(f) - .015
        sided = beam['sided_ft']
        intervals = []
        if beam['role'] == 'split':
            opening = openings[beam['opening']]
            for sign in (PORT_SIDE, -PORT_SIDE):
                x = opening.across + sign * (opening.clear_width + sided) / 2
                if sign > 0:
                    lo, hi = x + sided / 2 - .025, span
                else:
                    lo, hi = -span, x - sided / 2 + .025
                if hi - lo > .02:
                    intervals.append((lo, hi))
        else:
            lo, hi = -span, span
            cuts = []
            if TRUNK_AFT_FT < f < TRUNK_FORE_FT:
                slot = (TRUNK_GAP_FT + .10) / 2
                cuts.append((-slot, slot))
            if stock_f0 < f < stock_f1:
                cuts.append((stock.xmin - .01, stock.xmax + .01))
            cuts = sorted((max(lo, a), min(hi, b)) for a, b in cuts)
            cursor = lo
            for a, b in cuts:
                if a > cursor + .02:
                    intervals.append((cursor, a))
                cursor = max(cursor, b)
            if hi > cursor + .02:
                intervals.append((cursor, hi))
        supports.append(BeamSupport(beam['set'], beam['role'], f, sided,
                                    tuple(intervals)))
    return tuple(supports)


def _supported(support, x0, x1):
    margin = .03
    return any(x0 >= lo - margin and x1 <= hi + margin
               for lo, hi in support.intervals)


def _run_pieces(raw, run):
    return [piece for piece in raw if piece.run == run]


def _select_field_butts(run, pieces, previous):
    stations = []
    for piece in pieces:
        last = piece.f0
        while piece.f1 - last > DECK_MAX_BOARD_LENGTH_FT + 1e-9:
            target = last + DECK_MAX_BOARD_LENGTH_FT
            candidates = []
            for support in _beam_supports():
                f = support.forward
                if f < last + DECK_MIN_BOARD_LENGTH_FT - 1e-9:
                    continue
                if f > target + 1e-9:
                    continue
                if f < piece.f0 + DECK_BUTT_EDGE_CLEARANCE_FT - 1e-9:
                    continue
                if f > piece.f1 - DECK_BUTT_EDGE_CLEARANCE_FT + 1e-9:
                    continue
                if not _supported(support, piece.x0, piece.x1):
                    continue
                candidates.append(support)
            chosen = None
            for minimum in (DECK_STAGGER_FT, 2.0):
                for support in sorted(candidates,
                                      key=lambda item: abs(item.forward - target)):
                    if all(abs(support.forward - other) >= minimum
                           for other in previous):
                        chosen = support
                        break
                if chosen is not None:
                    break
            if chosen is None:
                break
            stations.append(Joint(chosen.forward, chosen.beam_set,
                                  chosen.sided_ft, 'butt'))
            last = chosen.forward
    return stations


def _scarf_tool(forward, x0, x1):
    width = x1 - x0
    length = max(DECK_SCARF_LENGTH_FT, width * 1.25)
    origin = cq.Vector(0, 25 - forward, 0)
    across = cq.Vector(width, length, 0)
    normal = cq.Vector(length, -width, 0)
    plane = cq.Plane(origin=origin, xDir=across, normal=normal)
    return cq.Face.makeFromWires(
        cq.Workplane(plane).rect(math.hypot(width, length) + .1, 20).val())


@lru_cache(maxsize=1)
def _kingplank_scarfs():
    raw, _ = _raw_pieces()
    pieces = _run_pieces(raw, 'Kingplank')
    if not pieces:
        return ()
    longest = max(pieces, key=lambda piece: piece.f1 - piece.f0)
    if longest.f1 - longest.f0 < DECK_SCARF_MIN_BOARD_FT:
        return ()
    stations = []
    length = longest.f1 - longest.f0
    if length <= DECK_MAX_BOARD_LENGTH_FT:
        stations = [longest.f0 + length / 2]
    else:
        cursor = longest.f0 + 10.0
        while cursor < longest.f1 - DECK_MIN_BOARD_LENGTH_FT:
            stations.append(cursor)
            cursor += 10.0
    result = []
    for forward in stations:
        width = longest.x1 - longest.x0
        scarf_length = max(DECK_SCARF_LENGTH_FT, width * 1.25)
        angle = math.degrees(math.atan2(scarf_length, width))
        seam = (cq.Workplane('XY').box(math.hypot(width, scarf_length), .012, .006)
                .rotate((0, 0, 0), (0, 0, 1), angle)
                .translate((0, 25 - forward, hull.deck_height(forward, 0) + .004)).val())
        result.append(dict(forward=forward, x0=longest.x0, x1=longest.x1,
                           shape=seam, angle=angle))
    return tuple(result)


def _local_f_tool(forward, x0, x1):
    return cq.Face.makeFromWires(
        cq.Workplane('XZ', origin=(0, 25 - forward, 0))
        .center((x0 + x1) / 2, 10).rect(x1 - x0, 20).val())


def _field_pieces(raw, order, selected):
    positive = _course_edges()
    tools = [plane_x(x) for edge in positive for x in (-edge, edge)]
    for run in order:
        pieces = _run_pieces(raw, run)
        for joint in selected[run]:
            candidates = [piece for piece in pieces
                          if piece.f0 - 1e-6 <= joint.forward <= piece.f1 + 1e-6]
            if not candidates:
                continue
            piece = candidates[0]
            if joint.kind == 'butt':
                tools.append(_local_f_tool(joint.forward, piece.x0, piece.x1))
            else:
                tools.append(_scarf_tool(joint.forward, piece.x0, piece.x1))
    pieces = split_material(_waterway_split()[0], tools)
    rows = []
    for shape in pieces:
        box = shape.BoundingBox()
        rows.append(dict(run=_label(shape.Center().x, positive), shape=shape,
                         f0=25 - box.ymax, f1=25 - box.ymin,
                         x0=box.xmin, x1=box.xmax))
    return rows


def _repair_long_boards(boards, selected, order, previous_run, next_run):
    """Split any board that the one-shot field split left over 12 ft.

    The field splitter can leave a board wrapped around an opening sliver
    connected. Re-cut those closures on a supporting beam so the standard
    lumber limit is hard, not just an aiming target.
    """
    repaired = []
    for board in boards:
        if board['length'] <= DECK_MAX_BOARD_LENGTH_FT + 1e-6:
            repaired.append(board)
            continue
        candidates = [support for support in _beam_supports()
                      if _supported(support, board['x0'], board['x1'])
                      and board['f0'] + DECK_MIN_BOARD_LENGTH_FT < support.forward
                      < board['f1'] - DECK_MIN_BOARD_LENGTH_FT]
        previous = [joint.forward for joint in selected[previous_run[board['run']]]]
        following = next_run.get(board['run'])
        if following is not None:
            previous += [joint.forward for joint in selected[following]]
        stations = []
        last = board['f0']
        while board['f1'] - last > DECK_MAX_BOARD_LENGTH_FT + 1e-6:
            target = last + DECK_MAX_BOARD_LENGTH_FT
            usable = [support for support in candidates
                      if last + DECK_MIN_BOARD_LENGTH_FT < support.forward <= target + 1e-9
                      and support.forward < board['f1'] - DECK_MIN_BOARD_LENGTH_FT]
            chosen = None
            for minimum in (DECK_STAGGER_FT, 2.0):
                for support in sorted(usable, key=lambda item: abs(item.forward - target)):
                    if all(abs(support.forward - other) >= minimum for other in previous):
                        chosen = support
                        break
                if chosen is not None:
                    break
            if chosen is None:
                break
            stations.append(chosen)
            last = chosen.forward
        if not stations:
            repaired.append(board)
            continue
        pieces = split_material(board['shape'],
                                [plane_f(support.forward) for support in stations])
        pieces.sort(key=lambda shape: 25 - shape.Center().y)
        for index, shape in enumerate(pieces):
            box = shape.BoundingBox()
            aft = board['butt_aft'] if index == 0 else Joint(
                stations[index - 1].forward, stations[index - 1].beam_set,
                stations[index - 1].sided_ft)
            fore = board['butt_fore'] if index == len(pieces) - 1 else Joint(
                stations[index].forward, stations[index].beam_set,
                stations[index].sided_ft)
            repaired.append(dict(board, name=board['name'], shape=shape,
                                 f0=25 - box.ymax, f1=25 - box.ymin,
                                 length=(25 - box.ymin) - (25 - box.ymax),
                                 butt_aft=aft, butt_fore=fore))
    for run in order:
        rows = sorted((board for board in repaired if board['run'] == run),
                      key=lambda board: board['f0'])
        for number, board in enumerate(rows, 1):
            board['name'] = f"{run} board {number:02d}"
    return repaired


ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / 'output'
CACHE_BREP = CACHE_DIR / 'm4_deck_cache.brep'
CACHE_META = CACHE_DIR / 'm4_deck_cache.json'
CACHE_SOURCES = (
    'parts/deck_planking.py', 'parts/board_tools.py', 'parts/params.py',
    'parts/beam_layout.py', 'parts/framing.py', 'parts/openings.py',
    'parts/hull.py', 'parts/centreline_layout.py',
    'drawing_package/m4_deck_schedule.json',
)


def _cache_key():
    digest = hashlib.sha256()
    for name in CACHE_SOURCES:
        digest.update((ROOT / name).read_bytes())
    source = hull.make_deck()
    box = source.BoundingBox()
    digest.update(repr((source.Volume(1e-6), box.xmin, box.xmax, box.ymin,
                        box.ymax, box.zmin, box.zmax)).encode())
    return digest.hexdigest()


def _joint_meta(joint):
    if joint is None:
        return None
    return dict(forward=joint.forward, beam_set=joint.beam_set,
                sided_ft=joint.sided_ft, kind=joint.kind)


def _joint_from(meta):
    if meta is None:
        return None
    return Joint(meta['forward'], meta['beam_set'], meta['sided_ft'], meta['kind'])


def _write_cache(boards, key):
    CACHE_DIR.mkdir(exist_ok=True)
    compound = cq.Compound.makeCompound([board['shape'] for board in boards])
    cq.exporters.export(compound, str(CACHE_BREP), exportType='BREP')
    rows = []
    for board in boards:
        rows.append(dict(
            name=board['name'], run=board['run'], f0=board['f0'], f1=board['f1'],
            length=board['length'], x0=board['x0'], x1=board['x1'],
            stock=board['stock'], material=board['material'],
            butt_aft=_joint_meta(board['butt_aft']),
            butt_fore=_joint_meta(board['butt_fore']),
            scarf=board['scarf'], scarf_aft=board['scarf_aft'],
            scarf_fore=board['scarf_fore']))
    CACHE_META.write_text(json.dumps(dict(key=key, boards=rows), indent=2) + '\n')


def _read_cache(key):
    if not CACHE_BREP.exists() or not CACHE_META.exists():
        return None
    meta = json.loads(CACHE_META.read_text())
    if meta.get('key') != key:
        return None
    compound = cq.importers.importBrep(str(CACHE_BREP)).val()
    solids = compound.Solids()
    rows = meta['boards']
    if len(solids) != len(rows):
        return None
    boards = []
    for shape, row in zip(solids, rows):
        boards.append(dict(
            name=row['name'], run=row['run'], shape=shape,
            f0=row['f0'], f1=row['f1'], length=row['length'],
            x0=row['x0'], x1=row['x1'], stock=row['stock'],
            material=row['material'], butt_aft=_joint_from(row['butt_aft']),
            butt_fore=_joint_from(row['butt_fore']), scarf=row['scarf'],
            scarf_aft=row['scarf_aft'], scarf_fore=row['scarf_fore']))
    source = _waterway_split()[0]
    total = sum(board['shape'].Volume(1e-9) for board in boards)
    if abs(total - source.Volume(1e-9)) > source.Volume(1e-9) * 1e-6:
        return None
    return tuple(boards)


@lru_cache(maxsize=1)
def deck_boards():
    key = _cache_key()
    cached = _read_cache(key)
    if cached is not None:
        return cached
    boards = _compute_deck_boards()
    _write_cache(boards, key)
    return boards


def _compute_deck_boards():
    raw, order = _raw_pieces()
    scarfs = _kingplank_scarfs()
    previous_run = {'Kingplank': None}
    next_run = {}
    for side in ('Port', 'Starboard'):
        runs = sorted(run for run in order if run.startswith(side))
        previous_run[runs[0]] = 'Kingplank'
        next_run['Kingplank'] = runs[0] if side == 'Port' else next_run.get('Kingplank')
        for aft, fore in zip(runs, runs[1:]):
            previous_run[fore] = aft
            next_run[aft] = fore
    selected = {}
    for run in order:
        if run == 'Kingplank':
            selected[run] = [Joint(scarf['forward'], None, None, 'scarf')
                             for scarf in scarfs]
        else:
            previous = [joint.forward for joint in selected[previous_run[run]]]
            selected[run] = _select_field_butts(run, _run_pieces(raw, run), previous)
    rows = _field_pieces(raw, order, selected)
    boards = []
    for run in order:
        run_rows = sorted((row for row in rows if row['run'] == run),
                          key=lambda row: (row['f0'], row['f1']))
        centre = run == 'Kingplank'
        stock = (f'{DECK_KINGPLANK_NOMINAL_IN}-in nominal '
                 f'({DECK_CENTRE_PLANK_WIDTH_FT * 12:g}-in actual)') if centre else (
                 f'{DECK_PLANK_NOMINAL_IN}-in nominal '
                 f'({DECK_PLANK_WIDTH_FT * 12:g}-in actual)')
        for number, row in enumerate(run_rows, 1):
            butt_aft = next((joint for joint in selected[run]
                             if abs(row['f0'] - joint.forward) <= 1e-4), None)
            butt_fore = next((joint for joint in selected[run]
                              if abs(row['f1'] - joint.forward) <= 1e-4), None)
            boards.append(dict(
                name=f'{run} board {number:02d}', run=run, shape=row['shape'],
                f0=row['f0'], f1=row['f1'], length=row['f1'] - row['f0'],
                x0=row['x0'], x1=row['x1'], stock=stock,
                material='kingplank stock; scarf joint inferred' if centre else
                'fir; individual pine replacement identity unresolved',
                butt_aft=butt_aft, butt_fore=butt_fore,
                scarf=centre and any(row['f0'] - .1 <= scarf['forward'] <= row['f1'] + .1
                                     for scarf in scarfs),
                scarf_aft=centre and any(abs(row['f0'] - scarf['forward']) < .5
                                         for scarf in scarfs),
                scarf_fore=centre and any(abs(row['f1'] - scarf['forward']) < .5
                                          for scarf in scarfs),
            ))
    boards = _repair_long_boards(boards, selected, order, previous_run, next_run)
    source = _waterway_split()[0]
    total = sum(row['shape'].Volume(1e-9) for row in boards)
    expected = source.Volume(1e-9)
    assert abs(total - expected) < expected * 1e-6, 'Deck board material lost or duplicated'
    assert all(row['shape'].isValid() and len(row['shape'].Solids()) == 1
               for row in boards), 'Invalid deck board'
    return tuple(boards)


def pattern_supports():
    return _beam_supports()


def pattern_scarfs():
    return _kingplank_scarfs()


def pattern_waterway():
    return _waterway_split()


def make_deck_board_parts():
    for row in deck_boards():
        yield row['name'], row['shape'], (.63, .60, .51), 'Deck/Planking/' + row['run']


def make_waterway_parts():
    """Provisional oak deck margin; waterway section is not final."""
    number = 0
    for shape in _waterway_split()[1]:
        for solid in sorted(shape.Solids(), key=lambda item: item.Center().x, reverse=True):
            number += 1
            label = 'Port' if solid.Center().x > 0 else 'Starboard'
            yield f'{label} waterway {number:02d}', solid, (.53, .37, .22)


def make_kingplank_scarf_parts():
    for index, scarf in enumerate(_kingplank_scarfs(), 1):
        yield f'Kingplank scarf {index:02d}', scarf['shape'], (.30, .18, .10)
