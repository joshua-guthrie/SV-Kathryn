"""Actual M3 frame material, source registration, joint/support and void checks."""
import json
import sys
from pathlib import Path
import numpy as np
import cadquery as cq

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from parts import deck_beams,hull,hull_frames as hf,frame_layout as schedule,centreline,centreline_layout as cl,framing,deck,spars
from parts.params import *
from geometry_checks import Contains
from check_hatches import overlap


def inner_z(f,x):
    points=[v.Center() for v in hf.frame_profile(f).Vertices()]
    points=sorted([(p.x,p.z) for p in points if p.x>=-1e-7 and p.z<hull.deck_height(f)-.15])
    return float(np.interp(abs(x),[p[0] for p in points],[p[1] for p in points]))


def check():
    frames={n:s for n,s,_ in hf.make_frame_parts()}
    supports={n:s for n,s,_ in hf.make_support_parts()}
    beams={n:s for n,s,_ in deck_beams.make_deck_beam_parts()}
    all_parts={**frames,**supports,**beams}
    for name,shape in all_parts.items():
        assert shape.isValid() and len(shape.Solids())==1,name
    print(f'PASS: {len(frames)} individual frame pieces plus {len(supports)} supports are valid single solids.',flush=True)
    rows=schedule.MEMBERS
    assert set(r['set'] for r in rows if isinstance(r['set'],int))==set(range(1,21))
    primary={r['set']:r for r in rows if r['side']==1 and r['role']=='primary' and isinstance(r['set'],int)}
    assert primary[4]['forward_ft']>primary[5]['forward_ft']>MAST_DECK_FORWARD_FT
    assert primary[13]['forward_ft']>WINCH_FORWARD_FT
    assert primary[20]['forward_ft']<KEELSON_SCARF_AFT_FT<KEELSON_SCARF_FORE_FT<primary[15]['forward_ft']
    assert len({round(r['sided_ft'],4) for r in rows})>15,'Substituted uniform beam stock'
    assert all(r['age']=='older, possibly original' for r in rows if r['older_graphic'])
    print('PASS: independent hull-frame numbering agrees with mast/winder/scarf evidence; irregular sided stock and qualified ages retained.',flush=True)
    for row in rows:
        if row['role']!='repair-pattern':continue
        shape=frames[hf.label(row)+' bottom and chine knee']
        assert any(e.geomType()=='CIRCLE' and e.radius()>.049 for e in shape.Edges()),('Unrounded replacement knee',row['id'])
    outer=Contains(hull.solid_envelope())
    shell=[Contains(s) for s in hull.make_hull()]
    timber={n:Contains(s) for n,s in all_parts.items()}
    keelsons=[Contains(s) for s in centreline.make_keelsons()]
    outside=[]
    exterior_samples=0
    for name,shape in all_parts.items():
        if 'stanchion' in name.lower() or 'strongback' in name.lower() or 'supporting deck beam' in name:continue
        samples={}
        for edge in shape.Edges():
            points=[edge.startPoint(),edge.endPoint()]
            if edge.Length()>.15:points.append(edge.positionAt(.5))
            for p in points:samples[tuple(round(v,7) for v in (p.x,p.y,p.z))]=p
        for p in samples.values():
                f=25-p.y
                if p.z>hull.deck_height(f,p.x)-DECK_THICKNESS_FT-.025:continue # Head/deck bearing.
                exterior_samples+=1
                if not outer((p.x,p.y,p.z)):
                    outside.append((name,tuple(round(v,4) for v in (p.x,f,p.z))))
    assert not outside,('Frame/support protrudes outside exterior',outside[:20],len(outside))
    print(f'PASS: {exterior_samples} distinct frame/support samples remain within the accepted exterior, including fine bow bevels.',flush=True)
    missing=[]
    limbers=0
    for row in rows:
        f,side=row['forward_ft'],row['side']
        name=hf.label(row)
        bottom_name=(f'F{row["set"]:02d} continuous oak floor under keelson'
                     if row['keelson_joint']=='underpass' else name+' bottom and chine knee')
        bottom=timber[bottom_name]
        side_shape=frames[hf.side_label(row)]
        bb=frames[bottom_name].BoundingBox()
        lo,hi=(bb.xmin,bb.xmax) if side>0 else (-bb.xmax,-bb.xmin)
        probes=[side*(lo+(hi-lo)*t) for t in (.30,.55,.80)]
        if not any(bottom(boat_point(x,f,inner_z(f,x)+d)) and any(test(boat_point(x,f,inner_z(f,x)+d)) for test in shell)
                   for x in probes for d in (-.014,-.008,0,.008,.014)):
            missing.append((row['id'],'bottom shell seating'))
        # Classified physical timber on either side of the small drainage notch.
        xhole=side*(cl.keelson_width(f)/2+.35)
        zhole=hf.frame_inner_height(f,xhole) if f<STERN_BLEND_END_FT else hull.inner_bottom_height(f,xhole)
        p=boat_point(xhole,f,zhole+.04)
        assert not bottom(p),('Closed limber notch',row['id'])
        limbers+=1
        if row['keelson_joint']=='mortised':
            xjoint=side*(cl.keelson_width(f)/2-FRAME_TENON_FT/2)
            zjoint=inner_z(f,xjoint)+.10
            p=boat_point(xjoint,f,zjoint)
            assert bottom(p),('Missing tenon',row['id'])
            assert not any(test(p) for test in keelsons),('Uncut frame mortise',row['id'])
        if row['role']=='repair-pattern':
            p=boat_point(side*(cl.keelson_width(f)/2-.025),f,inner_z(f,cl.keelson_width(f)/2)+.10)
            assert not bottom(p),('Replacement incorrectly inletted',row['id'])
        assert overlap(side_shape,frames[bottom_name])<.02,('Excessive chine joint overlap',row['id'])
        assert side_shape.distance(frames[bottom_name])<.02,('Disconnected chine joint',row['id'])
    assert not missing,('Unseated frame material',missing)
    print(f'PASS: all bottom members seat on planking; {limbers} limber notches are open; primary tenons and uninletted repairs are distinct.',flush=True)
    for row in schedule.underpass_rows():
        f=row['forward_ft']
        z=inner_z(f,0)
        floor=timber[f'F{row["set"]:02d} continuous oak floor under keelson']
        assert floor(boat_point(0,f,z+.12))
        assert not any(test(boat_point(0,f,z+.12)) for test in keelsons)
        assert any(test(boat_point(0,f,z-.05)) for test in shell),'Planking missing under underpass floor'
    print('PASS: F19/F20 cross continuously below the keelson, with actual bottom planking retained beneath.',flush=True)
    opening_parts={n:s for n,s,_ in framing.make_opening_frames()}
    clamps={n:s for n,s in opening_parts.items() if n.endswith('clamp')}
    unsupported=[]
    for row in rows:
        shape=frames[hf.side_label(row)]
        side_name='port' if row['side']>0 else 'starboard'
        candidates=[s for n,s in clamps.items() if side_name in n]
        if not any(overlap(shape,s)>1e-7 for s in candidates):unsupported.append(row['id'])
    assert not unsupported,('Frame heads not seated to clamps',unsupported)
    print('PASS: every individual side-frame head seats against a continuous pine clamp; forward oak reinforcement is separate.',flush=True)
    for i in range(1,4):
        post=supports[f'Hold oak stanchion {i}']
        f=schedule.source_plan_forward(schedule.SOURCE['supports']['stanchion_plan_preview_x'][i-1])
        name,_,new=hf.stanchion_beam(i,f)
        beam=supports[name] if new else {**opening_parts,**beams}[name]
        assert overlap(post,beam)>1e-6
        assert any(overlap(post,s)>1e-6 for s in centreline.make_keelsons())
    knee=supports['Oak stem knee with Samson-post mortise']
    post=deck.make_bow_post()
    assert post.isValid() and len(post.Solids())==1
    assert overlap(knee,post)>1e-6
    assert overlap(knee,post)<.02
    assert overlap(post,hull.make_deck())<1e-7,'Post/deck passage closed'
    assert overlap(post,spars.make_bowsprit())<1e-7,'Post crown/bowsprit collision'
    assert post.BoundingBox().ymin>spars.make_bowsprit().BoundingBox().ymax,'Bowsprit heel still extends aft through Samson post'
    assert overlap(supports['Aft composite pine strongback top'],supports['Aft composite pine strongback lower'])>1e-6
    print('PASS: stanchions have real keelson/beam seats; strongback components join; Samson post enters the stem-knee mortise through open deck.',flush=True)
    for angle in np.linspace(0,CENTREBOARD_ANGLE_DEG,5):
        board=cl.make_board(float(angle))
        for name,shape in all_parts.items():
            assert overlap(board,shape)<1e-7,('New member fouls board',angle,name)
    steering=hull.make_rudder().fuse(hull.make_steering_shaft())
    for angle in (-35,0,35):
        moved=steering.rotate(hull.rudder_axis_point(hull._blade_bottom_z),hull.rudder_axis_point(hull._head_z),angle)
        for name,shape in all_parts.items():
            assert overlap(moved,shape)<1e-7,('New member fouls steering',angle,name)
    # Bay samples deliberately lie between actual frame planes, rather than
    # treating a legitimately placed structural timber as residual filler.
    air=0
    planes=sorted(set(round(r['forward_ft'],5) for r in rows))
    for a,b in zip(planes[:-1],planes[1:]):
        if b-a<.75:continue
        f=(a+b)/2
        for side in (-1,1):
            x=side*2
            z=(hull.inner_bottom_height(f,x)+hull.deck_height(f,x)-.5)/2
            p=boat_point(x,f,z)
            assert not any(test(p) for test in timber.values()),('Filled frame bay',f,x,z)
            air+=1
    print(f'PASS: new structure clears five board poses; {air} bay samples retain genuine interior space.',flush=True)
    return dict(status='passed',frame_pieces=len(frames),support_parts=len(supports),
                half_frame_members=len(rows),repair_pattern_additions=sum(r['role']=='repair-pattern' for r in rows),
                limbers=limbers,air_samples=air,exterior_violations=0,
                source='drawing_package/m3_frame_schedule.json',
                unresolved=['inaccessible cabin and two aft planes','individual repair dates','fine laps and hidden head shapes'])


if __name__=='__main__':
    report=check()
    (ROOT/'checks/m3_acceptance.json').write_text(json.dumps(report,indent=2)+'\n')
