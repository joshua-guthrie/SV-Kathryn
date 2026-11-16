"""Exact interior witnesses avoid expensive all-face extrema on thin relief."""
import cadquery as cq
import numpy as np


def contact_distance(shape,support):
    a,b=shape.BoundingBox(),support.BoundingBox()
    lo,hi=max(a.xmin,b.xmin),min(a.xmax,b.xmax)
    if hi-lo>1e-8:
        x=(lo+hi)/2
        centre=shape.Center()
        vertices=shape.Vertices()
        indices=np.linspace(0,len(vertices)-1,min(20,len(vertices)),dtype=int)
        for i in indices:
            v=vertices[i].Center()
            for blend in (.002,.02):
                p=cq.Vector(x,v.y*(1-blend)+centre.y*blend,v.z*(1-blend)+centre.z*blend)
                if shape.isInside(p,1e-8) and support.isInside(p,1e-8):
                    return 0.0
    return shape.distance(support)
