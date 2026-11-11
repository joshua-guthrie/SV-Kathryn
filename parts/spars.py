"""Bare spars shown in sheets 3 and 4; no sails, ropes or wire rigging."""
import cadquery as cq
import numpy as np

from .params import (
    boat_point, MAST_POSITION_FT, MAST_DIAMETER_FT, MAST_HEIGHT_FT,
    MAST_STEP_HEIGHT_FT, MAST_RAKE_FT, BOOM_AFT_POSITION_FT, BOWSPRIT_END_FT,
    WOOD, IRON, BOWSPRIT_HEEL_FT, BOOM_FRONT_HEIGHT_FT, BOOM_AFT_HEIGHT_FT,
    BOWSPRIT_HEEL_RADIUS_FT, BOWSPRIT_TIP_RADIUS_FT,
    MAST_DECK_FORWARD_FT, JIB_TRAVELLER_FORWARD_FT, legacy_forward,
    RIG_HEIGHT_RISE_FT,
)
from .primitives import spar_between
from .bow import bowsprit_height, make_walking_boards
from .hull import deck_height, rabbet_height
from . import centreline_layout as centreline


def mast_forward_at(z):
    return MAST_DECK_FORWARD_FT - MAST_RAKE_FT * (z - deck_height(MAST_DECK_FORWARD_FT)) / MAST_HEIGHT_FT


def mast_heel_height():
    f = mast_forward_at(MAST_STEP_HEIGHT_FT)
    return max(rabbet_height(f+d) for d in (-MAST_DIAMETER_FT/2,0,MAST_DIAMETER_FT/2)) + .35


def mast_radius_at(z):
    return MAST_DIAMETER_FT / 2 + (.16 - MAST_DIAMETER_FT / 2) * (z - MAST_STEP_HEIGHT_FT) / MAST_HEIGHT_FT


def make_mast():
    mast = spar_between(
        boat_point(0, mast_forward_at(MAST_STEP_HEIGHT_FT), MAST_STEP_HEIGHT_FT),
        boat_point(0, mast_forward_at(MAST_STEP_HEIGHT_FT+MAST_HEIGHT_FT),
                   MAST_STEP_HEIGHT_FT + MAST_HEIGHT_FT),
        MAST_DIAMETER_FT / 2, .16,
    )
    # Keep the accepted mast axis/head fixed; trim only its hidden heel so
    # it cannot protrude below the planked hull at the mast step.
    heel_z = mast_heel_height()
    below = (cq.Workplane('XY').box(40, 100, 40, centered=(True, True, False))
             .translate((0, 0, heel_z - 40)).val())
    # S06: faceted at/below deck to receive pine chocks. The hidden heel and
    # deck axis stay fixed. The octagon's corner count/transition are inferred.
    transition=deck_height(MAST_DECK_FORWARD_FT)+.45
    upper_keep=(cq.Workplane('XY').box(40,100,100,centered=(True,True,False))
                .translate((0,0,transition)).val())
    faceted=centreline.mast_octagonal_prism(heel_z-.2,transition+.20,deck_height).cut(below)
    return mast.intersect(upper_keep).fuse(faceted).clean()


_boom_front_forward = (mast_forward_at(BOOM_FRONT_HEIGHT_FT)
                       - mast_radius_at(BOOM_FRONT_HEIGHT_FT) - .17)


def make_boom_gooseneck():
    z = BOOM_FRONT_HEIGHT_FT
    radius = mast_radius_at(z)
    centre = np.array(boat_point(0, mast_forward_at(z), z))
    axis = np.array((0., MAST_RAKE_FT, MAST_HEIGHT_FT))
    axis /= np.linalg.norm(axis)
    collar = spar_between(tuple(centre - axis * .14), tuple(centre + axis * .14), radius + .055)
    bore = spar_between(tuple(centre - axis * .2), tuple(centre + axis * .2), radius + .006)
    collar = collar.cut(bore)
    pin = spar_between(boat_point(0, mast_forward_at(z) - radius + .025, z),
                       boat_point(0, _boom_front_forward - .15, z), .09)
    return collar.fuse(pin)


def make_bowsprit():
    return spar_between(
        boat_point(0,BOWSPRIT_HEEL_FT,bowsprit_height(BOWSPRIT_HEEL_FT)),
        boat_point(0,BOWSPRIT_END_FT,bowsprit_height(BOWSPRIT_END_FT)),
        BOWSPRIT_HEEL_RADIUS_FT,BOWSPRIT_TIP_RADIUS_FT)


def make_spars():
    yield "Mast", make_mast(), WOOD
    boom_front = boat_point(0, _boom_front_forward, BOOM_FRONT_HEIGHT_FT)
    yield "Main boom", spar_between(
        boom_front, boat_point(0, BOOM_AFT_POSITION_FT, BOOM_AFT_HEIGHT_FT), .24, .15,
    ), WOOD
    yield 'Boom gooseneck', make_boom_gooseneck(), IRON
    yield "Bowsprit",make_bowsprit(),WOOD
    yield "Jib club", spar_between(
        boat_point(0, JIB_TRAVELLER_FORWARD_FT, 10.8+RIG_HEIGHT_RISE_FT),
        boat_point(0, legacy_forward(49.1), 11.6+RIG_HEIGHT_RISE_FT), .11, .07,
    ), WOOD
    yield from make_walking_boards()
    support_f = legacy_forward(1.5)
    t = (support_f - _boom_front_forward) / (BOOM_AFT_POSITION_FT - _boom_front_forward)
    boom_z = BOOM_FRONT_HEIGHT_FT + t * (BOOM_AFT_HEIGHT_FT - BOOM_FRONT_HEIGHT_FT)
    boom_r = .24 + t * (.15 - .24)
    yield "Boom support", spar_between(
        boat_point(0, support_f, deck_height(support_f) - .04),
        boat_point(0, support_f, boom_z - boom_r + .03), .065,
    ), IRON
