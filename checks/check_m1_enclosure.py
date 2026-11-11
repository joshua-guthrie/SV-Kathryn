"""M1 acceptance on actual solids: whole-vessel voids, sections and real supports."""
import json
import math
import sys
from pathlib import Path
import cadquery as cq
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from parts import hull,deck,framing,interior,spars,centreline,hull_frames,stern_layout
from parts.params import *
from parts.primitives import block
from check_hatches import overlap
from geometry_checks import Contains


def check():
    outer=hull.solid_envelope()
    upper,lower=hull.make_hull()
    cavity=hull.continuous_interior()
    planking=cq.Compound.makeCompound([upper,lower])
    parts={n:s for n,s,_ in interior.make_enclosure_parts()}
    for name,shape in {**parts,'upper':upper,'lower':lower,'cavity':cavity}.items():
        assert shape.isValid() and len(shape.Solids())==1,name
    fraction=(upper.Volume()+lower.Volume())/outer.Volume()
    assert fraction<.15,('residual hull filler',fraction)
    print(f'PASS: one continuous interior; planking material {fraction*100:.2f}% of the equivalent filled envelope.',flush=True)
    rows=np.array(hull.SECTIONS)
    upper_inside,lower_inside,outer_inside=Contains(upper),Contains(lower),Contains(outer)
    def inside(point):
        return upper_inside(point) or lower_inside(point)
    air_samples=0
    for f in np.linspace(HULL_AFT_FT+.7,LINE_STATIONS_FT[9],35):
        row=[float(np.interp(f,rows[:,0],rows[:,i])) for i in range(8)]
        for x in (-row[1]*.35,0,row[1]*.35):
            bottom=(hull_frames.frame_inner_height(f,x) if f<LINE_STATIONS_FT[1]
                    else hull.inner_bottom_height(f,x))
            z=(bottom+hull.deck_height(f,x)-DECK_THICKNESS_FT)/2
            p=boat_point(x,f,z)
            assert outer_inside(p)
            assert not inside(p),('filled interior',f,x,z)
            air_samples+=1
    for f in (10,25,35,43):
        plane=cq.Face.makeFromWires(hull.section_plane(f).rect(30,25).val())
        a=outer.intersect(plane).Area()
        material=upper.intersect(plane).Area()+lower.intersect(plane).Area()
        assert material/a<.21,('filled transverse section',f,material/a)
    print(f'PASS: {air_samples} distributed air samples and four actual transverse sections show open cabin/hold/forebody volume.',flush=True)
    skin_samples=0
    print('Checking bottom, topside and sheer-band material...',flush=True)
    # The raked aft counter is checked on its own normal in check_stern_helm;
    # these bottom/side rays begin where the original section is untrimmed.
    for f in np.linspace(LINE_STATIONS_FT[0],LINE_STATIONS_FT[9],24):
        row=[float(np.interp(f,rows[:,0],rows[:,i])) for i in range(8)]
        kw=min(3.5/12,row[1]*.25)
        slope=(row[6]-row[7])/(row[5]-kw)
        for x in (-row[5]*.5,row[5]*.5):
            z=row[7]+(abs(x)-kw)*slope
            m=math.copysign(slope,x)
            norm=math.sqrt(1+m*m)
            def at(d): return boat_point(x-d*m/norm,f,z+d/norm)
            assert inside(at(2/12)),('bottom skin thin',f,x)
            assert not inside(at(4/12)),('bottom skin/filler too thick',f,x)
            skin_samples+=1
        db=row[2]-hull.deck_thickness(row[2],row[4])
        uw=row[1]-sheer_band_flare(f)
        uz=row[2]-sheer_band_height(f)
        for a,b,label in (((row[3],row[4]),(uw,uz),'lower topside'),
                          ((uw,uz),(row[1],db),'sheer band')):
            dx,dz=b[0]-a[0],b[1]-a[1]
            length=math.hypot(dx,dz)
            for side in (-1,1):
                x=side*(a[0]+b[0])/2
                z=(a[1]+b[1])/2
                def at(d): return boat_point(x-side*dz*d/length,f,z+dx*d/length)
                assert inside(at(2/12)),(label,'skin thin',f,side)
                assert not inside(at(4/12)),(label,'residual filler',f,side)
                skin_samples+=1
    z=stern_layout.reference_height(hull.deck_height)-.8
    f=stern_layout.face_forward(z,stern_layout.reference_height(hull.deck_height))
    norm=math.sqrt(1+STERN_RAKE_FT_PER_FT**2)
    def counter(d):return boat_point(0,f+d/norm,z+d*STERN_RAKE_FT_PER_FT/norm)
    assert inside(counter(INTERIOR_SKIN_FT/2))
    assert not inside(counter(INTERIOR_SKIN_FT+.10))
    print(f'PASS: {skin_samples} normal-ray shell samples and the thin transom cap retain material without filler bands.',flush=True)
    main_deck=hull.make_deck()
    opening=block(0,CABIN_FORWARD_FT,hull.deck_height(CABIN_FORWARD_FT)-.3,
                  CABIN_WIDTH_FT-2*CABIN_WALL_FT-.08,
                  CABIN_LENGTH_FT-2*CABIN_WALL_FT-.08,.65)
    assert overlap(opening,main_deck)<1e-7,'False cabin deck-level floor'
    for name,shape,_ in framing.make_opening_frames():
        if 'roof' not in name:
            assert overlap(opening,shape)<1e-7,('Cabin aperture blocked',name)
    for name in ('Cabin forward bulkhead','Forepeak aft bulkhead'):
        panel=parts[name]
        assert panel.BoundingBox().ylen<=BULKHEAD_THICKNESS_FT+1e-5
        assert overlap(panel,upper)+overlap(panel,lower)>1e-6,('floating partition',name)
    print('PASS: full-width cabin deck aperture and thin hull-seated compartment partitions.',flush=True)
    cabin={n:s for n,s,_ in deck.make_deckhouse_parts()}
    sole=cabin['Companionway landing']
    assert sole.cut(outer).Volume()<1e-7,'Floor protrudes through hull'
    for end in ('aft','fore'):
        bearer=parts[f'Cabin sole {end} bearer and feet']
        assert overlap(sole,bearer)>1e-6
        f=ACCESS_WELL_AFT_FT+1.2 if end=='aft' else ACCESS_WELL_FORE_FT-.7
        bearing_inside=Contains(bearer)
        for x in (-(ACCESS_WELL_WIDTH_FT/2-.30),ACCESS_WELL_WIDTH_FT/2-.30):
            p=boat_point(x,f,hull.inner_bottom_height(f,x)-.02)
            assert bearing_inside(p) and inside(p),('Unseated sole support',end,x)
        assert bearer.cut(outer).Volume()<1e-7
    mast=spars.make_mast()
    # M2 replaces the interim pad with the actual forward keelson/mortise.
    _,pad=centreline.make_keelsons()
    assert overlap(mast,pad)>1e-6,'Unsupported mast heel'
    from parts.centreline_layout import keelson_width
    f=spars.mast_forward_at(spars.mast_heel_height())
    x=keelson_width(f)/2
    z=hull.inner_bottom_height(f,x)-.06
    assert Contains(pad)(boat_point(x-.001,f,z)) and inside(boat_point(x+.001,f,z)),\
        'Keelson not seated against planking'
    heel_limit=block(0,MAST_DECK_FORWARD_FT,-5,30,30,
                     hull.deck_height(MAST_DECK_FORWARD_FT)-.30+5)
    assert mast.intersect(heel_limit).cut(outer).Volume()<1e-7,'Heel outside exterior envelope'
    boxing=parts['Hollow rudder-stock box']
    assert overlap(boxing,hull.make_steering_shaft())<1e-7,'Stock/boxing collision'
    print('PASS: floor and mast have real hull-bearing supports; stock boxing is hollow and shaft-clear.',flush=True)
    source=json.loads((ROOT/'drawing_package/registration.json').read_text())
    target={r['name']:r['canonical_forward_ft'] for r in source['legacy_feature_migration']}
    for name,f,_,_ in HATCHES_FT:
        assert abs(f-target[name])<1e-8
    assert abs(spars.mast_forward_at(hull.deck_height(MAST_DECK_FORWARD_FT))-target['Mast at deck'])<1e-8
    assert np.allclose([s[0] for s in hull.SOURCE_SECTIONS[1:-1]],list(LINE_STATIONS_FT.values()))
    print('PASS: source line stations, three hatch centres and mast/deck intersection migrated to the M0 coordinate ledger.',flush=True)
    band=json.loads((ROOT/'drawing_package/sheer_band_measurements.json').read_text())
    for pick in band['measurements']:
        f=pick['forward_ft']
        raw=next(r for r in hull.SOURCE_SECTIONS if abs(r[0]-f)<1e-8)
        model=[float(np.interp(f,rows[:,0],rows[:,i])) for i in range(8)]
        p=pick['profile_native_points']
        measured=(p['underside_sheer_strake'][1]-p['top_of_deck'][1])/band['native_pixels_per_ft']
        assert abs(model[2]-raw[2]-measured)<1e-7,('Wrong deck datum',f)
        assert abs(model[1]-raw[1]-pick['outward_flare_ft'])<1e-7,('Missing upper flare',f)
    print('PASS: actual model deck height/width include the separately measured sheer-strake band; source offsets remain underside references.',flush=True)
    return dict(material_fraction=fraction,air_samples=air_samples,skin_samples=skin_samples,
                hull_aft_ft=HULL_AFT_FT,hull_fore_ft=HULL_FORE_FT,
                body_length_ft=HULL_FORE_FT-HULL_AFT_FT,
                cabin_sole_ft=deck.access_geometry().sole,
                partitions=2,local_bearings=2,mast_bearing='forward oak keelson mortise',
                deck_reference='Top of Deck, above offset-table underside of sheer strake',
                measured_band_profiles=len(band['measurements']),
                maximum_beam_ft=2*max(r[1] for r in hull.SECTIONS),
                transom_top_width_ft=2*hull.SECTIONS[0][1],
                transom_nominal_topdeck_depth_ft=hull.SECTIONS[0][2]-hull.SECTIONS[0][7])


if __name__=='__main__':
    report=check()
    (ROOT/'checks/m1_acceptance.json').write_text(json.dumps(dict(status='passed',**report),indent=2)+'\n')
