"""Stem, projecting headrails and decorated trailboards from HAER sheets 1/3/4.

Carving proportions are traced visually; fine relief cuts and colours are
approximations at display scale. All positions below are in source feet.
"""
import math
import numpy as np
import cadquery as cq
from scipy.interpolate import PchipInterpolator

from .params import (
    boat_point, HULL_LENGTH_FT, WATERLINE_FT, BOWSPRIT_HEEL_FT,
    BOWSPRIT_END_FT, BOWSPRIT_HEEL_RADIUS_FT, BOWSPRIT_TIP_RADIUS_FT,
    BOWSPRIT_TIP_HEIGHT_FT, HEADRAIL_ROOT_FT, HEADRAIL_TIP_FT,
    TRAILBOARD_ROOT_FT, TRAILBOARD_TIP_FT, TRAILBOARD_THICKNESS_FT,
    IVORY, IRON, WOOD, TRAILBOARD_PAINT,
    CARVED_IVORY, PORT_SIDE,
    legacy_forward, RIG_HEIGHT_RISE_FT,FRAME_SOURCE,BOW_POST_FORWARD_FT,
)
from .hull import SECTIONS, deck_height, section_plane, fair_loft, topside_halfwidth, smooth_blend
from .primitives import block, beam_between, spar_between

_heel_z = deck_height(BOW_POST_FORWARD_FT)+FRAME_SOURCE['bowsprit_heel_above_post_deck_ft']
_headrail_root_x = float(np.interp(HEADRAIL_ROOT_FT,
                                  [s[0] for s in SECTIONS],
                                  [s[1] for s in SECTIONS])) - .08
_headrail_root_z = deck_height(HEADRAIL_ROOT_FT) + .36


def bowsprit_height(forward):
    t = (forward - BOWSPRIT_HEEL_FT) / (BOWSPRIT_END_FT - BOWSPRIT_HEEL_FT)
    return _heel_z + t * (BOWSPRIT_TIP_HEIGHT_FT - _heel_z)


def bowsprit_radius(forward):
    t = (forward - BOWSPRIT_HEEL_FT) / (BOWSPRIT_END_FT - BOWSPRIT_HEEL_FT)
    return BOWSPRIT_HEEL_RADIUS_FT + t * (BOWSPRIT_TIP_RADIUS_FT - BOWSPRIT_HEEL_RADIUS_FT)


def headrail_point(side, forward):
    t = (forward - HEADRAIL_ROOT_FT) / (HEADRAIL_TIP_FT - HEADRAIL_ROOT_FT)
    across = side * (_headrail_root_x + t * (.16 - _headrail_root_x))
    z = _headrail_root_z + t * (bowsprit_height(HEADRAIL_TIP_FT) - .1 - _headrail_root_z)
    return across, z


def make_walking_boards():
    for side, label in ((PORT_SIDE, 'Port'), (-PORT_SIDE, 'Starboard')):
        wires = []
        start = BOWSPRIT_HEEL_FT
        for f in np.linspace(start, BOWSPRIT_END_FT - .3, 12):
            t = (f - start) / (BOWSPRIT_END_FT - .3 - start)
            x = side * (.62 + t * (.23 - .62))
            z = bowsprit_height(f) + bowsprit_radius(f) + .03
            wires.append(section_plane(f).center(x, z)
                         .rect(.45 + t * (.18 - .45), .09).val())
        yield f'{label} bowsprit walking board', fair_loft(wires), IVORY


_stem_sections = [s for s in SECTIONS if s[0] >= legacy_forward(43.125)]
_stem_forward = PchipInterpolator([s[7] for s in _stem_sections],
                                  [s[0] for s in _stem_sections])


def stem_forward_at(z):
    return float(_stem_forward(z))


def make_stem():
    points = [(s[0], s[7]) for s in _stem_sections]
    front = [(HULL_LENGTH_FT / 2 - f - .12, z) for f, z in points]
    back = [(HULL_LENGTH_FT / 2 - f + .12, z) for f, z in reversed(points)]
    return (cq.Workplane('YZ').moveTo(*front[0]).spline(front[1:], includeCurrent=True)
            .lineTo(*back[0]).spline(back[1:], includeCurrent=True).close()
            .extrude(.23, both=True).val())


_lower_edge = PchipInterpolator(
    [legacy_forward(f) for f in (48, 50, 54, 57, 59, 60.2)],
    [z+RIG_HEIGHT_RISE_FT for z in (6.75, 7.05, 7.8, 8.6, 9.15, 9.38)])


def panel_top(f):
    # One board on the centreline, seated directly into the bowsprit's
    # underside. The two decorated faces are not separated headrail panels.
    return bowsprit_height(f) - bowsprit_radius(f) + .025


def panel_bottom(f):
    return float(_lower_edge(f))


_panel_length_factor = 1.0
_relief_offset = -.005


def panel_plane(side, offset=0):
    normal = cq.Vector(side, 0, 0)
    origin = cq.Vector(*boat_point(side * TRAILBOARD_THICKNESS_FT / 2,
                                  TRAILBOARD_ROOT_FT, 0)) + normal * offset
    return cq.Plane(origin=origin, xDir=(0, side, 0), normal=normal)


def panel_u(side, forward):
    return -side * (forward - TRAILBOARD_ROOT_FT) * _panel_length_factor


def panel_outline(side):
    plane = panel_plane(side)
    lower = [(panel_u(side, f), panel_bottom(f))
             for f in np.linspace(TRAILBOARD_TIP_FT, TRAILBOARD_ROOT_FT, 12)]
    return (cq.Workplane(plane)
            .moveTo(panel_u(side, TRAILBOARD_ROOT_FT), panel_top(TRAILBOARD_ROOT_FT))
            .lineTo(panel_u(side, TRAILBOARD_TIP_FT), panel_top(TRAILBOARD_TIP_FT))
            .lineTo(*lower[0]).spline(lower[1:], includeCurrent=True).close().val())


def _extrude_wire(wire, side, height, offset=0):
    return (cq.Workplane(panel_plane(side)).add(wire).toPending().extrude(height)
            .val().translate(panel_plane(side).zDir.multiply(offset)))


def _ribbon(side, points, width=.035):
    points = np.asarray(points)
    tangents = np.gradient(points, axis=0)
    normals = np.column_stack((-tangents[:, 1], tangents[:, 0]))
    normals /= np.linalg.norm(normals, axis=1)[:, None]
    outline = np.vstack((points + width / 2 * normals,
                         (points - width / 2 * normals)[::-1]))
    return (cq.Workplane(panel_plane(side, _relief_offset)).polyline(outline.tolist())
            .close().extrude(.035).val())


def _leaf(side, f, upper):
    u = panel_u(side, f)
    z = panel_top(f) - .025 if upper else panel_bottom(f) + .025
    length = min(.34, (panel_top(f) - panel_bottom(f)) * .6)
    du, dz = -side * length * .75, (-1 if upper else 1) * length * .65
    return _leaf_at(side, u, z, du, dz, length * .22)


def _leaf_at(side, u, z, du, dz, w):
    length = math.hypot(du, dz)
    return (cq.Workplane(panel_plane(side, _relief_offset)).moveTo(u, z)
            .threePointArc((u + du * .45 - dz * w / length,
                            z + dz * .45 + du * w / length), (u + du, z + dz))
            .threePointArc((u + du * .55 + dz * w / length,
                            z + dz * .55 - du * w / length), (u, z))
            .close().extrude(.035).val())


def _vine(side, start, end):
    fs = np.linspace(start, end, 100)
    def centre(f):
        h = panel_top(f) - panel_bottom(f)
        wave = ((panel_top(f) + panel_bottom(f)) / 2
                + h * .22 * math.sin(2 * math.pi * (f - start) / 1.6))
        border = panel_bottom(f) + .02
        blend = smooth_blend((f-start)/.30)*smooth_blend((end-f)/.30)
        return border + blend*(wave-border)
    # Blend continuously into the border; vertical endpoint jumps could make
    # the thin ribbon self-intersect after the source-coordinate migration.
    path = [(panel_u(side, f), centre(f)) for f in fs]
    stem = _ribbon(side, path, .04)
    leaves = []
    for i, f in enumerate(np.linspace(start + .25, end - .2, max(3, int((end - start) / .5)))):
        h = panel_top(f) - panel_bottom(f)
        length = min(.30, h * .45)
        leaves.append(_leaf_at(side, panel_u(side, f), centre(f),
                               -side * length * .8, (-1 if i % 2 else 1) * length * .6,
                               length * .22))
    return stem.fuse(*leaves)


def make_trailboard_relief(side, outline):
    border = _extrude_wire(outline, side, .035, _relief_offset)
    inner_wires = outline.offset2D(-.065)
    assert inner_wires, 'Trailboard border needs an inset'
    for inner in inner_wires:
        border = border.cut(_extrude_wire(inner, side, .08, _relief_offset - .02))
    leaves = [_leaf(side, legacy_forward(f), upper) for f in (49.8, 50.2, 54.8, 55.8, 56.8, 57.8, 58.8)
              for upper in (False, True)]
    # Volutes at the broad aft end and the carved forward head. Their stems
    # meet the continuous border, keeping the relief a single carved part.
    scrolls = []
    for f, r in ((50.3, .22), (59.1, .12)):
        f = legacy_forward(f)
        centre = np.array((panel_u(side, f),
                           (panel_top(f) + panel_bottom(f)) / 2))
        theta = np.linspace(-math.pi / 2, 2.5 * math.pi, 40)
        radius = np.linspace(r, .025, len(theta))
        spiral = centre + np.column_stack((radius * np.cos(theta), radius * np.sin(theta)))
        start = (panel_u(side, f), panel_bottom(f) + .015)
        scrolls.append(_ribbon(side, [start, *spiral.tolist()]))
    vines = [_vine(side, legacy_forward(48.35), legacy_forward(50.6)),
             _vine(side, legacy_forward(54.4), legacy_forward(59.4))]
    relief = border.fuse(*leaves, *scrolls, *vines).clean()
    assert relief.isValid() and len(relief.Solids()) == 1, 'Carving must join its border'
    return relief


def make_name_letters(side, label):
    # Begin the name forward of the cutwater so its first letter is not
    # hidden where the centreline board passes into the stem structure.
    forward_positions = np.linspace(legacy_forward(51.1), legacy_forward(53.8), 7)
    if side > 0:
        forward_positions = forward_positions[::-1]
    plane = panel_plane(side, _relief_offset)
    for char, f in zip('KATHRYN', forward_positions):
        centre = plane.toWorldCoords((panel_u(side, f), (panel_top(f) + panel_bottom(f)) / 2))
        letter_plane = cq.Plane(origin=centre, xDir=plane.xDir, normal=plane.zDir)
        letter = cq.Workplane(letter_plane).text(
            char, .48, .035, font='DejaVu Serif', kind='bold',
            halign='center', valign='center', combine=False).solids().val()
        angle = -side * math.degrees(math.atan(.15 / _panel_length_factor))
        letter = letter.rotate(centre.toTuple(), (centre + plane.zDir).toTuple(), angle)
        yield f'{label} trailboard letter {char}', letter, CARVED_IVORY


_chain_link = (cq.Workplane('XY').ellipse(.17, .078).ellipse(.136, .044)
               .extrude(.018, both=True).val())


def linked_chain(start, end):
    """Alternating oval links, fused at small contact patches for this static
    exterior model. Each complete chain remains one valid registered solid.
    """
    start, end = np.asarray(start), np.asarray(end)
    direction = end - start
    length = float(np.linalg.norm(direction))
    tangent = direction / length
    normal = np.array((1., 0., 0.))
    normal -= tangent * np.dot(normal, tangent)
    normal /= np.linalg.norm(normal)
    other_normal = np.cross(tangent, normal)
    count = max(3, round(length / .27) + 1)
    links = []
    for i, t in enumerate(np.linspace(0, 1, count)):
        plane = cq.Plane(origin=tuple(start + t * direction), xDir=tuple(tangent),
                         normal=tuple(normal if i % 2 == 0 else other_normal))
        links.append(_chain_link.moved(plane.location))
    chain = links[0].fuse(*links[1:]).clean()
    assert chain.isValid() and len(chain.Solids()) == 1, 'Chain link contacts must join'
    return chain


def _bowsprit_band(f):
    p = np.array(boat_point(0, f, bowsprit_height(f)))
    tangent = np.array((0., -1., (BOWSPRIT_TIP_HEIGHT_FT - _heel_z)
                        / (BOWSPRIT_END_FT - BOWSPRIT_HEEL_FT)))
    tangent /= np.linalg.norm(tangent)
    outer = spar_between(tuple(p - tangent * .09), tuple(p + tangent * .09),
                         bowsprit_radius(f) + .045)
    inner = spar_between(tuple(p - tangent * .14), tuple(p + tangent * .14),
                         bowsprit_radius(f) + .004)
    return outer.cut(inner)


def _bobstay_anchors(stem_z, tip_f):
    return (boat_point(0, stem_forward_at(stem_z) + .20, stem_z),
            boat_point(0, tip_f, bowsprit_height(tip_f) - bowsprit_radius(tip_f) - .10))


def _stem_eye(stem_z, point):
    f = stem_forward_at(stem_z)
    strap = block(0, f, stem_z - .075, .75, .24, .15)
    eye = cq.Solid.makeTorus(.10, .025, point, (1, 0, 0))
    return strap.fuse(eye)


def _side_anchor(side):
    f = legacy_forward(45.5)
    z = deck_height(f) - .45
    x = side * (topside_halfwidth(f, z) + .15)
    return boat_point(x, f, z)


def _side_tip(side):
    f = legacy_forward(62.0)
    return boat_point(side * (bowsprit_radius(f) + .10), f, bowsprit_height(f))


def make_bow_chains():
    for name, z, f in (('Bowsprit bobstay', 4.7, 62.3),
                       ('Bowsprit inner bobstay', 5.25, 60.4)):
        f = legacy_forward(f)
        root, tip = _bobstay_anchors(z, f)
        yield f'{name} stem strap and eye', _stem_eye(z, root), IRON
        band = _bowsprit_band(f).fuse(cq.Solid.makeTorus(.10, .025, tip, (1, 0, 0)))
        yield f'{name} collar and eye', band, IRON
        yield name, linked_chain(root, tip), IRON
    tip_band = _bowsprit_band(legacy_forward(62.0))
    for side in (-1, 1):
        tip_band = tip_band.fuse(cq.Solid.makeTorus(.10, .025, _side_tip(side), (0, 1, 0)))
    yield 'Bowsprit side-stay collar', tip_band, IRON
    for side, label in ((PORT_SIDE, 'Port'), (-PORT_SIDE, 'Starboard')):
        root = _side_anchor(side)
        x, _, z = root
        plate = block(x - side * .12, legacy_forward(45.5), z - .17, .12, .32, .34)
        eye = cq.Solid.makeTorus(.10, .025, root, (0, 1, 0))
        yield f'{label} bowsprit chainplate and eye', plate.fuse(eye), IRON
        yield f'{label} bowsprit shroud', linked_chain(root, _side_tip(side)), IRON


def make_bow_details():
    stem = make_stem()
    water = (cq.Workplane('XY').box(40, 100, 40, centered=(True, True, False))
             .translate((0, 0, WATERLINE_FT - 40)).val())
    yield 'Painted stem and cutwater', stem.cut(water), IVORY
    yield 'Underwater stem shoe', stem.intersect(water), (.13, .18, .18)
    outline = panel_outline(-1)
    yield 'Centreline carved trailboard', _extrude_wire(
        outline, -1, TRAILBOARD_THICKNESS_FT, -TRAILBOARD_THICKNESS_FT), TRAILBOARD_PAINT
    for side, label in ((PORT_SIDE, 'Port'), (-PORT_SIDE, 'Starboard')):
        start_x, start_z = headrail_point(side, HEADRAIL_ROOT_FT)
        end_x, end_z = headrail_point(side, HEADRAIL_TIP_FT)
        yield f'{label} projecting headrail', beam_between(
            boat_point(start_x, HEADRAIL_ROOT_FT, start_z),
            boat_point(end_x, HEADRAIL_TIP_FT, end_z), .17, .16), IVORY
        knee_x, knee_z = headrail_point(side, legacy_forward(48.0))
        yield f'{label} headrail knee', beam_between(
            boat_point(side * .4, legacy_forward(48.6), 7.0+RIG_HEIGHT_RISE_FT),
            boat_point(knee_x, legacy_forward(48.0), knee_z), .16, .15), IVORY
        outline = panel_outline(side)
        yield f'{label} carved border and scrollwork', make_trailboard_relief(side, outline), CARVED_IVORY
        yield from make_name_letters(side, label)
    for i,f in enumerate((BOWSPRIT_HEEL_FT,legacy_forward(54.8),legacy_forward(60.0)),1):
        x, rail_z = headrail_point(1, f)
        top = bowsprit_height(f) + bowsprit_radius(f) + .01
        bearer = block(0, f, top - .12, 2 * abs(x) + .2, .18, .12)
        feet = [block(side * abs(x), f, rail_z - .05, .16, .18,
                      top - .12 - rail_z + .08) for side in (-1, 1)]
        yield f'Bowsprit cross-bearer {i}', bearer.fuse(*feet), IVORY
    floor=bowsprit_height(BOWSPRIT_HEEL_FT)-BOWSPRIT_HEEL_RADIUS_FT
    saddle=block(0,BOWSPRIT_HEEL_FT,floor-.18,1.0,.7,.24)
    sprit=spar_between(boat_point(0,BOWSPRIT_HEEL_FT,bowsprit_height(BOWSPRIT_HEEL_FT)),
                       boat_point(0,BOWSPRIT_END_FT,bowsprit_height(BOWSPRIT_END_FT)),
                       BOWSPRIT_HEEL_RADIUS_FT,BOWSPRIT_TIP_RADIUS_FT)
    yield 'Bowsprit heel saddle',saddle.cut(sprit),IVORY
    x,z=headrail_point(1,BOWSPRIT_HEEL_FT)
    top=floor-.18+.012
    yield 'Bowsprit heel bearing cross-timber',block(0,BOWSPRIT_HEEL_FT,top-.22,
                                                   2*abs(x)+.20,.32,.22),IVORY
    yield 'Bowsprit heel band', _bowsprit_band(BOWSPRIT_HEEL_FT + .5), IRON
    yield 'Bowsprit stem-head band', _bowsprit_band(BOWSPRIT_HEEL_FT+.08), IRON
    yield from make_bow_chains()
