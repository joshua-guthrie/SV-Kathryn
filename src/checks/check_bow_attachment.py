"""Check G1-G8 against the exact BREP from a completed SOMA build.

Uses exported solids, rather than rebuilding the lengthy chains. Run after
`soma build`; --project can inspect a source-identical isolated build.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
import numpy as np
import cadquery as cq

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from soma.measure import Model
from parts import bow,rigging
from parts.bow_layout import SOURCE,SPAR,HEADWORK,LONGHEAD,RIG
from parts.params import BOW_POST_FORWARD_FT,boat_point
from solid_contacts import contact_distance

CAD_TOL_FT=1/304.8  # 1 mm CAD attachment tolerance, not source uncertainty.


def check(project=ROOT,out=None):
    project=Path(project)
    inputs=[ROOT/'model.py',*sorted((ROOT/'src/parts').glob('*.py')),
            ROOT/'references/drawing_package/bow_remedy_registration.json',
            ROOT/'references/drawing_package/jib_club.json']
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    changed=[name for name,digest in hashes.items()
             if hashlib.sha256((project/name).read_bytes()).hexdigest()!=digest]
    assert not changed,('Inspected build uses different model sources',changed)
    build=json.loads((project/'.soma/build.json').read_text())
    assert build['status']=='ok' and not build['warnings'],build.get('error')
    model=Model(project/'.soma')
    records={p['name']:p for p in model.map['parts']}
    cache={}
    def part(name):
        if name not in cache:
            cache[name]=model.shape(records[name]['id']).scale(1/304.8)
        return cache[name]
    required=('Bowsprit','Bowsprit inboard heel bed','Bowsprit stem-head extension',
              'Bowsprit heel bearing cross-timber','Bowsprit heel saddle','Bowsprit fid',
              'Bowsprit fid retaining clip','Stem-head splice bolt 1','Stem-head splice bolt 2',
              'Longhead trailboard backing','Jib tack collar and fork','Jib tack pivot pin',
              'Head stay stem-head fitting','Head stay stem-head pin','Jib club',
              'Bowsprit cheek block','Bowsprit downhaul sheave','Jib downhaul foredeck cleat',
              'Jib stay','Head stay','Jib downhaul','Bowsprit bobstay','Bowsprit inner bobstay')
    assert all(name in records for name in required),set(required)-set(records)
    assert 'Bobstay' not in records,'Unexplained third bobstay remains'
    assert 'Bowsprit heel knee' not in records,'Old prop around the truncated spar remains'
    for name in required:
        a=part(name);assert a.isValid() and len(a.Solids())==1,name
    # The complete timber, not just the outer cone, must meet its surveyed after stop.
    length=math.hypot(SPAR['end_f']-SPAR['heel_f'],(SPAR['end_f']-SPAR['heel_f'])*SPAR['slope'])
    assert 21.0<length<22.1,length
    assert abs(SPAR['heel_f']-(BOW_POST_FORWARD_FT+5/24))<1e-8
    section=cq.Face.makeFromWires(bow.spar_section(SPAR['heel_f']+1).rect(3,3).val())
    cross=part('Bowsprit').intersect(section).BoundingBox()
    assert abs(cross.xlen-1.0)<1e-5 and abs(cross.zlen-11/12)<1e-5,('Inboard section',cross.xlen,cross.zlen)
    assert part('Bowsprit').distance(part('Samson post'))<CAD_TOL_FT
    assert part('Bowsprit').intersect(part('Samson post')).Volume()<1e-8,'Spar intersects unchanged post'
    # Exact housed interfaces: zero distance is required, positive volume is not a joint.
    contacts=[('Bowsprit','Bowsprit inboard heel bed'),('Bowsprit','Bowsprit heel saddle'),
              ('Bowsprit heel saddle','Bowsprit heel bearing cross-timber'),
              ('Bowsprit heel bearing cross-timber','Bowsprit stem-head extension'),
              ('Bowsprit stem-head extension','Oak stem knee with Samson-post mortise'),
              ('Bowsprit stem-head extension','Painted stem and cutwater'),
              ('Longhead trailboard backing','Bowsprit stem-head extension'),
              ('Jib tack pivot pin','Jib tack collar and fork'),
              ('Jib stay','Jib tack pivot pin'),('Head stay','Head stay stem-head pin'),
              ('Bowsprit cheek block','Bowsprit'),('Bowsprit downhaul sheave','Bowsprit cheek block'),
              ('Jib downhaul','Jib downhaul foredeck cleat'),
              ('Port projecting headrail','Port lower rail'),('Starboard projecting headrail','Starboard lower rail')]
    distances={}
    for a,b in contacts:
        value=part(a).distance(part(b));distances[a+' / '+b]=value*304.8
        assert value<=CAD_TOL_FT,(a,b,value*304.8)
    # Drilled primary passages must remove the timber occupied by each shaft.
    uncut=[]
    for fastener,wood in [('Bowsprit fid','Bowsprit'),('Bowsprit fid','Bowsprit heel saddle'),
                          ('Bowsprit fid','Bowsprit heel bearing cross-timber'),
                          ('Bowsprit fid','Bowsprit stem-head extension'),
                          ('Jib tack pivot pin','Jib tack collar and fork')]:
        volume=part(fastener).intersect(part(wood)).Volume()
        if volume>1e-7:uncut.append((fastener,wood,volume))
    assert not uncut,('Fastener through uncut material',uncut)
    # Verify the source-located complete load chain is connected in either direction.
    assert part('Bowsprit stem-head extension').intersect(part('Oak stem knee with Samson-post mortise')).Volume()<1e-7
    assert part('Bowsprit heel saddle').intersect(part('Bowsprit heel bearing cross-timber')).Volume()<1e-7
    for side,label in ((1,'Port'),(-1,'Starboard')):
        board=part(label+' trailboard board');core=part('Longhead trailboard backing')
        assert board.distance(core)<CAD_TOL_FT
        assert board.intersect(core).Volume()<1e-7
        assert board.intersect(part('Bowsprit')).Volume()<1e-7
        assert board.intersect(part(label+' projecting headrail')).Volume()<1e-6,'Rail still cuts the carved field'
        carvings=[name for name in records if name.startswith(label+' trailboard carving ')]
        assert len(carvings)>=10,'Source carving regions are missing'
        for name in carvings:
            assert contact_distance(part(name),board)<CAD_TOL_FT,(name,'Carving misses board')
        for char in 'KATHRYN':assert part(label+' trailboard letter '+char).distance(board)<CAD_TOL_FT
        for f in LONGHEAD['mount_stations_f']:
            fixing=part(f'{label} trailboard fixing F{f:.1f}')
            assert fixing.distance(board)<CAD_TOL_FT
        assert part(label+' headrail knee').distance(part(label+' projecting headrail'))<CAD_TOL_FT
    for i in range(1,len(HEADWORK['cross_bearer_stations_f'])+1):
        support=part(f'Bowsprit cross-bearer {i}')
        assert support.distance(part('Bowsprit'))<CAD_TOL_FT
        for label in ('Port','Starboard'):assert support.distance(part(label+' bowsprit walking board'))<CAD_TOL_FT
    for i,t in enumerate((1/3,2/3),1):
        strop=part(f'Jib club lazyjack strop {i}')
        assert strop.distance(part('Jib club'))<CAD_TOL_FT
        for label in ('Port','Starboard'):assert part(f'{label} jib lazyjack leg {i}').distance(strop)<CAD_TOL_FT
    # Sail is solved on its physical stay; no whole-triangle lift is accepted.
    T=np.array(rigging.JIB_TACK);H=np.array(rigging.JIB_HEAD);M=np.array(rigging.HEAD);C=np.array(rigging.JIB_CLEW)
    head_residual=float(np.linalg.norm(np.cross(H-T,M-T))/np.linalg.norm(M-T))
    assert head_residual*304.8<.01,head_residual
    club=rigging.JIB_CLUB
    lengths={'luff':float(np.linalg.norm(H-T)),'foot':float(np.linalg.norm(C-T)),'leech':float(np.linalg.norm(H-C))}
    expected={'luff':49.5,'foot':club['jib_pose']['foot_ft'],
              'leech':club['jib_pose']['straight_leech_ft']}
    for key,value in expected.items():assert abs(lengths[key]-value)<1e-7,(key,lengths[key],value)
    clearance=part('Bowsprit').distance(part('Jib club'))
    assert clearance>.02,('Club fouls spar',clearance)
    assert part('Jib sail (S08 demonstration)').intersect(part('Bowsprit')).Volume()<1e-8
    assert part('Jib sail (S08 demonstration)').intersect(part('Jib club')).Volume()<1e-8
    # Downhaul has a connected return from the actual sheave to the actual cleat.
    route=bow.downhaul_route(rigging.JIB_HEAD)
    assert math.dist(route[0],rigging.JIB_HEAD)<1e-8
    assert math.dist(route[-1],bow.downhaul_cleat_point())<1e-8
    assert part('Jib downhaul').distance(part('Bowsprit downhaul sheave'))<CAD_TOL_FT
    assert len(route)>10
    result={'status':'passed','built_parts':len(records),'build_id':model.build,
            'method':'Exact completed-build BREP solids; 1 mm CAD tolerance; source picks remain +/-0.2 ft.',
            'full_spar_axis_ft':length,'inboard_section_in':[cross.xlen*12,cross.zlen*12],
            'unchanged_samson_station_ft':BOW_POST_FORWARD_FT,'attachment_distances_mm':distances,
            'head_to_stay_mm':head_residual*304.8,'jib_lengths_ft':lengths,
            'club_to_bowsprit_clearance_in':clearance*12,
            'jib_club_length_ft':rigging.JIB_CLUB_LENGTH_FT,
            'jib_clew_above_deck_ft':rigging.JIB_CLEW_ABOVE_DECK_FT,
            'source_registration_sha256':hashlib.sha256((ROOT/'references/drawing_package/bow_remedy_registration.json').read_bytes()).hexdigest(),
            'model_input_sha256':hashes,
            'closed_findings':['G1 full spar and source stations','G2 fitted bed, stem splice and drilled retention',
                               'G3 supported, fixed board faces','G4 coordinated headrail/board silhouette',
                               'G5 jib tack collar, fork and pivot','G6 jib head on stay',
                               'G7 two bobstays and returning sheaved downhaul','G8 exact exported-solid acceptance'],
            'limits':SOURCE['inferred_details']+['Timber/fastener strength and flexible cloth/rope dynamics are not certified.',
                                      'The jib clew follows the high S03/S04 short club; the straight 3D leech chord is shorter than the S08 plan leech.']}
    if out:
        out=Path(out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project',type=Path,default=ROOT)
    p.add_argument('--out',type=Path,default=ROOT/'docs/images/bow_remedy/acceptance.json');a=p.parse_args()
    check(a.project,a.out)
