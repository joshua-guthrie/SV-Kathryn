"""M2 separately inspectable centreline oak, pine trunk and mast foundations.

Printed stock sizes and older-member evidence: S05-12, S06-08/12–14,
S07-03/12. Located arrangement/inferred joints: m2_centreline_measurements.json.
"""
from functools import lru_cache
import math
import numpy as np
import cadquery as cq
from .params import *
from . import hull,spars,framing
from . import centreline_layout as layout
from . import frame_layout
from .primitives import block,spar_between


def sole():
    return hull.centreline_sole_height()


@lru_cache(maxsize=1)
def keelson_material():
    allowed=hull.solid_envelope().fuse(hull.keel_material_envelope(),hull.skeg_material_envelope())
    return hull.keelson_seating_tool().intersect(allowed)


def scarf_half(upper):
    aft,fore=KEELSON_SCARF_AFT_FT,KEELSON_SCARF_FORE_FT
    fs=np.linspace(aft,fore,24)
    seam=[]
    for f in fs:
        t=(f-aft)/(fore-aft)
        bottom=hull.rabbet_height(f)-KEELSON_FOOT_FT
        top=layout.keelson_top(f,hull.rabbet_height,sole())
        seam.append((25-f,bottom+(top-bottom)*t))
    edge=20 if upper else -10
    polygon=[(25-aft,edge),*seam,(25-fore,edge)]
    return cq.Workplane('YZ').polyline(polygon).close().extrude(2,both=True).val()


def mast_mortise():
    heel=spars.mast_heel_height()
    high=layout.keelson_top(spars.mast_forward_at(heel),hull.rabbet_height,sole())+.5
    bore=layout.mast_octagonal_prism(heel-.2,high,hull.deck_height,.035)
    # Small seating allowance at the bottom is an intentional timber bearing,
    # not a filler block. Hoop and heel fit into the reconstructed mortise.
    keep=block(0,spars.mast_forward_at(heel),heel+.015,4,4,10)
    return bore.intersect(keep)


@lru_cache(maxsize=1)
def make_keelsons():
    stock=keelson_material()
    aft_keep=block(0,(KEELSON_AFT_FT+KEELSON_SCARF_AFT_FT)/2,-5,4,
                   KEELSON_SCARF_AFT_FT-KEELSON_AFT_FT,25)
    fore_keep=block(0,(KEELSON_SCARF_FORE_FT+KEELSON_FORE_FT)/2,-5,4,
                    KEELSON_FORE_FT-KEELSON_SCARF_FORE_FT,25)
    aft=stock.intersect(aft_keep.fuse(scarf_half(True)))
    fore=stock.intersect(fore_keep.fuse(scarf_half(False)))
    tools=[layout.centreboard_slot(),mast_mortise(),*frame_layout.mortise_tools(hull.inner_bottom_height)]
    return aft.cut(*tools),fore.cut(*tools)


def trunk_course(side,index):
    wires=[]
    for f in np.linspace(TRUNK_AFT_FT,TRUNK_FORE_FT,12):
        bottom=layout.case_bottom(f,hull.rabbet_height,sole())
        top=layout.case_top(f,hull.rabbet_height,sole(),hull.deck_height)
        low=bottom+index*TRUNK_COURSE_FT
        high=min(bottom+(index+1)*TRUNK_COURSE_FT,top)
        assert high>low+.02,('Trunk course too shallow',index,f)
        wires.append(cq.Workplane(cq.Plane(
            origin=boat_point(side*(TRUNK_GAP_FT+TRUNK_WALL_FT)/2,f,(low+high)/2),
            xDir=(1,0,0),normal=(0,-1,0))).rect(TRUNK_WALL_FT,high-low).val())
    return cq.Solid.makeLoft(wires,ruled=False).cut(layout.pivot_bore())


def trunk_end(forward):
    # End timbers occupy the gap; side planks butt against their sides.
    wires=[]
    for f in (forward-TRUNK_END_FT/2,forward+TRUNK_END_FT/2):
        low=layout.case_bottom(f,hull.rabbet_height,sole())
        high=layout.case_top(f,hull.rabbet_height,sole(),hull.deck_height)
        wires.append(cq.Workplane(cq.Plane(origin=boat_point(0,f,(low+high)/2),
                    xDir=(1,0,0),normal=(0,-1,0))).rect(TRUNK_GAP_FT,high-low).val())
    return cq.Solid.makeLoft(wires,ruled=True)


def trunk_cap(side):
    wires=[]
    for f in np.linspace(TRUNK_AFT_FT,TRUNK_FORE_FT,12):
        z=layout.case_top(f,hull.rabbet_height,sole(),hull.deck_height)
        wires.append(cq.Workplane(cq.Plane(
            origin=boat_point(side*(TRUNK_GAP_FT+TRUNK_WALL_FT)/2,f,z+.035),
            xDir=(1,0,0),normal=(0,-1,0))).rect(TRUNK_WALL_FT+.04,.08).val())
    return cq.Solid.makeLoft(wires,ruled=False)


def make_chocks():
    low,high=layout.chock_levels(hull.deck_height)
    for i in range(8):
        wires=[]
        for z in (low,high):
            inner=layout.octagon(layout.mast_radius(z)+.003)
            outer=layout.octagon(layout.mast_radius(z)+.003+MAST_CHOCK_FT/math.cos(math.pi/8))
            plane=cq.Plane(origin=boat_point(0,layout.mast_forward(z,hull.deck_height),z),
                           xDir=(1,0,0),normal=layout.mast_axis())
            j=(i+1)%8
            wires.append(cq.Workplane(plane).polyline([inner[i],outer[i],outer[j],inner[j]]).close().val())
        yield f'Mast pine chock {i+1}',cq.Solid.makeLoft(wires,ruled=True),WOOD


def make_mast_hoop():
    # Keep the whole raked hoop above the horizontally trimmed heel/mortise
    # seat; the inclined end plane otherwise dips through the bearing land.
    low=spars.mast_heel_height()+.22
    return layout.mast_octagonal_prism(low,low+.17,hull.deck_height,.023).cut(
        layout.mast_octagonal_prism(low-.1,low+.27,hull.deck_height,.004))


def make_mast_supports():
    partners=layout.mast_partner_blanks(hull.deck_height)
    for label,blank in zip(('aft','fore'),partners):
        yield f'Mast {label} oak partner',blank.cut(layout.mast_chock_envelope(hull.deck_height,.006)),WOOD
    yield from make_chocks()
    yield 'Mast heel iron hoop',make_mast_hoop(),IRON
    # The source plan shows the partner/carlings frame. Fine laps and exact
    # association with hull-frame numbers remain explicitly reconstructed.
    forepeak=next(o for o in framing.framed_openings() if o.name=='Forepeak hatch')
    aft=forepeak.frame_fore-.025
    fore=MAST_FORWARD_SUPPORT_FT+.025
    for side,label in ((1,'Port'),(-1,'Starboard')):
        wires=[]
        x=side*(MAST_PARTNER_SPAN_FT/2-.125)
        for f in np.linspace(aft,fore,16):
            top=hull.deck_height(f,x)-DECK_THICKNESS_FT-.01-MAST_PARTNER_DEPTH_FT/2
            wires.append(cq.Workplane(cq.Plane(origin=boat_point(x,f,top-MAST_PARTNER_DEPTH_FT/2),
                         xDir=(1,0,0),normal=(0,-1,0))).rect(.25,MAST_PARTNER_DEPTH_FT).val())
        carling=cq.Solid.makeLoft(wires,ruled=True).cut(*partners)
        yield f'{label} mast-partner carling',carling,WOOD
    span=framing.clamp_outer(MAST_FORWARD_SUPPORT_FT)-.015
    yield 'Mast forward support beam',framing.make_cross_beam(MAST_FORWARD_SUPPORT_FT,-span,span),WOOD


def make_centreline_parts():
    aft,fore=make_keelsons()
    yield 'Aft oak keelson section',aft,WOOD
    yield 'Forward oak keelson section (possibly original)',fore,(.48,.32,.19)
    for side,label in ((1,'Port'),(-1,'Starboard')):
        for index in range(TRUNK_COURSES):
            yield f'{label} trunk pine course {index+1}',trunk_course(side,index),(.68,.54,.34)
        yield f'{label} trunk top rail',trunk_cap(side),WOOD
    for label,f in (('aft',TRUNK_AFT_FT+TRUNK_END_FT/2),('fore',TRUNK_FORE_FT-TRUNK_END_FT/2)):
        yield f'Centreboard trunk {label} end timber',trunk_end(f),WOOD
    yield 'Centreboard pivot pin',spar_between(
        boat_point(-TRUNK_OUTER_WIDTH_FT/2-.03,CENTREBOARD_PIVOT_FT,CENTREBOARD_PIVOT_Z_FT),
        boat_point(TRUNK_OUTER_WIDTH_FT/2+.03,CENTREBOARD_PIVOT_FT,CENTREBOARD_PIVOT_Z_FT),
        CENTREBOARD_PIN_RADIUS_FT),IRON
    yield from make_mast_supports()
