"""S05-07 deck beams: full headers and paired half beams around openings.

Geometry follows the accepted deck camber through framing.make_cross_beam.
Every set in the measured schedule is registered exactly once; openings use
the same set as a pair of half beams, so no continuous beam blocks a hatch.
"""
from functools import lru_cache

import numpy as np

from . import centreline_layout, framing, hull
from .beam_layout import BEAMS, beam_name, forward as beam_forward
from .openings import framed_openings
from .params import (CENTREBOARD_ANGLE_DEG, DECK_BEAM_SIDED_FT,
                     PORT_SIDE, TRUNK_AFT_FT, TRUNK_FORE_FT, TRUNK_GAP_FT,
                     WOOD)
from .primitives import block

OAK_BEAM = (.53, .37, .22)


def _color(beam):
    return OAK_BEAM if beam['material'] == 'oak' else WOOD


@lru_cache(maxsize=1)
def _stock_passage():
    return hull.rudder_stock_passage()


@lru_cache(maxsize=1)
def _raised_board_top():
    return max(centreline_layout.make_board(float(angle)).BoundingBox().zmax
               for angle in np.linspace(0, CENTREBOARD_ANGLE_DEG, 7))


def _clear_centreboard(shape, beam):
    """Notch a full beam over the centreboard trunk for the raised board."""
    forward = beam_forward(beam)
    if not TRUNK_AFT_FT < forward < TRUNK_FORE_FT:
        return shape
    box = shape.BoundingBox()
    top = _raised_board_top() + .03
    if box.zmin >= top:
        return shape
    slot = block(0, forward, box.zmin - .01, TRUNK_GAP_FT + .10,
                 beam['sided_ft'] + .06, top - box.zmin + .01)
    shape = shape.cut(slot)
    assert shape.isValid() and len(shape.Solids()) == 1, \
        f'Centreboard notch split beam {beam_name(beam)}'
    return shape


def _clear_stock(shape, name):
    beam_box, stock_box = shape.BoundingBox(), _stock_passage().BoundingBox()
    if (beam_box.xmin < stock_box.xmax and stock_box.xmin < beam_box.xmax and
            beam_box.ymin < stock_box.ymax and stock_box.ymin < beam_box.ymax and
            beam_box.zmin < stock_box.zmax and stock_box.zmin < beam_box.zmax):
        shape = shape.cut(_stock_passage())
        assert shape.isValid() and len(shape.Solids()) == 1, f'Stern beam split by stock passage: {name}'
    return shape


def _full_beam(beam):
    forward = beam_forward(beam)
    span = framing.clamp_outer(forward) - .015
    shape = framing.make_cross_beam(forward, -span, span,
                                    beam['sided_ft'], beam['molded_ft'])
    shape = _clear_centreboard(shape, beam)
    return _clear_stock(shape, beam_name(beam))


def _half_beam(beam, opening, side):
    forward = beam_forward(beam)
    x = opening.across + side * (opening.clear_width + DECK_BEAM_SIDED_FT) / 2
    span = framing.clamp_outer(forward) - .015
    if side > 0:
        left, right = x + DECK_BEAM_SIDED_FT / 2 - .025, span
    else:
        left, right = -span, x - DECK_BEAM_SIDED_FT / 2 + .025
    shape = framing.make_cross_beam(forward, left, right,
                                    beam['sided_ft'], beam['molded_ft'])
    name = f"{opening.name} {'Port' if side > 0 else 'Starboard'} half beam {beam['set']}"
    return _clear_stock(shape, name)


def make_deck_beam_parts():
    openings = {opening.name: opening for opening in framed_openings()}
    for beam in BEAMS:
        if beam['role'] == 'split':
            opening = openings[beam['opening']]
            for side, label in ((PORT_SIDE, 'port'), (-PORT_SIDE, 'starboard')):
                name = f"{opening.name} {label} half beam {beam['set']}"
                yield name, _half_beam(beam, opening, side), _color(beam)
        else:
            yield beam_name(beam), _full_beam(beam), _color(beam)
