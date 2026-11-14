"""Painted oak rails and iron stanchions, assembled in the common datum."""
import numpy as np
import cadquery as cq
from scipy.interpolate import PchipInterpolator

from .params import (
    boat_point, RAIL_TOP_FT, RAIL_LOWER_FT, RAIL_WIDTH_FT,
    RAIL_THICKNESS_FT, IVORY, IRON, PORT_SIDE,
    legacy_forward, HULL_AFT_FT, STERN_REMEDY_SOURCE,
)
from .hull import (SECTIONS, section_plane, fair_loft, deck_height,
                   topside_halfwidth, deck_thickness)
from .primitives import spar_between
from . import stern_layout
from .board_tools import segmented_loft


_side=np.array([(p['forward_ft'],p['across_ft']) for p in STERN_REMEDY_SOURCE['side_rail_observations']])
_side_curve=PchipInterpolator(_side[:,0],_side[:,1])
_turn_x=float(_side[2,1])
_turn_f=float(_side[2,0])


def side_across(f):
    if f<=_side[-1,0]:return float(_side_curve(f))
    width=float(np.interp(f,[s[0] for s in SECTIONS],[s[1] for s in SECTIONS]))-.08
    t=min(1,max(0,(f-_side[-1,0])/5))
    blend=t*t*t*(10+t*(-15+6*t))
    return float(_side_curve(min(f,_side[-1,0]+1)))*(1-blend)+width*blend


def rail_section(x,f,above_deck,tangent):
    # S07 section / LOC-P07: broad 3.5-in face horizontal, 1.75-in vertical.
    dx,dy=tangent
    plane=cq.Plane(origin=boat_point(x,f,deck_height(f,x)+stern_layout.rail_height(f,above_deck)),
                   normal=(dx,dy,0),xDir=(-dy,dx,0))
    return cq.Workplane(plane).rect(RAIL_WIDTH_FT,RAIL_THICKNESS_FT).val()


def make_side_rail(side, above_deck):
    wires=[]
    for f in np.linspace(_turn_f,legacy_forward(47.5),120):
        dx=side*(side_across(f+.001)-side_across(f-.001))/.002
        wires.append(rail_section(side*side_across(f),f,above_deck,(dx,-1)))
    return segmented_loft(wires,intervals=12)


def make_transom_rail(height):
    xs=sorted(set([*np.linspace(-_turn_x,_turn_x,65),*_side[:3,1],*-_side[:3,1]]))
    wires=[rail_section(float(x),stern_layout.rail_forward(x),height,
                        (1,-stern_layout.rail_derivative(x))) for x in xs]
    # Bounded cubic patches preserve the measured section sweep without the
    # enormous excursions OCC can introduce in a single many-section loft.
    shape=segmented_loft(wires,intervals=6)
    bounds=shape.BoundingBox()
    assert bounds.xlen<2*_turn_x+1 and bounds.ylen<8,'Rear rail loft escaped source bounds'
    return shape


def make_rubbing_strake(side):
    wires = []
    end=STERN_REMEDY_SOURCE['moulding_handoff']['forward_ft']
    rows=np.array(SECTIONS)
    first=tuple(float(np.interp(end,rows[:,0],rows[:,i])) for i in range(8))
    for forward, width, sheer, _, top_z, *_ in [first,*[s for s in SECTIONS if s[0]>end+1e-6]]:
        # Exact shared handoff, rather than a gap to the next hull station.
        # Do not loft a narrow side strake through the transom plan closure.
        taper = min(1, max(.12, width / .7))
        thickness = RAIL_THICKNESS_FT * taper
        z = min(sheer - .38 * min(1, width / 1.25),
                sheer - deck_thickness(sheer, top_z) - thickness / 2)
        face = topside_halfwidth(forward, z)
        w = RAIL_WIDTH_FT * taper
        x = side * (face + w / 2 - .035 * taper)
        wires.append(section_plane(forward).center(x, z).rect(w, thickness).val())
    # Rubbing stock projects outside the wood surface. Clipping it to the hull
    # plan keep removes its outer half and can sever the shoulder altogether.
    return fair_loft(wires)


def make_rails():
    for side, label in ((PORT_SIDE, "Port"), (-PORT_SIDE, "Starboard")):
        for level, height in (("top rail", RAIL_TOP_FT), ("lower rail", RAIL_LOWER_FT)):
            yield f"{label} {level}", make_side_rail(side, height), IVORY
        yield f"{label} rubbing strake", make_rubbing_strake(side), IVORY
        positions=[(p['forward_ft'],p['across_ft']) for p in STERN_REMEDY_SOURCE['side_rail_observations'][3:]]
        positions.extend((legacy_forward(old),None) for old in np.linspace(.7,46.7,25)
                         if legacy_forward(old)>_side[-1,0]+.5)
        for index,(forward,custom_width) in enumerate(positions,1):
            width = float(np.interp(forward, [s[0] for s in SECTIONS],
                                    [s[1] for s in SECTIONS]))
            across = side * (custom_width if custom_width is not None else side_across(forward))
            floor = deck_height(forward, across)
            yield f"{label} stanchion {index:02d}", spar_between(
                boat_point(across, forward, floor - .06),
                 boat_point(across, forward, floor + stern_layout.rail_height(forward,RAIL_TOP_FT)), .036,
            ), IRON
    # Fair rectangular oak, including the measured quarter turn; no cylinders.
    for level, height in (("top", RAIL_TOP_FT), ("lower", RAIL_LOWER_FT)):
        yield f"Transom {level} rail",make_transom_rail(height),IVORY
    rear_x=[p['across_ft'] for p in STERN_REMEDY_SOURCE['rail_fastener_observations']]
    rear_x.extend(side*p['across_ft'] for p in STERN_REMEDY_SOURCE['side_rail_observations'][:3] for side in (-1,1))
    for i,x in enumerate(rear_x,1):
        f=stern_layout.rail_forward(x)
        z=deck_height(f,x)
        yield f'Transom stanchion {i}',spar_between(boat_point(x,f,z-.04),
              boat_point(x,f,z+stern_layout.rail_height(f,RAIL_TOP_FT)),.036),IRON
