"""Shared M2 cutting/member interfaces. Callbacks avoid hull/spar import cycles."""
from functools import lru_cache
import math
import cadquery as cq
import numpy as np
from .params import *
from .primitives import block,spar_between


def keelson_width(f):
    if f<KEELSON_SCARF_AFT_FT:return KEELSON_AFT_WIDTH_FT
    if f<KEELSON_SCARF_FORE_FT:
        t=(f-KEELSON_SCARF_AFT_FT)/(KEELSON_SCARF_FORE_FT-KEELSON_SCARF_AFT_FT)
        return KEELSON_AFT_WIDTH_FT*(1-t)+KEELSON_FORE_WIDTH_FT*t
    t=min(1,max(0,(f-KEELSON_TAPER_START_FT)/(KEELSON_FORE_FT-KEELSON_TAPER_START_FT)))
    return KEELSON_FORE_WIDTH_FT*(1-t)+KEELSON_TIP_WIDTH_FT*t


def keelson_top(f,rabbet,sole):
    top=rabbet(f)+KEELSON_ABOVE_GARBOARD_FT
    if f<CABIN_FORE_FT:
        # Inaccessible aft continuation is lower under the cabin sole; leave
        # an unbroken land above the sole-bearer notch.
        top=min(top,sole-ACCESS_TIMBER_FT-.10)
    return top


def keelson_positions(aft,fore,rabbet=None):
    positions=sorted(set([aft,fore,*np.linspace(aft,fore,max(3,int((fore-aft)/1.5)+2)),
                       *[f for f in (CABIN_FORE_FT,KEELSON_SCARF_AFT_FT,KEELSON_SCARF_FORE_FT,
                                     KEELSON_TAPER_START_FT) if aft<f<fore]]))
    if rabbet is not None:
        # Refine only where the rising bow needs it, rather than burdening
        # every long timber and every mating Boolean with dense ruled faces.
        for _ in range(10):
            extra=[]
            for a,b in zip(positions[:-1],positions[1:]):
                error=max(abs(rabbet(a+(b-a)*t)-(rabbet(a)*(1-t)+rabbet(b)*t))
                          for t in (.25,.5,.75))
                if error>KEELSON_PROFILE_TOLERANCE_FT:extra.append((a+b)/2)
            if not extra:break
            positions=sorted([*positions,*extra])
    return positions


@lru_cache(maxsize=8)
def keelson_blank(rabbet,sole,aft=KEELSON_AFT_FT,fore=KEELSON_FORE_FT):
    wires=[]
    for f in keelson_positions(aft,fore,rabbet):
        w=keelson_width(f)
        foot=min(KEEL_THICKNESS_FT,w*.75)
        base=rabbet(f)
        top=keelson_top(f,rabbet,sole)
        wire=(cq.Workplane(cq.Plane(origin=boat_point(0,f,0),xDir=(1,0,0),normal=(0,-1,0)))
              .polyline([(-foot/2,base-KEELSON_FOOT_FT),(foot/2,base-KEELSON_FOOT_FT),
                         (w/2,base+.06),(w/2,top),(-w/2,top),(-w/2,base+.06)])
              .close().val())
        wires.append(wire)
    return cq.Solid.makeLoft(wires,ruled=True)


@lru_cache(maxsize=1)
def centreboard_slot():
    return block(0,(CB_SLOT_AFT_FT+CB_SLOT_FORE_FT)/2,-5,
                 TRUNK_GAP_FT,CB_SLOT_FORE_FT-CB_SLOT_AFT_FT,25)


def pivot_bore(radius=CENTREBOARD_PIN_RADIUS_FT+.004):
    return spar_between(boat_point(-1,CENTREBOARD_PIVOT_FT,CENTREBOARD_PIVOT_Z_FT),
                        boat_point(1,CENTREBOARD_PIVOT_FT,CENTREBOARD_PIVOT_Z_FT),radius)


def case_bottom(f,rabbet,sole):
    return keelson_top(f,rabbet,sole)-.015


def case_top(f,rabbet,sole,deck):
    return min(case_bottom(f,rabbet,sole)+TRUNK_COURSES*TRUNK_COURSE_FT,
               deck(f)-DECK_THICKNESS_FT-DECK_BEAM_DEPTH_FT-.04)


@lru_cache(maxsize=2)
def trunk_envelope(rabbet,sole,deck):
    wires=[]
    for f in np.linspace(TRUNK_AFT_FT,TRUNK_FORE_FT,12):
        bottom=case_bottom(f,rabbet,sole)
        top=case_top(f,rabbet,sole,deck)+.10
        wires.append(cq.Workplane(cq.Plane(origin=boat_point(0,f,(top+bottom)/2),
                     xDir=(1,0,0),normal=(0,-1,0))).rect(TRUNK_OUTER_WIDTH_FT+.05,top-bottom).val())
    return cq.Solid.makeLoft(wires,ruled=True)


def mast_forward(z,deck):
    return MAST_DECK_FORWARD_FT-MAST_RAKE_FT*(z-deck(MAST_DECK_FORWARD_FT))/MAST_HEIGHT_FT


def mast_radius(z):
    return MAST_DIAMETER_FT/2+(.16-MAST_DIAMETER_FT/2)*(z-MAST_STEP_HEIGHT_FT)/MAST_HEIGHT_FT


def mast_axis():
    return cq.Vector(0,MAST_RAKE_FT,MAST_HEIGHT_FT).normalized()


def octagon(radius):
    return [(radius*math.cos(math.pi/8+i*math.pi/4),
             radius*math.sin(math.pi/8+i*math.pi/4)) for i in range(8)]


def mast_polygon(z,radius,deck):
    plane=cq.Plane(origin=boat_point(0,mast_forward(z,deck),z),xDir=(1,0,0),normal=mast_axis())
    return cq.Workplane(plane).polyline(octagon(radius)).close().val()


def mast_octagonal_prism(low,high,deck,extra=0):
    return cq.Solid.makeLoft([mast_polygon(z,mast_radius(z)+extra,deck) for z in (low,high)],ruled=True)


def chock_levels(deck):
    level=deck(MAST_DECK_FORWARD_FT)
    return level-DECK_THICKNESS_FT-MAST_PARTNER_DEPTH_FT-.03,level+.10


@lru_cache(maxsize=2)
def mast_chock_envelope(deck,clearance=0):
    low,high=chock_levels(deck)
    extra=.003+MAST_CHOCK_FT/math.cos(math.pi/8)+clearance
    return mast_octagonal_prism(low-.10,high+.10,deck,extra)


def mast_partner_centres(deck):
    centre=mast_forward(deck(MAST_DECK_FORWARD_FT)-.30,deck)
    radius=mast_radius(deck(MAST_DECK_FORWARD_FT)-.3)
    half=(radius*math.cos(math.pi/8)+MAST_CHOCK_FT)*mast_axis().z+.015
    return centre-half-MAST_PARTNER_SIDED_FT/2,centre+half+MAST_PARTNER_SIDED_FT/2


@lru_cache(maxsize=2)
def mast_partner_blanks(deck):
    result=[]
    for f in mast_partner_centres(deck):
        top=deck(f)-DECK_THICKNESS_FT-.01
        result.append(block(0,f,top-MAST_PARTNER_DEPTH_FT,
                            MAST_PARTNER_SPAN_FT,MAST_PARTNER_SIDED_FT,MAST_PARTNER_DEPTH_FT))
    return tuple(result)


def make_board(angle=CENTREBOARD_ANGLE_DEG):
    wire=[(HULL_LENGTH_FT/2-f,z) for f,z in CENTRELINE_SOURCE['board_source_outline_FZ']]
    board=cq.Workplane('YZ').polyline(wire).close().extrude(CENTREBOARD_THICKNESS_FT/2,both=True).val()
    board=board.cut(pivot_bore())
    origin=boat_point(0,CENTREBOARD_PIVOT_FT,CENTREBOARD_PIVOT_Z_FT)
    return board.rotate(origin,(1,origin[1],origin[2]),-angle)
