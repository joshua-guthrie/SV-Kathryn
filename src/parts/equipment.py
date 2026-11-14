"""Simplified oyster-dredging equipment, based on sheets 4 and 7."""
import math
import cadquery as cq
from .params import (boat_point, WINCH_FORWARD_FT, ENGINE_FORWARD_FT, IVORY, IRON,
                     PORT_SIDE, legacy_forward, sheer_band_height, ENGINE_COVER_LENGTH_FT)
from .hull import deck_height
from .primitives import block, spar_between


def make_winder_drum(across, forward, height):
    body = spar_between(boat_point(across, forward - .85, height),
                        boat_point(across, forward + .85, height), .57)
    ends = []
    for end in (-.85, .85):
        plate = spar_between(boat_point(across, forward + end - .075, height),
                             boat_point(across, forward + end + .075, height),
                             .93 if end > 0 else .86)
        holes = []
        for i in range(8):
            angle = i * math.tau / 8
            x, z = across + .70 * math.cos(angle), height + .70 * math.sin(angle)
            holes.append(spar_between(boat_point(x, forward + end - .2, z),
                                      boat_point(x, forward + end + .2, z), .065))
        ends.append(plate.cut(*holes))
    axle = spar_between(boat_point(across, forward - 1.75, height),
                        boat_point(across, forward + 1.35, height), .13)
    return body.fuse(axle, *ends)


def make_winder_frame(forward, floor):
    pieces = []
    for end in (-1.15, 1.15):
        for side in (-1, 1):
            foot = boat_point(side * 2.2, forward + end, floor + .1)
            shoulder = boat_point(side * 2.2, forward + end, floor + 2.65)
            corner = boat_point(side * .85, forward + end, floor + 3.45)
            pieces.extend((spar_between(foot, shoulder, .09),
                           spar_between(shoulder, corner, .09)))
        pieces.append(spar_between(boat_point(-.85, forward + end, floor + 3.45),
                                   boat_point(.85, forward + end, floor + 3.45), .09))
        pieces.append(spar_between(boat_point(-2.2, forward + end, floor + 1.05),
                                   boat_point(2.2, forward + end, floor + 1.05), .09))
    for side in (-1, 1):
        pieces.append(spar_between(boat_point(side * 2.2, forward - 1.15, floor + .15),
                                   boat_point(side * 2.2, forward + 1.15, floor + .15), .09))
        pieces.append(spar_between(boat_point(side * .85, forward - 1.15, floor + 3.45),
                                   boat_point(side * .85, forward + 1.15, floor + 3.45), .09))
        pieces.append(spar_between(boat_point(side * .85, forward - 1.15, floor + 3.45),
                                   boat_point(-side * .85, forward + 1.15, floor + 3.45), .055))
    return pieces[0].fuse(*pieces[1:])


def make_winder_bearing(across, forward, floor):
    bearing = block(across, forward, floor + 1.04, .36, .30, .42)
    bore = spar_between(boat_point(across, forward - .25, floor + 1.3),
                        boat_point(across, forward + .25, floor + 1.3), .15)
    return bearing.cut(bore)


def make_winder_drive_wheel(across, forward, height):
    wheel = spar_between(boat_point(across, forward - .07, height),
                         boat_point(across, forward + .07, height), .96)
    hub = spar_between(boat_point(across, forward - .11, height),
                       boat_point(across, forward + .11, height), .23)
    plane = cq.Plane(origin=boat_point(across, forward, height), xDir=(1, 0, 0), normal=(0, -1, 0))
    slots = []
    for i in range(4):
        angle = math.pi / 4 + i * math.pi / 2
        def p(radius, theta):
            return radius * math.cos(theta), radius * math.sin(theta)
        a, b = angle - .31, angle + .31
        slots.append((cq.Workplane(plane).moveTo(*p(.78, a))
                      .threePointArc(p(.78, angle), p(.78, b)).lineTo(*p(.42, b))
                      .threePointArc(p(.42, angle), p(.42, a)).close()
                      .extrude(.2, both=True).val()))
    return wheel.fuse(hub).cut(*slots)


def make_winder_brake(side, forward, floor):
    across = side * 1.1
    f = forward - 1.42
    band = cq.Solid.makeTorus(.99, .025, boat_point(across, f, floor + 1.3), (0, 1, 0))
    attach = boat_point(across + side * 1.02 / math.sqrt(2), f,
                        floor + 1.3 - 1.02 / math.sqrt(2))
    foot = boat_point(side * 2.1, f, floor + .20)
    anchor = spar_between(attach, foot, .045)
    lever = spar_between(foot, boat_point(side * 2.3, forward - 1.55, floor + 2.1), .045)
    base = block(side * 2.1, f, floor + .12, .18, .24, .15)
    return band.fuse(anchor, lever, base)


def make_winder_clutch(across, forward, floor):
    f = forward - 1.62
    collar = spar_between(boat_point(across, f - .06, floor + 1.3),
                          boat_point(across, f + .06, floor + 1.3), .22)
    lever = spar_between(boat_point(across, f, floor + 1.3),
                         boat_point(across, forward - 1.72, floor + .6), .045)
    paddle = block(across, forward - 1.72, floor + .53, .30, .20, .14)
    bore = spar_between(boat_point(across, f - .2, floor + 1.3),
                        boat_point(across, f + .2, floor + 1.3), .145)
    return collar.fuse(lever, paddle).cut(bore)


def make_equipment():
    forward = WINCH_FORWARD_FT
    floor = deck_height(forward)
    yield "Dredge winder frame", make_winder_frame(forward, floor), IRON
    for side, label in ((PORT_SIDE, "Port"), (-PORT_SIDE, "Starboard")):
        yield f"{label} winder drum", make_winder_drum(side * 1.1, forward,
                                                      floor + 1.3), IRON
        yield f"{label} winder skid", block(side * 2.1, forward, floor - .08,
                                            .45, 3.3, .25), IVORY
        for end, name in ((-1.15, 'aft'), (1.15, 'fore')):
            yield f'{label} {name} winder bearing', make_winder_bearing(side * 1.1, forward + end, floor), IRON
        yield f'{label} winder drive wheel', make_winder_drive_wheel(
            side * 1.1, forward - 1.42, floor + 1.3), IRON
        yield f'{label} winder brake and lever', make_winder_brake(side, forward, floor), IRON
        yield f'{label} winder clutch control', make_winder_clutch(side * 1.1, forward, floor), IRON
        across = side * 7.55
        yield f"{label} dredge roller", spar_between(
            boat_point(across, 21.8, deck_height(21.8, across) + .65),
            boat_point(across, 27.4, deck_height(27.4, across) + .65), .17,
        ), IRON
        for index, position in enumerate((21.8, 27.4), 1):
            floor_at_side = deck_height(position, across)
            yield f"{label} roller support {index}", block(
                across, position, floor_at_side - .05, .4, .55, .8,
            ), IVORY
    engine_floor = deck_height(ENGINE_FORWARD_FT) - .04
    enclosure = block(0, ENGINE_FORWARD_FT, engine_floor, 4.0, ENGINE_COVER_LENGTH_FT, 1.65)
    inside = block(0, ENGINE_FORWARD_FT, engine_floor-.1, 3.75, ENGINE_COVER_LENGTH_FT-.25, 1.9)
    yield "Winder engine cover", enclosure.cut(inside), IVORY
    yield "Engine cover top", block(0, ENGINE_FORWARD_FT, engine_floor + 1.65,
                                      4.12, ENGINE_COVER_LENGTH_FT+.12, .12), IVORY
