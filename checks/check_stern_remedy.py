"""Independent native-control/actual-CAD stern comparisons and integration QA."""
import json
import math
import sys
from pathlib import Path
import cadquery as cq
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from parts import hull,rails,deck,hull_frames,framing,stern_fittings,interior
from parts.params import *
from geometry_checks import Contains
from check_hatches import overlap


def cross_section(shape,x):
    plane=cq.Face.makeFromWires(cq.Workplane('YZ',origin=(x,0,0)).rect(250,60).val())
    return shape.intersect(plane)


def check():
    target=json.loads((ROOT/'drawing_package/stern_remedy_targets.json').read_text())
    upper,lower=hull.make_hull()
    main=hull.make_deck()
    mould=hull.stern_moulding()
    timbers={n:s for n,s,_ in hull.make_stern_moulding_parts()}
    rail={n:s for n,s,_ in rails.make_rails()}
    helm={n:s for n,s,_ in deck.make_helm()}
    fits={n:s for n,s,_ in stern_fittings.make_stern_fittings()}
    supports={n:s for n,s,_ in hull_frames.make_support_parts()}
    for n,s in {**timbers,**rail,**helm,**fits,**supports,'deck':main,'upper':upper,'lower':lower}.items():
        assert s.isValid() and len(s.Solids())==1,('Invalid stern part',n)
    assert abs(sum(s.Volume() for s in timbers.values())-mould.Volume())<1e-4
    for s in (main,upper,lower):
        assert overlap(mould,s)<1e-5,'Moulding material duplicated in planking/deck'
    print('PASS: valid individual stern solids; separate moulding partition conserves timber without duplicate material.',flush=True)
    wood=[]
    for point in target['outer_wood_observations']+target['side_wood_observations']:
        x=point['across_ft']
        sections=[cross_section(s,x) for s in (main,mould)]
        bounds=[s.BoundingBox() for s in sections if s.Faces()]
        assert bounds,('No actual wood at observed X',x)
        actual=25-max(b.ymax for b in bounds)
        error=actual-point['forward_ft']
        wood.append(dict(X_ft=x,source_F_ft=point['forward_ft'],actual_F_ft=actual,error_inches=12*error))
    errors=np.array([p['error_inches'] for p in wood])
    rms=float(np.sqrt(np.mean(errors**2)))
    assert max(abs(errors))<=12*target['pick_uncertainty_ft'],('Wood source residual',wood)
    assert rms<=1.5,('Wood RMS exceeds1.5 in',rms)
    print(f'PASS: {len(wood)} independent raw wood controls: RMS {rms:.3f} in; max {max(abs(errors)):.3f} in.',flush=True)
    rail_errors=[]
    rear=sorted(target['rail_fastener_observations']+target['side_rail_observations'][:3],key=lambda p:p['across_ft'])
    for point in target['rail_fastener_observations']+target['side_rail_observations']:
        x=point['across_ft']
        name='Transom top rail' if abs(x)<=rails._turn_x+.001 else ('Port top rail' if x>0 else 'Starboard top rail')
        family=rear if name.startswith('Transom') else target['side_rail_observations']
        index=family.index(point)
        a=family[max(0,index-1)];b=family[min(len(family)-1,index+1)]
        normal=(b['across_ft']-a['across_ft'],a['forward_ft']-b['forward_ft'],0)
        f=point['forward_ft']
        z=hull.deck_height(f,x)+target['rail_heights']['top_ft']
        origin=cq.Vector(*boat_point(x,f,z))
        plane=cq.Face.makeFromWires(cq.Workplane(cq.Plane(origin=origin,normal=normal)).rect(250,60).val())
        section=rail[name].intersect(plane)
        assert section.Faces(),('No rail at observation',point)
        centre=min((face.Center() for face in section.Faces()),key=lambda p:(p-origin).Length)
        rail_errors.append(math.hypot(centre.x-origin.x,centre.y-origin.y)*12)
    rail_rms=float(np.sqrt(np.mean(np.array(rail_errors)**2)))
    assert max(abs(e) for e in rail_errors)<=2.4,('Rail control residuals',rail_errors)
    assert rail_rms<=1.5,('Rail RMS exceeds1.5 in',rail_rms)
    print(f'PASS: actual rectangular rails versus {len(rail_errors)} raw fastener controls, RMS {rail_rms:.3f} in.',flush=True)
    # Profile guides are raw observations; section material must meet them.
    profile=[]
    for p in target['counter']['guide_controls']:
        line=cq.Edge.makeLine(cq.Vector(0,40,p['Z_ft']),cq.Vector(0,-40,p['Z_ft']))
        section=hull.solid_envelope().intersect(line)
        actual=25-section.BoundingBox().ymax
        profile.append((actual-p['F_ft'])*12)
    assert max(abs(e) for e in profile)<2.4,('Counter source residual',profile)
    print('PASS: actual centreline counter meets independently picked profile guides.',flush=True)
    shell=[Contains(s) for s in (upper,lower,mould)]
    cavity=Contains(hull.continuous_interior())
    normal=math.sqrt(1+STERN_RAKE_FT_PER_FT**2)
    for x in (-3,0,3):
        for z in (5.8,6.4,6.8):
            # Source-guide interpolation, not the implementation helper.
            a,b=target['counter']['guide_controls']
            f=a['F_ft']+(a['Z_ft']-z)*(b['F_ft']-a['F_ft'])/(a['Z_ft']-b['Z_ft'])
            def p(d):return boat_point(x,f+d/normal,z+d*STERN_RAKE_FT_PER_FT/normal)
            assert any(s(p(INTERIOR_SKIN_FT/2)) for s in shell),('Missing counter skin',x,z)
            assert cavity(p(INTERIOR_SKIN_FT+.07)),('Filled counter cavity',x,z)
            assert not any(s(p(INTERIOR_SKIN_FT+.07)) for s in shell),('Excess counter thickness',x,z)
    print('PASS: nine source-referenced normal sections retain real counter skin and interior air.',flush=True)
    for name,post in rail.items():
        if 'stanchion' not in name:continue
        if 25-post.Center().y>14:continue
        assert overlap(post,main)+overlap(post,mould)>1e-7,('Floating aft rail post',name)
        top=rail['Transom top rail'] if name.startswith('Transom') else rail[name.split()[0]+' top rail']
        assert overlap(post,top)>1e-7,('Aft post misses top rail',name)
    for label in ('Port','Starboard'):
        assert rail[label+' top rail'].distance(rail['Transom top rail'])<.005,('Rail join gap',label)
    opening={n:s for n,s,_ in framing.make_opening_frames()}
    for name,s in supports.items():
        if name.startswith('Stern oak deck timber'):
            # The aftmost source timber bears on the transom framing/hull;
            # forward timbers also land on the side clamps.
            bearings=[t for n,t in opening.items() if n.endswith('clamp')]
            bearings += [t for n,t in supports.items()
                         if n.startswith('Transom oak fore-aft frame')]
            assert (sum(overlap(s,t) for t in bearings)>1e-6 or
                    overlap(s,upper)+overlap(s,lower)>1e-6),('Unseated stern beam',name)
        if name.startswith('Transom oak fore-aft frame'):
            assert sum(overlap(s,t) for t in (upper,lower,mould))>1e-7,('Unseated transom frame',name)
    print('PASS: aft posts bear on real wood; fair rail joins and source-stock stern deck timbers have real support.',flush=True)
    handoff=[]
    for f in (6,10,13.749,14.5,16,17.99,18.01,20):
        plane=cq.Face.makeFromWires(hull.section_plane(f).rect(30,30).val())
        sections=[s.intersect(plane) for s in (main,mould,rail['Port rubbing strake'],rail['Starboard rubbing strake'])]
        bounds=[s.BoundingBox() for s in sections if s.Faces()]
        handoff.append(dict(F_ft=f,port_halfwidth_ft=max(b.xmax for b in bounds),
                            starboard_halfwidth_ft=-min(b.xmin for b in bounds)))
    for side in ('port','starboard'):
        widths=[r[side+'_halfwidth_ft'] for r in handoff]
        assert min(np.diff(widths))>-.04,('Inward shoulder pinch at handoff',side,handoff)
    for label in ('Port','Starboard'):
        assert mould.distance(rail[label+' rubbing strake'])<.005,('Moulding/strake gap',label)
    print('PASS: actual port/starboard shoulder widths fair into the side stock with no material gap or marked inward pinch.',flush=True)
    for name,s in fits.items():
        if any(k in name for k in ('traveller foot','bearing foot','pivot pedestal','control pedestal')):
            assert overlap(s,main)+overlap(s,mould)>1e-7,('Floating stern fitting base',name)
    controls={n:s for n,s in fits.items() if 'control' in n or 'speaker' in n}
    for angle in (0,45,90):
        for name,door,_ in deck.make_companionway_doors(angle):
            for n,s in {**controls,'case':helm['Steering pedestal'],'wheel':helm['Helm wheel']}.items():
                assert overlap(door,s)<1e-7,('Stern operating-space door collision',angle,name,n)
    case=Contains(helm['Steering pedestal'])
    floor=hull.deck_height(HELM_FORWARD_FT)
    assert not case(boat_point(0,STERN_SOURCE['helm_box_fore_ft']-.04,floor+.35)),'Front opening closed'
    assert case(boat_point(0,STERN_SOURCE['helm_box_fore_ft']-.04,floor+1.05)),'Front header missing'
    lids=[s for n,s in helm.items() if n.startswith('Helm lid timber')]
    for name,s in helm.items():
        if any(k in name.lower() for k in ('hydraulic','ram barrel','ram polished','uni-flo','tiller link','helm pump')):
            assert all(overlap(s,lid)<1e-7 for lid in lids),('Mechanism hits closed lid',name)
    moving=hull.make_rudder().fuse(hull.make_steering_shaft())
    fixed={**supports,**rail,**fits,'upper':upper,'lower':lower,'deck':main,'mould':mould,
           'case':helm['Steering pedestal'],'boxing':interior.make_rudder_box()}
    for angle in (-35,0,35):
        moved=moving.rotate(hull.rudder_axis_point(hull._blade_bottom_z),hull.rudder_axis_point(hull._head_z),angle)
        for name,s in fixed.items():
            assert overlap(moved,s)<1e-7,('Steering collision',angle,name)
    print('PASS: real front opening/header, closed-lid mechanism clearance and -35/0/+35-degree stern steering.',flush=True)
    return dict(status='passed',wood_controls=wood,wood_rms_inches=rms,
                rail_control_errors_inches=rail_errors,rail_rms_inches=rail_rms,quarter_handoff=handoff,
                counter_profile_errors_inches=profile,source=target['source_sha256'],
                photo_dimensions='Qualitative only; unprinted fitting sections and hidden joints remain inferred.',
                acceptance_scope='Source and geometry checks; rendered/photo appearance review also required.')


if __name__=='__main__':
    result=check()
    (ROOT/'checks/stern_remedy_acceptance.json').write_text(json.dumps(result,indent=2)+'\n')
