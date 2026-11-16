"""M6 standing and running rigging from S03 and S08.

The spar axes and hull attachment points come from the accepted model. Line
paths are reconstructions of the S03 rigging key; sails follow the S08 plan
and are registered as display references because the notes call the hoops/hanks
demonstration only.
"""
import math
import numpy as np

import cadquery as cq

from .params import (
    boat_point, MAST_STEP_HEIGHT_FT, MAST_HEIGHT_FT, MAST_DECK_FORWARD_FT,
    MAST_DIAMETER_FT, BOOM_FRONT_HEIGHT_FT, BOOM_AFT_POSITION_FT,
    BOOM_AFT_HEIGHT_FT, BOWSPRIT_HEEL_FT, BOWSPRIT_END_FT,
    JIB_TRAVELLER_FORWARD_FT, RIG_HEIGHT_RISE_FT, WATERLINE_FT,
    STERN_REMEDY_SOURCE, IRON, WOOD, HULL_LENGTH_FT,
)
from .spars import mast_forward_at, mast_radius_at, _boom_front_forward
from .bow import (bowsprit_height, stem_forward_at, tack_point, headstay_point, make_tack_pin, make_downhaul_block, downhaul_route)
from .bow_layout import RIG,SPAR
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
TIP = boat_point(0, SPAR['end_f'], bowsprit_height(SPAR['end_f']))
TIP_UNDER = boat_point(0, SPAR['end_f']-.12, bowsprit_height(SPAR['end_f'])-.13)
BOWSPRIT_HEEL = headstay_point()  # Source stem-head eye, distinct from timber after end.
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
# Solve the sail on the physical tack/stay. No whole-triangle translation.
JIB_CLUB_RADIUS_FORE=RIG['club_fore_radius_ft']
JIB_CLUB_RADIUS_AFT=RIG['club_aft_radius_ft']
JIB_TACK=tack_point()
JIB_FOOT_RAISE_FT=JIB_TACK[2]-TIP[2]  # Measured fitting elevation, not an arbitrary offset.
_t=np.array(JIB_TACK);_mast=np.array(HEAD)
JIB_HEAD=tuple(_t+(_mast-_t)*JIB_LUFF_FT/np.linalg.norm(_mast-_t))
_u=(np.array(JIB_HEAD)-_t)/JIB_LUFF_FT
_a=(JIB_FOOT_FT**2-JIB_LEECH_FT**2+JIB_LUFF_FT**2)/(2*JIB_LUFF_FT)
_half=math.sqrt(JIB_FOOT_FT**2-_a**2)
_perp=np.array((0.,-_u[2],_u[1]))
_candidates=[_t+_u*_a+sign*_perp*_half for sign in (-1,1)]
JIB_CLEW=tuple(max(_candidates,key=lambda p:p[1]))


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


def _rope_path(points,r):
    segments=[_line(a,b,r) for a,b in zip(points,points[1:])]
    nodes=[cq.Solid.makeSphere(r,cq.Vector(*p)) for p in points[1:-1]]
    return segments[0].fuse(*segments[1:],*nodes).clean()


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


def _club_station(t):
    point=np.array(JIB_TACK)+(np.array(JIB_CLEW)-np.array(JIB_TACK))*t
    length=math.dist(JIB_TACK,JIB_CLEW)
    q=(length*t+RIG['club_fore_overhang_ft'])/(length+RIG['club_fore_overhang_ft'])
    radius=JIB_CLUB_RADIUS_FORE+(JIB_CLUB_RADIUS_AFT-JIB_CLUB_RADIUS_FORE)*q
    return point,radius


def _jib_club_point(t, side):
    point,radius=_club_station(t)
    point[0]=side*(radius+.013)  # Centreline of the actual rope strop.
    return tuple(point)


def _jib_club_strop(t):
    point,radius=_club_station(t)
    direction=np.array(JIB_CLEW)-np.array(JIB_TACK)
    direction/=np.linalg.norm(direction)
    return cq.Solid.makeTorus(radius+.013,.012,tuple(point),tuple(direction))


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
    yield 'Jib downhaul', _rope_path(downhaul_route(JIB_HEAD),.013), ROPE
    yield 'Spectacle/jack iron', _line(HEAD, _pin_rail(-1), .015), ROPE


def _fitting_parts():
    for i,t in enumerate((1/3,2/3),1):
        yield f'Jib club lazyjack strop {i}',_jib_club_strop(t),ROPE
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
    yield 'Bowsprit cheek block', make_downhaul_block(), IRON
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


def make_jib_club():
    t=np.array(JIB_TACK);c=np.array(JIB_CLEW);u=(c-t)/np.linalg.norm(c-t)
    start=tuple(t-u*RIG['club_fore_overhang_ft'])
    raw=spar_between(start,tuple(c),JIB_CLUB_RADIUS_FORE,JIB_CLUB_RADIUS_AFT)
    # Transverse pivot passage aligns with the retained tack pin.
    x,y,z=JIB_TACK
    bore=spar_between((-.3,y,z),(.3,y,z),RIG['tack_pin_radius_ft']+.0015)
    return raw.cut(bore).clean()


def make_sail_spars():
    yield 'Jib club', make_jib_club(), WOOD


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
    yield 'Jib sail (S08 demonstration)', max(_triangle(jib_tack, jib_head, jib_clew).cut(make_jib_club()).Solids(),key=lambda s:s.Volume()), SAIL, 'Sails'
