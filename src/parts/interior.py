"""Thin partitions and local sole bearings in the hollow enclosure.

Panel thickness and local access/mast bearing details are construction-inferred;
M2 adds keelson/trunk reliefs; full frames and individual boards follow in M3/M4.
"""
import cadquery as cq

from .params import (
    boat_point, WOOD, IVORY, BULKHEAD_THICKNESS_FT, CABIN_FORE_FT,
    FOREPEAK_BULKHEAD_FT, ACCESS_WELL_AFT_FT, ACCESS_WELL_FORE_FT,
    ACCESS_WELL_WIDTH_FT, ACCESS_TIMBER_FT, HELM_FORWARD_FT,
)
from .hull import (shell_inner_profile, solid_envelope, inner_bottom_height,
                   deck_height, rudder_axis_point, _stock_up, _post_forward_at)
from .deck import access_geometry
from .primitives import block
from . import centreline_layout as centreline
from .hull import rabbet_height,keelson_seating_tool


def make_bulkhead(forward):
    start = forward - BULKHEAD_THICKNESS_FT/2
    outline = shell_inner_profile(start).offset2D(.035)[0]
    panel = cq.Solid.extrudeLinear(outline, [], (0, -BULKHEAD_THICKNESS_FT, 0))
    return panel.intersect(solid_envelope()).cut(
        keelson_seating_tool(),
        centreline.trunk_envelope(rabbet_height,access_geometry().sole,deck_height))


def make_landing_support(forward):
    access = access_geometry()
    top = access.sole - ACCESS_TIMBER_FT + .015
    depth = .20
    bearer = block(0, forward, top-depth, ACCESS_WELL_WIDTH_FT+.35, .22, depth)
    posts = []
    for x in (-(ACCESS_WELL_WIDTH_FT/2-.30),ACCESS_WELL_WIDTH_FT/2-.30):
        bottom = min(inner_bottom_height(forward+d, x+dx)
                     for d in (-.10,.10) for dx in (-.07,.07)) - .035
        assert bottom < top-depth, 'Landing support must have positive bearing height'
        posts.append(block(x, forward, bottom, .14, .22, top-depth-bottom+.025))
    return bearer.fuse(*posts).cut(keelson_seating_tool())


def make_rudder_box():
    # Survey note 18 identifies an inaccessible composite timber rudder box.
    # Reconstruct its hollow envelope on the already verified stock axis.
    low, high = 3.5, deck_height(HELM_FORWARD_FT)+.025
    origin = cq.Vector(*rudder_axis_point(low))
    plane = cq.Plane(origin=origin, xDir=(1,0,0), normal=tuple(_stock_up))
    length = (high-low)/_stock_up[2]
    boxing = (cq.Workplane(plane).rect(.74,.74).rect(.50,.50)
              .extrude(length).val())
    upper_keep = block(0,HELM_FORWARD_FT,deck_height(HELM_FORWARD_FT)-.25,4,4,2)
    return boxing.intersect(solid_envelope().fuse(upper_keep))


def make_enclosure_parts():
    yield 'Cabin forward bulkhead',make_bulkhead(CABIN_FORE_FT),IVORY
    yield 'Forepeak aft bulkhead',make_bulkhead(FOREPEAK_BULKHEAD_FT),IVORY
    for forward,label in ((ACCESS_WELL_AFT_FT+1.2,'aft'),(ACCESS_WELL_FORE_FT-.7,'fore')):
        yield f'Cabin sole {label} bearer and feet',make_landing_support(forward),WOOD
    yield 'Hollow rudder-stock box',make_rudder_box(),WOOD


# M5 cabin fit-out. Source: S07-V01/V02 cabin sections and S04-V01/V04.
# Dimensions are scale-measured or construction-inferred; the fit-out is kept
# clear of the companionway, steps and moving gear.
from .params import (CABIN_AFT_FT as _CABIN_AFT, CABIN_FORE_FT as _CABIN_FORE,
                     INTERIOR_SKIN_FT as _SKIN, WOOD as _WOOD, IRON as _IRON)
from .hull import topside_halfwidth as _halfwidth, deck_height as _deck, continuous_interior
from .deck import access_geometry as _access


def _cabin_sole_z():
    return _access().sole


def _cabin_half(f, z):
    return max(.1, _halfwidth(f, z) - _SKIN - .03)


def make_cabin_sole_parts():
    """Individual athwartships cabin sole boards on the existing bearers."""
    z = _cabin_sole_z() - .14
    f = _CABIN_AFT + 1.95
    index = 0
    while f < _CABIN_FORE - .25:
        index += 1
        half = _cabin_half(f, z)
        yield (f'Cabin sole board {index:02d}',
               block(0, f, z, 2 * half, .72, .14), _WOOD)
        f += .75


def make_cabin_settee_parts():
    """Port/starboard cabin settees/berths, with front panels and tops."""
    z0 = _cabin_sole_z()
    z1 = z0 + 1.35
    f0, f1 = _CABIN_AFT + 2.05, _CABIN_FORE - 1.75
    length = f1 - f0
    centre = (f0 + f1) / 2
    for side, label in ((1, 'Port'), (-1, 'Starboard')):
        half = min(_cabin_half(f, z1) for f in (f0, centre, f1))
        front = side * max(2.0, half - 1.65)
        top_inner = side * (half - .10)
        x = (front + top_inner) / 2
        width = abs(top_inner - front)
        yield (f'{label} cabin settee top',
               block(x, centre, z1 - .14, width, length, .14), _WOOD)
        yield (f'{label} cabin settee front',
               block(front, centre, z0, .10, length, z1 - z0), _WOOD)
        yield (f'{label} cabin settee aft end',
               block(x, f0, z0, width, .10, z1 - z0), _WOOD)
        yield (f'{label} cabin settee fore end',
               block(x, f1, z0, width, .10, z1 - z0), _WOOD)


def make_cabin_lining_parts():
    """Vertical pine cabin lining boards just inboard of the hull skin."""
    z0 = _cabin_sole_z()
    f = _CABIN_AFT + .60
    index = 0
    while f < _CABIN_FORE - .2:
        index += 1
        z1 = _deck(f) - .22
        half = _cabin_half(f, (z0 + z1) / 2)
        for side, label in ((1, 'Port'), (-1, 'Starboard')):
            yield (f'{label} cabin lining board {index:02d}',
                   block(side * (half - .06), f, z0, .08, .72, z1 - z0), _WOOD)
        f += .75


def make_cabin_stove_parts():
    """Four-burner cabin range against the forward cabin bulkhead (S07-V02)."""
    f = _CABIN_FORE - 1.05
    z = _cabin_sole_z()
    yield 'Cabin stove body', block(0, f, z, 1.82, 1.18, 1.34), _IRON
    for x in (-.46, .46):
        for df in (-.31, .31):
            yield (f'Cabin stove burner {x:+.2f}/{df:+.2f}',
                   block(x, f + df, z + 1.34, .28, .28, .055), _IRON)
    yield 'Cabin stove oven door', block(0, f - .60, z + .20, 1.0, .055, .72), _IRON
    yield 'Cabin stove flue', block(.55, f - .18, z + 1.34, .16, .16,
                                    max(.2, _deck(f) - (z + 1.34) - .18)), _IRON


def make_cabin_table_parts():
    """Small central cabin table on a sole pedestal."""
    f = (_CABIN_AFT + _CABIN_FORE) / 2 - .35
    z = _cabin_sole_z()
    yield 'Cabin table top', block(0, f, z + 1.95, 2.3, 1.35, .12), _WOOD
    yield 'Cabin table pedestal', block(0, f, z, .28, .28, 1.90), _WOOD


def make_cabin_locker_parts():
    """Aft cabin lockers above the settees, clear of the companionway."""
    f = _CABIN_AFT + 1.90
    z = _cabin_sole_z() + 1.35
    for side, label in ((1, 'Port'), (-1, 'Starboard')):
        x = side * 2.05
        yield (f'{label} aft cabin locker',
               block(x, f, z, 1.55, .46, .95), _WOOD)
        yield (f'{label} aft cabin locker door',
               block(x, f - .255, z + .12, 1.38, .035, .80), _WOOD)


def _cabin_air():
    return continuous_interior()


def _fitted(shape, name):
    shape = shape.intersect(_cabin_air())
    assert shape.isValid() and len(shape.Solids()) == 1, f'Cabin fit-out must stay inside the hull: {name}'
    return shape


def make_cabin_fitout_parts():
    for maker in (make_cabin_sole_parts, make_cabin_settee_parts,
                  make_cabin_lining_parts, make_cabin_stove_parts,
                  make_cabin_table_parts, make_cabin_locker_parts):
        for name, shape, color in maker():
            yield name, _fitted(shape, name), color
