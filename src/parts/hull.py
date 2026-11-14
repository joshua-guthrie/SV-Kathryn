"""Loft the measured hull sections and the cambered deck."""
import math
from functools import lru_cache
import cadquery as cq
import numpy as np
from scipy.interpolate import PchipInterpolator, CubicHermiteSpline
from scipy.optimize import brentq, minimize
from scipy.special import comb

from .params import (
    HULL_LENGTH_FT, DECK_CAMBER_FT, DECK_THICKNESS_FT, WATERLINE_FT,
    STATIONS, SHEER_HEIGHTS, CHINE_TOP_HEIGHTS, CHINE_BOTTOM_HEIGHTS,
    RABBET_HEIGHTS, SHEER_WIDTHS, CHINE_TOP_WIDTHS, CHINE_BOTTOM_WIDTHS,
    offset, boat_point,
    HELM_FORWARD_FT, HELM_STOCK_HEAD_ABOVE_DECK_FT, RUDDER_RAKE_DEG,
    RUDDER_THICKNESS_FT, RUDDER_POST_RADIUS_FT, RUDDER_BLADE_TOP_DROP_FT,
    RUDDER_BLADE_HEIGHT_FT, RUDDER_AFT_EDGE_FROM_HELM_FT, RUDDER_AFT_BULGE_FT,
    RUDDER_BLADE_CORNER_RADIUS, RUDDER_GUDGEON_FRACTIONS,
    RUDDER_RUNNING_CLEARANCE_FT, STERNPOST_DEPTH_FT,
    KEEL_THICKNESS_FT, KEEL_EXPOSED_DEPTH_FT, WORM_SHOE_DEPTH_FT,
    WORM_SHOE_MAX_WIDTH_FT, STERN_DEADWOOD_END_FT, INTERIOR_SKIN_FT,
    HULL_AFT_FT, HULL_FORE_FT, LINE_STATIONS_FT, legacy_forward,
    CABIN_FORWARD_FT, CABIN_WIDTH_FT, CABIN_LENGTH_FT, CABIN_WALL_FT,
    sheer_band_height, sheer_band_flare,
    CB_SLOT_AFT_FT,CB_SLOT_FORE_FT,
    BOW_POST_FORWARD_FT,
    STERN_RAKE_FT_PER_FT,
    STERN_BLEND_END_FT,STERN_MOULDING_DEPTH_FT,STERN_MOULDING_NORMAL_FT,STERN_REMEDY_SOURCE,
    RAIL_THICKNESS_FT,RAIL_WIDTH_FT,
)
from .primitives import spar_between, beam_between
from .access import companionway_access
from .openings import hatch_openings, framed_openings
from .primitives import block
from . import centreline_layout as centreline
from . import frame_layout
from . import stern_layout
from .board_tools import segmented_loft


def measured_sections():
    """Return forward position, sheer, chine top/bottom, and rabbet heights.

    Longitudinal positions follow M0's checked source-coordinate ledger.
    """
    # Sheet 2 body-plan trace: approximately 11.4 ft broad, with about 1.8 ft
    # centre depth below the sheer (railwork excluded). Width was already
    # close; the previous 5.25-ft bottom made the transom face too shallow.
    sections = [(HULL_AFT_FT, 5.65, 6.6, 5.35, 6.05, 4.9, 5.7, 4.8)]
    for index, station in enumerate(STATIONS):
        position = LINE_STATIONS_FT[station]
        width, height = offset(SHEER_WIDTHS[index]), offset(SHEER_HEIGHTS[index])
        if index < len(CHINE_TOP_WIDTHS):
            top_width = offset(CHINE_TOP_WIDTHS[index])
            top_height = offset(CHINE_TOP_HEIGHTS[index])
            bottom_width = offset(CHINE_BOTTOM_WIDTHS[index])
            bottom_height = offset(CHINE_BOTTOM_HEIGHTS[index])
        else:
            # The offset table omits the chine as it merges into the stem.
            top_width, bottom_width = width * .77, width * .52
            keel_height = offset(RABBET_HEIGHTS[index])
            top_height = keel_height + .55 * (height - keel_height)
            bottom_height = keel_height + .25 * (height - keel_height)
        sections.append((position, width, height, top_width, top_height,
                         bottom_width, bottom_height, offset(RABBET_HEIGHTS[index])))
    # The lower lines rise into the raked stem head; a deep final section
    # here would produce a blunt vertical stump below the bowsprit.
    sections.append((HULL_FORE_FT, .04, 8.3, .034, 8.23, .028, 8.19, 8.15))
    return sections


SOURCE_SECTIONS = measured_sections()
# Local bounded section lofting avoids the lobes of a global CAD spline loft.
# The longitudinal chine runs are faired independently, not pulled inward by
# a transverse "flat entry" blend. That old blend made unplankable shoulders.
_source = np.array(SOURCE_SECTIONS)
_fair_source = _source.copy()


def smooth_blend(t):
    """Quintic easing: zero first/second derivatives at the blend ends."""
    t = min(1, max(0, t))
    return t * t * t * (10 + t * (-15 + 6 * t))


# Sheet 2's station 8.5 lower half-breadth is retained as a measurement but
# given low weight when fairing the plank run: it is an isolated hollow.
_entry_mid = int(np.argmin(abs(_source[:, 0] - LINE_STATIONS_FT[8.5])))
_base_sections = PchipInterpolator(_source[:, 0], _source[:, 1:], axis=0)
_rabbet_curve = PchipInterpolator(_source[:, 0], _source[:, 7])
_fair_start = float(_source[np.argmax(_source[:, 3]), 0])
_chine_table_end = LINE_STATIONS_FT[9]
_chine_top_end = brentq(lambda f: float(_rabbet_curve(f)) - 5.0, LINE_STATIONS_FT[9.5], LINE_STATIONS_FT[10])
_chine_bottom_end = brentq(lambda f: float(_rabbet_curve(f)) - 4.4, LINE_STATIONS_FT[9.5], LINE_STATIONS_FT[10])
# Compatibility names for the geometric review helpers: the final flat entry
# now starts at the actual chine/stem intersection, not at station 9.
_entry_begin, _entry_flat = _fair_start, _chine_top_end


def _bernstein_basis(t):
    t = np.asarray(t)
    return np.column_stack([comb(5, i) * t ** i * (1 - t) ** (5 - i) for i in range(6)])


def _fit_chine_run(column, end_f, end_value):
    samples = _source[(_source[:, 0] >= _fair_start) & (_source[:, 0] <= _chine_table_end)]
    first = float(samples[0, column])
    a = _bernstein_basis((samples[:, 0] - _fair_start) / (end_f - _fair_start))
    target = (samples[:, column] - first) / (end_value - first)
    weights = np.ones(len(samples))
    if column == 5:
        weights[np.argmin(abs(samples[:, 0] - _source[_entry_mid, 0]))] = .03

    def objective(q):
        controls = np.array((0., 0., *q, 1.))
        return float(np.dot(weights, (a @ controls - target) ** 2)
                     + .002 * np.sum(np.diff(controls, 2) ** 2))

    fit = minimize(objective, (.25, .6, .9), method='SLSQP', bounds=((0, 1),) * 3,
                   constraints=({'type': 'ineq', 'fun': lambda q: np.diff(q)},),
                   options={'ftol': 1e-12, 'maxiter': 100})
    assert fit.success, f'Chine fairing failed: {fit.message}'
    return first + (end_value - first) * np.array((0., 0., *fit.x, 1.))


_chine_controls = {
    'top_width': _fit_chine_run(3, _chine_top_end, 3.5 / 12),
    'top_height': _fit_chine_run(4, _chine_top_end, 5.0),
    'bottom_width': _fit_chine_run(5, _chine_bottom_end, 3.5 / 12),
    'bottom_height': _fit_chine_run(6, _chine_bottom_end, 4.4),
}


def chine_run(forward, level='top'):
    """Fair longitudinal chine centreline, ending at the lower stem."""
    end = _chine_top_end if level == 'top' else _chine_bottom_end
    t = min(1, max(0, (forward - _fair_start) / (end - _fair_start)))
    basis = _bernstein_basis([t])[0]
    return (float(basis @ _chine_controls[f'{level}_width']),
            float(basis @ _chine_controls[f'{level}_height']))


_sample_positions = np.unique(np.concatenate([
    np.linspace(a, b, 9 if b >= _fair_start else 5)
    for a, b in zip(_source[:-1, 0], _source[1:, 0])
    ] + [np.linspace(_fair_start, HULL_FORE_FT, 100),
         np.array((_chine_bottom_end, _chine_top_end))]))
_sampled = np.column_stack((
    _sample_positions,
    _base_sections(_sample_positions),
))
for row in _sampled:
    f, width, sheer = row[:3]
    if f < _fair_start:
        continue
    kw, rz = min(3.5 / 12, width * .25), row[7]
    if f < _chine_top_end:
        tw, tz = chine_run(f, 'top')
        tw, tz = max(tw, kw + .003), max(tz, rz + .003)
        if f < _chine_bottom_end:
            bw, bz = chine_run(f, 'bottom')
            bw, bz = max(bw, kw + .001), max(bz, rz + .001)
        else:
            # The bottom run has met the stem. A tiny collinear edge retains
            # loft topology without turning the chine up the topside.
            bw, bz = kw + .01 * (tw - kw), rz + .01 * (tz - rz)
    else:
        # Both chine runs have terminated: this is the natural final V entry.
        # Small collinear subdivisions are CAD topology only, not real chines.
        a, b = .02, .01
        db = max(sheer,
                 (.4 * sheer + .6 * (1 - a) * rz) / (1 - .6 * a))
        tw, tz = kw + a * (width - kw), rz + a * (db - rz)
        bw, bz = kw + b * (width - kw), rz + b * (db - rz)
    row[3:7] = (tw, tz, bw, bz)
for row in _sampled:
    # Offset-table "Sheer" is the underside of the sheer strake. M1's native
    # curve picks supply the missing upper band to the actual deck edge.
    row[1] += sheer_band_flare(row[0])
    row[2] += sheer_band_height(row[0])
SECTIONS = [tuple(row) for row in _sampled]


def fair_loft(wires):
    return cq.Solid.makeLoft(wires, ruled=True)


def camber(width):
    return DECK_CAMBER_FT * width / max(s[1] for s in SECTIONS)


def deck_thickness(sheer_height, chine_top_height):
    # Taper the deck at the fine stem so its underside stays above the chine.
    return min(DECK_THICKNESS_FT, .6 * (sheer_height - chine_top_height))


def deck_height(forward, across=0.0):
    width = np.interp(forward, [s[0] for s in SECTIONS], [s[1] for s in SECTIONS])
    sheer = np.interp(forward, [s[0] for s in SECTIONS], [s[2] for s in SECTIONS])
    return float(sheer + camber(width) * max(0, 1 - (across / width) ** 2))


def topside_halfwidth(forward, height):
    """Half-width on the straight topside segment, below the sheer/deck edge."""
    section = [float(np.interp(forward, [s[0] for s in SECTIONS],
                              [s[i] for s in SECTIONS])) for i in range(8)]
    _, width, sheer, top_w, top_z, *_ = section
    under_w = width - sheer_band_flare(forward)
    under_z = sheer - sheer_band_height(forward)
    if height <= under_z:
        t = min(1,max(0,(height-top_z)/(under_z-top_z)))
        value=top_w+t*(under_w-top_w)
    else:
        bottom = sheer - deck_thickness(sheer, top_z)
        t = min(1,max(0,(height-under_z)/(bottom-under_z)))
        value=under_w+t*(width-under_w)
    return min(value,stern_layout.wood_halfwidth(forward)) if forward<STERN_BLEND_END_FT else value


def rabbet_height(forward):
    return float(np.interp(forward, [s[0] for s in SECTIONS], [s[7] for s in SECTIONS]))


def inner_bottom_height(forward, across=0):
    """Bottom-panel inner surface near the centreline, before floor/framing."""
    row = [float(np.interp(forward, [s[0] for s in SECTIONS], [s[i] for s in SECTIONS]))
           for i in range(8)]
    kw = min(3.5 / 12, (row[1]-sheer_band_flare(forward)) * .25)
    slope = (row[6]-row[7])/(row[5]-kw)
    return (row[7] + max(0., abs(across)-kw)*slope
            + INTERIOR_SKIN_FT*(math.sqrt(1+slope*slope) if abs(across)>kw else 1))


def section_plane(forward):
    return cq.Workplane(cq.Plane(
        origin=boat_point(0, forward, 0), xDir=(1, 0, 0), normal=(0, -1, 0),
    ))


def hull_wire(section, include_deck=False):
    forward, width, height, top_w, top_z, bottom_w, bottom_z, rabbet_z = section
    under_width = width - sheer_band_flare(forward)
    under_height = height - sheer_band_height(forward)
    keel_w = min(3.5 / 12, under_width * .25)
    deck_bottom = height - deck_thickness(height, top_z)
    rounding = smooth_blend((_chine_top_end - forward) / .8)
    round_mid = (bottom_w + (.5 + .2 * rounding) * (top_w - bottom_w),
                 bottom_z + (.5 - .2 * rounding) * (top_z - bottom_z))
    wire = (
        section_plane(forward).moveTo(-keel_w, rabbet_z)
        .lineTo(keel_w, rabbet_z).lineTo(bottom_w, bottom_z)
    )
    wire = (wire.lineTo(top_w, top_z) if rounding < 1e-6 else
            wire.threePointArc(round_mid, (top_w, top_z)))
    wire = wire.lineTo(under_width, under_height).lineTo(width, deck_bottom)
    roof = height + .015 if include_deck else deck_bottom
    if include_deck:
        wire = wire.lineTo(width, roof)
    wire = wire.threePointArc((0, roof + camber(width)), (-width, roof))
    if include_deck:
        wire = wire.lineTo(-width, deck_bottom)
    wire = wire.lineTo(-under_width, under_height).lineTo(-top_w, top_z)
    wire = (wire.lineTo(-bottom_w, bottom_z) if rounding < 1e-6 else
            wire.threePointArc((-round_mid[0], round_mid[1]), (-bottom_w, bottom_z)))
    return wire.close().val()


def interior_wire(forward):
    """True inward offset of the outer section, opened above its deck edge."""
    rows = np.array(SECTIONS)
    section = tuple(float(np.interp(forward, rows[:, 0], rows[:, i])) for i in range(8))
    offset_wires = hull_wire(section).offset2D(-INTERIOR_SKIN_FT)
    assert len(offset_wires) == 1, 'Interior offset must not split'
    inside = offset_wires[0]
    edges = inside.Edges()
    roof = max(edges, key=lambda edge: edge.Center().z)
    start, end = roof.startPoint(), roof.endPoint()
    top_z = deck_height(forward) + 1
    high_start = cq.Vector(start.x, start.y, top_z)
    high_end = cq.Vector(end.x, end.y, top_z)
    return cq.Wire.assembleEdges(
        [edge for edge in edges if not edge.isSame(roof)] + [
            cq.Edge.makeLine(start, high_start), cq.Edge.makeLine(high_start, high_end),
             cq.Edge.makeLine(high_end, end)])


def shell_inner_profile(forward):
    """Fixed-topology inner polygon sampled from a true section offset.

    Chords lie inside the offset cavity and retain material at the chine. Fixed
    topology avoids OCC's slow, unstable edge rematching when tiny offset joins
    appear/disappear along the rounded-to-flat entry.
    """
    rows = np.array(SECTIONS)
    section = tuple(float(np.interp(forward, rows[:, 0], rows[:, i])) for i in range(8))
    wires = hull_wire(section).offset2D(-INTERIOR_SKIN_FT)
    if len(wires) != 1:
        raise ValueError('Section is too fine for an open interior')
    offset = wires[0]
    edges = offset.Edges()
    roof = max(edges, key=lambda edge: edge.Center().z)
    target = max((roof.startPoint(), roof.endPoint()), key=lambda point: point.x)
    right = [edge for edge in edges if not edge.isSame(roof) and edge.Center().x > 1e-7]
    crossing = [edge for edge in edges if not edge.isSame(roof)
                and min(edge.startPoint().x, edge.endPoint().x) < -1e-7
                and max(edge.startPoint().x, edge.endPoint().x) > 1e-7]
    if crossing:
        flat = min(crossing, key=lambda edge: edge.Center().z)
        end = max((flat.startPoint(), flat.endPoint()), key=lambda point: point.x)
        current = cq.Vector(0, end.y, end.z)
        right.insert(0, cq.Edge.makeLine(current, end))
    else:
        current = min((vertex.Center() for vertex in offset.Vertices()), key=lambda point: point.z)
    chain = []
    while (current - target).Length > 1e-5:
        matches = [(edge, (edge.startPoint()-current).Length < 1e-5)
                   for edge in right if min((edge.startPoint()-current).Length,
                                             (edge.endPoint()-current).Length) < 1e-5]
        if not matches:
            raise ValueError('Could not follow offset section boundary')
        edge, ahead = matches[0]
        chain.append((edge, ahead, edge.Length()))
        right.remove(edge)
        current = edge.endPoint() if ahead else edge.startPoint()
    lengths = np.cumsum([0., *[record[2] for record in chain]])
    fractions = (0, .04, .20, .40, .60, .75, .82, .86, .90, .94, .97, 1)
    points = []
    for fraction in fractions:
        distance = fraction * lengths[-1]
        index = min(len(chain)-1, int(np.searchsorted(lengths, distance, side='right')-1))
        edge, ahead, length = chain[index]
        t = min(1., max(0., (distance-lengths[index])/length))
        p = edge.positionAt(t if ahead else 1-t)
        points.append((p.x, p.z))
    top = deck_height(forward) + 1
    profile = [*points, (points[-1][0], top), (-points[-1][0], top),
               *[(-x,z) for x,z in points[:0:-1]]]
    wire = section_plane(forward).polyline(profile).close().val()
    if not wire.isValid() or cq.Face.makeFromWires(wire).Area() < .025:
        raise ValueError('Interior at this station has collapsed')
    return wire


@lru_cache(maxsize=1)
def continuous_interior():
    aft = SECTIONS[0][0] + INTERIOR_SKIN_FT
    fore = SECTIONS[-1][0] - .05
    while fore > SECTIONS[-1][0]-2:
        try:
            shell_inner_profile(fore)
            break
        except Exception:
            fore -= .025
    else:
        raise ValueError('Cannot close interior against the stem')
    positions = np.unique(np.concatenate((
        np.linspace(aft, fore, int((fore-aft)/.5)+2),
        [row[0] for row in SOURCE_SECTIONS if aft < row[0] < fore],
        np.linspace(max(aft, fore-2), fore, 20),
        [f for f in (_chine_bottom_end, _chine_top_end) if aft < f < fore],
    )))
    cavity = segmented_loft([shell_inner_profile(float(f)) for f in positions])
    assert cavity.isValid() and len(cavity.Solids()) == 1, 'Invalid continuous interior'
    return cavity.intersect(stern_layout.keep(stern_layout.reference_height(deck_height),INTERIOR_SKIN_FT))


@lru_cache(maxsize=8)
def local_interior(aft, fore):
    stations = [aft, *[s[0] for s in SECTIONS if aft + 1e-6 < s[0] < fore - 1e-6], fore]
    inside = fair_loft([interior_wire(f) for f in stations])
    assert inside.isValid() and len(inside.Solids()) == 1, 'Invalid local inner envelope'
    return inside


@lru_cache(maxsize=1)
def opening_interior_tools():
    tools = []
    hatches = {opening.name for opening in hatch_openings()}
    for opening in framed_openings():
        aft, fore = opening.frame_aft - .08, opening.frame_fore + .08
        inside = local_interior(aft, fore)
        # Shallow relief exposes the new under-deck members. The rest of the
        # interior will be reconstructed in later board-level stages.
        bottom = min(deck_height(f, 7) for f in (aft, opening.forward, fore)) - .9
        relief = block(0, (aft + fore) / 2, bottom, 30, fore - aft, 15)
        tools.append(inside.intersect(relief))
        if opening.name in hatches:
            # The shaft reaches the offset bottom planking, not an invented
            # horizontal floor; intersecting the offset preserves the exterior.
            tools.append(inside.intersect(opening.passage_tool()))
    return tuple(tools)


@lru_cache(maxsize=1)
def solid_envelope():
    """Reference exterior for material checks, partitions and inspection tests."""
    hull = segmented_loft([hull_wire(section) for section in SECTIONS]).intersect(
        stern_layout.keep(stern_layout.reference_height(deck_height)))
    assert hull.isValid() and len(hull.Solids()) == 1, "Hull loft must be one valid solid"
    bounds = hull.BoundingBox()
    actual_aft=25-bounds.ymax
    assert stern_layout.wood_forward(0)-.25<actual_aft<stern_layout.wood_forward(0)+.5,'Hull aft extent misses classified source controls'
    assert abs(25-bounds.ymin-HULL_FORE_FT)<1e-4,'Forebody reference unexpectedly changed'
    assert bounds.xlen <= 2 * max(s[1] for s in SECTIONS) + .05, "Hull has an unwanted side bulge"
    return hull


@lru_cache(maxsize=1)
def planking_envelope():
    hull = solid_envelope().cut(continuous_interior(), rudder_stock_passage(),
                                keelson_seating_tool(),centreline.centreboard_slot(),stern_moulding())
    assert hull.isValid() and len(hull.Solids()) == 1, 'Planking envelope must be one hollow solid'
    return hull


@lru_cache(maxsize=1)
def make_hull():
    hull=planking_envelope()
    water = (cq.Workplane("XY").box(40, 80, 30, centered=(True, True, False))
             .translate((0, 0, WATERLINE_FT - 30)).val())
    return hull.cut(water), hull.intersect(water)


@lru_cache(maxsize=1)
def deck_material_reference():
    wires = []
    aft=list(SECTIONS[0]);aft[0]-=STERN_RAKE_FT_PER_FT*DECK_THICKNESS_FT+.04
    for forward, width, height, _, top_z, *_ in [tuple(aft),*SECTIONS]:
        bottom = height - deck_thickness(height, top_z)
        wires.append(
            section_plane(forward).moveTo(-width, height + .015)
            .threePointArc((0, height + camber(width) + .015), (width, height + .015))
            .lineTo(width, bottom)
            .threePointArc((0, bottom + camber(width)), (-width, bottom)).close().val()
        )
    deck = segmented_loft(wires)
    deck=deck.intersect(stern_layout.keep(stern_layout.reference_height(deck_height)))
    assert deck.isValid() and len(deck.Solids()) == 1, "Deck loft must be one valid solid"
    cabin_opening = block(0, CABIN_FORWARD_FT, -5,
                          CABIN_WIDTH_FT-2*CABIN_WALL_FT,
                          CABIN_LENGTH_FT-2*CABIN_WALL_FT, 25)
    return deck.cut(rudder_stock_passage(), cabin_opening,
                     block(0,BOW_POST_FORWARD_FT,-5,5/12+.012,5/12+.012,25),
                     centreline.mast_chock_envelope(deck_height,.006),
                      *[opening.passage_tool() for opening in hatch_openings()])


@lru_cache(maxsize=1)
def stern_moulding():
    # One continuous outer blank, including the deck thickness. Fusing the two
    # independently lofted, tangent hull/deck roofs can produce an empty OCC
    # result. This section-built blank has no coincident internal interface.
    wires=[]
    shoulder=STERN_REMEDY_SOURCE['side_wood_observations'][-1]
    handoff=STERN_REMEDY_SOURCE['moulding_handoff']
    positions=np.array(SECTIONS)
    end=handoff['forward_ft']
    samples=sorted(set([r[0] for r in SECTIONS if r[0]<end]+[shoulder['forward_ft'],14,15,16,17,end]))
    runout=[]
    for f in samples:
        _,width,height,*_=tuple(float(np.interp(f,positions[:,0],positions[:,i])) for i in range(8))
        # The classified outside wood line is the outside of the substantial
        # moulding, not an instruction to widen all the thin hull planking.
        outside=min(stern_layout.wood_halfwidth(f),handoff['outer_halfwidth_ft'])
        span=max(width,outside+.03)
        t=smooth_blend((f-shoulder['forward_ft'])/(end-shoulder['forward_ft']))
        top=height+.015*(1-t)+(-.38+RAIL_THICKNESS_FT/2)*t
        bottom=top-(STERN_MOULDING_DEPTH_FT*(1-t)+RAIL_THICKNESS_FT*t)
        rise=camber(width)*(1-t)
        wire=section_plane(f).moveTo(-span,top)
        wire=(wire.threePointArc((0,top+rise),(span,top)) if rise>1e-8 else wire.lineTo(span,top))
        wire=wire.lineTo(span,bottom)
        wire=(wire.threePointArc((0,bottom+rise),(-span,bottom)) if rise>1e-8 else wire.lineTo(-span,bottom))
        wires.append(wire.close().val())
        if f>=shoulder['forward_ft']:
            inner=outside-(STERN_MOULDING_NORMAL_FT*(1-t)+RAIL_WIDTH_FT*t)
            runout.append(section_plane(f).rect(2*inner,40).val())
    reference=segmented_loft(wires)
    near_face=reference.intersect(stern_layout.keep()).cut(
        stern_layout.keep(inset=STERN_MOULDING_NORMAL_FT))
    timber=near_face.cut(rudder_stock_passage(),segmented_loft(runout))
    assert timber.isValid() and len(timber.Solids())==1,'Invalid fitted oak stern moulding'
    return timber


def make_stern_moulding_parts():
    """S05 8 x 6-in oak; hidden three-piece joint arrangement is inferred."""
    joint=3.677
    regions=(('Transom',0,2*joint),('Port quarter',(joint+15)/2,15-joint),
             ('Starboard quarter',-(joint+15)/2,15-joint))
    for name,x,width in regions:
        shape=stern_moulding().intersect(block(x,6,-5,width,25,25))
        assert shape.isValid() and len(shape.Solids())==1,f'Invalid {name} moulding'
        yield f'{name} oak stern moulding',shape,(.88,.88,.83)


@lru_cache(maxsize=1)
def make_deck():
    return deck_material_reference().cut(stern_moulding())


def centreline_sole_height():
    return companionway_access(deck_height,inner_bottom_height).sole


@lru_cache(maxsize=1)
def keelson_seating_tool():
    return centreline.keelson_blank(rabbet_height,centreline_sole_height()).cut(
        *frame_layout.underpass_tools(inner_bottom_height))


# All rudder-related parts use one straight, inclined axis. A vertical stock
# plus a diagonal connecting rod would introduce a non-rotating elbow.
_rake = math.radians(RUDDER_RAKE_DEG)
_stock_up = np.array((0.0, math.sin(_rake), math.cos(_rake)))
_stock_forward = np.array((0.0, -math.cos(_rake), math.sin(_rake)))
_head_z = deck_height(HELM_FORWARD_FT) + HELM_STOCK_HEAD_ABOVE_DECK_FT
_blade_top_z = _head_z - RUDDER_BLADE_TOP_DROP_FT
_blade_bottom_z = _blade_top_z - RUDDER_BLADE_HEIGHT_FT
_shaft_joint_z = _blade_top_z + .15


def _post_forward_at(z):
    """Stock heel lies forward of its head, directly below the wheel box."""
    return HELM_FORWARD_FT + (_head_z - z) * math.tan(_rake)


def rudder_axis_point(z):
    return boat_point(0, _post_forward_at(z), z)


def rudder_stock_passage():
    """Clear passage through the counter and deck, coaxial with the stock."""
    return spar_between(rudder_axis_point(_blade_bottom_z - .5),
                        rudder_axis_point(_head_z + .5),
                        RUDDER_POST_RADIUS_FT + RUDDER_RUNNING_CLEARANCE_FT)


# The sternpost is forward of the rotating stock. The keel overlaps the
# forward edge of that timber, rather than filling the rudder's swept space.
_sternpost_offset = (RUDDER_POST_RADIUS_FT + RUDDER_RUNNING_CLEARANCE_FT
                    + STERNPOST_DEPTH_FT / 2)
_keel_offset = _sternpost_offset + STERNPOST_DEPTH_FT / 2 - .02
_heel_z = _blade_bottom_z - .1
_heel_forward = _post_forward_at(_heel_z) + _keel_offset / math.cos(_rake)


def _keel_tip_taper(forward):
    return .08 + .92 * smooth_blend((HULL_FORE_FT - forward) / 2.5)


def _main_shoe_bottom(forward):
    return rabbet_height(forward) - (KEEL_EXPOSED_DEPTH_FT + WORM_SHOE_DEPTH_FT) * _keel_tip_taper(forward)


_aft_keel_join_z = _main_shoe_bottom(STERN_DEADWOOD_END_FT)
_aft_keel_heel_slope = ((_aft_keel_join_z - _heel_z)
                        / (STERN_DEADWOOD_END_FT - _heel_forward))
_aft_keel_join_slope = float(_rabbet_curve.derivative()(STERN_DEADWOOD_END_FT))
# Define the keel run directly, rather than subtracting an eased depth from
# the falling hull rabbet. The latter produced a dip followed by a hump.
_aft_keel_profile = CubicHermiteSpline(
    [_heel_forward, STERN_DEADWOOD_END_FT], [_heel_z, _aft_keel_join_z],
    [_aft_keel_heel_slope, _aft_keel_join_slope], extrapolate=False)
assert np.min(_aft_keel_profile.derivative()(
    np.linspace(_heel_forward, STERN_DEADWOOD_END_FT, 129))) >= -1e-9, \
    'Aft keel must run forward without a dip or hump'


def keel_bottom(forward):
    """Continuous heel-to-body shoe run with no reverse hollow."""
    if forward < _heel_forward:
        return _heel_z + _aft_keel_heel_slope * (forward - _heel_forward)
    if forward < STERN_DEADWOOD_END_FT:
        return float(_aft_keel_profile(forward))
    return _main_shoe_bottom(forward)


def _keel_keep():
    low, high = _blade_bottom_z - 2, _head_z + 2
    return (cq.Workplane("YZ").polyline([
        _rudder_pt(_post_forward_at(low) + _keel_offset / math.cos(_rake), low),
        _rudder_pt(HULL_FORE_FT + 2, low),
        _rudder_pt(HULL_FORE_FT + 2, high),
        _rudder_pt(_post_forward_at(high) + _keel_offset / math.cos(_rake), high),
    ]).close().extrude(2, both=True).val())


def _keel_strip(shoe=False):
    wires = []
    for forward, _, _, _, _, bottom_w, _, rabbet_z in SECTIONS:
        taper = _keel_tip_taper(forward)
        base = keel_bottom(forward)
        bottom = base if shoe else base + WORM_SHOE_DEPTH_FT * taper
        top = (base + WORM_SHOE_DEPTH_FT * taper + .012 if shoe else
               bottom + KEEL_EXPOSED_DEPTH_FT * taper + .04)
        centreboard_flare = (smooth_blend((forward-(CB_SLOT_AFT_FT-.75))/.75)
                             * smooth_blend(((CB_SLOT_FORE_FT+.75)-forward)/.75))
        nominal_width = KEEL_THICKNESS_FT
        if shoe:
            nominal_width += (WORM_SHOE_MAX_WIDTH_FT - KEEL_THICKNESS_FT) * centreboard_flare
        width = min(nominal_width, max(.035, bottom_w * 1.4))
        wires.append(section_plane(forward)
                      .center(0, (top + bottom) / 2)
                      .rect(width, top - bottom).val())
    return fair_loft(wires).intersect(_keel_keep())


@lru_cache(maxsize=1)
def keel_material_envelope():
    return _keel_strip()


def make_keel():
    """Oak keel timber, not a deep external fin or the internal keelson."""
    return keel_material_envelope().cut(centreline.centreboard_slot(),keelson_seating_tool())


def make_worm_shoe():
    return _keel_strip(shoe=True).cut(centreline.centreboard_slot())


def _rudder_pt(forward, height):
    """A point on the centreline, given feet forward of the transom and height."""
    return (HULL_LENGTH_FT / 2 - forward, height)


@lru_cache(maxsize=1)
def skeg_material_envelope():
    """Localized aft deadwood and its inclined sternpost, ahead of the stock."""
    rabbet = PchipInterpolator(_source[:, 0], _source[:, 7])
    exit_z = brentq(lambda z: z - float(rabbet(_post_forward_at(z))),
                    _blade_top_z, deck_height(HELM_FORWARD_FT))
    shift = _stock_forward * _sternpost_offset
    post = beam_between(tuple(np.array(rudder_axis_point(_heel_z)) + shift),
                        tuple(np.array(rudder_axis_point(exit_z + .15)) + shift),
                        KEEL_THICKNESS_FT, STERNPOST_DEPTH_FT)
    wires = []
    for f, _, _, _, _, _, _, rabbet_z in SECTIONS:
        if f > STERN_DEADWOOD_END_FT:
            break
        bottom = (keel_bottom(f) + WORM_SHOE_DEPTH_FT + KEEL_EXPOSED_DEPTH_FT + .025)
        top = rabbet_z + .06
        wires.append(section_plane(f).center(0, (top + bottom) / 2)
                     .rect(KEEL_THICKNESS_FT, top - bottom).val())
    deadwood = fair_loft(wires).intersect(_keel_keep())
    return deadwood.fuse(post).clean()


def make_skeg():
    return skeg_material_envelope().cut(centreline.centreboard_slot(),keelson_seating_tool())


def make_rudder():
    """Rounded blade below the counter, keyed to the inclined stock."""
    post = spar_between(
        rudder_axis_point(_blade_bottom_z - .05),
        rudder_axis_point(_shaft_joint_z),
        RUDDER_POST_RADIUS_FT,
    )
    top = _blade_top_z
    bottom = _blade_bottom_z
    mid = (top + bottom) / 2
    fwd_top = _post_forward_at(top)
    fwd_bot = _post_forward_at(bottom)
    aft = HELM_FORWARD_FT + RUDDER_AFT_EDGE_FROM_HELM_FT
    # Spade outline: flat top, a big rounded aft edge bulging through mid-height,
    # then a rounded heel; the forward edge follows the raked stock.
    blade = (cq.Workplane("YZ")
             .moveTo(*_rudder_pt(fwd_top, top))
             .lineTo(*_rudder_pt(aft, top))
             .threePointArc(_rudder_pt(aft - RUDDER_AFT_BULGE_FT, mid),
                             _rudder_pt(aft, bottom))
             .lineTo(*_rudder_pt(fwd_bot, bottom))
             .close()
             .extrude(RUDDER_THICKNESS_FT / 2, both=True))
    blade = blade.edges("|X").fillet(RUDDER_BLADE_CORNER_RADIUS).val()
    # Leave room for the fixed gudgeon rings around the rotating stock. The
    # shaft itself is added afterwards, so these small reliefs do not cut it.
    for fraction in RUDDER_GUDGEON_FRACTIONS:
        z = bottom + fraction * RUDDER_BLADE_HEIGHT_FT
        centre = np.array(rudder_axis_point(z))
        relief = spar_between(tuple(centre - _stock_up * .12),
                              tuple(centre + _stock_up * .12),
                              RUDDER_POST_RADIUS_FT + .11)
        blade = blade.cut(relief)
    return post.fuse(blade)


def make_steering_shaft():
    """Continuation of the blade stock straight into the wheel-box underside."""
    assert abs(_post_forward_at(_head_z) - HELM_FORWARD_FT) < 1e-9
    return spar_between(rudder_axis_point(_shaft_joint_z - .08),
                        rudder_axis_point(_head_z), RUDDER_POST_RADIUS_FT)


def make_rudder_upper_bearing():
    z = deck_height(HELM_FORWARD_FT) + .05
    centre = np.array(rudder_axis_point(z))
    outer = spar_between(tuple(centre - _stock_up * .12),
                         tuple(centre + _stock_up * .12), .28)
    bore = spar_between(tuple(centre - _stock_up * .2),
                        tuple(centre + _stock_up * .2),
                        RUDDER_POST_RADIUS_FT + .025)
    return outer.cut(bore)


def make_rudder_fittings():
    """Bored gudgeons share the stock axis and strap onto the sternpost."""
    for label, fraction in zip(("lower", "upper"), RUDDER_GUDGEON_FRACTIONS):
        z = _blade_bottom_z + fraction * RUDDER_BLADE_HEIGHT_FT
        centre = np.array(rudder_axis_point(z))
        outer = spar_between(tuple(centre - _stock_up * .1),
                             tuple(centre + _stock_up * .1),
                             RUDDER_POST_RADIUS_FT + .09)
        strap = beam_between(tuple(centre),
                             tuple(centre + _stock_forward * (_keel_offset + .1)),
                             KEEL_THICKNESS_FT + .1, .14)
        bore = spar_between(tuple(centre - _stock_up * .2),
                            tuple(centre + _stock_up * .2),
                            RUDDER_POST_RADIUS_FT + .025)
        yield f"Rudder {label} gudgeon", outer.fuse(strap).cut(bore)


def make_centreboard():
    return centreline.make_board()
