"""Source-traced facing regions. Full-size feet; every separate island is kept."""
from functools import lru_cache
import cadquery as cq
import numpy as np
from .params import boat_point,CARVED_IVORY,IRON
from .bow_layout import LONGHEAD
from .trailboard_layout import TARGET,FEATURES,native_to_fz
from .hull import solid_envelope
from .primitives import spar_between

THICK=LONGHEAD['board_thickness_ft']
HALF_BACK=LONGHEAD['backing_width_ft']/2
ROOT_F=LONGHEAD['root_f']
RELIEF=TARGET['assumptions']['relief_extrusion_ft']
EMBED=TARGET['assumptions']['relief_embed_ft']


def plane(side,offset=0):
    return cq.Plane(origin=boat_point(side*(HALF_BACK+THICK+offset),ROOT_F,0),
                    xDir=(0,side,0),normal=(side,0,0))


def wire(side,points,reflect=False):
    fz=native_to_fz(points,reflect_name=reflect)
    local=np.column_stack((-side*(fz[:,0]-ROOT_F),fz[:,1]))
    keep=np.r_[True,np.linalg.norm(np.diff(local,axis=0),axis=1)>1e-7]
    local=local[keep]
    if np.linalg.norm(local[0]-local[-1])<1e-7:local=local[:-1]
    return cq.Workplane(plane(side)).polyline(local.tolist()).close().val()


def outline(side):return wire(side,FEATURES['outer-facing']['native_points'])


def polygon_solid(side,polygon,depth,offset=0,reflect=False):
    outside=wire(side,polygon['outer'],reflect)
    holes=[wire(side,h,reflect) for h in polygon.get('holes',[])]
    solid=cq.Solid.extrudeLinear(outside,holes,cq.Vector(side*depth,0,0))
    return solid.translate((side*offset,0,0))


def fastener_centre(f):
    from .trailboard_layout import panel_top,panel_bottom
    bottom=panel_bottom(f)
    return bottom+TARGET['assumptions']['fastener_height_fraction']*(panel_top(f)-bottom)


def fixing_bore(side,f):
    z=fastener_centre(f)
    return spar_between(boat_point(side*.12,f,z),boat_point(side*.43,f,z),LONGHEAD['fastener_radius_ft']+.0015)


@lru_cache(maxsize=2)
def field(side):
    shape=polygon_solid(side,FEATURES['paint-field']['polygons'][0],.006,-.002)
    for f in LONGHEAD['mount_stations_f']:shape=shape.cut(fixing_bore(side,f))
    return shape.cut(solid_envelope()).clean()


def region_parts(side,label):
    for feature in TARGET['features']:
        role=feature['role']
        if role in ('outline','field'):continue
        reflect=side>0 and role=='letter'
        if role=='letter':name=label+' trailboard letter '+feature['character']
        elif role=='eye':name=label+' longhead eagle eye'
        elif role=='recess':name=label+' trailboard '+feature['id']+' recess'
        else:name=label+' trailboard carving '+feature['id']
        color=IRON if role in ('eye','recess') else CARVED_IVORY
        # Dark separators occupy shallow recesses; they do not pierce the timber.
        depth,offset=(.006,-.002) if role=='recess' else (.008,-.002) if role=='eye' else (RELIEF,-EMBED)
        for j,polygon in enumerate(feature['polygons'],1):
            shape=polygon_solid(side,polygon,depth,offset,reflect)
            for f in LONGHEAD['mount_stations_f']:shape=shape.cut(fixing_bore(side,f))
            shape=shape.cut(solid_envelope()).clean()
            for k,solid in enumerate(shape.Solids(),1):
                suffix='' if j==1 and k==1 else f' {j}.{k}'
                assert solid.isValid(),name+suffix
                yield name+suffix,solid,color
