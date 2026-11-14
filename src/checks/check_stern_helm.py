"""Drawing-governed stern/helm correction, closure, support and steering checks."""
import json
import math
import sys
from pathlib import Path
import cadquery as cq
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from parts import hull,deck,rails,stern_layout,hull_frames,interior
from parts.params import *
from geometry_checks import Contains
from check_hatches import overlap


def check():
    upper,lower=hull.make_hull()
    main_deck=hull.make_deck()
    helm={n:s for n,s,_ in deck.make_helm()}
    aft={n:s for n,s,_ in hull_frames.make_support_parts() if n.startswith('Transom') or 'transom oak' in n}
    rail={n:s for n,s,_ in rails.make_rails()}
    for name,shape in {**helm,**aft,**rail,'upper':upper,'lower':lower,'deck':main_deck}.items():
        assert shape.isValid() and len(shape.Solids())==1,name
    box=helm['Steering pedestal'].BoundingBox()
    assert abs(25-box.ymax-STERN_SOURCE['helm_box_aft_ft'])<1e-5
    assert abs(25-box.ymin-STERN_SOURCE['helm_box_fore_ft'])<1e-5
    assert abs(box.xlen-HELM_BOX_WIDTH_FT)<1e-5
    assert abs(25-helm['Helm wheel'].Center().y-HELM_WHEEL_FORWARD_FT)<.05
    gap=STERN_SOURCE['helm_box_aft_ft']-STERN_SOURCE['rear_rail_centre_ft']
    assert 1.2<gap<1.7
    print(f'PASS: measured S04 box faces, wheel and separate stock position; aft box-to-rail gap {gap:.3f} ft.',flush=True)
    shell=[Contains(s) for s in (upper,lower)]
    cavity=Contains(hull.continuous_interior())
    reference=stern_layout.reference_height(hull.deck_height)
    normal=math.sqrt(1+STERN_RAKE_FT_PER_FT**2)
    samples=0
    for x in (-3,0,3):
        for z in (5.8,6.4,7.0):
            f=stern_layout.face_forward(z,reference)
            def p(d):return boat_point(x,f+d/normal,z+d*STERN_RAKE_FT_PER_FT/normal)
            assert any(test(p(INTERIOR_SKIN_FT/2)) for test in shell),('Missing raked counter planking',x,z)
            assert cavity(p(INTERIOR_SKIN_FT+.07)),('Counter filled/thick',x,z)
            assert not any(test(p(INTERIOR_SKIN_FT+.07)) for test in shell)
            samples+=1
    for x in (-2.5,0,2.5):
        assert not any(test(boat_point(x,HULL_AFT_FT+.3,5.8)) for test in shell),'Old vertical lower stern remains'
    print(f'PASS: {samples} normal counter sections retain real thickness and open interior; old vertical lower extension removed.',flush=True)
    fixed={**aft,**rail,'upper':upper,'lower':lower,'deck':main_deck,
           'pedestal':helm['Steering pedestal'],'boxing':interior.make_rudder_box(),
           'keel':hull.make_keel(),'shoe':hull.make_worm_shoe(),'skeg':hull.make_skeg()}
    fixed.update(dict(hull.make_rudder_fittings()))
    moving=hull.make_rudder().fuse(hull.make_steering_shaft())
    for angle in (-35,0,35):
        shape=moving.rotate(hull.rudder_axis_point(hull._blade_bottom_z),hull.rudder_axis_point(hull._head_z),angle)
        for name,obstacle in fixed.items():
            assert overlap(shape,obstacle)<1e-7,('Stern steering collision',angle,name)
    assert overlap(helm['Wheel shaft'],helm['Steering pedestal'])<1e-7,'Wheel shaft lacks a real case bore'
    for i in range(1,4):
        assert overlap(helm[f'Helm lid timber {i}'],helm['Steering pedestal'])>1e-6
        assert overlap(helm[f'Helm lid timber {i}'],moving)<1e-7
    print('PASS: corrected counter/frames/boxing clear -35/0/+35-degree steering; axle bore and individual lid timbers fit.',flush=True)
    moulding=hull.stern_moulding()
    for i in range(1,4):
        post=rail[f'Transom stanchion {i}']
        # Inset stern posts land on the stern moulding (post 1 also grazes
        # the deck edge); the moulding is the accepted wood bearing.
        assert overlap(post,main_deck)+overlap(post,moulding)>1e-7,('Rear rail post floats',i)
        assert overlap(post,rail['Transom top rail'])>1e-7
    for label in ('Port','Starboard'):
        assert rail[f'{label} top rail'].distance(rail['Transom top rail'])<.01
    print('PASS: inset bowed stern rails have actual deck-supported posts and meet side rails.',flush=True)
    return dict(status='passed',box_aft_ft=STERN_SOURCE['helm_box_aft_ft'],box_fore_ft=STERN_SOURCE['helm_box_fore_ft'],
                box_to_rear_rail_gap_ft=gap,counter_forward_per_vertical_ft=STERN_RAKE_FT_PER_FT,
                counter_normal_checks=samples,source='references/drawing_package/stern_helm_registration.json',
                photo_cross_checks=['LOC-P28','LOC-P29','LOC-P30'],model_scale=MODEL_SCALE,
                expected_body_length_mm=(HULL_FORE_FT-HULL_AFT_FT)*MODEL_MM_PER_FOOT)


if __name__=='__main__':
    result=check()
    (ROOT/'src/checks/stern_helm_acceptance.json').write_text(json.dumps(result,indent=2)+'\n')
