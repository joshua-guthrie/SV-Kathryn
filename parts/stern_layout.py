"""Classified surveyed stern: curved wood planform plus independent counter.

The 50-ft datum, aft reference bound, actual wood contour and counter anchor are
different objects. The inward plan offset is a genuine 2D normal offset; the
counter offset is along its own normal, preserving material at the knuckle.
"""
from functools import lru_cache
import math
import cadquery as cq
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq
from .params import *

_wood=np.array(STERN_REMEDY_SOURCE['fitted_outer_wood_controls'])
_rail=np.array(STERN_REMEDY_SOURCE['fitted_rail_controls'])
_wood_curve=PchipInterpolator(_wood[:,0],_wood[:,1])
_rail_curve=PchipInterpolator(_rail[:,0],_rail[:,1])


def reference_height(deck=None):
    return STERN_REMEDY_SOURCE['counter']['anchor_height_ft']


def wood_forward(x):
    return float(_wood_curve(min(25,abs(x))))


def wood_halfwidth(f):
    if f<wood_forward(0):return 0.0
    if f>=_wood[-1,1]:return 25.0
    return float(brentq(lambda x:wood_forward(x)-f,0,25))


@lru_cache(maxsize=8)
def plan_keep(inset=0):
    # Exact cubic Bezier representation of the PCHIP pieces avoids a free
    # global spline bulging away from classified source controls.
    xs=sorted(set([*-_wood[::-1,0],*_wood[:,0]]))
    edges=[]
    for a,b in zip(xs[:-1],xs[1:]):
        h=b-a;fa,fb=wood_forward(a),wood_forward(b)
        da=float(_wood_curve.derivative()(abs(a)))*(-1 if a<0 else 1)
        db=float(_wood_curve.derivative()(abs(b)))*(-1 if b<0 else 1)
        controls=[cq.Vector(a,25-fa,-10),cq.Vector(a+h/3,25-fa-da*h/3,-10),
                  cq.Vector(b-h/3,25-fb+db*h/3,-10),cq.Vector(b,25-fb,-10)]
        edges.append(cq.Edge.makeBezier(controls))
    a,b=xs[0],xs[-1]
    edges.extend([cq.Edge.makeLine(cq.Vector(b,25-wood_forward(b),-10),cq.Vector(b,-100,-10)),
                  cq.Edge.makeLine(cq.Vector(b,-100,-10),cq.Vector(a,-100,-10)),
                  cq.Edge.makeLine(cq.Vector(a,-100,-10),cq.Vector(a,25-wood_forward(a),-10))])
    wire=cq.Wire.assembleEdges(edges)
    if inset:wire=wire.offset2D(-inset)[0]
    return cq.Solid.extrudeLinear(wire,[],(0,0,50))


@lru_cache(maxsize=256)
def plan_limit(x,inset=0):
    if not inset:return wood_forward(x)
    line=cq.Edge.makeLine(cq.Vector(x,40,0),cq.Vector(x,-100,0))
    region=plan_keep(inset).intersect(line)
    return 25-region.BoundingBox().ymax


def counter_forward(z,reference=None,inset=0):
    reference=reference_height() if reference is None else reference
    f=STERN_REMEDY_SOURCE['counter']['anchor_forward_ft']+STERN_RAKE_FT_PER_FT*(reference-z)
    return f+inset*math.sqrt(1+STERN_RAKE_FT_PER_FT**2)


def face_forward(z,reference=None,across=0,inset=0):
    return max(plan_limit(float(across),inset),counter_forward(z,reference,inset))


@lru_cache(maxsize=8)
def keep(reference=None,inset=0):
    reference=reference_height() if reference is None else reference
    low,high=-10,35
    a=counter_forward(low,reference,inset);b=counter_forward(high,reference,inset)
    counter=(cq.Workplane('YZ').polyline([(25-a,low),(25-100,low),(25-100,high),(25-b,high)])
             .close().extrude(25,both=True).val())
    shape=counter.intersect(plan_keep(inset))
    assert shape.isValid() and len(shape.Solids())==1,'Invalid classified stern keep volume'
    return shape


def knuckle_height(x,inset=0):
    return reference_height()-(plan_limit(float(x),inset)-STERN_REMEDY_SOURCE['counter']['anchor_forward_ft']
                               -inset*math.sqrt(1+STERN_RAKE_FT_PER_FT**2))/STERN_RAKE_FT_PER_FT


def rail_forward(x):
    return float(_rail_curve(min(abs(x),_rail[-1,0])))


def rail_derivative(x):
    return float(_rail_curve.derivative()(min(abs(x),_rail[-1,0])))*(-1 if x<0 else 1)


def rail_height(f,nominal):
    t=min(1,max(0,(f-4)/10));blend=t*t*t*(10+t*(-15+6*t))
    key='top_ft' if nominal==RAIL_TOP_FT else 'lower_ft'
    return STERN_REMEDY_SOURCE['rail_heights'][key]*(1-blend)+nominal*blend
