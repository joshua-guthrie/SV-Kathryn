"""Cabin, hatches and helm from the general arrangement, sheet 4."""
import math
import cadquery as cq

from .params import (
    boat_point, CABIN_FORWARD_FT, CABIN_WIDTH_FT, CABIN_LENGTH_FT,
    CABIN_HEIGHT_FT, COMPANIONWAY_FORWARD_FT, HATCHES_FT,
    HELM_FORWARD_FT, HELM_BOX_HEIGHT_FT, IVORY, WOOD, IRON, GLASS,
    HATCH_ACROSS_FT, JIB_TRAVELLER_FORWARD_FT,
    PORT_SIDE, COMPANIONWAY_WIDTH_FT, COMPANIONWAY_LENGTH_FT,
    COMPANIONWAY_HEIGHT_FT, COMPANIONWAY_FRONT_SETBACK_FT,
    CABIN_ROOF_CAMBER_FT, COMPANIONWAY_ROOF_CAMBER_FT, CABIN_ROOF_THICKNESS_FT,
    CABIN_WALL_FT, COMPANIONWAY_AFT_FT, ACCESS_CLEAR_WIDTH_FT,
    ACCESS_WELL_WIDTH_FT, ACCESS_WELL_AFT_FT, ACCESS_WELL_FORE_FT,
    ACCESS_TIMBER_FT, ACCESS_TREAD_COUNT, ACCESS_TREAD_GOING_FT,
    ACCESS_TREAD_DEPTH_FT, ACCESS_DOOR_THICKNESS_FT, ACCESS_DOOR_GAP_FT,
    ACCESS_DOOR_OPEN_DEG,
    HATCH_COVER_COUNTS, HATCH_COVER_THICKNESS_FT, HATCH_COVER_GAP_FT,
    HATCH_COVER_OVERHANG_FT, HATCH_COVER_LIFT_FT,
    CABIN_ROOF_OVERHANG_FT, BOW_POST_FORWARD_FT,
    HELM_BOX_FORWARD_FT,HELM_BOX_LENGTH_FT,HELM_BOX_WIDTH_FT,HELM_WHEEL_FORWARD_FT,
    HELM_WHEEL_RADIUS_FT,HELM_HANDLE_RADIUS_FT,HELM_WHEEL_HEIGHT_FT,
    STERN_SOURCE,
)
from .access import companionway_access
from .openings import DeckOpening, hatch_openings
from .hull import deck_height, inner_bottom_height, make_steering_shaft, make_rudder_upper_bearing, SECTIONS
from .primitives import block, spar_between


def access_geometry():
    return companionway_access(deck_height, inner_bottom_height)


def make_cabin(floor):
    cabin = block(0, CABIN_FORWARD_FT, floor, CABIN_WIDTH_FT,
                  CABIN_LENGTH_FT, CABIN_HEIGHT_FT)
    window_tools = [block(0, forward, floor + 1.1, CABIN_WIDTH_FT + 1, 1.15, .65)
                    for forward in (11.2, 12.8)]
    inside = block(0, CABIN_FORWARD_FT, floor - .1,
                   CABIN_WIDTH_FT - 2 * CABIN_WALL_FT,
                   CABIN_LENGTH_FT - 2 * CABIN_WALL_FT, CABIN_HEIGHT_FT + .2)
    return cabin.cut(inside, access_geometry().door_tool(), *window_tools)


def make_hatch(forward, width, length, across=0):
    opening = next(o for o in hatch_openings()
                   if abs(o.forward - forward) < 1e-6 and abs(o.across - across) < 1e-6)
    assert abs(width - opening.width) < 1e-6 and abs(length - opening.length) < 1e-6
    bottom, top = opening.coaming_levels(deck_height)
    return block(across, forward, bottom, width, length, top - bottom).cut(
        opening.passage_tool())


def make_hatch_covers(lift=HATCH_COVER_LIFT_FT):
    """Individual removable boards and two underside retaining cleats per hatch."""
    for opening in hatch_openings():
        _, top = opening.coaming_levels(deck_height)
        count = HATCH_COVER_COUNTS[opening.name]
        width = opening.width + 2 * HATCH_COVER_OVERHANG_FT
        length = opening.length + 2 * HATCH_COVER_OVERHANG_FT
        pitch = width / count
        for index in range(count):
            x = opening.across - width / 2 + (index + .5) * pitch
            yield f'{opening.name} cover board {index + 1}', block(
                x, opening.forward, top - .015 + lift,
                pitch - HATCH_COVER_GAP_FT, length, HATCH_COVER_THICKNESS_FT), IVORY
        for index, offset in enumerate((-.28, .28), 1):
            yield f'{opening.name} cover cleat {index}', block(
                opening.across, opening.forward + offset * opening.clear_length,
                top - .095 + lift, opening.clear_width - .08, .12, .10), WOOD


def make_wheel(forward, height):
    centre = boat_point(0, forward, height)
    wheel = cq.Solid.makeTorus(HELM_WHEEL_RADIUS_FT, .055, centre, (0, -1, 0))
    spokes = []
    for index in range(8):
        angle = index * math.tau / 8
        end = boat_point(HELM_HANDLE_RADIUS_FT * math.cos(angle), forward, height + HELM_HANDLE_RADIUS_FT * math.sin(angle))
        spokes.append(spar_between(centre, end, .035))
    hub = spar_between(boat_point(0, forward - .14, height),
                       boat_point(0, forward + .14, height), .14)
    return wheel.fuse(hub, *spokes)


def make_cambered_roof(forward, level, width, length, camber):
    """Shallow transverse roof camber, with its edges seated in the walls."""
    bottom = level - .04
    top = bottom + CABIN_ROOF_THICKNESS_FT
    return (cq.Workplane('XZ', origin=boat_point(0, forward, 0))
            .moveTo(-width / 2, bottom)
            .threePointArc((0, bottom + camber), (width / 2, bottom))
            .lineTo(width / 2, top)
            .threePointArc((0, top + camber), (-width / 2, top))
            .close().extrude(length / 2, both=True).val())


def companionway_base():
    return access_geometry().upper_base


def companionway_window_wire(base):
    # The forward glazing edge follows the raked wall in the side elevation.
    aft = COMPANIONWAY_AFT_FT
    fore = aft + COMPANIONWAY_LENGTH_FT
    return (cq.Workplane('YZ').polyline([
        (25 - aft - .4, base + .70), (25 - fore + .6, base + .70),
        (25 - fore + .9, base + 1.60), (25 - aft - .4, base + 1.60),
    ]).close().val())


def make_companionway(base):
    aft = COMPANIONWAY_FORWARD_FT - COMPANIONWAY_LENGTH_FT / 2
    fore = COMPANIONWAY_FORWARD_FT + COMPANIONWAY_LENGTH_FT / 2
    body = (cq.Workplane('YZ').polyline([
        (25 - aft, base), (25 - fore, base),
        (25 - fore + COMPANIONWAY_FRONT_SETBACK_FT, base + COMPANIONWAY_HEIGHT_FT),
        (25 - aft, base + COMPANIONWAY_HEIGHT_FT),
    ]).close().extrude(COMPANIONWAY_WIDTH_FT / 2, both=True).val())
    aperture = (cq.Workplane('YZ').add(companionway_window_wire(base)).toPending()
                .extrude(COMPANIONWAY_WIDTH_FT / 2 + .3, both=True).val())
    # Offset the raked front, not just the footprint, to retain a timber wall.
    low, high = base - .1, base + COMPANIONWAY_HEIGHT_FT + .1
    front_at = lambda z: fore - CABIN_WALL_FT - (
        COMPANIONWAY_FRONT_SETBACK_FT * (z - base) / COMPANIONWAY_HEIGHT_FT)
    inside = (cq.Workplane('YZ').polyline([
        (25 - aft - CABIN_WALL_FT, low), (25 - front_at(low), low),
        (25 - front_at(high), high), (25 - aft - CABIN_WALL_FT, high),
    ]).close().extrude(COMPANIONWAY_WIDTH_FT / 2 - CABIN_WALL_FT, both=True).val())
    return body.cut(inside, aperture, access_geometry().door_tool())


def make_companionway_doors(angle=ACCESS_DOOR_OPEN_DEG):
    """Paired full-height leaves; sheet 4 plan shows their outward swing."""
    access = access_geometry()
    outer = ACCESS_CLEAR_WIDTH_FT / 2 - ACCESS_DOOR_GAP_FT
    inner = ACCESS_DOOR_GAP_FT / 2
    width = outer - inner
    forward = COMPANIONWAY_AFT_FT - .1
    bottom = access.sill + ACCESS_DOOR_GAP_FT
    height = access.head - ACCESS_DOOR_GAP_FT - bottom
    window_bottom, window_height = access.upper_base + 1.0, .52
    for side, label in ((PORT_SIDE, "Port"), (-PORT_SIDE, "Starboard")):
        x = side * (outer + inner) / 2
        leaf = block(x, forward, bottom, width, ACCESS_DOOR_THICKNESS_FT, height)
        window = block(x, forward, window_bottom, width - .2, .3, window_height)
        leaf = leaf.cut(window)
        pane = block(x, forward, window_bottom - .008,
                     width - .184, .025, window_height + .016)
        hinge = boat_point(side * outer, forward - ACCESS_DOOR_THICKNESS_FT / 2, bottom)
        axis = (hinge[0], hinge[1], hinge[2] + 1)
        yield f"{label} companionway door", leaf.rotate(hinge, axis, -side * angle), WOOD
        yield f"{label} companionway door window", pane.rotate(hinge, axis, -side * angle), GLASS


def make_companionway_access_parts():
    access = access_geometry()
    aft = COMPANIONWAY_AFT_FT
    yield "Companionway sill", block(
        0, aft - .03, access.entry_deck - .05,
        ACCESS_CLEAR_WIDTH_FT + 2 * CABIN_WALL_FT, .42,
        access.sill - access.entry_deck + .05), WOOD
    for side, label in ((PORT_SIDE, "Port"), (-PORT_SIDE, "Starboard")):
        yield f"{label} companionway jamb", block(
            side * (ACCESS_CLEAR_WIDTH_FT + CABIN_WALL_FT) / 2,
            aft + .03, access.entry_deck - .04, CABIN_WALL_FT, .24,
            access.head + .12 - access.entry_deck + .04), IVORY
        for index, z in enumerate((access.sill + .55, access.head - .5), 1):
            hinge_x = side * (ACCESS_CLEAR_WIDTH_FT / 2 - ACCESS_DOOR_GAP_FT)
            hinge_f = aft - .1 - ACCESS_DOOR_THICKNESS_FT / 2
            barrel = spar_between(boat_point(hinge_x, hinge_f, z - .09),
                                  boat_point(hinge_x, hinge_f, z + .09), .035)
            strap = block(side * (ACCESS_CLEAR_WIDTH_FT / 2 + .055),
                          aft - .035, z - .045, .16, .15, .09)
            yield f"{label} companionway hinge {index}", barrel.fuse(strap), IRON
    yield "Companionway lintel", block(
        0, aft + .03, access.head, ACCESS_CLEAR_WIDTH_FT + 2 * CABIN_WALL_FT,
        .24, .12), IVORY
    yield from make_companionway_doors()

    yield "Companionway landing", block(
        0, (ACCESS_WELL_AFT_FT + ACCESS_WELL_FORE_FT) / 2,
        access.sole - ACCESS_TIMBER_FT, ACCESS_WELL_WIDTH_FT,
        ACCESS_WELL_FORE_FT - ACCESS_WELL_AFT_FT, ACCESS_TIMBER_FT), WOOD
    tread_width = ACCESS_CLEAR_WIDTH_FT + .08
    for index in range(1, ACCESS_TREAD_COUNT + 1):
        forward, top = access.tread(index)
        yield f"Companionway tread {index}", block(
            0, forward, top - ACCESS_TIMBER_FT, tread_width,
            ACCESS_TREAD_DEPTH_FT, ACCESS_TIMBER_FT), WOOD
    first_f, _ = access.tread(1)
    last_f, _ = access.tread(ACCESS_TREAD_COUNT)
    start_f = first_f - ACCESS_TREAD_DEPTH_FT / 2
    end_f = last_f + ACCESS_TREAD_GOING_FT
    stringer = (cq.Workplane('YZ').polyline([
        (25 - start_f, access.sill - .03), (25 - end_f, access.sole + .04),
        (25 - end_f, access.sole - .12), (25 - start_f, access.sill - .40),
    ]).close().extrude(ACCESS_TIMBER_FT / 2, both=True).val())
    for side, label in ((PORT_SIDE, "Port"), (-PORT_SIDE, "Starboard")):
        yield f"{label} companionway stringer", stringer.translate(
            (side * (tread_width / 2 - .04), 0, 0)), WOOD


def make_deckhouse_parts():
    access = access_geometry()
    floor = deck_height(CABIN_FORWARD_FT) - .1
    roof = floor + CABIN_HEIGHT_FT
    yield "Main cabin", make_cabin(floor), IVORY
    main_roof = make_cambered_roof(
        CABIN_FORWARD_FT, roof, CABIN_WIDTH_FT + 2*CABIN_ROOF_OVERHANG_FT, CABIN_LENGTH_FT + .32,
        CABIN_ROOF_CAMBER_FT)
    yield "Main cabin roof", main_roof.cut(access.roof_tool(), access.door_tool()), IVORY
    base = companionway_base()
    yield "Raised companionway", make_companionway(base), IVORY
    aft = COMPANIONWAY_FORWARD_FT - COMPANIONWAY_LENGTH_FT / 2 - .2
    fore = COMPANIONWAY_FORWARD_FT + COMPANIONWAY_LENGTH_FT / 2 - COMPANIONWAY_FRONT_SETBACK_FT + .2
    yield "Companionway roof", make_cambered_roof(
        (aft + fore) / 2, base + COMPANIONWAY_HEIGHT_FT,
        COMPANIONWAY_WIDTH_FT + .4, fore - aft, COMPANIONWAY_ROOF_CAMBER_FT), IVORY
    pane_wire = companionway_window_wire(base).offset2D(.025)[0]
    for side, label in ((PORT_SIDE, "Port"), (-PORT_SIDE, "Starboard")):
        for index, forward in enumerate((11.2, 12.8), 1):
            yield f"{label} cabin window {index}", block(
                side * (CABIN_WIDTH_FT / 2 - .05), forward,
                floor + 1.11, .045, 1.13, .63,
            ), GLASS
        pane = (cq.Workplane('YZ').add(pane_wire).toPending().extrude(.0175, both=True)
                .translate((side * (COMPANIONWAY_WIDTH_FT / 2 - .035), 0, 0)).val())
        yield f"{label} companionway window", pane, GLASS
    yield from make_companionway_access_parts()


def make_hatches():
    for name, forward, width, length in HATCHES_FT:
        yield name, make_hatch(forward, width, length, HATCH_ACROSS_FT.get(name, 0)), IVORY
    yield from make_hatch_covers()


def make_jib_traveller():
    f = JIB_TRAVELLER_FORWARD_FT
    # Item 14 on sheet 4: the athwartship rod just ahead of the mast.
    section = min(SECTIONS, key=lambda s: abs(s[0] - f))
    half_span = section[1] - .2
    top = deck_height(f) + .45
    bar = spar_between(boat_point(-half_span, f, top), boat_point(half_span, f, top), .04)
    feet = []
    for side in (-1, 1):
        x = side * half_span
        floor = deck_height(f, x) - .04
        feet.append(block(x, f, floor, .18, .24, top - floor + .04))
    return bar.fuse(*feet)


def make_helm():
    forward = HELM_BOX_FORWARD_FT
    floor = deck_height(HELM_FORWARD_FT)
    # Hollow wheel box: both the wheel axle and the rudder-stock head enter
    # its interior. Sheet 4 identifies the steering as hydraulic; do not
    # invent an external bent drive shaft between these two different axes.
    box = block(0, forward, floor - .05, HELM_BOX_WIDTH_FT,HELM_BOX_LENGTH_FT,HELM_BOX_HEIGHT_FT)
    inside = block(0, forward, floor - .15, HELM_BOX_WIDTH_FT-.20,HELM_BOX_LENGTH_FT-.20,HELM_BOX_HEIGHT_FT+.3)
    axle=spar_between(boat_point(0,STERN_SOURCE['helm_box_fore_ft']-.47,floor+HELM_WHEEL_HEIGHT_FT),
                     boat_point(0,HELM_WHEEL_FORWARD_FT+.1,floor+HELM_WHEEL_HEIGHT_FT),.075)
    bore=spar_between(boat_point(0,HELM_FORWARD_FT,floor+HELM_WHEEL_HEIGHT_FT),
                     boat_point(0,HELM_WHEEL_FORWARD_FT+.2,floor+HELM_WHEEL_HEIGHT_FT),.085)
    front_opening=block(0,STERN_SOURCE['helm_box_fore_ft'],floor-.12,
                        HELM_BOX_WIDTH_FT-.32,.45,1.02)
    yield "Steering pedestal", box.cut(inside,bore,front_opening), IVORY
    for i in range(3):
        width=(HELM_BOX_WIDTH_FT+.06)/3
        yield f'Helm lid timber {i+1}',block(-HELM_BOX_WIDTH_FT/2-.03+(i+.5)*width,forward,
              floor+HELM_BOX_HEIGHT_FT-.06,width-.003,HELM_BOX_LENGTH_FT+.06,.12),WOOD
    yield "Helm wheel", make_wheel(HELM_WHEEL_FORWARD_FT, floor + HELM_WHEEL_HEIGHT_FT), (.65,.67,.66)
    for i in range(8):
        a=i*math.tau/8
        start=boat_point(1.05*math.cos(a),HELM_WHEEL_FORWARD_FT,floor+HELM_WHEEL_HEIGHT_FT+1.05*math.sin(a))
        end=boat_point(HELM_HANDLE_RADIUS_FT*math.cos(a),HELM_WHEEL_FORWARD_FT,floor+HELM_WHEEL_HEIGHT_FT+HELM_HANDLE_RADIUS_FT*math.sin(a))
        yield f'Helm wheel wood grip {i+1}',spar_between(start,end,.065).fuse(cq.Solid.makeSphere(.065,end)),WOOD
    yield "Wheel shaft",axle,IRON
    yield "Steering shaft", make_steering_shaft(), IRON
    yield "Rudder upper bearing", make_rudder_upper_bearing(), IRON
    from .stern_fittings import make_hydraulics
    yield from make_hydraulics()
    # S04 item4d is a case-side cleat, distinct from the item18 traveller.
    x=HELM_BOX_WIDTH_FT/2+.035
    z=floor+HELM_BOX_HEIGHT_FT-.12
    base=block(x,forward,z-.06,.12,.55,.12)
    horn=spar_between(boat_point(x,forward-.43,z+.055),boat_point(x,forward+.43,z+.055),.045)
    stems=[spar_between(boat_point(x,forward+d,z-.02),boat_point(x,forward+d,z+.06),.04) for d in (-.16,.16)]
    yield 'Helm main-sheet cleat (S04 item4d)',base.fuse(horn,*stems),IRON


def make_bow_post():
    forward = BOW_POST_FORWARD_FT
    floor = deck_height(forward)
    # Sheets 5/6: 5-inch-square foot, tapering to a 14 x 5-inch head.
    from .frame_layout import samson_heel
    from .hull import rabbet_height
    heel=samson_heel(deck_height,rabbet_height)
    exposed=(cq.Workplane('XY', origin=boat_point(0, forward, floor + .1))
            .rect(5 / 12, 5 / 12).workplane(offset=1.9)
            .rect(14 / 12, 5 / 12).loft(ruled=True).val())
    post=exposed.fuse(block(0,forward,heel,5/12,5/12,floor+.1-heel+.015))
    return post
