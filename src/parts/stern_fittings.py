"""Survey-condition stern fittings, S04 and LOC-P28/P29/P30.

Major outlines/arrangement follow the vessel-specific evidence. Unprinted
sections, hidden mountings and hydraulic internals are visual reconstructions,
not manufacturing data or a claim of a particular replacement date.
"""
import math
import cadquery as cq
import numpy as np
from .params import *
from . import hull,stern_layout
from .primitives import block,spar_between,beam_between

STAINLESS=(.62,.66,.68)
RUBBER=(.075,.080,.075)


def hose(points,radius=.024):
    points=[cq.Vector(*p) for p in points]
    edge=cq.Edge.makeSpline(points)
    tangent=edge.tangentAt(0)
    plane=cq.Plane(origin=points[0],normal=tangent)
    return cq.Workplane(plane).circle(radius).sweep(cq.Wire.assembleEdges([edge]),isFrenet=True).val()


def make_hydraulics():
    """Recognizable open-case ram/guides, stock linkage and helm pump."""
    floor=hull.deck_height(HELM_FORWARD_FT)
    aft=HELM_FORWARD_FT-.48
    # Leave the forward pump/manifold its own space below the removable lid.
    fore=STERN_SOURCE['helm_box_fore_ft']-.70
    z0=hull._head_z+.13
    def p(x,f):return boat_point(x,f,z0+(f-aft)*math.tan(math.radians(RUDDER_RAKE_DEG)))
    shelf=block(0,HELM_BOX_FORWARD_FT,floor+.10,HELM_BOX_WIDTH_FT-.20,
                HELM_BOX_LENGTH_FT-.20,.12).cut(hull.rudder_stock_passage())
    yield 'Helm hydraulic mounting shelf',shelf,WOOD
    for side,label in ((1,'Port'),(-1,'Starboard')):
        for f,end in ((aft,'aft'),(fore,'fore')):
            top=p(side*.62,f)[2]
            yield f'{label} hydraulic {end} mounting bracket',block(side*.62,f,floor+.20,
                       .16,.22,top-floor-.16),IRON
        yield f'{label} hydraulic guide rail',spar_between(p(side*.62,aft-.08),p(side*.62,fore+.06),.045),STAINLESS
    for f,end in ((aft,'aft'),(fore,'fore')):
        yield f'Helm hydraulic {end} crosshead',beam_between(p(-.69,f),p(.69,f),.17,.15),IRON
    yield 'Hynautic replacement ram barrel',spar_between(p(0,aft+.95),p(0,fore),.155),IRON
    yield 'Hydraulic ram polished piston',spar_between(p(0,aft),p(0,aft+1.05),.055),STAINLESS
    # Stock collar and short tiller link meet the aft crosshead. Shaft contact
    # is intentional here, unlike a collision with fixed timber/case material.
    centre=np.array(hull.rudder_axis_point(hull._head_z-.02))
    axis=hull._stock_up
    collar=spar_between(tuple(centre-axis*.13),tuple(centre+axis*.15),.24)
    bore=spar_between(tuple(centre-axis*.2),tuple(centre+axis*.2),RUDDER_POST_RADIUS_FT+.006)
    link=beam_between(tuple(centre),p(0,aft),.23,.16)
    yield 'Rudder stock collar and tiller link',collar.fuse(link).cut(bore),IRON
    pump_f=STERN_SOURCE['helm_box_fore_ft']-.27
    pump_z=floor+HELM_WHEEL_HEIGHT_FT
    pump=spar_between(boat_point(0,pump_f-.20,pump_z),boat_point(0,pump_f+.18,pump_z),.19)
    pump=pump.fuse(block(0,pump_f,floor+1.08,.54,.38,.42))
    pump=pump.cut(spar_between(boat_point(0,pump_f-.3,pump_z),boat_point(0,pump_f+.3,pump_z),.081))
    yield 'Capilano helm pump and manifold',pump,IRON
    yield 'Hydraulic pump case mounting plate',block(0,pump_f+.18,floor+1.02,.75,.09,.60).cut(
        spar_between(boat_point(0,pump_f,pump_z),boat_point(0,pump_f+.4,pump_z),.085)),STAINLESS
    # Visible valve/reservoir volume and its two pressure-return circuits.
    valve_f=HELM_BOX_FORWARD_FT-.12
    yield 'Teleflex uni-flo valve enclosure (visual)',block(.34,valve_f,floor+.55,.48,.55,.38),STAINLESS
    for side,label in ((1,'Port'),(-1,'Starboard')):
        points=[boat_point(side*.20,pump_f-.05,floor+1.17),
                boat_point(side*.46,pump_f-.55,floor+1.36),
                boat_point(side*.60,valve_f+.22,floor+1.08),
                boat_point(.34+side*.20,valve_f,floor+.78)]
        yield f'{label} helm hydraulic pump hose',hose(points),RUBBER
        # Cross the centreline forward of the rudder-stock envelope, then land
        # on the crosshead outboard of it.  The hose routing is a
        # reconstruction and must clear the moving stock.
        points=[boat_point(.34+side*.20,valve_f-.1,floor+.65),
                boat_point(side*.48,aft+.78,floor+.48),
                boat_point(side*.34,aft+.92,floor+.95),p(side*.30,aft+1.03)]
        yield f'{label} hydraulic ram hose',hose(points),RUBBER


def davit_point(side,f):
    # S04 plan: long diagonal iron booms, distinct from curved rail/wood lines.
    aft,fore=-4.4,9.35
    t=(f-aft)/(fore-aft)
    x=side*(4.33+t*(6.79-4.33))
    z=hull.deck_height(0)+4.22+t*(hull.deck_height(fore)+1.22-hull.deck_height(0)-4.22)
    return boat_point(x,f,z)


def make_davits():
    for side,label in ((1,'Port'),(-1,'Starboard')):
        tip=davit_point(side,-4.4)
        root=davit_point(side,9.35)
        # Plate-web iron boom, not a wooden spar or a bent round placeholder.
        web=beam_between(tip,root,.095,.24)
        top=beam_between(tuple(np.array(tip)+(0,0,.13)),tuple(np.array(root)+(0,0,.13)),.25,.055)
        bottom=beam_between(tuple(np.array(tip)-(0,0,.13)),tuple(np.array(root)-(0,0,.13)),.25,.055)
        yield f'{label} iron pushboat davit',web.fuse(top,bottom),IRON
        foot_f=.55
        foot_x=side*4.95
        floor=hull.deck_height(foot_f,foot_x)
        yield f'{label} davit stern bearing foot',block(foot_x,foot_f,floor-.04,.40,.45,.14),IVORY
        for f,end in ((-1.25,'aft'),(2.05,'fore')):
            yield f'{label} davit stainless {end} strut',spar_between(
                boat_point(foot_x,foot_f,floor+.04),davit_point(side,f),.045),STAINLESS
        x,y,z=root
        f=25-y
        base=hull.deck_height(f,x)
        yield f'{label} davit pivot pedestal',block(x,f,base-.04,.36,.38,z-base+.04),IRON
        yield f'{label} davit pivot pin',spar_between((x-.25,y,z),(x+.25,y,z),.065),STAINLESS
        motor=np.array(davit_point(side,3.7))
        # S04 item9 electric davit winch, below the boom and attached by plate.
        housing=spar_between(tuple(motor+(0,0,-.44)),tuple(motor+(0,0,-.02)),.19)
        housing=housing.fuse(block(motor[0],25-motor[1],motor[2]-.08,.50,.40,.12))
        yield f'{label} electric davit winch',housing,IRON
        # Rigid tackle blocks retained; no rope/wire rigging is introduced.
        x,y,z=tip
        axle_z=z-.55
        yield f'{label} davit block hanger',spar_between((x,y,z-.55),(x,y,z+.02),.055),IRON
        yield f'{label} davit tackle pin',spar_between((x-.24,y,axle_z),(x+.24,y,axle_z),.065),STAINLESS
        for i,dx in enumerate((-.21,-.07,.07,.21),1):
            cheek=(cq.Workplane('YZ',origin=(x+dx,y,axle_z)).ellipse(.25,.39)
                   .extrude(.025,both=True).val())
            yield f'{label} davit tackle cheek {i}',cheek,WOOD
        for i,dx in enumerate((-.14,0,.14),1):
            sheave=spar_between((x+dx-.04,y,axle_z),(x+dx+.04,y,axle_z),.23)
            yield f'{label} davit tackle sheave {i}',sheave,IRON


def make_traveller():
    target=STERN_REMEDY_SOURCE['traveller']
    f=target['forward_ft'];half=target['span_ft']/2
    z=hull.deck_height(f)+target['height_above_deck_ft']
    yield 'Main-sheet traveller rod (S04 item18)',spar_between(boat_point(-half,f,z),boat_point(half,f,z),.035),IRON
    for side,label in ((1,'Port'),(-1,'Starboard')):
        floor=hull.deck_height(f,side*half)
        foot=block(side*half,f,floor-.04,.20,.26,.10)
        leg=spar_between(boat_point(side*half,f,floor),boat_point(side*half,f,z+.035),.052)
        yield f'{label} main-sheet traveller foot',foot.fuse(leg),IRON
    ring=cq.Solid.makeTorus(.082,.022,boat_point(0,f,z), (1,0,0))
    yield 'Main-sheet traveller sliding eye',ring,IRON


def make_bumper():
    deck=hull.deck_height(0)
    # S04 profile and LOC-P30. Hidden end joints and rubber section inferred.
    for side,label in ((1,'Port'),(-1,'Starboard')):
        low=boat_point(side*.31,-1.74,deck-1.85)
        high=boat_point(side*.31,-2.10,deck+1.35)
        yield f'{label} external pushboat bumper timber',beam_between(low,high,.27,.25),IVORY
        for z,end in ((deck-.52,'lower'),(deck+.18,'upper')):
            face=stern_layout.face_forward(z,across=side*.31)
            yield f'{label} bumper {end} bracket',beam_between(
                boat_point(side*.31,-1.95,z),boat_point(side*.31,face+.18,z),.16,.12),IRON
    yield 'Pushboat bumper rubber fender (photo)',cq.Solid.makeTorus(.62,.14,
        boat_point(0,-1.94,deck-.10),(0,1,0)),RUBBER


def make_controls():
    for side,label,count in ((1,'Port',1),(-1,'Starboard',3)):
        x=side*2.65;f=CABIN_AFT_FT-.22
        floor=hull.deck_height(f,x)
        # S04 item20/LOC-P28: off-centre controls leave the entry/wheel path.
        yield f'{label} stern control pedestal',block(x,f,floor-.03,.78,.48,1.26),IVORY
        for i in range(count):
            xx=x+(i-(count-1)/2)*.22
            housing=block(xx,f,floor+1.20,.20,.38,.20)
            yield f'{label} stern control housing {i+1}',housing,IRON
            start=boat_point(xx,f,floor+1.35)
            end=boat_point(xx,f-.15,floor+1.98)
            lever=spar_between(start,end,.024).fuse(cq.Solid.makeSphere(.075,end))
            yield f'{label} stern control lever {i+1}',lever,IRON
    z=hull.deck_height(CABIN_AFT_FT)+2.00
    yield 'Aft cabin speaker (S04 item25)',block(2.1,CABIN_AFT_FT-.08,z,.32,.18,.36),IRON


def make_stern_fittings():
    yield from make_traveller()
    yield from make_davits()
    yield from make_bumper()
    yield from make_controls()
