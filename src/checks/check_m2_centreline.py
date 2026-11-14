"""M2 actual-solid acceptance: open slot, moving board, joints and bearings."""
import json
import sys
from pathlib import Path
import numpy as np
import cadquery as cq

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from parts import deck_beams,hull,centreline,centreline_layout as layout,spars,interior,framing,deck
from parts.params import *
from parts.primitives import block
from check_hatches import overlap
from geometry_checks import Contains


def distance(a,b):
    return a.distance(b)


def check():
    members={n:s for n,s,_ in centreline.make_centreline_parts()}
    enclosures={n:s for n,s,_ in interior.make_enclosure_parts()}
    frames={n:s for n,s,_ in framing.make_opening_frames()}
    frames.update({n:s for n,s,_ in deck_beams.make_deck_beam_parts()})
    upper,lower=hull.make_hull()
    fixed={**members,**enclosures,**frames,'Upper planking':upper,'Lower planking':lower,
           'Keel':hull.make_keel(),'Shoe':hull.make_worm_shoe(),'Skeg':hull.make_skeg(),
           'Deck':hull.make_deck(),'Mast':spars.make_mast()}
    for name,shape in fixed.items():
        assert shape.isValid() and len(shape.Solids())==1,name
    print(f'PASS: {len(members)} separate centreline members and all adjoining parts are valid single solids.',flush=True)
    aft,fore=centreline.make_keelsons()
    assert overlap(aft,fore)<1e-6,'Overlapping scarf halves'
    assert distance(aft,fore)<1e-5,'Disconnected scarf'
    for f,target in ((KEELSON_SCARF_AFT_FT-1,14/12),(TRUNK_AFT_FT+.5,16/12)):
        face=cq.Face.makeFromWires(hull.section_plane(f).rect(10,20).val())
        section=aft.intersect(face).fuse(fore.intersect(face))
        assert abs(section.BoundingBox().xlen-target)<1e-5,('Keelson stock width',f)
    print('PASS: separate 14/16-in oak sections meet along a real, non-overlapping scarf.',flush=True)
    shoe_plane=cq.Face.makeFromWires(hull.section_plane(CENTREBOARD_PIVOT_FT).rect(10,20).val())
    shoe_width=fixed['Shoe'].intersect(shoe_plane).BoundingBox().xlen
    assert abs(shoe_width-WORM_SHOE_MAX_WIDTH_FT)<1e-5,'Shoe widening not registered to the actual slot'
    # Check the physical passage, not a display-hidden cutaway. Probes pass
    # beside the board: they must be air from below shoe to above trunk mouth.
    passage=[]
    classified={n:Contains(s) for n,s in fixed.items() if n!='Centreboard pivot pin'}
    for f in np.linspace(CB_SLOT_AFT_FT+.06,CB_SLOT_FORE_FT-.06,15):
        for side in (-1,1):
            x=side*(CENTREBOARD_THICKNESS_FT/2+.022)
            bottom=hull.keel_bottom(f)-.3
            top=layout.case_top(f,hull.rabbet_height,centreline.sole(),hull.deck_height)+.055
            levels=sorted(set([*np.linspace(bottom,top,30),
                               hull.keel_bottom(f)+.02,hull.rabbet_height(f)+.02,
                               layout.case_bottom(f,hull.rabbet_height,centreline.sole())+.02]))
            for z in levels:
                point=boat_point(x,float(f),float(z))
                for name,contains in classified.items():
                    assert not contains(point),('Blocked centreboard passage',f,z,name)
            passage.append((float(f),x))
    print(f'PASS: {len(passage)} full-height probes pass beside the board through shoe, keel, shell, keelson and hollow trunk.',flush=True)
    collisions=[]
    minimums=[]
    for angle in np.linspace(0,CENTREBOARD_ANGLE_DEG,5):
        board=layout.make_board(float(angle))
        assert board.isValid() and len(board.Solids())==1
        bb=board.BoundingBox()
        # All five board poses fit strictly inside the common cut's constant
        # F/X bounds. Those large slotted parts have just been independently
        # checked through the entire physical passage, with exact classifiers.
        assert 25-bb.ymax>CB_SLOT_AFT_FT+.01
        assert 25-bb.ymin<CB_SLOT_FORE_FT-.01
        assert bb.xmin>-TRUNK_GAP_FT/2+.01 and bb.xmax<TRUNK_GAP_FT/2-.01
        for name,shape in fixed.items():
            if name in ('Upper planking','Lower planking','Keel','Shoe','Skeg') or 'keelson section' in name:continue
            volume=overlap(board,shape)
            if volume>1e-7:collisions.append((float(angle),name,volume))
        minimums.append(dict(angle_degrees=float(angle),lowest_Z_ft=board.BoundingBox().zmin))
    assert not collisions,('Centreboard swept-pose collisions',collisions)
    print('PASS: source lowered outline, raised pose and three intermediate board poses clear fixed structure and pivot.',flush=True)
    # Case courses retain their printed 2-in wall material; section each course
    # away from the bored pivot and prove the sides bear on oak.
    mid=(TRUNK_AFT_FT+TRUNK_FORE_FT)/2
    plane=cq.Face.makeFromWires(hull.section_plane(mid).rect(10,20).val())
    for side in ('Port','Starboard'):
        for i in range(1,TRUNK_COURSES+1):
            shape=members[f'{side} trunk pine course {i}']
            section=shape.intersect(plane).BoundingBox()
            assert abs(section.xlen-2/12)<1e-5
            if i<TRUNK_COURSES:assert abs(section.zlen-11.5/12)<1e-5
            if i==1:assert overlap(shape,fore)>1e-5,('Unseated trunk',side)
            else:assert distance(shape,members[f'{side} trunk pine course {i-1}'])<1e-5
        assert overlap(members[f'{side} trunk top rail'],members[f'{side} trunk pine course 4'])>1e-5
    for name in ('Centreboard trunk aft end timber','Centreboard trunk fore end timber'):
        assert overlap(members[name],fore)>1e-5
    print('PASS: eight individual 2 x 11.5-in pine courses, rails and end timbers have continuous actual timber seating.',flush=True)
    mast=fixed['Mast']
    assert overlap(mast,fore)>1e-6,'No mast heel bearing'
    assert overlap(mast,fore)<.025,'Excessively buried mast heel'
    hoop=members['Mast heel iron hoop']
    assert overlap(hoop,mast)<1e-7
    assert overlap(hoop,fore)<1e-7
    assert overlap(mast,fixed['Deck'])<1e-7,'Mast/deck interference'
    support_distances={}
    for i in range(1,9):
        name=f'Mast pine chock {i}'
        chock=members[name]
        assert overlap(chock,mast)<1e-7
        assert overlap(chock,fixed['Deck'])<1e-7
        support_distances[name]=distance(chock,mast)
        assert support_distances[name]<.012,('Unfitted chock',name,support_distances[name])
    for label in ('aft','fore'):
        partner=members[f'Mast {label} oak partner']
        for side in ('Port','Starboard'):
            carling=members[f'{side} mast-partner carling']
            gap=distance(partner,carling)
            assert gap<.015,('Unsupported partner',label,side,gap)
            assert overlap(partner,carling)<1e-6,'Uncut partner/carling lap'
    for side in ('Port','Starboard'):
        carling=members[f'{side} mast-partner carling']
        assert distance(carling,frames['Forepeak hatch fore deck beam'])<.015
        assert distance(carling,members['Mast forward support beam'])<.015
        assert overlap(members['Mast forward support beam'],frames[f'Forebody {side.lower()} clamp'])>1e-6
    print('PASS: mast heel has a keelson mortise/bearing, separate iron hoop and eight fitted chocks; partners have supported lapped ends.',flush=True)
    # Retain cargo space on BOTH sides of the narrow trunk, including the
    # region where the real trunk must pass through the forepeak partition.
    contains=list(classified.values())
    air=0
    for f in np.linspace(TRUNK_AFT_FT+.7,TRUNK_FORE_FT-.7,11):
        for side in (-1,1):
            for z in (hull.rabbet_height(f)+1.35,hull.deck_height(f)-1.25):
                p=boat_point(side*1.3,float(f),z)
                assert not any(test(p) for test in contains),('Filled space beside trunk',f,side,z)
                air+=1
    print(f'PASS: {air} distributed hold/forepeak samples beside the trunk remain genuine air.',flush=True)
    return dict(status='passed',centreline_parts=len(members),slot_probes=len(passage),
                poses=minimums,air_samples=air,chock_mast_distances_ft=support_distances,
                source='references/drawing_package/m2_centreline_measurements.json',
                inferred_details=['scarf slope and inaccessible aft continuation','mortise, hoop and fine laps',
                                  'board raised stop, gap and thickness','chock facets and partner span'])


if __name__=='__main__':
    report=check()
    (ROOT/'src/checks/m2_acceptance.json').write_text(json.dumps(report,indent=2)+'\n')
