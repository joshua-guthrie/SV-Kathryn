"""Small solid-building helpers, using the common boat coordinates in feet."""
import cadquery as cq

from .params import boat_point


def spar_between(start, end, radius, end_radius=None):
    start, end = cq.Vector(*start), cq.Vector(*end)
    direction = end - start
    if end_radius is None or abs(end_radius - radius) < 1e-8:
        return cq.Solid.makeCylinder(radius, direction.Length, start, direction)
    return cq.Solid.makeCone(radius, end_radius, direction.Length, start, direction)


def block(across, forward, bottom, width, length, height):
    return (cq.Workplane("XY").box(width, length, height, centered=(True, True, False))
            .translate(boat_point(across, forward, bottom)).val())


def beam_between(start, end, width, thickness):
    start, end = cq.Vector(*start), cq.Vector(*end)
    direction = end - start
    # A crosswise beam cannot use its own axis as the section's x direction.
    x_dir=(0,1,0) if abs(direction.normalized().x)>.99 else (1,0,0)
    return (cq.Workplane(cq.Plane(origin=start, xDir=x_dir, normal=direction))
            .rect(width, thickness).extrude(direction.Length).val())
