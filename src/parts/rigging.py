"""M6 standing and running rigging from S03 and S08.

The spar axes and hull attachment points come from the accepted model. Line
paths are reconstructions of the S03 rigging key; sails follow the S08 plan
and are registered as display references because the notes call the hoops/hanks
demonstration only.
"""
import math

import cadquery as cq

from .params import (
    boat_point, MAST_STEP_HEIGHT_FT, MAST_HEIGHT_FT, MAST_DECK_FORWARD_FT,
    MAST_DIAMETER_FT, BOOM_FRONT_HEIGHT_FT, BOOM_AFT_POSITION_FT,
    BOOM_AFT_HEIGHT_FT, BOWSPRIT_HEEL_FT, BOWSPRIT_END_FT,
    JIB_TRAVELLER_FORWARD_FT, RIG_HEIGHT_RISE_FT, WATERLINE_FT,
    STERN_REMEDY_SOURCE, IRON, WOOD, HULL_LENGTH_FT,
)
from .spars import mast_forward_at, mast_radius_at, _boom_front_forward
from .bow import bowsprit_height, stem_forward_at
from .hull import deck_height, topside_halfwidth
from .primitives import spar_between, block

STAINLESS = (.62, .66, .68)
ROPE = (.58, .45, .29)
SAIL = (.88, .86, .78)

HEAD_Z = MAST_STEP_HEIGHT_FT + MAST_HEIGHT_FT
HEAD_F = mast_forward_at(HEAD_Z)
HEAD = boat_point(0, HEAD_F, HEAD_Z)
HOUNDS_Z = HEAD_Z - .8
HOUNDS = boat_point(0, mast_forward_at(HOUNDS_Z), HOUNDS_Z)
TIP = boat_point(0, BOWSPRIT_END_FT, bowsprit_height(BOWSPRIT_END_FT))
TIP_UNDER = boat_point(0, BOWSPRIT_END_FT - .12,
                       bowsprit_height(BOWSPRIT_END_FT) - .13)
BOWSPRIT_HEEL = boat_point(0, BOWSPRIT_HEEL_FT,
                           bowsprit_height(BOWSPRIT_HEEL_FT))
STEM_Z = WATERLINE_FT + 1.0
STEM = boat_point(0, stem_forward_at(STEM_Z), STEM_Z)
BOOM_FRONT = boat_point(0, _boom_front_forward, BOOM_FRONT_HEIGHT_FT)
BOOM_AFT = boat_point(0, BOOM_AFT_POSITION_FT, BOOM_AFT_HEIGHT_FT)

# Main lazyjacks (S03 key item 6): one pendant per side from the hounds to two
# junction blocks, then legs to four stations spread along the boom. The
# stations are model Y (aft to fore), measured on the S03 rigging sheet at
# about 14 / 38 / 65 / 89 % of the boom spar from the aft end.
MAIN_LAZYJACK_STATIONS_Y_FT = (30.3, 17.7, 4.0, -8.2)
MAIN_LAZYJACK_J1_Y_Z_FT = (-8.2, 37.0)
MAIN_LAZYJACK_J2_Y_Z_FT = (6.0, 26.0)
LAZYJACK_X_FT = .75
JIB_LAZYJACK_JUNCTION_Z_FT = 24.0
MAIN_LUFF_FT = 45 + 6 / 12
MAIN_FOOT_FT = 49 + 4 / 12
JIB_LUFF_FT = 49 + 6 / 12
JIB_FOOT_FT = 25 + 8 / 12
JIB_LEECH_FT = 42.0


def _mast_point_at_distance(tack, distance):
    lo, hi = tack[2], HEAD_Z
    for _ in range(70):
        z = (lo + hi) / 2
        p = boat_point(0, mast_forward_at(z), z)
        if math.dist(tack, p) < distance:
            lo = z
        else:
            hi = z
    z = (lo + hi) / 2
    return boat_point(0, mast_forward_at(z), z)


MAIN_TACK = BOOM_FRONT
MAIN_HEAD = _mast_point_at_distance(MAIN_TACK, MAIN_LUFF_FT)
_boom_length = math.dist(BOOM_FRONT, BOOM_AFT)
MAIN_CLEW = tuple(a + (b - a) * MAIN_FOOT_FT / _boom_length
                  for a, b in zip(BOOM_FRONT, BOOM_AFT))
# The jib foot is carried on a club above the bowsprit. Raising the whole
# S08 triangle by this amount clears the spar (about 0.5 ft of air above the
# club) without changing the sail's luff, foot or leech.
JIB_FOOT_RAISE_FT = .75
JIB_CLUB_RADIUS_FORE = .11
JIB_CLUB_RADIUS_AFT = .07
_JIB_RAISE = (0.0, 0.0, JIB_FOOT_RAISE_FT)
JIB_TACK = tuple(a + b for a, b in zip(TIP, _JIB_RAISE))
_JIB_HEAD_BASE = tuple(a + (b - a) * JIB_LUFF_FT / math.dist(TIP, HEAD)
                       for a, b in zip(TIP, HEAD))
JIB_HEAD = tuple(a + b for a, b in zip(_JIB_HEAD_BASE, _JIB_RAISE))
_t = __import__('numpy').array(JIB_TACK)
_h = __import__('numpy').array(JIB_HEAD)
_d = float(__import__('numpy').linalg.norm(_h - _t))
_u = (_h - _t) / _d
_a = (JIB_FOOT_FT ** 2 - JIB_LEECH_FT ** 2 + _d ** 2) / (2 * _d)
_half = math.sqrt(max(0.0, JIB_FOOT_FT ** 2 - _a ** 2))
_base = _t + _u * _a
_perp = __import__('numpy').array((0.0, -_u[2], _u[1]))
_perp /= __import__('numpy').linalg.norm(_perp)
_c1, _c2 = _base + _perp * _half, _base - _perp * _half
JIB_CLEW = tuple(_c1 if _c1[1] > _c2[1] else _c2)


def _chain_f(i=0):
    return MAST_DECK_FORWARD_FT + 1.0 + .22 * i


def _chain_x(i=0):
    f = _chain_f(i)
    return topside_halfwidth(f, deck_height(f)) - .16


def _chain(side, i=0):
    f = _chain_f(i)
    return boat_point(side * _chain_x(i), f, deck_height(f))


def _mast_cleat(side):
    z = deck_height(MAST_DECK_FORWARD_FT) + 3.0
    f = mast_forward_at(z)
    return boat_point(side * (mast_radius_at(z) + .13), f, z)


def _pin_rail(side):
    f = MAST_DECK_FORWARD_FT + 1.15
    x = side * (topside_halfwidth(f, deck_height(f)) - .32)
    return boat_point(x, f, deck_height(f, x) + .10)


def _line(a, b, r=.018):
    return spar_between(tuple(a), tuple(b), r)


def _boat_y(y):
    """Model Y (bow -Y) to the source forward coordinate of boat_point."""
    return HULL_LENGTH_FT / 2 - y


def _boom_at(f):
    t = (f - _boom_front_forward) / (BOOM_AFT_POSITION_FT - _boom_front_forward)
    z = BOOM_FRONT_HEIGHT_FT + t * (BOOM_AFT_HEIGHT_FT - BOOM_FRONT_HEIGHT_FT)
    return z, .24 + t * (.15 - .24)


def _main_lazyjack_station(side, y):
    f = _boat_y(y)
    z, radius = _boom_at(f)
    return boat_point(side * (radius + .12), f, z + .02)


def _main_lazyjack_junctions(side):
    j1 = boat_point(side * LAZYJACK_X_FT, _boat_y(MAIN_LAZYJACK_J1_Y_Z_FT[0]),
                    MAIN_LAZYJACK_J1_Y_Z_FT[1])
    j2 = boat_point(side * LAZYJACK_X_FT, _boat_y(MAIN_LAZYJACK_J2_Y_Z_FT[0]),
                    MAIN_LAZYJACK_J2_Y_Z_FT[1])
    return j1, j2


def _jib_lazyjack_junction(side):
    mid_y = (JIB_TACK[1] + JIB_CLEW[1]) / 2
    return (side * LAZYJACK_X_FT * 1.0,
            mid_y, JIB_LAZYJACK_JUNCTION_Z_FT)


def _jib_club_point(t, side):
    point = [a + (b - a) * t for a, b in zip(JIB_TACK, JIB_CLEW)]
    radius = (JIB_CLUB_RADIUS_FORE
              + (JIB_CLUB_RADIUS_AFT - JIB_CLUB_RADIUS_FORE) * t)
    point[0] = side * (radius + .10)
    point[2] += radius + .02
    return tuple(point)


def _main_lazyjack_lines():
    z_top = HOUNDS_Z - .3
    for side, label in ((1, 'Port'), (-1, 'Starboard')):
        top = boat_point(side * (mast_radius_at(z_top) + .05),
                         mast_forward_at(z_top) - mast_radius_at(z_top) - .04,
                         z_top)
        j1, j2 = _main_lazyjack_junctions(side)
        yield f'{label} main lazyjack pendant', _line(top, j1, .012), ROPE
        yield f'{label} main lazyjack branch', _line(j1, j2, .012), ROPE
        for i, y in enumerate(MAIN_LAZYJACK_STATIONS_Y_FT, 1):
            junction = j1 if i == len(MAIN_LAZYJACK_STATIONS_Y_FT) else j2
            yield f'{label} main lazyjack leg {i}', _line(
                junction, _main_lazyjack_station(side, y), .012), ROPE
        for i, junction in enumerate((j1, j2), 1):
            yield f'{label} main lazyjack tail {i}', _line(
                (junction[0], junction[1], junction[2] - .07),
                (junction[0], junction[1], junction[2] - .9), .012), ROPE


def _jib_lazyjack_lines():
    z_top = HOUNDS_Z - .3
    for side, label in ((1, 'Port'), (-1, 'Starboard')):
        top = boat_point(side * (mast_radius_at(z_top) + .05),
                         mast_forward_at(z_top) + mast_radius_at(z_top) + .04,
                         z_top)
        junction = _jib_lazyjack_junction(side)
        yield f'{label} jib lazyjack pendant', _line(top, junction, .012), ROPE
        for i, t in enumerate((1 / 3, 2 / 3), 1):
            yield f'{label} jib lazyjack leg {i}', _line(
                junction, _jib_club_point(t, side), .012), ROPE
        yield f'{label} jib lazyjack tail', _line(
            (junction[0], junction[1], junction[2] - .07),
            (junction[0], junction[1], junction[2] - .9), .012), ROPE


def _standing_parts():
    yield 'Bobstay', _line(TIP_UNDER, STEM, .024), STAINLESS
    yield 'Head stay', _line(HEAD, BOWSPRIT_HEEL, .024), STAINLESS
    yield 'Jib stay', _line(HEAD, JIB_TACK, .022), STAINLESS
    for side, label in ((1, 'Port'), (-1, 'Starboard')):
        for i in (0, 1):
            yield f'{label} shroud {i + 1}', _line(HOUNDS, _chain(side, i), .022), STAINLESS
    yield 'Jack stay', _line(HEAD, boat_point(0, JIB_TRAVELLER_FORWARD_FT,
                                             deck_height(JIB_TRAVELLER_FORWARD_FT) + .25), .018), STAINLESS


def _running_parts():
    yield 'Main halyard', _line(HEAD, _mast_cleat(-1), .017), ROPE
    yield 'Jib halyard', _line(JIB_HEAD, _mast_cleat(1), .017), ROPE
    yield 'Topping lift', _line(HEAD, BOOM_AFT, .016), ROPE
    boom_lift_z = BOOM_FRONT_HEIGHT_FT + 1.4
    boom_lift_f = mast_forward_at(boom_lift_z)
    yield 'Boom lift', _line(boat_point(0, boom_lift_f, boom_lift_z), BOOM_FRONT, .016), ROPE
    yield from _main_lazyjack_lines()
    yield from _jib_lazyjack_lines()
    trav = STERN_REMEDY_SOURCE['traveller']
    tf = trav['forward_ft']
    tz = deck_height(tf) + trav['height_above_deck_ft']
    traveller = boat_point(0, tf, tz + .08)
    # The main sheet hangs vertically from the boom directly above the
    # traveller car. It does not lead aft to the boom end or through the rails.
    t = (traveller[1] - BOOM_FRONT[1]) / (BOOM_AFT[1] - BOOM_FRONT[1])
    boom_sheet = tuple(a + (b - a) * t for a, b in zip(BOOM_FRONT, BOOM_AFT))
    yield 'Main sheet', _line(boat_point(0, tf, boom_sheet[2]), traveller, .017), ROPE
    yield 'Jib sheet to hounds', _line(JIB_CLEW, HOUNDS, .015), ROPE
    yield 'Jib sheet to pin rail', _line(HOUNDS, _pin_rail(1), .015), ROPE
    yield 'Jib downhaul', _line(JIB_HEAD, TIP, .013), ROPE
    yield 'Spectacle/jack iron', _line(HEAD, _pin_rail(-1), .015), ROPE


def _fitting_parts():
    # Hounds band and masthead cap
    hz = HOUNDS_Z
    hf = mast_forward_at(hz)
    hr = mast_radius_at(hz)
    band = spar_between(boat_point(0, hf, hz - .07),
                        boat_point(0, hf, hz + .07), hr + .045)
    yield 'Mast hounds band', band.cut(
        spar_between(boat_point(0, hf, hz - .10),
                     boat_point(0, hf, hz + .10), hr + .006)), IRON
    yield 'Masthead cap', spar_between(boat_point(0, HEAD_F, HEAD_Z - .04),
                                       boat_point(0, HEAD_F, HEAD_Z + .10), .22), IRON
    for side, label in ((1, 'Port'), (-1, 'Starboard')):
        for i in (0, 1):
            f = _chain_f(i)
            x = side * _chain_x(i)
            z = deck_height(f)
            yield f'{label} chainplate {i + 1}', block(x, f, z - .18, .18, .22, .28), IRON
        cz = deck_height(MAST_DECK_FORWARD_FT) + 3.0
        cf = mast_forward_at(cz)
        yield f'{label} mast cleat', block(side * (mast_radius_at(cz) + .15),
                                          cf, cz - .06, .22, .28, .12), IRON
        pf = MAST_DECK_FORWARD_FT + 1.15
        px = side * (topside_halfwidth(pf, deck_height(pf)) - .32)
        py = 25 - pf
        yield f'{label} pin rail', block(px, pf, deck_height(pf, px) + .02,
                                        .12, 1.20, .10), WOOD
    yield 'Bowsprit cheek block', block(.18, BOWSPRIT_END_FT - .55,
                                        bowsprit_height(BOWSPRIT_END_FT - .55),
                                        .18, .30, .20), IRON
    yield 'Boom reefing cheek block', block(.20, _boom_front_forward + 1.0,
                                            BOOM_FRONT_HEIGHT_FT + .18,
                                            .16, .28, .18), IRON
    for side, label in ((1, 'Port'), (-1, 'Starboard')):
        for i, (y, z) in enumerate((MAIN_LAZYJACK_J1_Y_Z_FT,
                                    MAIN_LAZYJACK_J2_Y_Z_FT), 1):
            yield (f'{label} main lazyjack junction {i}',
                   block(side * LAZYJACK_X_FT, _boat_y(y), z - .06,
                         .10, .12, .14), IRON)
        jib_mid_y = (JIB_TACK[1] + JIB_CLEW[1]) / 2
        yield (f'{label} jib lazyjack junction',
               block(side * LAZYJACK_X_FT, _boat_y(jib_mid_y),
                     JIB_LAZYJACK_JUNCTION_Z_FT - .06, .10, .12, .14), IRON)


def make_rigging_parts():
    yield from ((name, shape, color, 'Rigging/Standing')
                for name, shape, color in _standing_parts())
    yield from ((name, shape, color, 'Rigging/Running')
                for name, shape, color in _running_parts())
    yield from ((name, shape, color, 'Rigging/Fittings')
                for name, shape, color in _fitting_parts())


def _triangle(a, b, c, thickness=.018):
    wire = cq.Wire.makePolygon([cq.Vector(*a), cq.Vector(*b), cq.Vector(*c), cq.Vector(*a)])
    face = cq.Face.makeFromWires(wire)
    normal = face.normalAt()
    return cq.Solid.extrudeLinear(wire, [], normal.multiply(thickness))


def make_sail_spars():
    yield 'Jib club', spar_between(JIB_TACK, JIB_CLEW,
                                   JIB_CLUB_RADIUS_FORE, JIB_CLUB_RADIUS_AFT), WOOD


def make_sail_parts():
    # S08 sail plan: main luff 45'-6", foot 49'-4", leech 68'-0";
    # jib luff 49'-6", foot 25'-8", leech 42'-0".
    main_tack = MAIN_TACK
    main_clew = MAIN_CLEW
    main_head = MAIN_HEAD
    jib_head = JIB_HEAD
    jib_tack = JIB_TACK
    jib_clew = JIB_CLEW
    yield 'Main sail (S08 demonstration)', _triangle(main_tack, main_head, main_clew), SAIL, 'Sails'
    yield 'Jib sail (S08 demonstration)', _triangle(jib_tack, jib_head, jib_clew), SAIL, 'Sails'
