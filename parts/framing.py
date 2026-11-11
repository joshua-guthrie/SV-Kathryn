"""Opening support timberwork, from sheet 5 plan and sheets 6/7 sections."""
import cadquery as cq
import numpy as np

from .params import (
    boat_point, DECK_THICKNESS_FT, DECK_BEAM_SIDED_FT, DECK_BEAM_DEPTH_FT,
    DECK_CLAMP_SIDED_FT, DECK_CLAMP_DEPTH_FT, INTERIOR_SKIN_FT,
    CABIN_FORWARD_FT, CABIN_HEIGHT_FT, CABIN_WIDTH_FT, CABIN_WALL_FT,
    ACCESS_WELL_WIDTH_FT, ACCESS_WELL_AFT_FT, ACCESS_CLEAR_WIDTH_FT,
    COMPANIONWAY_AFT_FT, COMPANIONWAY_LENGTH_FT,
    CABIN_ROOF_CAMBER_FT, ROOF_BEAM_SIDED_FT, ROOF_BEAM_DEPTH_FT,
    PORT_SIDE, WOOD,
    CABIN_ROOF_OVERHANG_FT,
    MAST_FORWARD_SUPPORT_FT,
    FRAME_HEAD_MOLDED_FT,HULL_AFT_FT,KEELSON_FORE_FT,
)
from .openings import framed_openings
from .hull import deck_height, topside_halfwidth
from . import stern_layout


def beam_top(forward, across):
    return deck_height(forward, across) - DECK_THICKNESS_FT + .015


def make_cross_beam(forward, left, right, sided=DECK_BEAM_SIDED_FT,
                    depth=DECK_BEAM_DEPTH_FT, roof=False):
    def top(x):
        if roof:
            level = deck_height(CABIN_FORWARD_FT) - .1 + CABIN_HEIGHT_FT - .04
            return level + CABIN_ROOF_CAMBER_FT * (1 - (2 * x / (CABIN_WIDTH_FT + 2*CABIN_ROOF_OVERHANG_FT)) ** 2) + .015
        return beam_top(forward, x)
    mid = (left + right) / 2
    return (cq.Workplane('XZ', origin=boat_point(0, forward, 0))
            .moveTo(left, top(left)).threePointArc((mid, top(mid)), (right, top(right)))
            .lineTo(right, top(right) - depth)
            .threePointArc((mid, top(mid) - depth), (left, top(left) - depth))
            .close().extrude(sided / 2, both=True).val())


def clamp_outer(forward):
    z = beam_top(forward, 7) - DECK_CLAMP_DEPTH_FT / 2
    return topside_halfwidth(forward, z) - INTERIOR_SKIN_FT - FRAME_HEAD_MOLDED_FT + .025


def make_longitudinal(aft, fore, across, sided=DECK_BEAM_SIDED_FT,
                       depth=DECK_BEAM_DEPTH_FT, roof=False, clamp=False):
    if clamp:aft=max(aft,-.45)
    wires = []
    for f in np.linspace(aft, fore, max(3, int((fore - aft) / (.8 if clamp else .3)) + 1)):
        x = across
        if clamp:
            x = np.sign(across) * (clamp_outer(f) - sided / 2)
        if roof:
            level = deck_height(CABIN_FORWARD_FT) - .1 + CABIN_HEIGHT_FT - .04
            z = level + CABIN_ROOF_CAMBER_FT * (1 - (2 * x / (CABIN_WIDTH_FT + 2*CABIN_ROOF_OVERHANG_FT)) ** 2) + .015
        else:
            z = beam_top(f, x)
        wires.append(cq.Workplane(cq.Plane(origin=boat_point(x, f, z - depth / 2),
                                           xDir=(1, 0, 0), normal=(0, -1, 0)))
                     .rect(sided, depth).val())
    shape=cq.Solid.makeLoft(wires, ruled=not clamp)
    if clamp:shape=shape.intersect(stern_layout.keep(stern_layout.reference_height(deck_height),INTERIOR_SKIN_FT))
    return shape


def make_opening_frames():
    openings = framed_openings()
    forepeak = next(o for o in openings if o.name == 'Forepeak hatch')
    after=next(o for o in openings if o.name=='After deck hatch')
    main=next(o for o in openings if o.name=='Main hold hatch')
    for opening in openings:
        prefix = opening.name
        aft_f = opening.aft - DECK_BEAM_SIDED_FT / 2
        fore_f = opening.fore + DECK_BEAM_SIDED_FT / 2
        for f, label in ((aft_f, 'aft'), (fore_f, 'fore')):
            span = clamp_outer(f) - .015
            # S05-07: stern member d is 6 x 3-in pine, not the general average.
            size=(6/12,3/12) if prefix=='Cabin deck opening' and label=='aft' else (DECK_BEAM_SIDED_FT,DECK_BEAM_DEPTH_FT)
            yield f'{prefix} {label} deck beam', make_cross_beam(f, -span, span,*size), WOOD
        for side, label in ((PORT_SIDE, 'Port'), (-PORT_SIDE, 'Starboard')):
            x = opening.across + side * (opening.clear_width + DECK_BEAM_SIDED_FT) / 2
            yield f'{prefix} {label.lower()} carling', make_longitudinal(
                opening.frame_aft + .015, opening.frame_fore - .015, x), WOOD
            if prefix != 'Forepeak hatch':
                start,end=((main.frame_aft-.04,KEELSON_FORE_FT) if prefix=='Main hold hatch' else
                           (HULL_AFT_FT+.3,after.frame_aft+.025) if prefix=='Cabin deck opening' else
                           (after.frame_aft-.025,main.frame_aft+.025))
                name = 'Forebody' if prefix == 'Main hold hatch' else prefix
                yield f'{name} {label.lower()} clamp', make_longitudinal(
                    start, end, side,
                    DECK_CLAMP_SIDED_FT, DECK_CLAMP_DEPTH_FT, clamp=True), WOOD
            span = clamp_outer(opening.forward) - .015
            if side > 0:
                left, right = x + DECK_BEAM_SIDED_FT / 2 - .025, span
            else:
                left, right = -span, x - DECK_BEAM_SIDED_FT / 2 + .025
            yield f'{prefix} {label.lower()} half beam', make_cross_beam(
                opening.forward, left, right), WOOD

    # The aft header is split around the full-height doorway; a single full
    # beam here would recreate the roof-level obstacle corrected previously.
    roof_aft = COMPANIONWAY_AFT_FT + .07
    roof_fore = COMPANIONWAY_AFT_FT + COMPANIONWAY_LENGTH_FT - .2 + ROOF_BEAM_SIDED_FT / 2
    span = CABIN_WIDTH_FT / 2 - CABIN_WALL_FT / 2
    yield 'Companionway roof fore header', make_cross_beam(
        roof_fore, -span, span, ROOF_BEAM_SIDED_FT, ROOF_BEAM_DEPTH_FT, roof=True), WOOD
    for side, label in ((PORT_SIDE, 'Port'), (-PORT_SIDE, 'Starboard')):
        left, right = ((ACCESS_CLEAR_WIDTH_FT / 2, span) if side > 0 else
                       (-span, -ACCESS_CLEAR_WIDTH_FT / 2))
        yield f'{label} companionway roof aft half header', make_cross_beam(
            roof_aft, left, right, ROOF_BEAM_SIDED_FT, ROOF_BEAM_DEPTH_FT, roof=True), WOOD
        yield f'{label} companionway roof carling', make_longitudinal(
            roof_aft - ROOF_BEAM_SIDED_FT / 2 + .01,
            roof_fore + ROOF_BEAM_SIDED_FT / 2 - .01,
            side * (ACCESS_WELL_WIDTH_FT + ROOF_BEAM_SIDED_FT) / 2,
            ROOF_BEAM_SIDED_FT, ROOF_BEAM_DEPTH_FT, roof=True), WOOD
