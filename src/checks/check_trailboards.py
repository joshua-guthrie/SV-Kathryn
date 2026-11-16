"""Check source fidelity and attachments against completed-export trailboard BREPs.

Independent source pixels/held-out landmarks live in the target ledger, not in
this CAD acceptance implementation. Run after soma build. Native trace error,
historical uncertainty and full-size CAD contact tolerances remain distinct.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import numpy as np
from scipy.spatial import cKDTree
from PIL import Image
from scipy import ndimage as ndi

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
import cadquery as cq
from soma.measure import Model
from parts.trailboard_layout import TARGET,FEATURES,MAPPING,PHYSICAL,SCALE,fz_to_native,source_guides
from parts.bow_layout import LONGHEAD
from parts import bow
from solid_contacts import contact_distance


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def unreflect_name(points):
    p=np.asarray(points,float);x=p[:,0];v=p[:,1]-MAPPING['flat_vertical_offset_px']+MAPPING['flat_shear']*x
    top,bottom=source_guides(x);depth=(v-top)/(bottom-top)
    x=sum(MAPPING['letter_reflection_flat_x'])-x
    top,bottom=source_guides(x);v=top+depth*(bottom-top)
    return np.column_stack((x,v+MAPPING['flat_vertical_offset_px']-MAPPING['flat_shear']*x))


def cloud(paths,step=1.7):
    output=[]
    for p in paths:
        p=np.asarray(p,float)
        for a,b in zip(p,np.roll(p,-1,axis=0)):
            n=max(2,int(math.ceil(np.linalg.norm(b-a)/step))+1)
            output.extend(a+(b-a)*t for t in np.linspace(0,1,n))
    return np.asarray(output)


def outside_masks(points):
    p=np.asarray(points);keep=np.ones(len(p),bool)
    for mask in TARGET['uncertainty_masks']:
        if mask['source_id']=='S01-V03':
            x0,y0,x1,y1=mask['native_box']
            keep &= ~((p[:,0]>=x0)&(p[:,0]<=x1)&(p[:,1]>=y0)&(p[:,1]<=y1))
    # Inferred mounting holes and the hull trim are absent from the ornament drawing.
    f=MAPPING['physical_root_f']+(p[:,0]-MAPPING['source_root_x'])*SCALE
    keep &= f>51.05
    for station in LONGHEAD['mount_stations_f']:
        keep &= np.abs(f-station)>.065
    return keep


def check(project=ROOT,out=None,strict=True):
    project=Path(project)
    build=json.loads((project/'.soma/build.json').read_text())
    assert build['status']=='ok' and not build['warnings']
    model=Model(project/'.soma');records={p['name']:p for p in model.map['parts']};cache={}
    def part(name):
        if name not in cache:cache[name]=model.shape(records[name]['id']).scale(1/304.8)
        return cache[name]
    sources={}
    for key,source in TARGET['sources'].items():
        p=ROOT/source.get('path',source.get('file'))
        digest=sha(p);assert digest==source['sha256'],('Source changed',key)
        sources[key]=digest
    checks=[]
    def result(cid,status,actual,limit,units,method,evidence=None):
        checks.append(dict(id=cid,status='pass' if status else 'fail',actual=actual,limit=limit,units=units,
                           method=method,evidence_paths=evidence or []))
    baseline=json.loads((ROOT/'docs/images/trailboard_correction/baseline-fixed-parts.json').read_text())
    changed={}
    for name,expected in baseline['parts'].items():
        if name not in records:changed[name]='missing';continue
        error=float(np.max(np.abs(np.asarray(records[name]['bbox'])-expected)))
        if error>.1:changed[name]=error
    result('AC-01',not changed,{'changed_fixed_parts':changed,'fixed_parts_compared':len(baseline['parts'])},.1,'mm',
           'Compare accepted hull/stern/spar/jib and remaining fixed-part bounds against the frozen 928-part map')
    print('Fixed assembly witnesses checked.',flush=True)
    board=part('Starboard trailboard board');rail=part('Starboard projecting headrail')
    residuals=[]
    for row in TARGET['held_out_landmarks']:
        f=row['forward_ft'];target=row['height_ft']
        face=cq.Face.makeFromWires(cq.Workplane(cq.Plane(origin=(0,25-f,10),xDir=(1,0,0),normal=(0,1,0))).rect(20,30).val())
        shape=rail if row['role']=='rail' else board
        section=shape.intersect(face);bounds=section.BoundingBox()
        actual=(bounds.zmin+bounds.zmax)/2 if row['role']=='rail' else bounds.zmax if row['role']=='upper' else bounds.zmin
        residuals.append({**row,'actual_height_ft':actual,'residual_ft':abs(actual-target)})
    max_physical=max(row['residual_ft'] for row in residuals)
    result('AC-02',max_physical<=.20,{'maximum_residual_ft':max_physical,'held_out_points':residuals},.20,'ft',
           'Intersect actual exported board/rail with independent source-station planes; no per-part fit')
    print('Independent source stations checked.',flush=True)
    contour_errors={};missing=[];contacts={};valid=True
    for label in ('Port','Starboard'):
        for feature in TARGET['features']:
            role=feature['role']
            if role in ('outline','field'):continue
            if role=='letter':prefix=label+' trailboard letter '+feature['character']
            elif role=='eye':prefix=label+' longhead eagle eye'
            elif role=='recess':prefix=label+' trailboard '+feature['id']+' recess'
            else:prefix=label+' trailboard carving '+feature['id']
            names=[n for n in records if n==prefix or n.startswith(prefix+' ')]
            if not names:missing.append(prefix);continue
            samples=[]
            for name in names:
                shape=part(name);valid &= shape.isValid() and len(shape.Solids())==1
                contacts[name]=contact_distance(shape,part(label+' trailboard board'))*304.8
                for edge in shape.Edges():
                    n=max(2,min(1000,int(edge.Length()/SCALE/2)+2))
                    for t in np.linspace(0,1,n):
                        p=edge.positionAt(float(t));samples.append([25-p.y,p.z])
            native=fz_to_native(samples)
            if label=='Port' and role=='letter':native=unreflect_name(native)
            target_cloud=cloud([p['outer'] for p in feature['polygons']]+[h for p in feature['polygons'] for h in p.get('holes',[])])
            native=native[outside_masks(native)];target_cloud=target_cloud[outside_masks(target_cloud)]
            if len(native) and len(target_cloud):
                forward=float(cKDTree(target_cloud).query(native)[0].max())
                reverse=float(cKDTree(native).query(target_cloud)[0].max())
                contour_errors[prefix]={'model_to_source_px':forward,'source_to_model_px':reverse,'maximum_px':max(forward,reverse)}
        print(label+' exported carving/letter contours checked.',flush=True)
    outer_points=[]
    for edge in board.Edges():
        for t in np.linspace(0,1,max(2,min(500,int(edge.Length()/SCALE/2)+2))):
            p=edge.positionAt(float(t));outer_points.append([25-p.y,p.z])
    native=fz_to_native(outer_points);native=native[outside_masks(native)]
    target_cloud=cloud([FEATURES['outer-facing']['native_points']]);target_cloud=target_cloud[outside_masks(target_cloud)]
    outer_error=max(float(cKDTree(target_cloud).query(native)[0].max()),float(cKDTree(native).query(target_cloud)[0].max()))
    result('AC-03',outer_error<=6,{'outer_profile_trace_error_px':outer_error},6,'native pixels',
           'Invert the declared transfer on actual exported edges; compare both directions to independent native boundary paths')
    head_errors=[v['maximum_px'] for k,v in contour_errors.items() if any(t in k for t in ('head-face','neck-ground','eagle eye','mouth'))]
    result('AC-04',bool(head_errors) and max(head_errors)<=6,{'head_maximum_trace_error_px':max(head_errors,default=None)},6,'native pixels',
           'Actual head, neck, eye and mouth edges compared with classified source contours; retained negative region is a recess')
    ornament_errors=[v['maximum_px'] for k,v in contour_errors.items() if 'carving' in k]
    result('AC-05',not missing and bool(ornament_errors) and max(ornament_errors)<=6,
           {'missing_regions':missing,'maximum_ornament_error_px':max(ornament_errors,default=None),'all_region_errors':contour_errors},
           6,'native pixels','Retain every source region/island; compare actual exported edge clouds against reviewed contours')
    letter_errors=[v['maximum_px'] for k,v in contour_errors.items() if 'letter' in k]
    letter_contact=[]
    for label in ('Port','Starboard'):
        for char in 'KATHRYN':
            names=[n for n in records if n==label+' trailboard letter '+char or n.startswith(label+' trailboard letter '+char+' ')]
            for name in names:
                for f in LONGHEAD['mount_stations_f']:
                    fixing=part(f'{label} trailboard fixing F{f:.1f}')
                    if part(name).distance(fixing)<1/304.8:letter_contact.append([name,f])
    result('AC-06',len(letter_errors)==14 and max(letter_errors)<=6 and not letter_contact,
           {'glyphs_compared':len(letter_errors),'maximum_glyph_error_px':max(letter_errors,default=None),'unintended_fixing_contacts':letter_contact},
           6,'native pixels','Trace seven glyphs; invert the declared port name reflection; check counters and fixing clearance')
    max_contact=max(contacts.values(),default=0);intersections={}
    for label in ('Port','Starboard'):
        for other in ('Bowsprit',label+' projecting headrail','Longhead trailboard backing'):
            v=part(label+' trailboard board').intersect(part(other)).Volume()
            if v>1e-6:intersections[label+' board / '+other]=v
    result('AC-07',valid and max_contact<=1 and not intersections,
           {'valid_region_solids':bool(valid),'maximum_region_to_board_mm':max_contact,'region_contacts_mm':contacts,'unintended_common_ft3':intersections},
           {'contact_mm':1,'unintended_common_ft3':1e-6},'mixed',
           'Exact exported solids; paint/relief embed classified separately from timber interference')
    result('AC-08',True,TARGET['assumptions'],'explicit evidence classes','qualified reconstruction',
           'Keep thickness, backing, relief depth and palette provisional; do not promote them to historical measurements')
    rail_residual=max(row['residual_ft'] for row in residuals if row['role']=='rail')
    rail_contacts={label:part(label+' projecting headrail').distance(part(label+' lower rail'))*304.8 for label in ('Port','Starboard')}
    result('AC-09',rail_residual<=.2 and max(rail_contacts.values())<=1,
           {'source_profile_residual_ft':rail_residual,'hull_rail_contact_mm':rail_contacts,'handoff':PHYSICAL['handoff']},
           {'source_ft':.2,'contact_mm':1},'mixed','Item-11 plan/profile registration and actual after-handoff contact; short concealed handoff remains inferred')
    paths=[ROOT/'model.py',*sorted((ROOT/'src/parts').glob('*.py')),ROOT/'references/drawing_package/bow_remedy_registration.json',ROOT/'references/drawing_package/trailboard_targets.json',ROOT/'references/drawing_package/longhead_envelope.json',ROOT/'references/drawing_package/jib_club.json']
    record={'schema_version':1,'status':'passed' if all(c['status']=='pass' for c in checks) else 'failed',
            'model_commit':None,'model_commit_note':'Filled by the committed-tree validation record after the model commit',
            'model_source_hashes':{str(p.relative_to(ROOT)):sha(p) for p in paths},
            'build_hashes':{str(p.relative_to(project)):sha(p) for p in [project/'.soma/build.json',project/'.soma/model.glb',project/'.soma/model.map.json',project/'output/model.step']},
            'target_hash':sha(ROOT/'references/drawing_package/trailboard_targets.json'),'part_count':len(records),'checks':checks,
            'finding_disposition':{'TB-01':'Source head, eye, mouth and feather regions implemented','TB-02':'Source regions replace generated waves/leaves','TB-03':'Traced name enclosure and seven glyphs on both outward faces','TB-04':'Traced oblique return and physical body envelope',
                                   'TB-05':'Traced border/field boundaries; relief depth remains an explicit assumption','TB-06':'Source headrails corrected; local after handoff remains an inferred fitting','TB-07':'Exported-edge, held-out-source and contact acceptance added','TB-08':'Palette and photo state retained as qualified observations'},
            'remaining_assumptions':TARGET['assumptions'], 'source_hashes':sources}
    proof_path=ROOT/'docs/images/trailboard_correction/committed-build.json'
    proof=json.loads(proof_path.read_text()) if proof_path.exists() else {}
    record['package_validation']='pending clean committed-tree build'
    if proof.get('status')=='passed':
        same_sources=proof['model_source_hashes']==record['model_source_hashes']
        changed_images=[name for name,digest in proof['image_hashes'].items() if sha(ROOT/name)!=digest]
        result('AC-10',same_sources and not changed_images,
               {'verified_model_commit':proof['model_commit'],'same_model_sources':same_sources,'changed_images':changed_images,
                'clean_build_parts':proof['part_count'],'proof':'docs/images/trailboard_correction/committed-build.json'},
               'Same model sources; fresh committed-tree build and checked documentation images','package',
               'The model commit is rebuilt from an archive without app state or caches; final documentation keeps the verified geometry unchanged')
        record['model_commit']=proof['model_commit']
        record['model_commit_note']='Geometry commit validated from scratch; later documentation-only checkpoints retain these source hashes'
        record['package_validation']='passed' if checks[-1]['status']=='pass' else 'failed'
        record['status']='passed' if all(c['status']=='pass' for c in checks) else 'failed'
    if out:
        out=Path(out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'status':record['status'],'parts':len(records),'checks':[{k:c[k] for k in ('id','status')} for c in checks],
                      'max_physical_ft':max_physical,'outer_trace_px':outer_error,'max_region_contact_mm':max_contact},indent=2),flush=True)
    if strict:assert record['status']=='passed',[(c['id'],c['actual']) for c in checks if c['status']=='fail']
    return record


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project',type=Path,default=ROOT)
    p.add_argument('--out',type=Path,default=ROOT/'docs/images/trailboard_correction/acceptance.json');p.add_argument('--report-only',action='store_true');a=p.parse_args()
    check(a.project,a.out,strict=not a.report_only)
