"""Evidence-only stern audit: snapshot CAD, locked-scale overlays and arrowed figures.

Does not modify the model. Source crops remain traceable to M0's native images;
the report snapshot records hashes of the live GLB/map and reference images.
"""
import json
import math
import hashlib
import sys
from pathlib import Path
import numpy as np
import cadquery as cq
import vtk
from PIL import Image,ImageDraw,ImageFont,ImageOps
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from parts import hull,deck,rails,stern_layout
from parts.params import *

OUT=ROOT/'renders/stern_review'
PACKAGE=ROOT/'drawing_package'
RED='#cf2929';BLUE='#006fae';AMBER='#a86900';GREEN='#16704a'


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def font(size=27):
    try:return ImageFont.truetype('DejaVuSans.ttf',size)
    except OSError:return ImageFont.load_default(size=size)


def annotate(image,items):
    image=image.convert('RGB')
    draw=ImageDraw.Draw(image)
    for text,box,target,color in items:
        x,y=box;lines=text.split('\n');f=font(27)
        width=max(draw.textbbox((0,0),line,font=f)[2] for line in lines)+26
        height=len(lines)*35+20
        cx,cy=x+width/2,y+height/2
        tx,ty=target
        if abs(tx-cx)/width>abs(ty-cy)/height:
            start=(x+width if tx>cx else x,cy)
        else:start=(cx,y+height if ty>cy else y)
        draw.line((start,target),fill=color,width=5)
        dx,dy=tx-start[0],ty-start[1];length=max(1,math.hypot(dx,dy))
        ux,uy=dx/length,dy/length
        head=[(tx,ty),(tx-22*ux+9*uy,ty-22*uy-9*ux),(tx-22*ux-9*uy,ty-22*uy+9*ux)]
        draw.polygon(head,fill=color)
        draw.ellipse((tx-5,ty-5,tx+5,ty+5),outline=color,width=3)
        draw.rounded_rectangle((x,y,x+width,y+height),radius=9,fill='white',outline=color,width=3)
        for i,line in enumerate(lines):draw.text((x+13,y+9+i*35),line,font=f,fill=color)
    return image


def source_crop(manifest,key,box,name):
    view=next(v for v in manifest['views'] if v['id']==key)
    sx,sy=[n/p for n,p in zip(view['native_size'],view['preview_size'])]
    bounds=tuple(round(v*(sx if i%2==0 else sy)) for i,v in enumerate(box))
    with Image.open(PACKAGE/view['native_image']) as image:crop=image.crop(bounds).convert('RGB')
    crop.thumbnail((1800,2000),Image.Resampling.LANCZOS)
    ratio=crop.width/(bounds[2]-bounds[0])
    crop.save(OUT/f'{name}-clean.png')
    def point(x,y):return ((x*sx-bounds[0])*ratio,(y*sy-bounds[1])*ratio)
    record=dict(view=key,source_sha256=view['source_sha256'],preview_box=box,
                view_native_box=bounds,display_size=list(crop.size),name=name)
    return crop,point,record


def render_view(name,position,focus,scale,up=(0,0,1),cut=False,helm_only=False):
    mapping=json.loads((ROOT/'.soma/model.map.json').read_text())['parts']
    importer=vtk.vtkGLTFImporter();importer.SetFileName(str(ROOT/'.soma/model.glb'));importer.Update()
    ren=importer.GetRenderer();ren.SetBackground(.94,.96,.98)
    collection=ren.GetActors();collection.InitTraversal()
    actors=[collection.GetNextActor() for _ in range(collection.GetNumberOfItems())]
    assert len(actors)==2*len(mapping)
    plane=vtk.vtkPlane();plane.SetOrigin(0,0,0);plane.SetNormal(1,0,0)
    for i,part in enumerate(reversed(mapping)):
        pair=actors[2*i:2*i+2]
        assert abs(pair[0].GetBounds()[2]-part['bbox'][0][1])<.2,part['name']
        visible=not part['group'].startswith('Spars')
        if helm_only:visible=part['group']=='Deck/Helm' and part['name']!='Steering pedestal' and not part['name'].startswith('Helm lid')
        for actor in pair:
            actor.SetVisibility(visible)
            actor.GetProperty().SetAmbient(.40);actor.GetProperty().SetDiffuse(.60)
            if cut:actor.GetMapper().AddClippingPlane(plane)
    window=vtk.vtkEGLRenderWindow();window.SetOffScreenRendering(True);window.SetSize(1800,1200);window.AddRenderer(ren)
    lights=vtk.vtkLightKit();lights.SetKeyLightIntensity(1);lights.AddLightsToRenderer(ren)
    camera=ren.GetActiveCamera();camera.ParallelProjectionOn();camera.SetViewUp(*up)
    camera.SetPosition(*(v*MODEL_MM_PER_FOOT for v in position))
    camera.SetFocalPoint(*(v*MODEL_MM_PER_FOOT for v in focus))
    camera.SetParallelScale(scale*MODEL_MM_PER_FOOT)
    ren.ResetCameraClippingRange();window.Render()
    def point(x,f,z):
        p=boat_point(x,f,z);ren.SetWorldPoint(*(v*MODEL_MM_PER_FOOT for v in p),1)
        ren.WorldToDisplay();p=ren.GetDisplayPoint();return (p[0],1200-p[1])
    targets={
        'wing':point(-4.5,-1.5,hull.deck_height(-1.5,-4.5)+.05),
        'rail':point(-2.5,stern_layout.rail_forward(-2.5),hull.deck_height(stern_layout.rail_forward(-2.5),-2.5)+STERN_SOURCE['aft_top_rail_above_deck_ft']),
        'box':point(0,HELM_BOX_FORWARD_FT,hull.deck_height(HELM_FORWARD_FT)+HELM_BOX_HEIGHT_FT),
        'front':point(-.55,STERN_SOURCE['helm_box_fore_ft'],hull.deck_height(HELM_FORWARD_FT)+.5),
        'controls':point(-1.8,CABIN_AFT_FT-.35,hull.deck_height(CABIN_AFT_FT)+.6),
        'counter':point(-1.5,stern_layout.face_forward(6,stern_layout.reference_height(hull.deck_height)),6),
        'traveller':point(0,.35,hull.deck_height(.35)+.25),
        'davit':point(-4.1,(legacy_forward(1.5)+legacy_forward(-3.4))/2,10.6+sheer_band_height(legacy_forward(1.5))),
        'wheel':point(0,HELM_WHEEL_FORWARD_FT,hull.deck_height(HELM_FORWARD_FT)+HELM_WHEEL_HEIGHT_FT),
        'hydraulics':point(0,HELM_FORWARD_FT,hull.deck_height(HELM_FORWARD_FT)+.65),
    }
    capture=vtk.vtkWindowToImageFilter();capture.SetInput(window);capture.Update()
    writer=vtk.vtkPNGWriter();writer.SetFileName(str(OUT/f'{name}-clean.png'));writer.SetInputConnection(capture.GetOutputPort());writer.Write()
    image=Image.open(OUT/f'{name}-clean.png').convert('RGB')
    window.Finalize()
    return image,targets


def boundary_edges(shape):
    edges={};counts={}
    for face in shape.Faces():
        if face.normalAt().z<.8:continue
        for edge in face.Edges():
            key=edge.hashCode();edges[key]=edge;counts[key]=counts.get(key,0)+1
    return [edges[k] for k,count in counts.items() if count==1]


def plan_overlay(manifest,registration,crop_record):
    view=next(v for v in manifest['views'] if v['id']=='S04-V02')
    source=next(s for s in manifest['sources'] if s['id']=='S04')
    a,b=registration['transformations']['S04']['grid_x_to_F']
    centre=registration['transformations']['S04']['centreline_grid_y']*source['native_size'][1]/960
    cal=json.loads((PACKAGE/'calibration.json').read_text())
    ppf=cal['calibrated_sheets']['S04']['native_pixels_per_ft']
    native_box=crop_record['view_native_box'];ratio=crop_record['display_size'][0]/(native_box[2]-native_box[0])
    def xy(points):
        native_x=(points[:,0]-b)/a*source['native_size'][0]/1440
        native_y=centre-points[:,1]*ppf
        return ((native_x-view['native_box'][0]-native_box[0])*ratio,
                (native_y-view['native_box'][1]-native_box[1])*ratio)
    image=Image.open(OUT/'source-plan-clean.png')
    fig,ax=plt.subplots(figsize=(12,12),dpi=170);ax.imshow(image)
    for i,edge in enumerate(boundary_edges(hull.make_deck())):
        points=np.array([(25-p.y,p.x) for p in [edge.positionAt(float(t)) for t in np.linspace(0,1,35)]])
        x,y=xy(points);ax.plot(x,y,color=RED,lw=1.5,label='Actual CAD deck top boundary' if i==0 else None)
    for level in ('top',):
        xs=np.linspace(-5,5,29)
        points=np.array([(stern_layout.rail_forward(x),x) for x in xs])
        x,y=xy(points);ax.plot(x,y,color='#8844b2',lw=2,label='Current stern rail centre path')
    f0,f1=STERN_SOURCE['helm_box_aft_ft'],STERN_SOURCE['helm_box_fore_ft'];w=HELM_BOX_WIDTH_FT/2
    x,y=xy(np.array([(f0,-w),(f1,-w),(f1,w),(f0,w),(f0,-w)]));ax.plot(x,y,color=GREEN,lw=2,label='Current helm-case footprint')
    px,py=xy(np.array([(-1.98,4.5)]))
    ax.annotate('R1: current deck quarter lies outside\nthe source shoulder/boundary group',xy=(px[0],py[0]),
                xytext=(image.width*.48,image.height*.20),fontsize=10,color=RED,
                bbox=dict(boxstyle='round',fc='white',ec=RED),arrowprops=dict(arrowstyle='-|>',color=RED,lw=2.2))
    px,py=xy(np.array([(stern_layout.rail_forward(-4.5),-4.5)]))
    ax.annotate('R3: trace the rail and corner continuation;\nthe present quadratic is a reconstruction',xy=(px[0],py[0]),
                xytext=(image.width*.40,image.height*.75),fontsize=10,color='#8844b2',
                bbox=dict(boxstyle='round',fc='white',ec='#8844b2'),arrowprops=dict(arrowstyle='-|>',color='#8844b2',lw=2.2))
    ax.set_xlim(0,image.width);ax.set_ylim(image.height,0);ax.axis('off')
    ax.legend(loc='upper right',fontsize=9)
    ax.set_title('Locked S04 scale / F registration: red = current CAD deck, black = source drawing',fontsize=12)
    fig.text(.5,.012,'No independent X/Y stretching. Existing M0 registration retained; boundary identification and surveyed/corrected condition still require resolution.',ha='center',fontsize=8)
    fig.tight_layout(rect=(0,.04,1,1));fig.savefig(OUT/'plan-locked-overlay.png',facecolor='white');plt.close(fig)


def profile_overlay(manifest,registration,crop_record):
    view=next(v for v in manifest['views'] if v['id']=='S04-V01')
    source=next(s for s in manifest['sources'] if s['id']=='S04')
    a,b=registration['transformations']['S04']['grid_x_to_F']
    ppf=json.loads((PACKAGE/'calibration.json').read_text())['calibrated_sheets']['S04']['native_pixels_per_ft']
    anchor=next(p for p in json.loads((PACKAGE/'stern_review_picks.json').read_text())
                if p['view']=='S04-V01' and p['label']=='stock at deck')
    anchor_z=hull.deck_height(anchor['canonical_F_ft'])
    bounds=crop_record['view_native_box'];ratio=crop_record['display_size'][0]/(bounds[2]-bounds[0])
    def xy(f,z):
        x=(f-b)/a*source['native_size'][0]/1440-view['native_box'][0]-bounds[0]
        y=anchor['source_native_point'][1]-(z-anchor_z)*ppf-view['native_box'][1]-bounds[1]
        return x*ratio,y*ratio
    image=Image.open(OUT/'source-profile-clean.png')
    fig,ax=plt.subplots(figsize=(14,11),dpi=160);ax.imshow(image)
    plane=cq.Face.makeFromWires(cq.Workplane('YZ').rect(160,50).val())
    for shape,color,label in ((hull.solid_envelope(),RED,'Actual CAD centreline exterior outline'),
                               (hull.make_deck(),'#bd26aa','Actual CAD deck section')):
        section=shape.intersect(plane)
        for i,edge in enumerate(section.Edges()):
            ps=[edge.positionAt(float(t)) for t in np.linspace(0,1,50)]
            px,py=xy(np.array([25-p.y for p in ps]),np.array([p.z for p in ps]))
            ax.plot(px,py,color=color,lw=1.6,label=label if i==0 else None)
    zs=np.array([hull._blade_bottom_z,hull._head_z]);fs=np.array([hull._post_forward_at(z) for z in zs])
    px,py=xy(fs,zs);ax.plot(px,py,'--',color=GREEN,lw=1.5,label='Actual stock axis')
    z=6.0;f=stern_layout.face_forward(z,stern_layout.reference_height(hull.deck_height));point=xy(f,z)
    ax.annotate('R2: current counter plane lies aft\nof the existing S04 guide picks',xy=point,xytext=(image.width*.05,image.height*.80),
                fontsize=11,color=RED,bbox=dict(boxstyle='round',fc='white',ec=RED),
                arrowprops=dict(arrowstyle='-|>',color=RED,lw=2.5))
    picks=json.loads((PACKAGE/'stern_review_picks.json').read_text())
    for pick in picks:
        if pick['view']!='S04-V01' or not pick['label'].startswith('counter'):continue
        x=(pick['source_native_point'][0]-view['native_box'][0]-bounds[0])*ratio
        y=(pick['source_native_point'][1]-view['native_box'][1]-bounds[1])*ratio
        ax.scatter([x],[y],s=38,color=BLUE,zorder=8)
    ax.set_xlim(0,image.width);ax.set_ylim(image.height,0);ax.axis('off');ax.legend(loc='upper right',fontsize=8)
    ax.set_title('Locked longitudinal scale: current CAD centreline section over S04',fontsize=12)
    fig.text(.5,.02,'Review-only vertical anchor: the picked stock/deck crossing. No best-fit translation was applied.\n'
             'Existing guide labels, local datum and corrected/as-surveyed condition require confirmation before final targets.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.065,1,1));fig.savefig(OUT/'profile-locked-overlay.png',facecolor='white');plt.close(fig)


def photo_figures():
    directory=ROOT/'Reference Material/LOC_Kathryn_photos'
    manifest=json.loads((directory/'manifest.json').read_text())
    layouts={
        'LOC-P30':[
            ('R6 reference: substantial iron davits\nwith stainless struts and real mountings.',(.04,.03),(.62,.27)),
            ('R1 / R2 reference: compare this\ncontinuous shoulder and lower contour.',(.38,.81),(.83,.72)),
            ('R6 reference: external pushboat bumper\nis a separate part, not hull extension.',(.04,.63),(.49,.61)),
            ('R8 reference: distinguish the substantial\ntransom moulding from thin deck planking.',(.55,.40),(.77,.67)),
        ],
        'LOC-P28':[
            ('R4 reference: removable timber lid;\nretain a properly hollow case.',(.03,.03),(.44,.34)),
            ('R4 reference: lower front opening\nexposes the mechanism / foot space.',(.03,.61),(.57,.55)),
            ('R6 reference: local control assemblies\nbelong in the stern inventory.',(.03,.86),(.69,.82)),
        ],
        'LOC-P29':[
            ('R4 reference: hydraulic replacement,\nmounting plate, arms and cylinders.',(.03,.03),(.55,.61)),
            ('Open-lid inspection reference.\nDo not model a filled box or wrong gearing.',(.03,.87),(.79,.78)),
        ],
        'LOC-P07':[
            ('R3 reference: flat rectangular oak rails\nwith fair curvature, not round tubing.',(.03,.03),(.52,.74)),
        ],
        'LOC-P25':[
            ('R7 reference: keep the aft cabin, roof\nand helm working space in the same review.',(.03,.03),(.57,.48)),
        ],
    }
    provenance=[]
    for identity,labels in layouts.items():
        row=next(r for r in manifest['photos'] if r['id']==identity)
        detail=directory/f'{identity}-detail.jpg'
        path=detail if detail.exists() else directory/row['review_file']
        image=ImageOps.contain(Image.open(path).convert('RGB'),(1800,1800))
        w,h=image.size
        items=[(text,(int(b[0]*w),int(b[1]*h)),(int(t[0]*w),int(t[1]*h)),BLUE) for text,b,t in labels]
        annotate(image,items).save(OUT/f'{identity}-annotated.png')
        provenance.append(dict(id=identity,page_url=row['page_url'],source_file=str(path.relative_to(ROOT)),sha256=sha(path),caption=row['title']))
    (OUT/'photo_provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')


def measurements():
    mapping=json.loads((ROOT/'.soma/model.map.json').read_text())
    build=json.loads((ROOT/'.soma/build.json').read_text())
    deck_shape=hull.make_deck()
    margin=[]
    for x in (0,2.5,4.5):
        face=cq.Face.makeFromWires(cq.Workplane('YZ',origin=(x,0,0)).rect(150,50).val())
        section=deck_shape.intersect(face)
        aft=25-section.BoundingBox().ymax
        rail=stern_layout.rail_forward(x)
        margin.append(dict(across_ft=x,deck_aft_ft=aft,rail_centre_ft=rail,
                           projected_deck_extension_aft_of_rail_ft=rail-aft))
    widths=[]
    for f in (0,2,4,6):
        face=cq.Face.makeFromWires(hull.section_plane(f).rect(50,40).val())
        widths.append(dict(forward_ft=f,deck_width_ft=deck_shape.intersect(face).BoundingBox().xlen))
    helm_floor=hull.deck_height(HELM_FORWARD_FT)
    ref=stern_layout.reference_height(hull.deck_height)
    picks=json.loads((PACKAGE/'stern_review_picks.json').read_text())
    anchor=next(p for p in picks if p['view']=='S04-V01' and p['label']=='stock at deck')
    cal=json.loads((PACKAGE/'calibration.json').read_text())['calibrated_sheets']['S04']['native_pixels_per_ft']
    residuals=[]
    for pick in picks:
        if pick['view']!='S04-V01' or not pick['label'].startswith('counter'):continue
        z=hull.deck_height(anchor['canonical_F_ft'])+(anchor['source_native_point'][1]-pick['source_native_point'][1])/cal
        predicted=stern_layout.face_forward(z,ref)
        residuals.append(dict(guide_label=pick['label'],source_forward_ft=pick['canonical_F_ft'],
            review_Z_ft=z,current_plane_forward_ft=predicted,source_minus_current_F_ft=pick['canonical_F_ft']-predicted,
            status='Provisional existing guide identification / local deck anchor; not a certified target.'))
    stern_parts=[]
    for p in mapping['parts']:
        lo,hi=p['bbox'];fa=25-hi[1]/MODEL_MM_PER_FOOT;ff=25-lo[1]/MODEL_MM_PER_FOOT
        if fa<10 and (p['group'].startswith('Deck/') or 'transom' in p['name'].lower()):
            stern_parts.append(dict(name=p['name'],group=p['group'],aft_ft=fa,fore_ft=ff))
    result=dict(snapshot=dict(parts=len(mapping['parts']),build_status=build['status'],warnings=build['warnings'],scale=MODEL_SCALE,
        glb_sha256=sha(ROOT/'.soma/model.glb'),map_sha256=sha(ROOT/'.soma/model.map.json')),
        margins=margin,deck_widths=widths,profile_guide_residuals=residuals,
        helm=dict(box_aft_ft=STERN_SOURCE['helm_box_aft_ft'],box_fore_ft=STERN_SOURCE['helm_box_fore_ft'],
                  box_width_ft=HELM_BOX_WIDTH_FT,case_height_ft=HELM_BOX_HEIGHT_FT,
                  wheel_forward_ft=HELM_WHEEL_FORWARD_FT,stock_head_ft=HELM_FORWARD_FT,
                  wheel_height_above_deck_ft=HELM_WHEEL_HEIGHT_FT,rim_radius_ft=HELM_WHEEL_RADIUS_FT,
                  handle_radius_ft=HELM_HANDLE_RADIUS_FT,cabin_aft_ft=CABIN_AFT_FT),
        current_stern_parts=stern_parts,
        overall_stern_acceptance=False,status='Remedy required; other milestones on hold')
    (ROOT/'checks/stern_review_measurements.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('snapshot','margins','deck_widths','profile_guide_residuals','helm')},indent=2),flush=True)
    return result


def main():
    OUT.mkdir(exist_ok=True)
    manifest=json.loads((PACKAGE/'manifest.json').read_text())
    registration=json.loads((PACKAGE/'registration.json').read_text())
    image,p,record=source_crop(manifest,'S04-V02',(0,90,350,440),'source-plan')
    annotate(image,[
        ('S04 item 18: short main-sheet traveller\njust aft of the helm; separate fitting.',(15,25),p(138,254),BLUE),
        ('Aft waterway / rail contours\nTrace each curve and its proper role.',(720,45),p(108,254),BLUE),
        ('Helm and wheel are distinct landmarks.\nKeep their measured chain to the cabin.',(720,1350),p(244,254),BLUE),
    ]).save(OUT/'source-plan-annotated.png')
    image,p,record2=source_crop(manifest,'S04-V01',(35,70,340,335),'source-profile')
    annotate(image,[
        ('Counter / transom: identify the actual\nplanked boundary and its knuckles.',(25,45),p(168,235),BLUE),
        ('Stock, wheel and box are separate\naxes / envelopes; preserve their chain.',(1000,30),p(190,203),BLUE),
        ('External bumper / fitting projection\nDo not turn it into hull material.',(1000,1160),p(85,210),BLUE),
    ]).save(OUT/'source-profile-annotated.png')
    image,p,_=source_crop(manifest,'S02-V01',(85,0,1050,430),'source-lines')
    annotate(image,[('50-foot recorded-length witnesses\nare a datum, not a traced stern surface.',(370,25),p(178,40),BLUE)]).save(OUT/'source-lines-annotated.png')
    views=[
        ('cad-plan',(0,22,60),(0,22,0),7.8,(1,0,0),False,False),
        ('cad-side',(-60,22,7),(0,22,7),7.8,(0,0,1),False,False),
        ('cad-section',(-60,22,7),(0,22,7),7.8,(0,0,1),True,False),
        ('cad-quarter',(-24,57,20),(0,23,6.5),12,(0,0,1),False,False),
        ('cad-aft',(0,65,8),(0,23,8),8,(0,0,1),False,False),
        ('cad-photo-quarter',(-24,57,13),(0,23,7.2),11,(0,0,1),False,False),
        ('cad-helm',(-5.5,19.5,14.5),(0,23,8.8),4.8,(0,0,1),False,False),
        ('cad-helm-internals',(-5.5,19.5,14.5),(0,23,8.8),4.8,(0,0,1),False,True),
    ]
    for name,pos,foc,scale,up,cut,isolated in views:
        image,points=render_view(name,pos,foc,scale,up,cut,isolated)
        if name=='cad-plan':
            items=[('R1 / R2: broad deck tail and corners\nMeasure wood outline independently.',(20,35),points['wing'],RED),
                   ('R3: rail is a faceted tubular path;\nreference is fair rectangular oak.',(1080,35),points['rail'],RED),
                   ('Retain the improved case footprint;\nrecheck the full cabin-wheel-stern chain.',(1060,1000),points['box'],GREEN)]
        elif name in ('cad-quarter','cad-photo-quarter'):
            items=[('R1: projecting slab / wing outside rail\nMain remaining silhouette concern.',(25,30),points['wing'],RED),
                   ('R3: segmented circular rear rails\nneed the source timber form.',(1050,30),points['rail'],RED),
                   ('R6: simple bent rods are only\nplaceholders for the davit assembly.',(1030,1000),points['davit'],RED)]
        elif name in ('cad-side','cad-section'):
            items=[('R2: a single planar rake is not yet\na complete registered counter surface.',(20,35),points['counter'],RED),
                   ('R5: traveller / bumper / davit projections\nneed separate source-based identities.',(1000,35),points['traveller'],AMBER)]
        elif name=='cad-helm':
            items=[('R4: lower front access opening\nshown in LOC-P28 is missing.',(20,35),points['front'],RED)]
        elif name=='cad-helm-internals':
            items=[('R4: casing and lid hidden for inspection.\nOnly shaft/bearing primitives remain;\nhydraulic gear is not modeled.',(20,35),points['hydraulics'],RED)]
        else:items=[('R1 / R3: check full aft outline,\ncorner rounding and rail fairing together.',(20,35),points['wing'],RED)]
        annotate(image,items).save(OUT/f'{name}-annotated.png')
        print(name,flush=True)
    plan_overlay(manifest,registration,record)
    profile_overlay(manifest,registration,record2)
    photo_figures()
    data=measurements()
    (OUT/'image_provenance.json').write_text(json.dumps(dict(source_crops=[record,record2],
        cad_snapshot=data['snapshot'],annotation_key=dict(red='Current CAD problem',blue='Source evidence',amber='Interpretation unresolved',green='Improvement to retain')),indent=2)+'\n')


if __name__=='__main__':main()
