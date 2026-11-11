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
