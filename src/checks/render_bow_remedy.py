"""Render corrected bow witnesses and actual-solid overlays on original drawings.

One process per view; never overwrites the as-found attachment review.
"""
import argparse
import hashlib
import json
import sys
import textwrap
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/images/bow_remedy'
FONTPATH='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
sys.path.insert(0,str(ROOT/'src'))


def font(n):return ImageFont.truetype(FONTPATH,n)


def render(project,view):
    import build_bow_gap_assets as old
    from parts.bow_layout import SPAR,HEADWORK,axis_height
    from parts.params import boat_point
    from parts import bow,rigging
    project=Path(project);old.ROOT=project;old.HILITE.clear()
    scene=old.ModelScene()
    hide=['Jib sail (S08 demonstration)','Main sail (S08 demonstration)']
    if view=='whole':hide=[]
    if view=='heel':
        hide.extend(p['name'] for p in scene.parts if 'trailboard' in p['name'].lower() or 'scrollwork' in p['name'].lower()
                    or 'longhead' in p['name'].lower() or 'walking board' in p['name'].lower())
    if view=='splice':
        show={'Bowsprit','Bowsprit inboard heel bed','Bowsprit stem-head extension','Oak stem knee with Samson-post mortise',
              'Samson post','Bowsprit heel bearing cross-timber','Bowsprit heel saddle','Bowsprit fid',
              'Bowsprit fid retaining clip','Stem-head splice bolt 1','Stem-head splice bolt 2'}
        hide=[p['name'] for p in scene.parts if p['name'] not in show]
    cameras={'quarter':((-.85,.55,.55),(0,-30,9.5),8.5),'profile':((-1,0,0),(0,-30,9.0),8.6),
             'port':((1,0,.08),(0,-30,9.0),8.6),'head':((-1,0,0),rigging.JIB_HEAD,1.2),
             'plan':((0,0,1),(0,-31,10),13.0),'heel':((-.9,.25,.35),(0,-25,9.1),4.8),
             'tip':((-.9,.25,.25),(0,-41.7,12),1.7),'underside':((-.9,-.1,-.3),(0,-29.5,8.8),8.0),
             'splice':((-1,0,.05),(0,-24.5,8.7),4.5),'whole':((-1,0,.04),(0,-1,31),39)}
    direction,focus,scale=cameras[view]
    witnesses={
        'post':(boat_point(0,SPAR['heel_f'],axis_height(SPAR['heel_f'])), 'Full square heel abuts the unchanged Samson post.'),
        'support':(boat_point(0,HEADWORK['bearing_f'],axis_height(HEADWORK['bearing_f'])-.55), 'Housed saddle and cross-timber bear on the stem-head structure.'),
        'board':(boat_point(-.40,56,bow.board_fastener_centre(56)), 'Decorated face is fixed to a common longhead backing.'),
        'tack':(bow.tack_point(), 'Jib club and stay terminate at the collar, fork and transverse pivot.'),
        'fid':(boat_point(0,HEADWORK['pin_f'],axis_height(HEADWORK['pin_f'])+.5), 'Retained fid passes through drilled timber and a flat head seat.'),
        'splice':(boat_point(-.26,49.65,7.65), 'Stem extension is housed and bolted into the receiving oak knee.'),
        'bed':(boat_point(-.58,47.7,9.1), 'Separate inboard bed carries the square run.'),
        'rail':(boat_point(bow.headrail_point(-1,54)[0],54,bow.headrail_point(-1,54)[1]), 'Headrail is separate from the carved face and hands off to the hull rail.'),
        'block':(bow.downhaul_block_point(), 'Returning downhaul follows the sheave groove in its slotted cheek block.'),
        'collar':(boat_point(-.18,SPAR['end_f']-.2,axis_height(SPAR['end_f']-.2)), 'Fitted collar carries the fork; the pin has real passages.'),
        'clearance':(boat_point(0,SPAR['end_f']-1,axis_height(SPAR['end_f']-1)+.26), 'Club clears the spar by 1.39 inches at the closest point.'),
        'head':(rigging.JIB_HEAD, 'Jib head lies on the actual tack-to-masthead stay.'),
        'clew':(rigging.JIB_CLEW, 'Sail triangle closes to the three printed Sheet 8 dimensions.'),
        'stays':(boat_point(0,59,8.2), 'Two chain bobstays remain; the extra schematic third stay is removed.')}
    keys={'quarter':['post','support','board','tack'],'profile':['post','board','rail','tack'],
          'plan':['post','support','rail','tack'],'heel':['bed','fid','support','splice'],
          'tip':['tack','collar','block','clearance'],'underside':['support','splice','board','stays'],
          'splice':['bed','fid','support','splice'],'whole':['post','tack','head','clew'],
          'port':['post','board','rail','tack'],'head':['head']}[view]
    image,points=scene.render(direction,(0,1,0) if view=='plan' else (0,0,1),focus,scale,
                              hide=tuple(hide),points=[witnesses[k][0] for k in keys])
    canvas=Image.new('RGB',(image.width,image.height+280),'white');canvas.paste(image,(0,70));d=ImageDraw.Draw(canvas)
    titles={'quarter':'Corrected bow: full spar, stem-head support and fitted longhead',
            'profile':'Corrected profile: source-based timber and curved trailboards',
            'plan':'Corrected plan: post abutment, headwork and complete forward spar',
            'heel':'Exposed heel: housed beds, stem splice and drilled retaining pin',
            'tip':'Jib tack: collar, fork, pivot, club and returning downhaul',
            'underside':'Underside: backing and the separate structural support path',
            'splice':'Receiving oak knee and fitted stem-head splice',
            'whole':'Complete vessel with the corrected bow and jib envelope',
            'port':'Corrected port profile: opposite face and independent headrail',
            'head':'Corrected jib head: halyard and sail head meet their actual stay'}
    d.text((24,14),titles[view],font=font(27),fill='#173044')
    colors=['#086d9f','#976000','#187447','#7836a1']
    for i,(key,(x,y),color) in enumerate(zip(keys,points,colors),1):
        # Numbered witnesses leave explanatory text outside the geometry.
        x,y=round(x),round(y+70)
        if 18<=x<image.width-18 and 88<=y<image.height+52:
            d.ellipse((x-17,y-17,x+17,y+17),fill='white',outline=color,width=3)
            d.text((x,y),str(i),anchor='mm',font=font(22),fill=color)
        col,row=(i-1)%2,(i-1)//2
        caption=f'{i}. '+witnesses[key][1]
        d.multiline_text((24+col*790,image.height+88+row*67),textwrap.fill(caption,67),font=font(20),fill=color,spacing=5)
    d.text((24,image.height+245),f'Actual completed SOMA export | {len(scene.parts)} parts | 1:1 mm | source geometry in feet',font=font(18),fill='#526473')
    OUT.mkdir(parents=True,exist_ok=True);canvas.save(OUT/f'after-{view}.png');print(OUT/f'after-{view}.png',flush=True)


def overlays(project):
    from soma.measure import Model
    from parts.bow_layout import SOURCE
    from parts.params import BOW_POST_FORWARD_FT
    from parts.hull import deck_height
    project=Path(project);model=Model(project/'.soma');parts={p['name']:p for p in model.map['parts']}
    man=json.loads((ROOT/'references/drawing_package/manifest.json').read_text())
    m,b=SOURCE['registration']['F_from_S04_grid_x'];u=SOURCE['registration']['profile_grid_height_ft_per_unit']
    deck=deck_height(BOW_POST_FORWARD_FT);centre=SOURCE['registration']['plan_centreline_grid_y']
    provenance={}
    for mode,key,gb in [('profile','S04-V01',(975,260,1325,350)),('plan','S04-V02',(975,585,1325,690))]:
        view=next(v for v in man['views'] if v['id']==key);source=next(s for s in man['sources'] if s['id']=='S04')
        sx,sy=source['native_size'][0]/1440,source['native_size'][1]/960
        box=tuple(round(g*(sx if i%2==0 else sy))-(view['native_box'][0] if i%2==0 else view['native_box'][1]) for i,g in enumerate(gb))
        image=Image.open(ROOT/'references/drawing_package'/view['native_image']).convert('RGB').crop(box)
        draw=ImageDraw.Draw(image)
        for name,color in [('Bowsprit','#d02632'),('Port trailboard board','#168348'),('Port projecting headrail','#086dba')]:
            shape=model.shape(parts[name]['id']).scale(1/304.8)
            if mode=='profile' and name=='Bowsprit':
                import cadquery as cq
                face=cq.Face.makeFromWires(cq.Workplane('YZ').rect(200,100).val());shape=shape.intersect(face)
            for edge in shape.Edges():
                pts=[]
                for t in np.linspace(0,1,25 if edge.geomType()!='LINE' else 2):
                    p=edge.positionAt(float(t));f=25-p.y;gx=(f-b)/m
                    gy=(318.5-(p.z-deck)/u) if mode=='profile' else (centre-p.x/u)
                    pts.append((gx*sx-view['native_box'][0]-box[0],gy*sy-view['native_box'][1]-box[1]))
                draw.line(pts,fill=color,width=5)
        image.thumbnail((2000,1400));canvas=Image.new('RGB',(image.width,image.height+140),'white');canvas.paste(image,(0,80));d=ImageDraw.Draw(canvas)
        d.text((20,15),f'Actual corrected solids over original S04 {mode}: locked drawing scale',font=font(27),fill='#173044')
        d.text((20,image.height+95),'Red = spar | Green = trailboard | Blue = headrail | Hidden joints remain documented reconstruction',font=font(20),fill='#526473')
        path=OUT/f'source-{mode}-overlay.png';OUT.mkdir(parents=True,exist_ok=True);canvas.save(path)
        provenance[mode]={'view':key,'view_native_crop':box,'drawing_grid_crop':gb,'source_native_sha256':hashlib.sha256((ROOT/'references/drawing_package'/view['native_image']).read_bytes()).hexdigest(),'model_build':model.build,'transform':'Source ledger F/grid fit; original imperial bar for Z/X; no independently fitted scaling per component.'}
    (OUT/'overlay-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project',type=Path,default=ROOT)
    p.add_argument('--view',choices=['quarter','profile','port','head','plan','heel','tip','underside','splice','whole']);p.add_argument('--overlays',action='store_true');a=p.parse_args()
    if a.view:render(a.project,a.view)
    if a.overlays:overlays(a.project)
