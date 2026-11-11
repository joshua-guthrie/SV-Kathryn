"""Exact M4 deck material partition; no continuous backing under the boards.

S05-08: longitudinal 1.75-in planking, normally 3.5-4 in wide, with broader
inboard stock. Individual historic seams/replacements are not fully recorded.
This first increment separates runs; supported butt joints follow the beam
integration. A hatch-separated segment is not an inferred timber butt.
"""
from bisect import bisect_right
from functools import lru_cache

from . import hull
from .board_tools import plane_x, split_material
from .params import DECK_PLANK_WIDTH_FT, DECK_CENTRE_PLANK_WIDTH_FT


@lru_cache(maxsize=1)
def deck_boards():
    source = hull.make_deck()
    maximum = max(abs(source.BoundingBox().xmin), abs(source.BoundingBox().xmax))
    positive = []
    edge = DECK_CENTRE_PLANK_WIDTH_FT / 2
    while edge < maximum:
        positive.append(edge)
        edge += DECK_PLANK_WIDTH_FT
    pieces = split_material(source, [plane_x(x) for edge in positive for x in (-edge, edge)])
    groups = {}
    for shape in pieces:
        x = shape.Center().x
        course = bisect_right(positive, abs(x))
        label = ('Deck centre plank' if course == 0 else
                 f'{"Port" if x > 0 else "Starboard"} deck plank {course:02d}')
        groups.setdefault(label, []).append(shape)
    result = []
    for label, shapes in sorted(groups.items()):
        for number, shape in enumerate(sorted(shapes, key=lambda s: 25 - s.Center().y), 1):
            result.append(dict(name=f'{label} segment {number:02d}', run=label, shape=shape,
                               material='undetermined kingplank stock' if label == 'Deck centre plank'
                               else 'fir; individual pine replacement identity unresolved'))
    total = sum(row['shape'].Volume(1e-9) for row in result)
    expected = source.Volume(1e-9)
    assert abs(total - expected) < expected * 1e-6, 'Deck board material lost or duplicated'
    assert all(row['shape'].isValid() and len(row['shape'].Solids()) == 1 for row in result)
    return tuple(result)


def make_deck_board_parts():
    for row in deck_boards():
        yield row['name'], row['shape'], (.63, .60, .51), 'Deck/Planking/' + row['run']
