"""M3 individual primary frames and added repair-pattern members.

Oak, highly irregular sided measurements: S05-10/16, S06-11/15, S07-08.
Rounded replacement knees are NOT described as grown knees. Hidden geometry and
fine laps are reconstructed; source graphic age applies to identified bottoms.
"""
from functools import lru_cache
import math
import cadquery as cq
import numpy as np
from .params import *
from . import beam_layout,hull,framing,frame_layout,stern_layout
from .centreline_layout import keelson_width
from .primitives import block,beam_between


def section_row(f):
    return [float(np.interp(f,[r[0] for r in hull.SECTIONS],[r[i] for r in hull.SECTIONS])) for i in range(8)]


@lru_cache(maxsize=128)
def frame_profile(f):
    if f>LINE_STATIONS_FT[9.5] or f<STERN_BLEND_END_FT:
        # The steep final bow changes appreciably between cavity loft stations.
        # Seat this frame to the actual loft section, not a separately computed
        # offset that can stand clear of the registered planking.
        plane=cq.Face.makeFromWires(hull.section_plane(f).rect(30,30).val())
        section=hull.continuous_interior().intersect(plane)
        return max(section.Faces(),key=lambda face:face.Area()).outerWire()
    return hull.shell_inner_profile(f)


def frame_inner_height(f,x):
    points=sorted((v.Center().x,v.Center().z) for v in frame_profile(f).Vertices()
                  if v.Center().x>=-1e-6 and v.Center().z<hull.deck_height(f)-.15)
    return float(np.interp(abs(x),[p[0] for p in points],[p[1] for p in points]))


@lru_cache(maxsize=128)
def band(f,sided,molded):
    # Use the ACTUAL cavity's sampled boundary, not a generic hard-chine rib.
    outer=frame_profile(f).offset2D(FRAME_SHELL_BEARING_FT)[0]
    inner=frame_profile(f).offset2D(-molded)[0]
    if molded>=REPAIR_FRAME_MOLDED_FT-1e-6 and f>=STERN_BLEND_END_FT:
        row=section_row(f)
        face=cq.Face.makeFromWires(inner)
        vertices=[]
        for vertex in face.Vertices():
            p=vertex.Center()
            if not (abs(p.x)>keelson_width(f)/2+1 and row[6]-.12<p.z<row[4]+.8):continue
            directions=[]
            for edge in face.Edges():
                a,b=edge.startPoint(),edge.endPoint()
                if (a-p).Length<1e-6:directions.append((b-p).normalized())
                elif (b-p).Length<1e-6:directions.append((a-p).normalized())
            if len(directions)==2 and directions[0].dot(directions[1])>-.9999:vertices.append(vertex)
        if vertices:
            # Rounded, NOT grown replacement knees (S06-11). Radii are fitted
            # to the irregular measured contour, not claimed printed sizes.
            for radius in (.35,.20,.10,.05):
                try:
                    rounded=face.fillet2D(radius,vertices)
                    if rounded.isValid():
                        inner=rounded.outerWire()
                        break
                except Exception:
                    continue
            else:raise ValueError(f'Cannot form rounded replacement knee at F={f:g}')
    return cq.Solid.extrudeLinear(outer,[inner],(0,-sided,0)).translate((0,sided/2,0))


def half_keep(f,side,start,width=15):
    return block(side*(start+width/2),f,-5,width,2,25)


def levels(member):
    f=member['forward_ft']
    row=section_row(f)
    bottom=min(v.Center().z for v in frame_profile(f).Vertices())
    # New bottom/knee rises farther up the side; primary lower timber tapers
    # toward the chine. A short scarf land joins the separate side futtock.
    joint=max((row[4]+.48 if member['role']=='repair-pattern' else row[6]+.10),bottom+.55)
    top=hull.deck_height(f,max(.1,row[1]-.35))-DECK_THICKNESS_FT+.012
    return joint,top


def taper_keep(member):
    f=member['forward_ft']
    row=section_row(f)
    width=max(row[5],keelson_width(f)/2+.3)
    half=keelson_width(f)/2
    slope=max(0,(row[6]-row[7])/(row[5]-min(3.5/12,row[1]*.25)))
    norm=math.sqrt(1+slope*slope)
    z0=hull.inner_bottom_height(f,0)+OLD_FRAME_MOLDED_FT*norm
    z1=hull.inner_bottom_height(f,half)+OLD_FRAME_MOLDED_FT*norm
    z2=hull.inner_bottom_height(f,width)+(2/12)*norm
    points=[(0,-5),(15,-5),(15,20),(width+.5,z2+1.5),(width,z2),(half,z1),(0,z0)]
    if member['side']<0:points=[(-x,z) for x,z in reversed(points)]
    return (cq.Workplane('XZ',origin=boat_point(0,f,0)).polyline(points).close()
            .extrude(member['sided_ft'],both=True).val())


def make_bottom_frame(member):
    f,side=member['forward_ft'],member['side']
    joint,_=levels(member)
    joint_type=member['keelson_joint']
    start=(keelson_width(f)/2-FRAME_TENON_FT if joint_type=='mortised' else
           max(keelson_width(f)/2,STEM_KNEE_WIDTH_FT/2 if f>STEM_KNEE_AFT_FT else 0)+.012
           if joint_type=='butt' and f>KEELSON_AFT_FT else 0)
    shape=band(f,member['sided_ft'],member['molded_ft'])
    shape=shape.intersect(half_keep(f,side,max(0,start))).intersect(
                          block(0,f,-5,30,2,joint+5))
    raised_counter=min(v.Center().z for v in frame_profile(f).Vertices())>hull.inner_bottom_height(f,0)+.05
    if member['role']=='primary' and not raised_counter:shape=shape.intersect(taper_keep(member))
    x=side*(keelson_width(f)/2+.35)
    z=(frame_inner_height(f,x) if f<STERN_BLEND_END_FT else hull.inner_bottom_height(f,x))-.08
    limber=block(x,f,z,FRAME_LIMBER_WIDTH_FT,member['sided_ft']+.1,FRAME_LIMBER_HEIGHT_FT+.08)
    tools=[limber]
    if f<STERN_BLEND_END_FT:tools.append(hull.rudder_stock_passage())
    return shape.cut(*tools).clean()


def make_side_frame(member):
    f,side=member['forward_ft'],member['side']
    joint,top=levels(member)
    # Side head deepens to the fitted clamp bearing; irregular head taper is
    # reconstruction, not an assertion of uniform original timber stock.
    lower=band(f,member['sided_ft'],member['molded_ft'])
    head=band(f,member['sided_ft'],FRAME_HEAD_MOLDED_FT).intersect(
        block(0,f,top-DECK_CLAMP_DEPTH_FT-.07,30,2,2))
    shape=lower.fuse(head).intersect(half_keep(f,side,0)).intersect(
            block(0,f,joint-.008,30,2,top-joint+.008))
    return shape.clean()


def label(member):
    side='Port' if member['side']>0 else 'Starboard'
    number=member['set']
    family=('older possibly original' if member['older_graphic'] else
            'repair-pattern' if member['role']=='repair-pattern' else 'primary age unresolved')
    return f'{member["id"]} {side} {family}'


def side_label(member):
    side='Port' if member['side']>0 else 'Starboard'
    family='repair-associated' if member['role']=='repair-pattern' else 'primary'
    return f'{member["id"]} {side} {family} age-unresolved side futtock'


def make_frame_parts():
    for member in frame_layout.MEMBERS:
        name=label(member)
        color=(.48,.33,.20) if member['older_graphic'] else (.69,.50,.28) if member['role']=='repair-pattern' else WOOD
        if member['keelson_joint']=='underpass':
            if member['side']>0:
                other=next(r for r in frame_layout.MEMBERS if r['set']==member['set'] and r['side']<0 and r['role']=='primary')
                floor=make_bottom_frame(member).fuse(make_bottom_frame(other)).clean()
                yield f'F{member["set"]:02d} continuous oak floor under keelson',floor,color
        else:
            yield name+' bottom and chine knee',make_bottom_frame(member),color
        yield side_label(member),make_side_frame(member),(.69,.50,.28) if member['role']=='repair-pattern' else WOOD


def make_stem_knee():
    wires=[]
    for f in np.linspace(STEM_KNEE_AFT_FT,STEM_KNEE_FORE_FT,18):
        low=hull.rabbet_height(f)+KEELSON_ABOVE_GARBOARD_FT-.012
        high=frame_layout.stem_knee_top(f,hull.deck_height,hull.rabbet_height)
        assert high>low+.02,('Stem knee ends too fine',f)
        wires.append(cq.Workplane(cq.Plane(origin=boat_point(0,f,(low+high)/2),xDir=(1,0,0),normal=(0,-1,0)))
                     .rect(STEM_KNEE_WIDTH_FT,high-low).val())
    knee=cq.Solid.makeLoft(wires,ruled=False).intersect(hull.solid_envelope())
    mortise=block(0,BOW_POST_FORWARD_FT,frame_layout.samson_heel(hull.deck_height,hull.rabbet_height)+.015,
                  5/12+.012,5/12+.012,4)
    return knee.cut(mortise)


def make_oak_reinforcement(side):
    aft=frame_layout.SOURCE['supports']['clamp_oak_reinforcement_aft_ft']
    fore=KEELSON_FORE_FT
    wires=[]
    for f in np.linspace(aft,fore,28):
        x=side*(framing.clamp_outer(f)-DECK_CLAMP_SIDED_FT*1.5+.012)
        z=framing.beam_top(f,x)-DECK_CLAMP_DEPTH_FT/2
        wires.append(cq.Workplane(cq.Plane(origin=boat_point(x,f,z),xDir=(1,0,0),normal=(0,-1,0)))
                     .rect(DECK_CLAMP_SIDED_FT,DECK_CLAMP_DEPTH_FT).val())
    return cq.Solid.makeLoft(wires,ruled=False)


def stanchion_beam(index,forward):
    # The M3 stanchions sit on measured S05 deck-beam stations.
    closest=min(beam_layout.BEAMS,key=lambda beam:abs(beam_layout.forward(beam)-forward))
    if abs(beam_layout.forward(closest)-forward)<DECK_BEAM_SIDED_FT*.8:
        return beam_layout.beam_name(closest),beam_layout.forward(closest),False
    return f'Stanchion {index} supporting deck beam',forward,True


def make_support_parts():
    yield 'Oak stem knee with Samson-post mortise',make_stem_knee(),WOOD
    # S05-07(c): the full transverse members aft of/at the rudder box are the
    # 4 x 3 1/2-in oak class.  The lettered 6 x 3-in pine "d" is not located
    # on the plan; beam_layout retains that open identification.
    for timber in beam_layout.STERN_TIMBERS:
        f=timber['forward_ft']
        span=framing.clamp_outer(f)-.015
        shape=framing.make_cross_beam(f,-span,span,timber['sided_ft'],timber['molded_ft'])
        yield timber['label'],shape.cut(hull.rudder_stock_passage()),WOOD
    for side,name in ((1,'Port'),(-1,'Starboard')):
        yield f'{name} forward oak clamp reinforcement',make_oak_reinforcement(side),(.53,.37,.22)
    for i,px in enumerate(frame_layout.SOURCE['supports']['stanchion_plan_preview_x'],1):
        f=frame_layout.source_plan_forward(px)
        name,beam_f,new=stanchion_beam(i,f)
        bottom=hull.rabbet_height(f)+KEELSON_ABOVE_GARBOARD_FT-.012
        top=framing.beam_top(beam_f,0)-DECK_BEAM_DEPTH_FT+.015
        yield f'Hold oak stanchion {i}',block(0,f,bottom,5.5/12,5.5/12,top-bottom),WOOD
        if new:
            span=framing.clamp_outer(f)-.015
            yield name,framing.make_cross_beam(f,-span,span),WOOD
    f=frame_layout.SOURCE['supports']['strongback_forward_ft']
    span=framing.clamp_outer(f)-.02
    top=framing.beam_top(f,0)
    yield 'Aft composite pine strongback top',framing.make_cross_beam(f,-span,span,5/12,5/12),WOOD
    # The source gives a 15-in central lower member tapered toward the sheer.
    # Keep its outer bearing within the actual hull instead of adding filler.
    edge=framing.beam_top(f,span)-5/12
    lower=(cq.Workplane('XZ',origin=boat_point(0,f,0))
           .moveTo(-span,edge+.008).threePointArc((0,top-5/12+.008),(span,edge+.008))
           .lineTo(span,edge-.16).lineTo(0,top-5/12-15/12).lineTo(-span,edge-.16).close()
           .extrude(5/24,both=True).val())
    yield 'Aft composite pine strongback lower',lower,WOOD
    # S05-27: 3.75-in sided fore/aft transom framing and 6.75 x 2-in braces.
    # Count, 6-in molding and exact diagonal end joints are scale/construction
    # inferences. Keep them explicitly separate from observed numbered sets.
    f=HULL_AFT_FT+INTERIOR_SKIN_FT+.24
    reference=stern_layout.reference_height(hull.deck_height)
    normal=math.sqrt(1+STERN_RAKE_FT_PER_FT**2)
    stiles=[]
    for i,x in enumerate((-4.75,-.56,.56,4.75),1):
        wires=[]
        zs=sorted(set([4.0,8.1,*[z for z in (stern_layout.knuckle_height(x),stern_layout.knuckle_height(x,INTERIOR_SKIN_FT)) if 4<z<8.1]]))
        for z in zs:
            forward=stern_layout.face_forward(z,reference,x,INTERIOR_SKIN_FT)+.24
            wires.append(cq.Workplane('XY',origin=boat_point(x,forward,z)).rect(3.75/12,.5).val())
        stile=cq.Solid.makeLoft(wires,ruled=True).intersect(hull.continuous_interior()).cut(hull.rudder_stock_passage())
        stiles.append(stile)
        yield f'Transom oak fore-aft frame {i}',stile,WOOD
    for side,name in ((1,'Port'),(-1,'Starboard')):
        base=hull.inner_bottom_height(f,0)+.25
        high=hull.deck_height(f,4.75)-DECK_THICKNESS_FT-.30
        brace=beam_between(boat_point(0,stern_layout.face_forward(base,reference,0,INTERIOR_SKIN_FT)+.55,base),
                           boat_point(side*4.75,stern_layout.face_forward(high,reference,side*4.75,INTERIOR_SKIN_FT)+.55,high),6.75/12,2/12)
        yield f'{name} transom oak diagonal brace',brace.intersect(hull.continuous_interior()).cut(hull.rudder_stock_passage()),WOOD
