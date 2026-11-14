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
    STERN_REMEDY_SOURCE, IRON, WOOD,
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
JIB_TACK = TIP
JIB_HEAD = tuple(a + (b - a) * JIB_LUFF_FT / math.dist(TIP, HEAD)
                 for a, b in zip(TIP, HEAD))
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


def _standing_parts():
    yield 'Bobstay', _line(TIP_UNDER, STEM, .024), STAINLESS
    yield 'Head stay', _line(HEAD, BOWSPRIT_HEEL, .024), STAINLESS
    yield 'Jib stay', _line(HEAD, TIP, .022), STAINLESS
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
    for side, label in ((1, 'Port'), (-1, 'Starboard')):
        for i, f in enumerate((BOOM_AFT_POSITION_FT - .5,
                               BOOM_AFT_POSITION_FT + .8), 1):
            t = (f - _boom_front_forward) / (BOOM_AFT_POSITION_FT - _boom_front_forward)
            z = BOOM_FRONT_HEIGHT_FT + t * (BOOM_AFT_HEIGHT_FT - BOOM_FRONT_HEIGHT_FT)
            yield f'{label} lazy jack {i}', _line(
                boat_point(side * .16, mast_forward_at(BOOM_FRONT_HEIGHT_FT + 5.0),
                           BOOM_FRONT_HEIGHT_FT + 5.0),
                boat_point(side * .16, f, z + .18), .012), ROPE
    trav = STERN_REMEDY_SOURCE['traveller']
    tf = trav['forward_ft']
    tz = deck_height(tf) + trav['height_above_deck_ft']
    yield 'Main sheet', _line(BOOM_AFT, boat_point(0, tf, tz + .08), .017), ROPE
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
