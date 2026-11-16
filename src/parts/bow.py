"""Source-coordinated full bowsprit, structural headwork and fitted trailboards.

Full-size feet. HAER source picks and qualified hidden construction details are
in bow_remedy_registration.json. Decorative facing boards are carried by the
longhead backing; the spar is seated and restrained by separate structural parts.
"""
import math
from functools import lru_cache
import numpy as np
import cadquery as cq
from scipy.interpolate import PchipInterpolator
from .params import boat_point,HULL_LENGTH_FT,WATERLINE_FT,IVORY,IRON,WOOD,CARVED_IVORY,PORT_SIDE,legacy_forward
from .hull import solid_envelope,SECTIONS,deck_height,section_plane,fair_loft,topside_halfwidth,smooth_blend
from .primitives import block,beam_between,spar_between
from .bow_layout import SOURCE,SPAR,HEADWORK,LONGHEAD,RIG,axis_height,radius_at,half_depth_at
from . import trailboards as traced
from .trailboard_layout import panel_top,panel_bottom,source_headrail_points

BOWSPRIT_HEEL_FT=SPAR['heel_f']
BOWSPRIT_END_FT=SPAR['end_f']
BOWSPRIT_HEEL_RADIUS_FT=SPAR['square_depth_ft']/2
BOWSPRIT_TIP_RADIUS_FT=SPAR['tip_radius_ft']
TRAILBOARD_ROOT_FT=LONGHEAD['root_f']
TRAILBOARD_TIP_FT=LONGHEAD['body_tip_f']
TRAILBOARD_THICKNESS_FT=LONGHEAD['board_thickness_ft']
TRAILBOARD_SIDE_OFFSET_FT=LONGHEAD['backing_width_ft']/2
TRAILBOARD_PAINT=(.035,.16,.09)
PANEL_FIELD=(.25,.045,.035)

bowsprit_height=axis_height
bowsprit_radius=radius_at


def spar_section(f):
    return cq.Workplane(cq.Plane(origin=boat_point(0,f,axis_height(f)),xDir=(1,0,0),normal=(0,-1,0)))


@lru_cache(maxsize=1)
def raw_bowsprit():
    rect=lambda f:spar_section(f).rect(SPAR['square_width_ft'],SPAR['square_depth_ft']).val()
    circ=lambda f:spar_section(f).circle(radius_at(f)).val()
    a,b,c,d=(SPAR[k] for k in ('heel_f','shoulder_f','round_start_f','end_f'))
    square=cq.Solid.makeLoft([rect(a),rect(b)],ruled=True)
    transition=cq.Solid.makeLoft([rect(b),circ(c)],ruled=True)
    round_part=cq.Solid.makeLoft([circ(c),circ(d)],ruled=True)
    result=square.fuse(transition,round_part).clean()
    assert result.isValid() and len(result.Solids())==1,'Full bowsprit loft'
    return result


def fid_head_counterbore():
    f=HEADWORK['pin_f'];bottom=axis_height(f)+half_depth_at(f)-.012
    return spar_between(boat_point(0,f,bottom),boat_point(0,f,bottom+1),HEADWORK['pin_radius_ft']+.0415)


def fid_bore():
    f=HEADWORK['pin_f'];r=HEADWORK['pin_radius_ft']+HEADWORK['pin_clearance_ft']
    return spar_between(boat_point(0,f,7.0),boat_point(0,f,12.0),r)


@lru_cache(maxsize=1)
def make_bowsprit_timber():
    return raw_bowsprit().cut(fid_bore()).cut(fid_head_counterbore()).clean().toNURBS()


def make_walking_boards():
    start=HEADWORK['walking_board_start_f'];end=SPAR['end_f']-.40
    for side,label in ((PORT_SIDE,'Port'),(-PORT_SIDE,'Starboard')):
        wires=[]
        for f in np.linspace(start,end,14):
            t=(f-start)/(end-start);x=side*(.64*(1-t)+.25*t)
            z=axis_height(f)+radius_at(f)+.075
            wires.append(section_plane(f).center(x,z).rect(.42*(1-t)+.20*t,.07).val())
        yield f'{label} bowsprit walking board',fair_loft(wires),IVORY


_stem_sections=[s for s in SECTIONS if s[0]>=legacy_forward(43.125)]
_stem_forward=PchipInterpolator([s[7] for s in _stem_sections],[s[0] for s in _stem_sections])

def stem_forward_at(z):return float(_stem_forward(z))


def make_stem():
    points=[(s[0],s[7]) for s in _stem_sections]
    front=[(HULL_LENGTH_FT/2-f-.12,z) for f,z in points]
    back=[(HULL_LENGTH_FT/2-f+.12,z) for f,z in reversed(points)]
    return (cq.Workplane('YZ').moveTo(*front[0]).spline(front[1:],includeCurrent=True)
            .lineTo(*back[0]).spline(back[1:],includeCurrent=True).close().extrude(.23,both=True).val())


def panel_plane(side,offset=0):
    normal=cq.Vector(side,0,0)
    origin=cq.Vector(*boat_point(side*(TRAILBOARD_SIDE_OFFSET_FT+TRAILBOARD_THICKNESS_FT),TRAILBOARD_ROOT_FT,0))+normal*offset
    return cq.Plane(origin=origin,xDir=(0,side,0),normal=normal)


def panel_u(side,f):return -side*(f-TRAILBOARD_ROOT_FT)


def panel_outline(side):
    return traced.outline(side)


def _extrude_wire(wire,side,height,offset=0):
    return cq.Workplane(panel_plane(side)).add(wire).toPending().extrude(height).val().translate(panel_plane(side).zDir.multiply(offset))


def board_fastener_centre(f):return traced.fastener_centre(f)


def board_fastener_bore(side,f):
    z=board_fastener_centre(f);r=LONGHEAD['fastener_radius_ft']+.0015
    return spar_between(boat_point(side*.12,f,z),boat_point(side*.42,f,z),r)


@lru_cache(maxsize=2)
def make_trailboard(side):
    panel=_extrude_wire(panel_outline(side),side,TRAILBOARD_THICKNESS_FT,-TRAILBOARD_THICKNESS_FT)
    for f in LONGHEAD['mount_stations_f']:panel=panel.cut(board_fastener_bore(side,f))
    return panel.cut(solid_envelope()).clean()


@lru_cache(maxsize=1)
def _raw_longhead_backing():
    core=_extrude_wire(panel_outline(1),1,LONGHEAD['backing_width_ft'],
                       -TRAILBOARD_THICKNESS_FT-LONGHEAD['backing_width_ft'])
    core=core.fuse(longhead_splice_mortise())
    for side in (-1,1):
        for f in LONGHEAD['mount_stations_f']:core=core.cut(board_fastener_bore(side,f))
    return core.clean()


@lru_cache(maxsize=1)
def longhead_backing():
    pieces=_raw_longhead_backing().cut(make_stemhead_extension()).Solids()
    return max(pieces,key=lambda s:s.Volume())


@lru_cache(maxsize=1)
def make_longhead_aft_filling():
    pieces=_raw_longhead_backing().cut(make_stemhead_extension()).Solids()
    return [p.cut(solid_envelope()).clean() for p in sorted(pieces,key=lambda s:s.Volume(),reverse=True)[1:]]


def make_painted_field(side):
    return traced.field(side)


_chain_link = (cq.Workplane('XY').ellipse(.17, .078).ellipse(.136, .044)
               .extrude(.018, both=True).val())


def linked_chain(start, end):
    """Alternating oval links, fused at small contact patches for this static
    exterior model. Each complete chain remains one valid registered solid.
    """
    start, end = np.asarray(start), np.asarray(end)
    direction = end - start
    length = float(np.linalg.norm(direction))
    tangent = direction / length
    normal = np.array((1., 0., 0.))
    normal -= tangent * np.dot(normal, tangent)
    normal /= np.linalg.norm(normal)
    other_normal = np.cross(tangent, normal)
    count = max(3, round(length / .27) + 1)
    links = []
    for i, t in enumerate(np.linspace(0, 1, count)):
        plane = cq.Plane(origin=tuple(start + t * direction), xDir=tuple(tangent),
                         normal=tuple(normal if i % 2 == 0 else other_normal))
        links.append(_chain_link.moved(plane.location))
    chain = links[0].fuse(*links[1:]).clean()
    assert chain.isValid() and len(chain.Solids()) == 1, 'Chain link contacts must join'
    return chain



def headrail_points(side):
    # The small after handoff retains the accepted hull rail; the visible arm
    # follows the independently identified S04 item-11 plan/profile points.
    return [[side*HEADWORK['headrail_root_x_ft'],HEADWORK['headrail_root_f'],HEADWORK['headrail_root_z']],
            *source_headrail_points(side)]


def headrail_point(side,f):
    points=np.asarray(headrail_points(side))
    return float(np.interp(f,points[:,1],points[:,0])),float(np.interp(f,points[:,1],points[:,2]))


@lru_cache(maxsize=2)
def make_headrail(side):
    points=headrail_points(side)
    pieces=[beam_between(boat_point(*a),boat_point(*b),HEADWORK['headrail_width_ft'],HEADWORK['headrail_depth_ft'])
            for a,b in zip(points,points[1:])]
    rail=pieces[0].fuse(*pieces[1:]).clean()
    assert rail.isValid() and len(rail.Solids())==1,'Fitted headrail and after handoff'
    return rail


def _bowsprit_band(f):
    # Loft both boundaries along the actual spar rake, not a horizontal extrusion.
    def wire(g,outer):
        pad=.045 if outer else .0015
        if g<=SPAR['shoulder_f']:
            return spar_section(g).rect(SPAR['square_width_ft']+2*pad,SPAR['square_depth_ft']+2*pad).val()
        return spar_section(g).circle(radius_at(g)+pad).val()
    outer=cq.Solid.makeLoft([wire(f-.09,True),wire(f+.09,True)],ruled=True)
    inner=cq.Solid.makeLoft([wire(f-.13,False),wire(f+.13,False)],ruled=True)
    return outer.cut(inner).cut(fid_bore())


def tack_point():
    f=SPAR['end_f']-RIG['tack_station_from_tip_ft']
    return boat_point(0,f,axis_height(f)+radius_at(f)+RIG['tack_eye_above_surface_ft'])


def headstay_point():
    f=RIG['headstay_f']
    return boat_point(0,f,axis_height(f)+half_depth_at(f)+.18)


def _ear(x,f,z,r=.03):
    outer=cq.Solid.makeCylinder(.12,.06,(x-.03,25-f,z),(1,0,0))
    bore=cq.Solid.makeCylinder(r+.0015,.10,(x-.05,25-f,z),(1,0,0))
    return outer.cut(bore)


@lru_cache(maxsize=1)
def make_tack_fitting():
    _,y,z=tack_point();f=25-y;parts=[_bowsprit_band(f)]
    bridge=block(0,f,axis_height(f)+radius_at(f)-.095,.43,.17,.16).cut(raw_bowsprit())
    parts.append(bridge)
    for side in (-1,1):
        x=side*.16
        web=block(x,f,axis_height(f)+radius_at(f)-.025,.06,.16,z-(axis_height(f)+radius_at(f))+.025)
        web=web.cut(spar_between((x-.1,y,z),(x+.1,y,z),RIG['tack_pin_radius_ft']+.0015))
        parts.extend([web,_ear(x,f,z,RIG['tack_pin_radius_ft'])])
    return parts[0].fuse(*parts[1:]).clean()


def make_tack_pin():
    _,y,z=tack_point();r=RIG['tack_pin_radius_ft']
    pin=spar_between((-.19,y,z),(.19,y,z),r)
    return pin.fuse(spar_between((-.22,y,z),(-.190,y,z),r+.026),spar_between((.190,y,z),(.22,y,z),r+.026)).clean()


def make_headstay_fitting():
    _,y,z=headstay_point();f=25-y
    base=_bowsprit_band(f)
    web=block(0,f,axis_height(f)+half_depth_at(f)-.02,.09,.17,z-axis_height(f)-half_depth_at(f)+.02)
    web=web.cut(spar_between((-.1,y,z),(.1,y,z),.0255))
    return base.fuse(web,_ear(0,f,z,.024)).clean()


def make_headstay_pin():
    _,y,z=headstay_point()
    return spar_between((-.03,y,z),(.03,y,z),.024).fuse(spar_between((-.06,y,z),(-.03,y,z),.045),spar_between((.03,y,z),(.06,y,z),.045))


def _bobstay_anchors(stem_z,f):
    return (boat_point(0,stem_forward_at(stem_z)+.20,stem_z),boat_point(0,f,axis_height(f)-radius_at(f)-.10))


def _stem_eye(z,point):
    f=stem_forward_at(z)
    return block(0,f,z-.075,.75,.24,.15).fuse(cq.Solid.makeTorus(.10,.025,point,(1,0,0)))


def _side_anchor(side):
    f=legacy_forward(45.5);z=deck_height(f)-.45
    return boat_point(side*(topside_halfwidth(f,z)+.15),f,z)


def _side_tip(side):
    f=SPAR['end_f']-.65
    return boat_point(side*(radius_at(f)+.10),f,axis_height(f))


def make_bow_chains():
    # Two survey chain bobstays; no third invented straight wire bobstay.
    for name,z,d in [('Bowsprit bobstay',4.7,.35),('Bowsprit inner bobstay',5.25,1.55)]:
        f=SPAR['end_f']-d;root,tip=_bobstay_anchors(z,f)
        yield name+' stem strap and eye',_stem_eye(z,root),IRON
        yield name+' collar and eye',_bowsprit_band(f).fuse(cq.Solid.makeTorus(.10,.025,tip,(1,0,0))),IRON
        yield name,linked_chain(root,tip),IRON
    f=SPAR['end_f']-.65;tip_band=_bowsprit_band(f)
    for side in (-1,1):tip_band=tip_band.fuse(cq.Solid.makeTorus(.10,.025,_side_tip(side),(0,1,0)))
    yield 'Bowsprit side-stay collar',tip_band,IRON
    for side,label in ((PORT_SIDE,'Port'),(-PORT_SIDE,'Starboard')):
        root=_side_anchor(side);x,y,z=root
        plate=block(x-side*.12,25-y,z-.17,.12,.32,.34)
        yield label+' bowsprit chainplate and eye',plate.fuse(cq.Solid.makeTorus(.10,.025,root,(0,1,0))),IRON
        yield label+' bowsprit shroud',linked_chain(root,_side_tip(side)),IRON


def longhead_splice_mortise():
    return beam_between(boat_point(0,49.45,7.58),boat_point(0,51.20,7.80),.50,.40)


def stem_splice_mortise():
    h=HEADWORK
    return beam_between(boat_point(0,h['stem_root_f'],h['stem_root_z']),
                        boat_point(0,h['stemhead_f'],h['stem_top_z']),h['stem_width_ft'],h['stem_molded_ft'])


def stem_splice_station(i):
    f=(49.40,49.65)[i]
    t=(f-HEADWORK['stem_root_f'])/(HEADWORK['stemhead_f']-HEADWORK['stem_root_f'])
    z=HEADWORK['stem_root_z']+t*(HEADWORK['stem_top_z']-HEADWORK['stem_root_z'])
    return f,z


def stem_splice_bore(i):
    f,z=stem_splice_station(i)
    return spar_between(boat_point(-.42,f,z),boat_point(.42,f,z),.0265)


def make_stem_splice_bolt(i):
    f,z=stem_splice_station(i)
    shaft=spar_between(boat_point(-1/3,f,z),boat_point(1/3,f,z),.025)
    caps=[spar_between(boat_point(side*(1/3),f,z),boat_point(side*(1/3+.035),f,z),.052) for side in (-1,1)]
    return shaft.fuse(*caps).clean()


@lru_cache(maxsize=1)
def make_stemhead_extension():
    member=stem_splice_mortise().cut(raw_bowsprit()).cut(fid_bore()).cut(make_cross_timber()).cut(make_stem())
    for i in (0,1):member=member.cut(stem_splice_bore(i))
    for side in (-1,1):
        for f in LONGHEAD['mount_stations_f']:member=member.cut(board_fastener_bore(side,f))
    return member.clean()


def _bed(f0,f1,width,bottom):
    wires=[]
    for f in np.linspace(f0,f1,10):
        top=axis_height(f)-half_depth_at(f)+.025
        low=bottom(f)
        wires.append(section_plane(f).center(0,(top+low)/2).rect(width,top-low).val())
    return cq.Solid.makeLoft(wires,ruled=False).cut(raw_bowsprit()).cut(fid_bore()).clean()


@lru_cache(maxsize=1)
def make_inboard_bed():
    return _bed(HEADWORK['inboard_bed_aft_f'],HEADWORK['inboard_bed_fore_f'],1.15,lambda f:deck_height(f)-.012)


def make_stemhead_saddle():
    f=HEADWORK['bearing_f']
    return _bed(f-.34,f+.34,1.12,lambda x:axis_height(x)-half_depth_at(x)-.17).cut(make_cross_timber())


def make_cross_timber():
    f=HEADWORK['bearing_f'];low=axis_height(f)-half_depth_at(f)-.35
    return block(0,f,low,1.85,.64,.20).cut(raw_bowsprit()).cut(fid_bore())


def fid_limits():
    f=HEADWORK['pin_f'];low=axis_height(f)-half_depth_at(f)-.35
    return low-.05,axis_height(f)+half_depth_at(f)+.013,low-.015


def make_fid():
    f=HEADWORK['pin_f'];r=HEADWORK['pin_radius_ft'];bottom,top,clip=fid_limits()
    pin=spar_between(boat_point(0,f,bottom),boat_point(0,f,top),r).fuse(
        spar_between(boat_point(0,f,top-.025),boat_point(0,f,top+.045),r+.04))
    return pin.cut(spar_between(boat_point(-.12,f,clip),boat_point(.12,f,clip),.0155))


def make_fid_clip():
    f=HEADWORK['pin_f'];_,_,z=fid_limits()
    return spar_between(boat_point(-.115,f,z),boat_point(.115,f,z),.014).fuse(
        spar_between(boat_point(-.13,f,z),boat_point(-.114,f,z),.024))


def make_cross_bearer(f):
    x,rail_z=headrail_point(1,f);r=radius_at(f);z=axis_height(f)+r+.04
    # Outboard spacers beyond the end of headrails seat directly on the spar.
    if f>HEADWORK['headrail_tip_f']:
        x=.32
        return block(0,f,axis_height(f)+r-.15,2*x+.3,.15,.19).cut(raw_bowsprit())
    bar=block(0,f,z-.13,2*abs(x)+.20,.18,.13)
    feet=[block(side*abs(x),f,rail_z-.04,.16,.18,z-.13-rail_z+.08) for side in (-1,1)]
    return bar.fuse(*feet).cut(raw_bowsprit()).clean()


def make_bow_structure():
    yield 'Bowsprit stem-head extension',make_stemhead_extension(),IVORY
    for i in (0,1):yield f'Stem-head splice bolt {i+1}',make_stem_splice_bolt(i),IRON
    yield 'Bowsprit inboard heel bed',make_inboard_bed(),IVORY
    yield 'Bowsprit heel bearing cross-timber',make_cross_timber(),IVORY
    yield 'Bowsprit heel saddle',make_stemhead_saddle(),IVORY
    yield 'Bowsprit fid',make_fid(),IRON
    yield 'Bowsprit fid retaining clip',make_fid_clip(),IRON
    # Side cheeks rise from the unchanged stem and receive the cross-timber.
    f=HEADWORK['bearing_f'];z=axis_height(f)-half_depth_at(f)
    for side,label in ((1,'Port'),(-1,'Starboard')):
        cheek=beam_between(boat_point(side*.24,50.0,8.0),boat_point(side*.70,f,z+.13),.26,.40)
        fitted=cheek.cut(raw_bowsprit()).cut(fid_bore()).cut(make_cross_timber()).cut(make_stemhead_extension())
        yield label+' stem-head cheek',max(fitted.Solids(),key=lambda s:s.Volume()),IVORY
    yield 'Head stay stem-head fitting',make_headstay_fitting(),IRON
    yield 'Head stay stem-head pin',make_headstay_pin(),IRON
    yield 'Jib tack collar and fork',make_tack_fitting(),IRON
    yield 'Jib tack pivot pin',make_tack_pin(),IRON
    for i,f in enumerate(HEADWORK['cross_bearer_stations_f'],1):
        yield f'Bowsprit cross-bearer {i}',make_cross_bearer(f),IVORY
    for side,label in ((1,'Port'),(-1,'Starboard')):
        rail=make_headrail(side)
        yield label+' projecting headrail',rail,IVORY
        kx,kz=headrail_point(side,49.4)
        knee=beam_between(boat_point(side*.58,49.35,7.65),boat_point(kx,49.4,kz),.19,.16)
        yield label+' headrail knee',max(knee.cut(rail).Solids(),key=lambda s:s.Volume()),IVORY


def make_bow_details():
    stem=make_stem();water=block(0,25,WATERLINE_FT-40,40,100,40)
    yield 'Painted stem and cutwater',stem.cut(water),IVORY
    yield 'Underwater stem shoe',stem.intersect(water),(.13,.18,.18)
    yield from make_bow_structure()
    yield 'Longhead trailboard backing',longhead_backing(),IVORY
    for i,filling in enumerate(make_longhead_aft_filling(),1):
        for k,solid in enumerate(filling.Solids(),1):yield f'Longhead aft filling {i}.{k}',solid,IVORY
    for side,label in ((PORT_SIDE,'Port'),(-PORT_SIDE,'Starboard')):
        outline=panel_outline(side)
        yield label+' trailboard board',make_trailboard(side),TRAILBOARD_PAINT
        yield label+' trailboard painted field',make_painted_field(side),PANEL_FIELD
        yield from traced.region_parts(side,label)
        for f in LONGHEAD['mount_stations_f']:
            z=board_fastener_centre(f);r=LONGHEAD['fastener_radius_ft'];inner=side*.14;outer=side*.37
            bolt=spar_between(boat_point(inner,f,z),boat_point(outer,f,z),r)
            head=spar_between(boat_point(side*.369,f,z),boat_point(side*.398,f,z),r+.021)
            yield f'{label} trailboard fixing F{f:.1f}',bolt.fuse(head),IRON
    yield 'Bowsprit downhaul sheave',make_downhaul_sheave(),IRON
    yield 'Jib downhaul foredeck cleat',make_downhaul_cleat(),IRON
    yield from make_bow_chains()


def downhaul_block_point():
    f=SPAR['end_f']-.70
    return boat_point(.24,f,axis_height(f)+.02)


def downhaul_cleat_point():
    f=RIG['downhaul_cleat_f'];x=RIG['downhaul_cleat_port_x_ft']
    return boat_point(x,f,deck_height(f,x)+.20)


def make_downhaul_block():
    x,y,z=downhaul_block_point();f=25-y
    frame=block(x,f,z-.17,.18,.38,.34)
    window=block(x,f,z-.13,.13,.28,.26)
    frame=frame.cut(window)
    axle=spar_between((x-.105,y,z),(x+.105,y,z),.020)
    return frame.fuse(axle,_bowsprit_band(f)).clean()


def make_downhaul_sheave():
    x,y,z=downhaul_block_point()
    wheel=spar_between((x-.031,y,z),(x+.031,y,z),.12)
    bore=spar_between((x-.06,y,z),(x+.06,y,z),.0215)
    groove=cq.Solid.makeTorus(.12,.014,(x,y,z),(1,0,0))
    return wheel.cut(bore).cut(groove).clean()


def make_downhaul_cleat():
    x,y,z=downhaul_cleat_point();f=25-y
    base=block(x,f,z-.208,.24,.48,.08)
    posts=[spar_between(boat_point(x,f+d,z-.15),boat_point(x,f+d,z),.026) for d in (-.12,.12)]
    horn=spar_between(boat_point(x,f-.34,z),boat_point(x,f+.34,z),.035)
    return base.fuse(*posts,horn).clean()


def downhaul_route(head):
    c=np.array(downhaul_block_point());a=np.array(head);b=np.array(downhaul_cleat_point());r=.12
    def angle(p,sign):
        delta=p[1:]-c[1:];distance=float(np.linalg.norm(delta))
        return math.atan2(delta[1],delta[0])+sign*math.acos(r/distance)
    start=angle(a,1);end=angle(b,-1)
    while end<start:end+=2*math.pi
    arc=[(float(c[0]),float(c[1]+r*math.cos(t)),float(c[2]+r*math.sin(t))) for t in np.linspace(start,end,18)]
    return [tuple(a),*arc,tuple(b)]


def make_varnished_tip_finish():
    a=SPAR['end_f']-SPAR['varnished_tip_length_ft'];b=SPAR['end_f']
    wires=[spar_section(f).circle(radius_at(f)+.0015).val() for f in (a,b)]
    return cq.Solid.makeLoft(wires,ruled=True).cut(raw_bowsprit()).clean()
