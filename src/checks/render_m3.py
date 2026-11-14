"""M3 actual assembly and fixed-registered-plane section/source comparisons."""
import json
import sys
from pathlib import Path
import numpy as np
import cadquery as cq
from PIL import Image,ImageDraw,ImageOps
from scipy.optimize import minimize_scalar
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from parts import hull,hull_frames as hf,frame_layout,centreline,framing
from parts.params import *
from render_m1 import render,edge_segments,point_distances


def section(view_id,number):
    package=ROOT/'references/drawing_package'
    manifest=json.loads((package/'manifest.json').read_text())
    cal=json.loads((package/'calibration.json').read_text())
    view=next(v for v in manifest['views'] if v['id']==view_id)
    image=Image.open(package/view['preview']).convert('RGB')
    ppf=cal['calibrated_sheets'][view_id[:3]]['native_pixels_per_ft']
    sx,sy=[n/p for n,p in zip(view['native_size'],view['preview_size'])]
    if number==4:
        trace=json.loads((package/'traces/S06-V01.json').read_text())
        origin=trace['origin_preview_pixels']
        source=np.array([p for path in trace['paths'] if 'outer_planking' in path['id'] for p in path['local_XZ_feet']])
        direction=-1
    else:
        origin=[929,1038]
        # Actual shell edges, excluding projected roller/rail/waterway overhangs.
        picks=[[80,544],[132,710],[171,824],[184,849],[207,870],[400,913],[650,967],[875,1014],
               [1006,1013],[1240,966],[1500,910],[1654,874],[1685,850],[1704,816],[1750,660],[1791,546]]
        source=np.array([((x-origin[0])*sx/ppf,(origin[1]-y)*sy/ppf) for x,y in picks])
        direction=1
        (package/'m3_S07-V01_shell_guide.json').write_text(json.dumps(dict(
            source_view=view_id,source_hash=view['source_sha256'],source_preview_picks=picks,
            native_points=[[view['native_box'][0]+x*sx,view['native_box'][1]+y*sy] for x,y in picks],
            origin_preview_pixels=origin,native_pixels_per_ft=ppf,
            datum='named local pixel reference; vertical registration fitted separately',
            scope='open planking-boundary guide; excludes projected overhangs'),indent=2)+'\n')
    member=next(r for r in frame_layout.MEMBERS if r['set']==number and r['side']==1 and r['role']=='primary')
    f=member['forward_ft']
    wire=hull.hull_wire(tuple(hf.section_row(f)))
    segments=edge_segments(wire)
    fit=minimize_scalar(lambda z:np.mean(point_distances(source+np.array([0,z]),segments)**2),
                        bounds=(-2,5),method='bounded',options={'xatol':1e-6})
    z=float(fit.x)
    rms=float(np.sqrt(fit.fun))*12
    assert rms<1.8,('Registered section exceeds 0.15-ft guide-pick allowance',view_id,rms)
    print(view_id,'registered F',f,'shell RMS in',rms,'local Z shift',z,flush=True)
    plane=cq.Face.makeFromWires(hull.section_plane(f).rect(30,25).val())
    objects=[('Actual planking',cq.Compound.makeCompound(hull.make_hull()),'#0876d0')]
    for name,shape,_ in hf.make_frame_parts():
        if name.startswith(f'F{number:02d}'):
            objects.append(('Actual oak frame',shape,'#c97813'))
    for shape in centreline.make_keelsons():objects.append(('Keelson and actual mortises',shape,'#8b4d25'))
    for name,shape,_ in framing.make_opening_frames():
        if name.endswith('clamp'):objects.append(('Pine clamp',shape,'#27954b'))
    fig,ax=plt.subplots(figsize=(12,10),dpi=150)
    ax.imshow(image)
    labels=set()
    for label,shape,color in objects:
        sliced=shape.intersect(plane)
        for a,b in edge_segments(sliced):
            points=np.array([a,b])
            px=origin[0]+direction*points[:,0]*ppf/sx
            py=origin[1]-(points[:,1]-z)*ppf/sy
            ax.plot(px,py,color=color,lw=1.1,label=label if label not in labels else None)
            labels.add(label)
    ax.set_xlim(0,image.width)
    ax.set_ylim(image.height,0)
    ax.axis('off')
    ax.legend(loc='upper right',fontsize=7)
    ax.set_title(f'M3 {view_id}: frame {number}, registered F={f:.3f} ft; shell-guide RMS={rms:.2f} in',fontsize=11)
    fig.text(.5,.015,'Scale and longitudinal frame registration fixed. Only local vertical reference is fitted; corrected/as-surveyed differences remain explicit.\n'
             'Source projected equipment/lining are not filled section material. Frame widths/hidden joints retain schedule uncertainty.',ha='center',fontsize=8)
    fig.tight_layout(rect=(0,.06,1,1))
    path=f'renders/m3-section-{view_id}.png'
    fig.savefig(ROOT/path,facecolor='white')
    plt.close(fig)
    return dict(source_view=view_id,frame_set=number,registered_forward_ft=f,
                local_Z_shift_ft=z,keel_shoe_global_Z_ft=hull.keel_bottom(f),
                shell_guide_RMS_inches=rms,source_overlay=path,
                plane_basis='M3 plan/caption/scarf registration; not free-fit longitudinally',
                source_condition='source section local datum / corrected lines retained separately')


def main():
    render('m3-open-interior.png',mast_clip=106,show_names=('Samson post',))
    render('m3-longitudinal-cutaway.png',True,mast_clip=106,show_names=('Samson post',))
    render('m3-framing-skeleton.png',mast_clip=106,hide_groups=('Hull/Planking envelope',),show_names=('Samson post',))
    render('m3-frame-pairings.png',camera=((180,80,190),(0,-29,43),100),mast_clip=106,
           hide_groups=('Hull/Planking envelope','Deck/Cabin'),show_names=('Samson post',))
    parts=json.loads((ROOT/'.soma/model.map.json').read_text())['parts']
    headwork=tuple(p['name'] for p in parts if p['group']=='Spars/Bow details')
    render('m3-forepeak-headwork.png',camera=((200,-100,240),(0,-250,85),145),mast_clip=106,
           hide_groups=('Hull/Planking envelope',),
           show_names=('Samson post','Bowsprit','Port bowsprit walking board','Starboard bowsprit walking board',*headwork))
    results=[section('S06-V01',4),section('S07-V01',13)]
    (ROOT/'src/checks/m3_section_comparison.json').write_text(json.dumps(results,indent=2)+'\n')
    canvas=Image.new('RGB',(1800,1810),'white')
    draw=ImageDraw.Draw(canvas)
    draw.text((25,18),'KATHRYN M3 - FRAMES, KNEES AND REPAIR MEMBERS',fill='black',font_size=28)
    for y,file,title,limit in ((75,'m3-framing-skeleton.png','Inspection skeleton: hull/deck/roofs hidden; real oak frame members',(1750,1090)),
                             (1220,'m3-longitudinal-cutaway.png','Longitudinal section: open bays, centreline joints and aft/forward supports',(1750,520))):
        image=ImageOps.contain(Image.open(ROOT/'renders'/file).convert('RGB'),limit)
        draw.text((25,y),title,fill='black',font_size=20)
        canvas.paste(image,((1800-image.width)//2,y+32))
    canvas.save(ROOT/'renders/m3-review.png')


if __name__=='__main__':main()
