"""Repeatable actual-export views and fixed-registration S04 comparisons."""
import json
import hashlib
from pathlib import Path
import numpy as np
import cadquery as cq
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from render_m1 import render
from parts import hull,rails

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'renders/stern_remedy'


def top_boundary(shape):
    edges={};counts={}
    for face in shape.Faces():
        if face.normalAt().z<.8:continue
        for edge in face.Edges():
            key=edge.hashCode();edges[key]=edge;counts[key]=counts.get(key,0)+1
    return [edges[k] for k,count in counts.items() if count==1]


def overlays():
    package=ROOT/'drawing_package'
    manifest=json.loads((package/'manifest.json').read_text())
    data=json.loads((package/'stern_remedy_targets.json').read_text())
    a,b=json.loads((package/'registration.json').read_text())['transformations']['S04']['grid_x_to_F']
    source=next(s for s in manifest['sources'] if s['id']=='S04')
    ppf=json.loads((package/'calibration.json').read_text())['calibrated_sheets']['S04']['native_pixels_per_ft']
    view=next(v for v in manifest['views'] if v['id']=='S04-V02')
    sx,sy=[n/p for n,p in zip(view['native_size'],view['preview_size'])]
    bounds=(round(20*sx),0,round(650*sx),view['native_size'][1])
    with Image.open(package/view['native_image']) as original:image=original.crop(bounds).convert('RGB')
    native_width=image.width;image.thumbnail((1800,1500));ratio=image.width/native_width
    def planxy(f,x):
        px=((f-b)/a*source['native_size'][0]/1440-view['native_box'][0]-bounds[0])*ratio
        py=(data['local_image_centre']['source_native_y']-x*ppf-view['native_box'][1])*ratio
        return px,py
    fig,ax=plt.subplots(figsize=(12,11),dpi=160);ax.imshow(image)
    for shape,color,label in ((hull.make_deck(),'#cd2929','Actual deck planking boundary'),
                               (hull.stern_moulding(),'#e28a00','Actual outside timber / moulding'),
                               (rails.make_transom_rail(.98),'#0868cc','Actual rectangular rear rail')):
        for i,edge in enumerate(top_boundary(shape)):
            ps=[edge.positionAt(float(t)) for t in np.linspace(0,1,25)]
            px,py=planxy(np.array([25-p.y for p in ps]),np.array([p.x for p in ps]))
            ax.plot(px,py,color=color,lw=1.2,label=label if i==0 else None)
    for p in data['outer_wood_observations']+data['side_wood_observations']:
        px,py=planxy(p['forward_ft'],p['across_ft']);ax.scatter(px,py,color='#22913d',s=9,zorder=10)
    for x in (-8,8):
        px,py=planxy(14,x)
        ax.annotate('Fair side handoff\n(markup QA)',xy=(px,py),xytext=(px-180,py-50 if x>0 else py+50),
                    color='#9b5b00',fontsize=8,arrowprops=dict(arrowstyle='->',color='#b46b00'))
    ax.set_xlim(0,image.width);ax.set_ylim(image.height,0);ax.axis('off');ax.legend(fontsize=8)
    ax.set_title('S04 fixed scale / F registration: actual CAD wood and rail boundaries')
    fig.tight_layout();fig.savefig(OUT/'plan-source-overlay.png',facecolor='white');plt.close(fig)
    view=next(v for v in manifest['views'] if v['id']=='S04-V01')
    crop=next(r for r in json.loads((package/'stern_review_crops.json').read_text()) if r['view']=='S04-V01')
    box=crop['view_native_box']
    image=Image.open(ROOT/'renders/stern-profile-source.png')
    anchor=data['counter'];z0=anchor['upper_deck_anchor_Z_ft'];y0=anchor['upper_deck_anchor_crop_point'][1]
    def profilexy(f,z):
        return ((f-b)/a*source['native_size'][0]/1440-view['native_box'][0]-box[0],y0-(z-z0)*ppf)
    fig,ax=plt.subplots(figsize=(12,9),dpi=160);ax.imshow(image)
    plane=cq.Face.makeFromWires(cq.Workplane('YZ').rect(160,50).val())
    for shape,color,label in ((hull.solid_envelope(),'#cd2929','Actual planked counter reference'),
                               (hull.make_deck(),'#ad26aa','Actual deck'),(hull.stern_moulding(),'#db8a00','Separate oak moulding')):
        section=shape.intersect(plane)
        for i,edge in enumerate(section.Edges()):
            ps=[edge.positionAt(float(t)) for t in np.linspace(0,1,25)]
            px,py=profilexy(np.array([25-p.y for p in ps]),np.array([p.z for p in ps]))
            ax.plot(px,py,color=color,lw=1.25,label=label if i==0 else None)
    for p in anchor['guide_controls']:
        px,py=profilexy(p['F_ft'],p['Z_ft']);ax.scatter(px,py,color='#0068cf',s=25,zorder=9)
    ax.set_xlim(0,image.width);ax.set_ylim(image.height,0);ax.axis('off');ax.legend(fontsize=8)
    ax.set_title('S04 profile: corrected upper-deck anchor; no fitted translation')
    fig.tight_layout();fig.savefig(OUT/'profile-source-overlay.png',facecolor='white');plt.close(fig)


def main():
    build=json.loads((ROOT/'.soma/build.json').read_text())
    inputs=[ROOT/'model.py',*sorted((ROOT/'parts').glob('*.py')),
            ROOT/'drawing_package/stern_remedy_targets.json']
    assert build['status']=='ok','A successful export is required before rendering acceptance images'
    assert build['finished']>=max(p.stat().st_mtime for p in inputs),'Export predates current geometry sources'
    parts=json.loads((ROOT/'.soma/model.map.json').read_text())['parts']
    show=tuple(p['name'] for p in parts if p['group'].startswith('Deck/'))
    render('stern_remedy/quarter.png',camera=((190,430,235),(0,205,76),102),show_names=show)
    render('stern_remedy/plan.png',camera=((0,180,650),(0,180,0),145),show_names=show)
    render('stern_remedy/aft.png',camera=((0,700,90),(0,215,75),100),show_names=show)
    inspection=tuple(p['name'] for p in parts if p['group'].startswith('Deck/Helm'))
    render('stern_remedy/helm-closed.png',camera=((0,80,88),(0,218,82),29),
           hide_groups=('',),show_names=inspection)
    opened=tuple(n for n in show if not n.startswith(('Helm lid','Steering pedestal')))
    render('stern_remedy/helm-open.png',camera=((100,330,230),(0,218,80),43),
           hide_groups=('Deck/Helm',),show_names=opened)
    overlays()
    provenance=dict(build_started=build['started'],build_finished=build['finished'],
                    timings=build['timings'],parts=len(parts),
                    glb_sha256=hashlib.sha256((ROOT/'.soma/model.glb').read_bytes()).hexdigest(),
                    sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
                    visibility={'helm-closed':'Helm assembly isolated; cabin/deck/rails hidden to expose the opening',
                                'helm-open':'Case and lid hidden; deck and rails retained'})
    (OUT/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')

if __name__=='__main__':main()
