"""M4 individually partitioned hull boards, with explicit physical board IDs.

Runs/three chine courses/materials follow S01/S05/S06/S07. Exact irregular
spiling and staggered butt assignments are reconstruction, not a cutting plan.
Waterline subdivisions are finish regions of ONE logical board, not timber seams.
"""
from functools import lru_cache
import bisect
import math
import cadquery as cq
import numpy as np
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.TopAbs import TopAbs_IN,TopAbs_ON,TopAbs_OUT
from OCP.gp import gp_Pnt
from .params import *
from . import hull,stern_layout,frame_layout
from .board_tools import split_material,plane_x,plane_f,plane_z,seam_surface,segmented_loft,ruled_loft

BOTTOM_WEIGHTS=(.17,.10,.115,.10,.105,.10,.10,.105,.105)
SIDE_WEIGHTS=(.32,.37,.31)
FAMILIES=[*[f'bottom {i+1:02d}' for i in range(9)],*[f'chine {i+1}' for i in range(3)],
          *[f'topside {i+1}' for i in range(3)],'sheer strake']
FORE_CLOSURE_FT=HULL_FORE_FT-.75
REPORT=None


def row(f):
    return (f,*[float(np.interp(f,[s[0] for s in hull.SECTIONS],[s[i] for s in hull.SECTIONS])) for i in range(1,8)])


@lru_cache(maxsize=2048)
def profile(f):
    _,width,sheer,tw,tz,bw,bz,rz=row(f)
    uw=width-sheer_band_flare(f);uz=sheer-sheer_band_height(f)
    kw=min(3.5/12,uw*.25)
    top=sheer-hull.deck_thickness(sheer,tz)
    def p(x,z):return cq.Vector(*boat_point(x,f,z))
    rounding=hull.smooth_blend((hull._chine_top_end-f)/.8)
    edges=[cq.Edge.makeLine(p(0,rz),p(kw,rz)),cq.Edge.makeLine(p(kw,rz),p(bw,bz))]
    if rounding>1e-6:
        mid=(bw+(.5+.2*rounding)*(tw-bw),bz+(.5-.2*rounding)*(tz-bz))
        edges.append(cq.Edge.makeThreePointArc(p(bw,bz),p(*mid),p(tw,tz)))
    else:edges.append(cq.Edge.makeLine(p(bw,bz),p(tw,tz)))
    edges.extend([cq.Edge.makeLine(p(tw,tz),p(uw,uz)),cq.Edge.makeLine(p(uw,uz),p(width,top))])
    lengths=np.array([e.Length() for e in edges])
    bottom=sum(lengths[:2]);chine=lengths[2];lower=lengths[3];upper=lengths[4];total=sum(lengths)
    boundaries=[0,*np.cumsum(BOTTOM_WEIGHTS)*bottom]
    boundaries.extend(bottom+chine*np.array([1/3,2/3,1]))
    boundaries.extend(bottom+chine+lower*np.cumsum(SIDE_WEIGHTS))
    boundaries.append(total)
    return edges,lengths,np.array(boundaries)/total


def boundaries(f):
    base=profile(float(f))[2]
    reference=profile(float(LINE_STATIONS_FT[5]))[2]
    # Spiling into the final V entry; never force nine microscopic ribbons
    # onto the obsolete subdivided chine points after the real chine terminates.
    t=hull.smooth_blend((f-LINE_STATIONS_FT[9.5])/(FORE_CLOSURE_FT-LINE_STATIONS_FT[9.5]))
    return base*(1-t)+reference*t


def surface_point(f,u,side):
    edges,lengths,_=profile(float(f))
    cumulative=np.cumsum([0,*lengths]);distance=min(1,max(0,u))*cumulative[-1]
    i=min(len(edges)-1,max(0,bisect.bisect_right(cumulative,distance)-1))
    t=min(1,max(0,(distance-cumulative[i])/lengths[i]))
    p=edges[i].positionAt(float(t));v=edges[i].tangentAt(float(t))
    normal=cq.Vector(side*v.z,0,-v.x).normalized()
    return cq.Vector(side*p.x,p.y,p.z),normal


def longitudinal_cutters(side):
    fs=sorted(set([*np.linspace(HULL_AFT_FT-.02,FORE_CLOSURE_FT+.02,48),
                   *np.linspace(LINE_STATIONS_FT[9.5],FORE_CLOSURE_FT+.02,18)]))
    tools=[]
    for i in range(1,16):
        segments=[]
        for f in fs:
            p,n=surface_point(float(f),float(boundaries(f)[i]),side)
            a,b=p+n*.8,p-n*.8
            segments.append((a.toTuple(),b.toTuple()))
        faces=[seam_surface(segments[j:min(len(segments),j+13)])
               for j in range(0,len(segments)-1,12)]
        tools.append(cq.Compound.makeCompound(faces))
    return tools


def sublevel_tool(side,index):
    fs=sorted(set([*np.linspace(HULL_AFT_FT-.05,FORE_CLOSURE_FT+.05,40),
                   *np.linspace(LINE_STATIONS_FT[9.5],FORE_CLOSURE_FT+.05,16)]))
    wires=[]
    for f in fs:
        p,n=surface_point(float(f),float(boundaries(f)[index]),side)
        tangent=cq.Vector(side*(-n.z),0,side*n.x)
        vertices=[p+n*20,p-n*20,p-n*20-tangent*20,p+n*20-tangent*20]
        wires.append(cq.Wire.makePolygon(vertices+[vertices[0]]))
    return ruled_loft(wires)


def split_strakes(half,side):
    remaining=[half]
    result=[]
    for boundary in range(1,16):
        tool=sublevel_tool(side,boundary)
        classifier=BRepClass3d_SolidClassifier(tool.wrapped)
        next_remaining=[]
        for shape in remaining:
            pieces=split_material(shape,[tool])
            for cell in pieces:
                outside=False
                for vertex in cell.Vertices():
                    p=vertex.Center();classifier.Perform(gp_Pnt(p.x,p.y,p.z),1e-5)
                    if classifier.State()==TopAbs_OUT:outside=True;break
                if outside:next_remaining.append(cell)
                else:result.append((boundary-1,cell))
        remaining=next_remaining
        if REPORT and boundary in (1,8,15):REPORT(side,boundary,len(result),len(remaining))
    result.extend((15,piece) for piece in remaining)
    return result


def identify_course(shape,side):
    bb=shape.BoundingBox();a,b=25-bb.ymax,25-bb.ymin
    fs=[(a+b)/2,a+(b-a)*.25,a+(b-a)*.75]
    classifier=BRepClass3d_SolidClassifier(shape.wrapped)
    for f in fs:
        bounds=boundaries(f)
        for i in range(16):
            for t in (.25,.50,.75):
                p,n=surface_point(float(f),float(bounds[i]*(1-t)+bounds[i+1]*t),side)
                p=p-n*(INTERIOR_SKIN_FT/2)
                classifier.Perform(gp_Pnt(p.x,p.y,p.z),1e-6)
                if classifier.State() in (TopAbs_IN,TopAbs_ON):return i
    raise ValueError(f'Unclassified strake region F={a:g}..{b:g}, volume={shape.Volume():g}')


def cap_plane():
    rake=STERN_RAKE_FT_PER_FT
    reference=stern_layout.reference_height(hull.deck_height)
    f=stern_layout.face_forward(0,reference)+INTERIOR_SKIN_FT*math.sqrt(1+rake*rake)
    plane=cq.Plane(origin=boat_point(0,f,0),xDir=(1,0,0),normal=(0,-1,rake))
    return cq.Face.makeFromWires(cq.Workplane(plane).rect(60,140).val())


@lru_cache(maxsize=1)
def hull_strakes():
    source=hull.planking_envelope()
    coarse=split_material(source,[cap_plane(),plane_f(FORE_CLOSURE_FT)])
    result=[]
    for piece in coarse:
        p=piece.Center();f=25-p.y
        distance=(f-stern_layout.face_forward(p.z,stern_layout.reference_height(hull.deck_height)))/math.sqrt(1+STERN_RAKE_FT_PER_FT**2)
        if distance<INTERIOR_SKIN_FT+.02:
            result.append(dict(id='Transom',family='transom',shape=piece,side=0,course=-1))
        elif f>FORE_CLOSURE_FT-.01:
            result.append(dict(id='Stem closure',family='stem closure',shape=piece,side=0,course=-1))
        else:
            halves=split_material(piece,[plane_x(0)])
            for half in halves:
                side=1 if half.Center().x>0 else -1
                label='Port' if side>0 else 'Starboard'
                cells=split_strakes(half,side)
                for index,(course,cell) in enumerate(cells):
                    result.append(dict(id=f'{label} {FAMILIES[course]} region {index+1}',family=FAMILIES[course],
                                       shape=cell,side=side,course=course))
    assert abs(sum(r['shape'].Volume(1e-9) for r in result)-source.Volume(1e-9))<source.Volume(1e-9)*1e-6
    for side in (-1,1):
        assert {r['course'] for r in result if r['side']==side}==set(range(16)),('Incomplete strake partition',side)
    return tuple(result)


@lru_cache(maxsize=1)
def physical_hull_boards():
    boards=[]
    counters={}
    for strake in hull_strakes():
        shape=strake['shape'];side=strake['side'];course=strake['course']
        if strake['family']=='transom':
            pieces=split_material(shape,[plane_z(float(z)) for z in np.arange(4.4,7.8,.4)])
        elif strake['family']=='stem closure':pieces=[shape]
        else:
            sets=((20,13,5),(19,12,4),(18,11,3))[course%3]
            fs=[next(r['forward_ft'] for r in frame_layout.MEMBERS if r['set']==n and r['side']==side and r['role']=='primary') for n in sets]
            pieces=split_material(shape,[plane_f(float(f)) for f in fs])
        for piece in sorted(pieces,key=lambda s:25-s.Center().y):
            family=('Port ' if side>0 else 'Starboard ' if side<0 else '')+strake['family']
            counters[family]=counters.get(family,0)+1
            boards.append(dict(id=f'{family} board {counters[family]:02d}',family=family,
                shape=piece,side=side,course=course,
                material='pine' if course>=12 else 'oak' if course>=0 or strake['family']=='transom' else 'oak closing timber',
                butt_basis='staggered at registered frame planes; exact historic butt positions inferred'))
    return tuple(boards)


def hull_board_parts():
    for board in physical_hull_boards():
        regions=split_material(board['shape'],[plane_z(WATERLINE_FT)])
        for i,region in enumerate(regions,1):
            underwater=region.BoundingBox().zmax<WATERLINE_FT+1e-5
            finish='underwater finish' if underwater else 'topside finish'
            yield f'{board["id"]} {finish} region {i}',region,((.11,.17,.19) if underwater else (.88,.88,.83)),\
                  'Hull/Individual planking/'+board['id']
