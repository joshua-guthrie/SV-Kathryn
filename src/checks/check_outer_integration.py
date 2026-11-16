"""Exterior/steering regressions after M1's source datum and hollow-shell change."""
import sys
from pathlib import Path
import cadquery as cq
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from parts import bow,hull,spars,rails,deck,interior,equipment
from parts.params import *
from check_hatches import overlap


def check():
    upper,lower=hull.make_hull()
    body=cq.Compound.makeCompound([upper,lower])
    parts={n:s for n,s,_ in spars.make_spars()}
    from check_bow_attachment import check as check_bow
    check_bow(out=None)
    assert overlap(parts['Boom gooseneck'],parts['Main boom'])>1e-7
    assert overlap(parts['Boom support'],hull.make_deck())>1e-8
    moulding=hull.stern_moulding()
    for side in (-1,1):
        strake=rails.make_rubbing_strake(side)
        assert strake.isValid() and len(strake.Solids())==1
        # The aft shoulder hands off from the hull planking to the separate
        # stern moulding; check that joint directly, then sample the body.
        assert moulding.distance(strake)<.005,('strake/moulding handoff',side)
        for old in (25,38,43,47,49):
            f=legacy_forward(old)
            w=float(np.interp(f,[s[0] for s in hull.SECTIONS],[s[1] for s in hull.SECTIONS]))
            sheer=float(np.interp(f,[s[0] for s in hull.SECTIONS],[s[2] for s in hull.SECTIONS]))
            z=sheer-.38*min(1,w/1.25)
            x=side*(hull.topside_halfwidth(f,z)-.015*min(1,max(.12,w/.7)))
            p=cq.Vector(*boat_point(x,f,z))
            assert upper.isInside(p,1e-5) or lower.isInside(p,1e-5),('strake/planking',side,f)
            assert strake.isInside(p,1e-5)
    print('PASS: full housed bow, fitted facing boards, pivoted tack, stay alignment and downhaul checks.',flush=True)
    keel,shoe,deadwood=hull.make_keel(),hull.make_worm_shoe(),hull.make_skeg()
    assert overlap(keel,shoe)>1e-6 and overlap(keel,deadwood)>1e-6
    for f in (STERN_DEADWOOD_END_FT,28,30,32,34.375,38.75,40.9375,43.125):
        face=cq.Face.makeFromWires(hull.section_plane(f).rect(20,30).val())
        assert abs(hull.rabbet_height(f)-shoe.intersect(face).BoundingBox().zmin-.75)<1e-5
    moving=hull.make_rudder().fuse(hull.make_steering_shaft())
    assert moving.isValid() and len(moving.Solids())==1
    fixed=dict(upper=upper,lower=lower,deck=hull.make_deck(),keel=keel,
               shoe=shoe,deadwood=deadwood,boxing=interior.make_rudder_box())
    fixed.update(dict(hull.make_rudder_fittings()))
    fixed.update({n:s for n,s,_ in deck.make_helm() if n!='Steering shaft'})
    for angle in (-35,0,35):
        turned=moving.rotate(hull.rudder_axis_point(hull._blade_bottom_z),
                            hull.rudder_axis_point(hull._head_z),angle)
        for name,shape in fixed.items():
            assert overlap(turned,shape)<1e-7,('steering collision',angle,name)
    print('PASS: body keel/shoe depth, stern contacts and -35/0/+35 steering including the new hollow stock box.',flush=True)
    machinery={n:s for n,s,_ in equipment.make_equipment()}
    engine=machinery['Winder engine cover'].fuse(machinery['Engine cover top'])
    frame=machinery['Dredge winder frame']
    for label in ('Port','Starboard'):
        drum=machinery[f'{label} winder drum']
        wheel=machinery[f'{label} winder drive wheel']
        skid=machinery[f'{label} winder skid']
        brake=machinery[f'{label} winder brake and lever']
        clutch=machinery[f'{label} winder clutch control']
        assert overlap(frame,skid)>1e-6
        assert overlap(wheel,drum)>1e-6
        assert overlap(brake,skid)>1e-7
        for obj in (wheel,brake,clutch):
            assert overlap(obj,engine)<1e-7,('engine/control collision',label)
        for end in ('aft','fore'):
            bearing=machinery[f'{label} {end} winder bearing']
            assert overlap(bearing,frame)>1e-7
            assert overlap(bearing,drum)<1e-7
            assert overlap(bearing,wheel)<1e-7
    print('PASS: migrated machinery frame/skids, wheel/axle and bearing contacts; controls clear the source-sized hollow engine housing.',flush=True)


if __name__=='__main__':
    check()
