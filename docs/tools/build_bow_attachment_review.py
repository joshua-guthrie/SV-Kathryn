"""Evidence/report generator; never changes CAD or original references.

Run from the project root:
  python docs/tools/build_bow_attachment_review.py --measure
  python docs/tools/build_bow_attachment_review.py --figures
  python docs/tools/build_bow_attachment_review.py --pdf

Each VTK view runs in a fresh process (the importer owns its renderer).
PDF uses matplotlib's vector PDF backend; reportlab is unavailable in SOMA.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import subprocess
import sys
import textwrap
import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/kathryn-bow-matplotlib')

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/images/bow_attachment_review'
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'src/checks'))
from PIL import Image, ImageDraw, ImageFont, ImageOps

INK = '#173044'
RED = '#be3037'
BLUE = '#086d9f'
GREEN = '#187447'
AMBER = '#976000'
PURPLE = '#7836a1'
FONTS = '/usr/share/fonts/truetype/dejavu/'


def font(n, bold=False):
    return ImageFont.truetype(FONTS + ('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'), n)


def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def guard_snapshot():
    provenance=OUT/'provenance.json'
    if not provenance.exists():return
    recorded=json.loads(provenance.read_text())['model']['files']
    changed=[name for name,digest in recorded.items()
             if (name=='model.py' or name.startswith('src/parts/')) and sha(ROOT/name)!=digest]
    if changed:
        raise RuntimeError('As-found geometry changed; create a new review snapshot instead of overwriting this one: '+', '.join(changed))


def plate(image, title, subtitle, marks, notes, file):
    """Numbered witnesses on the image, explanations in a separate margin."""
    image = image.convert('RGB')
    width = 1800
    ratio = width / image.width
    image = image.resize((width, round(image.height * ratio)), Image.Resampling.LANCZOS)
    header, footer = 110, 255
    canvas = Image.new('RGB', (width, image.height + header + footer), 'white')
    canvas.paste(image, (0, header))
    d = ImageDraw.Draw(canvas)
    d.text((30, 16), title, font=font(32, True), fill=INK)
    d.text((30, 66), subtitle, font=font(22), fill='#465868')
    for label, point, color, offset in marks:
        x, y = point[0] * ratio, point[1] * ratio + header
        tx, ty = x + offset[0], y + offset[1]
        d.ellipse((x-10, y-10, x+10, y+10), outline=color, width=4)
        d.line((x, y, tx, ty), fill=color, width=4)
        d.rounded_rectangle((tx-29, ty-22, tx+29, ty+22), 8, fill='white', outline=color, width=3)
        d.text((tx, ty), label, anchor='mm', font=font(23, True), fill=color)
    y = image.height + header + 18
    d.line((30, y-8, width-30, y-8), fill='#d5dce3', width=2)
    for i, (label, note, color) in enumerate(notes):
        x = 30 + (i % 2) * 890
        yy = y + (i // 2) * 110
        d.text((x, yy), label, font=font(25, True), fill=color)
        lines = textwrap.wrap(note, 60)
        assert len(lines) <= 3, (file, note)
        for k, line in enumerate(lines):
            d.text((x+110, yy+k*30), line, font=font(23), fill=INK)
    canvas.save(OUT / file)


VIEWS = {
    'model-profile': ((-1, 0, 0), (0, -28, 9.3), 7.5, False),
    'model-quarter': ((-.8, .6, .65), (0, -27, 9.8), 6, False),
    'model-plan': ((0, 0, 1), (0, -29.8, 10), 10, False),
    'model-heel-exposed': ((-.9, .3, .5), (0, -27, 9.7), 3.8, True),
    'model-tack': ((-1, 0, 0), (0, -38.1, 11.5), 1.8, False),
    'model-jib-head': ((-1, 0, 0), (0, -11.35, 52.75), 1.25, False),
}


def render_view(name):
    guard_snapshot()
    import numpy as np
    import build_bow_gap_assets as old
    from parts import rigging, bow
    old.HILITE.update({
        'Port trailboard board': (.10, .60, .25),
        'Starboard trailboard board': (.10, .60, .25),
        'Bowsprit heel knee': (.85, .15, .65),
        'Bowsprit fid': (.75, .10, .15),
        'Jib stay': (.04, .40, .75),
    })
    scene = old.ModelScene()
    direction, focus, scale, expose = VIEWS[name]
    hide = ['Jib sail (S08 demonstration)']
    if expose:
        hide.extend(p['name'] for p in scene.parts if 'trailboard' in p['name'].lower()
                    or 'scrollwork' in p['name'].lower() or 'walking board' in p['name'].lower())
    targets = {
        'heel': rigging.BOWSPRIT_HEEL,
        'post': (0, -20.71742, 10.0),
        'board': (-.32, -30.0, 9.6),
        'rail': (-1.21, -30.0, 10.17),
        'knee': (0, -26.4, 9.0),
        'fid': (0, -27.76993, 10.6),
        'bed': (0, -27.76993, 9.95),
        'boardroot': (-.32, -24.2, 8.9),
        'tack': rigging.JIB_TACK,
        'tip': rigging.TIP,
        'club': (0, -37.8, 11.95),
        'head': rigging.JIB_HEAD,
        'stayhead': (0, -11.080225862, 52.725786614),
    }
    image, points = scene.render(direction, (0, 1, 0) if name=='model-plan' else (0, 0, 1),
                                 focus, scale, hide=tuple(hide), points=tuple(targets.values()))
    px = dict(zip(targets, points))
    Image.Image.save(image, OUT / f'{name}-clean.png')
    if name=='model-profile':
        title='C1 | Current bow: the inboard spar is missing'
        specs=[('G1','heel',RED,(-110,-120)),('G3','board',GREEN,(-110,100)),
               ('G4','rail',AMBER,(160,-90)),('G2','knee',PURPLE,(-120,150))]
        notes=[('G1','Red spar starts outboard of stem; square inboard continuation is absent.',RED),
               ('G2','Knee is behind the board in this view; see exposed view C4.',PURPLE),
               ('G3','Green boards remain parallel to centreline, under the spar.',GREEN),
               ('G4','Orange headrail crosses the carved field in side projection.',AMBER)]
    elif name=='model-quarter':
        title='C2 | Current bow: boards and supporting structure disagree'
        specs=[('G1','heel',RED,(-130,-120)),('G3','boardroot',GREEN,(-140,60)),
               ('G4','rail',AMBER,(190,95)),('G2','fid',PURPLE,(40,-160))]
        notes=[('G1','Spar ends about 7.05 ft forward of the correctly located Samson post.',RED),
               ('G2','Vertical pin is drawn through solid spar; no mortise is cut.',PURPLE),
               ('G3','Two boards are only 5.76 in apart at their inner faces.',GREEN),
               ('G4','Boards lack a traced longhead backing and defined fixing lands.',AMBER)]
    elif name=='model-plan':
        title='C3 | Plan view: moving a fin sideways did not make fitted trailboards'
        specs=[('G1','heel',RED,(-230,-70)),('G3','boardroot',GREEN,(260,50)),
               ('G4','rail',AMBER,(-250,30))]
        notes=[('G1','Short outer cone begins here; inboard square heel must be reconstructed.',RED),
               ('G3','Boards stay at X = +/-0.24 to 0.40 ft without a traced backing surface.',GREEN),
               ('G4','Headrails flare outboard; rear board-to-rail gap is much larger.',AMBER),
               ('KEY','Sails hidden; red spar, green boards, orange rails, blue heel bed.',BLUE)]
    elif name=='model-heel-exposed':
        title='C4 | Heel exposed: support has been added, but joinery is unresolved'
        specs=[('G2','fid',RED,(120,-120)),('G2','bed',BLUE,(-220,10)),
               ('G2','knee',PURPLE,(-110,130))]
        notes=[('G2','Fid overlaps uncut timber; a rendered intersection is not a pin joint.',RED),
               ('BED','Saddle touches the spar, but cross-timber is an independent solid.',BLUE),
               ('KNEE','Magenta knee does meet the stem/bed; earlier "no knee" diagnosis is stale.',PURPLE),
               ('G1','This support was built around the end of the shortened spar.',AMBER)]
    elif name=='model-tack':
        title='C5 | Jib tack: the raised sail/stay has no fitting to the bowsprit'
        specs=[('G5','tack',RED,(-170,-110)),('G5','tip',BLUE,(-240,110)),
               ('G5','club',PURPLE,(-260,-60))]
        notes=[('G5','Blue jib stay terminates at raised tack, 9 in above the spar axis.',RED),
               ('TIP','The actual spar and lower stay hardware remain below it.',BLUE),
               ('CLUB','Purple club follows sail foot; its fore end still needs a real joint.',PURPLE),
               ('NOTE','Axes and endpoints are highlighted; this is current CAD, not a proposal.',AMBER)]
    else:
        title='C6 | Jib head: preserving sail dimensions did not fit the new stay'
        specs=[('G6','head',RED,(-160,-140)),('G6','stayhead',BLUE,(170,90))]
        notes=[('G6','Sail head is about 3.90 in away from the new stay centreline.',RED),
               ('STAY','Blue line runs from masthead to the raised tack.',BLUE),
               ('CAUSE','Whole sail triangle was translated upward; stay top stayed fixed.',AMBER),
               ('FIX','Solve head on the stay, then solve clew from S08 lengths.',GREEN)]
    marks=[(lab,px[key],col,off) for lab,key,col,off in specs]
    plate(image,title,'As found at e341989 | false colors identify parts | 1 source ft = 304.8 mm',marks,notes,f'{name}-annotated.png')
    print(name,flush=True)


def source_plate(key, box, title, specs, notes, file, grid=False):
    manifest=json.loads((ROOT/'references/drawing_package/manifest.json').read_text())
    view=next(v for v in manifest['views'] if v['id']==key)
    image=Image.open(ROOT/'references/drawing_package'/view['native_image']).convert('RGB')
    source=next(s for s in manifest['sources'] if s['id']==view['source_id'])
    if grid:
        sx,sy=source['native_size'][0]/1440,source['native_size'][1]/960
        def point(p): return (p[0]*sx-view['native_box'][0],p[1]*sy-view['native_box'][1])
        a=point(box[:2]);b=point(box[2:]);box=(*a,*b)
        specs=[(lab,point(pt),color,off) for lab,pt,color,off in specs]
    box=tuple(round(v) for v in box)
    image=image.crop(box)
    marks=[(lab,(p[0]-box[0],p[1]-box[1]),color,off) for lab,p,color,off in specs]
    ratio=min(1,1800/image.width)
    image=image.resize((round(image.width*ratio),round(image.height*ratio)),Image.Resampling.LANCZOS)
    marks=[(lab,(p[0]*ratio,p[1]*ratio),color,off) for lab,p,color,off in marks]
    plate(image,title,f'Original HAER MD-117 drawing | {key} | crop coordinates retained in provenance.json',marks,notes,file)
    return {'view':key,'native_crop_box':box,'source_file':'references/drawings/'+Path(source['path']).name,'source_sha256':source['sha256'],'view_sha256':sha(ROOT/'references/drawing_package'/view['native_image'])}


def figures(sources_only=False):
    guard_snapshot()
    OUT.mkdir(parents=True,exist_ok=True)
    for name in (() if sources_only else VIEWS):
        subprocess.run([sys.executable,__file__,'--render',name],check=True,cwd=ROOT)
    provenance={}
    provenance['source-s04-profile-annotated.png']=source_plate('S04-V01',(940,258,1323,425),
        'D1 | Sheet 4 inboard profile: restore the square inboard spar',
        [('G1',(1018,309),RED,(40,-150)),('G1',(1101,292),BLUE,(115,-110)),
         ('G2',(1082,317),PURPLE,(-90,130)),('G4',(1180,315),AMBER,(160,100))],
        [('G1','Square section continues inboard toward item 24 (Samson post).',RED),
         ('PICK','Current heel pick at grid X about 1102 identifies the rounded transition.',BLUE),
         ('G2','Stem/knighthead geometry belongs under and around this assembly.',PURPLE),
         ('G4','Headrail lies beneath the spar, with its own hull connection.',AMBER)],
        'source-s04-profile-annotated.png',grid=True)
    provenance['source-s04-plan-annotated.png']=source_plate('S04-V02',(940,558,1323,713),
        'D2 | Sheet 4 deck plan: square section, converging headrails and support',
        [('G1',(1027,639),RED,(15,-140)),('PICK',(1101,640),BLUE,(80,130)),
         ('G3',(1137,666),GREEN,(110,80)),('POST',(996,641),PURPLE,(-100,145))],
        [('G1','The inboard square portion is visible aft of the rounded outer section.',RED),
         ('PICK','Rounded section begins here; this is not evidence that the spar ends here.',BLUE),
         ('G3','Headrail/headwork footprint widens substantially toward the hull.',GREEN),
         ('POST','Post location is supported by S04 and S05; do not move it speculatively.',PURPLE)],
        'source-s04-plan-annotated.png',grid=True)
    provenance['source-s01-ornament-annotated.png']=source_plate('S01-V03',(0,0,3960,2107),
        'D3 | Sheet 1 ornament: use this silhouette and layer order',
        [('G4',(1900,500),AMBER,(40,-95)),('G3',(1800,900),GREEN,(0,100)),
         ('G7',(3550,380),BLUE,(-130,-90)),('G2',(900,380),PURPLE,(-150,100))],
        [('G3','Longhead carries a tapered carved field with lettering and border.',GREEN),
         ('G4','Upper headrail and carved field have a deliberate, separate silhouette.',AMBER),
         ('G7','Eagle/billet detail and outer termination require a source-based trace.',BLUE),
         ('G2','Visible vertical fastening detail: confirm function before sizing it.',PURPLE)],
        'source-s01-ornament-annotated.png')
    provenance['source-s03-stays-annotated.png']=source_plate('S03-V01',(6700,4200,9489,6500),
        'D4 | Sheet 3 rigging: stay forces must terminate on real fittings',
        [('G5',(9350,5420),RED,(-130,-100)),('G5',(8300,5980),BLUE,(100,120)),
         ('G4',(7850,5850),AMBER,(-150,-80)),('G6',(8920,4850),GREEN,(-140,-80))],
        [('G5','Stay and bobstay attachment stations are on the bowsprit hardware.',RED),
         ('PATH','Bobstays return load to straps at the raking stem.',BLUE),
         ('G4','Headrail/headwork profile must be traced with S04, not guessed independently.',AMBER),
         ('G6','Dashed sail geometry is a separate reference, not license to float the tack.',GREEN)],
        'source-s03-stays-annotated.png')
    provenance['source-s05-structure-annotated.png']=source_plate('S05-V01',(807,137,1055,333),
        'D5 | Sheet 5 structure: retain a coherent connection to the hull',
        [('POST',(862,232),PURPLE,(-100,-100)),('STEM',(939,232),BLUE,(140,-100)),
         ('G4',(911,210),AMBER,(-90,-130))],
        [('POST','Samson post is tied into the internal structure at its surveyed station.',PURPLE),
         ('STEM','Stem/knightheads meet the converging sides at the bow.',BLUE),
         ('G4','Deck clamps and beams provide hull structure for the headwork connections.',AMBER),
         ('LIMIT','This sheet does not define every external bolt or hidden joint.',GREEN)],
        'source-s05-structure-annotated.png',grid=True)
    provenance['source-s08-dimensions-annotated.png']=source_plate('S08-V01',(0,0,3000,1550),
        'D6 | Sheet 8: jib dimensions and the limit on demonstration details',
        [('G6',(1500,1380),RED,(190,50)),('NOTE',(1900,700),BLUE,(160,-40))],
        [('G6','Use labelled jib lengths: luff 49 ft 6 in; foot 25 ft 8 in; leech 42 ft.',RED),
         ('NOTE','Hoops/hanks are demonstration details; do not infer actual hardware from them.',BLUE),
         ('DRAFT','Original note records about 6 in of built-in draft at the jib foot.',GREEN),
         ('LIMIT','Detail shapes are not to scale; dimensions govern the sail triangle.',AMBER)],
        'source-s08-dimensions-annotated.png')
    photo=ROOT/'references/loc_photos/LOC_Kathryn_photos/23-LOC-P22.jpg'
    photo_witness=Image.new('RGB',(1500,1100),'#f1f5f8')
    photo_image=Image.open(photo).convert('RGB')
    photo_witness.paste(photo_image,(110,36))
    pd=ImageDraw.Draw(photo_witness)
    pd.text((910,145),'Survey-state witness',font=font(31,True),fill=INK)
    for n,line in enumerate(['Square inboard spar','continues toward the post.','','Fitted headwork surrounds','the spar at the stem.','','Anchor windlass removed.','','Photo is perspective;','use drawings for dimensions.']):
        pd.text((910,215+n*42),line,font=font(27),fill=INK)
    plate(photo_witness,'P1 | LOC-P22: square spar inboard and fitted stem-head surround',
          'HAER MD-117-22 | LOC gallery page 23 | perspective witness, not a dimensional ruler',
          [('G1',(492,598),RED,(-140,-70)),('G2',(365,476),BLUE,(-100,-70)),
           ('POST',(685,636),PURPLE,(170,-30)),('G4',(232,726),AMBER,(-50,140))],
          [('G1','Square spar continues aft into the foredeck/post region.',RED),
           ('G2','Fitted surround and visible fastening differ from an isolated saddle.',BLUE),
           ('POST','Photo records windlass removed; compare geometry, not just equipment.',PURPLE),
           ('G4','Headrail/side framing is outboard of the spar, with bolts visible.',AMBER)],
          'source-loc-p22-annotated.png')
    provenance['source-loc-p22-annotated.png']={'file':str(photo.relative_to(ROOT)),'sha256':sha(photo),'url':'https://www.loc.gov/resource/hhh.md1454.photos/?sp=23'}
    files=['model.py',*map(str,(ROOT/'src/parts').glob('*.py')),'.soma/model.glb','.soma/model.map.json','.soma/build.json']
    provenance['model']={'commit':subprocess.check_output([str(ROOT/'project-git'),'rev-parse','HEAD'],text=True).strip(),
                         'files':{str(Path(p).relative_to(ROOT) if Path(p).is_absolute() else p):sha(ROOT/p) for p in files},
                         'render_source':'Existing successful 903-part SOMA GLB; fresh targeted BREP audit; no model edits.',
                         'soma_render':'Viewer RPC unavailable in sandbox; VTK EGL reads the actual exported GLB.',
                         'new_full_build':'Attempt interrupted (exit 143); prior successful cache retained. No fresh full-build claim.'}
    (OUT/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    load_diagram()


def load_diagram():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    fig,ax=plt.subplots(figsize=(12,7));fig.patch.set_facecolor('white');ax.set(xlim=(-.35,12),ylim=(0,7));ax.axis('off')
    ax.text(.25,6.65,'R1 | Required load paths and correction order',fontsize=19,color=INK,weight='bold')
    ax.text(.25,6.2,'Conceptual diagram - relationships only; not a fabrication drawing or force solution',fontsize=11,color='#465868')
    nodes={'sail':(1.5,4.8,'Jib / sail loads'),'tip':(5.4,4.8,'Tack + stay fitting'),'spar':(9.7,4.8,'Full bowsprit'),
           'stem':(5.4,2.8,'Bobstay straps / stem'),'hull':(9.7,.9,'Primary hull structure'),
           'heel':(9.7,2.8,'Inboard heel / bed'), 'side':(1.5,2.8,'Side-stay chainplates'),
           'board':(2.0,.9,'Trailboards: fitted ornament')}
    for key,(x,y,t) in nodes.items():
        col=GREEN if key=='board' else BLUE
        ax.add_patch(FancyBboxPatch((x-1.45,y-.42),2.9,.84,boxstyle='round,pad=.08',fc='#f1f5f8',ec=col,lw=1.6))
        ax.text(x,y,t,ha='center',va='center',fontsize=10,color=INK)
    def arr(a,b,label='',dy=0):
        x,y,_=nodes[a];u,v,_=nodes[b]
        if y==v:x+=1.55;u-=1.55
        else:y-=.52;v+=.52
        ax.annotate('',(u,v),(x,y),arrowprops={'arrowstyle':'->','color':RED,'lw':1.8})
        if label:ax.text((x+u)/2,(y+v)/2+dy,label,ha='center',fontsize=9,color=RED,bbox={'fc':'white','ec':'none'})
    for a,b in [('sail','tip'),('tip','spar'),('tip','stem'),('tip','side'),('spar','heel'),('heel','hull'),('stem','hull'),('side','hull')]:arr(a,b)
    ax.text(.4,.15,'Order: register source -> restore full spar and bed -> fittings/stays -> fitted boards -> rig checks',fontsize=10,color=INK)
    fig.tight_layout();fig.savefig(OUT/'required-load-path.png',dpi=180);plt.close(fig)


def measure():
    guard_snapshot()
    import numpy as np
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape
    from parts import bow,spars,deck,hull_frames,rigging
    from parts.params import BOWSPRIT_HEEL_FT,BOW_POST_FORWARD_FT,BOWSPRIT_END_FT,TRAILBOARD_ROOT_FT,TRAILBOARD_TIP_FT
    s={'Bowsprit':spars.make_bowsprit(),'Samson post':deck.make_bow_post(),'Oak stem knee':hull_frames.make_stem_knee()}
    for n,a,c in bow.make_bow_details():
        s[n]=a
        if n=='Bowsprit stem-head band':break
    s.update({n:a for n,a,c in bow.make_walking_boards()})
    s['Jib club']=next(rigging.make_sail_spars())[1]
    s['Jib stay']=rigging._line(rigging.HEAD,rigging.JIB_TACK,.022)
    pairs=[('Bowsprit','Bowsprit heel saddle'),('Bowsprit','Bowsprit heel bearing cross-timber'),
           ('Bowsprit heel knee','Bowsprit heel bearing cross-timber'),('Bowsprit heel knee','Painted stem and cutwater'),
           ('Bowsprit heel knee','Oak stem knee'),('Bowsprit','Samson post'),('Bowsprit fid','Bowsprit'),
           ('Port trailboard board','Painted stem and cutwater'),('Port trailboard board','Port projecting headrail'),
           ('Port trailboard board','Bowsprit'),('Port trailboard board','Port headrail knee'),
           ('Port trailboard board','Bowsprit heel bearing cross-timber'),('Port trailboard board','Port bowsprit walking board'),
           ('Bowsprit','Jib stay'),('Bowsprit','Jib club'),('Bowsprit','Bowsprit heel band')]
    r={}
    for a,b in pairs:
        q=BRepExtrema_DistShapeShape(s[a].wrapped,s[b].wrapped);q.Perform()
        d=q.Value();p=q.PointOnShape1(1);v=q.PointOnShape2(1)
        vol=s[a].intersect(s[b]).Volume() if d<1e-6 else 0
        r[a+' / '+b]={'distance_ft':d,'distance_in':d*12,'intersection_ft3':vol,
                      'closest_a_ft':[p.X(),p.Y(),p.Z()],'closest_b_ft':[v.X(),v.Y(),v.Z()]}
    t=np.array(rigging.JIB_TACK);head=np.array(rigging.HEAD);jh=np.array(rigging.JIB_HEAD);d=head-t
    near=t+float(np.dot(jh-t,d)/np.dot(d,d))*d
    r['derived']={'spar_axis_length_ft':math.dist(rigging.BOWSPRIT_HEEL,rigging.TIP),
        'heel_to_post_longitudinal_ft':BOWSPRIT_HEEL_FT-BOW_POST_FORWARD_FT,
        'jib_head_to_stay_ft':float(np.linalg.norm(jh-near)),'jib_head_stay_closest_ft':near.tolist(),
        'tack_raise_ft':rigging.JIB_FOOT_RAISE_FT,'trailboard_x_ft':[.24,.4],
        'trailboard_length_ft':TRAILBOARD_TIP_FT-TRAILBOARD_ROOT_FT,
        'heel_ends_F_ft':BOWSPRIT_HEEL_FT,'spar_tip_F_ft':BOWSPRIT_END_FT}
    r['parts']={n:{'solids':len(a.Solids()),'valid':a.isValid(),
                  'bbox_ft':[[a.BoundingBox().xmin,a.BoundingBox().ymin,a.BoundingBox().zmin],
                             [a.BoundingBox().xmax,a.BoundingBox().ymax,a.BoundingBox().zmax]]} for n,a in s.items()}
    # Targeted BREP witnesses must match the existing export before using its images.
    mapping={p['name']:p for p in json.loads((ROOT/'.soma/model.map.json').read_text())['parts']}
    residuals={n:max(abs(v*304.8-w) for row,old in zip(rec['bbox_ft'],mapping[n]['bbox']) for v,w in zip(row,old))
               for n,rec in r['parts'].items() if n in mapping}
    assert max(residuals.values())<.02,residuals
    assert all(p['valid'] for p in r['parts'].values())
    r['export_bbox_max_residual_mm']=max(residuals.values())
    r['method']='OCCT BREP extrema and common volumes in full-size feet; all exported witnesses agree within 0.02 mm.'
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'measurements.json').write_text(json.dumps(r,indent=2,default=float)+'\n')
    print(json.dumps(r['derived'],indent=2))
    print('Largest bbox residual (mm):',max(residuals.values()))


def pdf():
    """Paginate the exact Markdown report, with searchable vector text."""
    import re
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    from matplotlib.font_manager import FontProperties
    matplotlib.rcParams['pdf.fonttype']=42
    matplotlib.rcParams['figure.max_open_warning']=0
    source=ROOT/'docs/BOWSPRIT_ATTACHMENT_REVIEW.md'
    output=ROOT/'docs/bowsprit-trailboards-gap-analysis.pdf'
    output.parent.mkdir(parents=True,exist_ok=True)
    # Markdown is deliberately simple: paragraphs, headings, bullets, figures.
    lines=source.read_text().splitlines()
    pages=[];page=None;y=0
    def newpage():
        nonlocal page,y
        page=plt.figure(figsize=(8.5,11),facecolor='white');pages.append(page);y=10.1
        page.text(.065,.957,'KATHRYN  /  BOW ATTACHMENT REVIEW',fontsize=9,weight='bold',color=BLUE)
        page.text(.065,.033,'2026-11-15 | As found: e341989 | Geometry review and correction plan',fontsize=8,color='#526473')
        page.text(.935,.033,str(len(pages)),ha='right',fontsize=8,color='#526473')
    def textline(t,size=10.5,bold=False,color=INK,indent=0):
        nonlocal y
        h=size/72*1.35
        if page is None or y-h<.7:newpage()
        page.text((.56+indent)/8.5,y/11,t,fontsize=size,weight='bold' if bold else 'normal',color=color,va='top')
        y-=h
    def clean(t):
        t=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'\1',t)
        return t.replace('**','').replace('`','').replace('\u2014','-').replace('\u2013','-').replace('\u2019',"'").replace('\u201c','"').replace('\u201d','"')
    from matplotlib.textpath import TextToPath
    metrics=TextToPath()
    def wrap_width(text,size=10.5,bold=False,width=525):
        prop=FontProperties(family='DejaVu Sans',weight='bold' if bold else 'normal',size=size)
        result=[];current=''
        for word in text.split():
            candidate=(current+' '+word).strip()
            measured=metrics.get_text_width_height_descent(candidate,prop,ismath=False)[0]
            if current and measured>width:result.append(current);current=word
            else:current=candidate
        if current:result.append(current)
        return result
    paragraph=[]
    def flush():
        nonlocal y
        if not paragraph:return
        text=' '.join(paragraph);paragraph.clear()
        text=clean(text)
        isbullet=text.startswith(('- ','1. ','2. ','3. ','4. ','5. ','6. ','7. ','8. '))
        width=99 if not isbullet else 94
        wrapped=wrap_width(text,width=516 if isbullet else 525)
        height=len(wrapped)*10.5/72*1.35+.09
        if page is None or y-height<.7:newpage()
        for n,line in enumerate(wrapped):textline(line,indent=.13 if isbullet and n else 0)
        y-=.10
    for line in lines:
        if line.startswith('!['):
            flush()
            match=re.match(r'!\[(.*?)\]\((.*?)\)',line);assert match,line
            file=source.parent/match.group(2)
            im=Image.open(file);width=7.35;height=width*im.height/im.width
            height=min(height,8.25);width=height*im.width/im.height
            if page is None or y-height-.45<.7:newpage()
            ax=page.add_axes([(.5+(7.5-width)/2)/8.5,(y-height)/11,width/8.5,height/11]);ax.imshow(im);ax.axis('off')
            y-=height+.12
            for t in textwrap.wrap(clean(match.group(1)),112):textline(t,8.5,color='#526473')
            y-=.13
        elif line.startswith('#'):
            flush();level=len(line)-len(line.lstrip('#'));size={1:21,2:15,3:12}.get(level,11)
            text=clean(line.lstrip('# '));wrapped=wrap_width(text,size=size,bold=True)
            if text.startswith('4. Detailed correction plan'):newpage()
            if page is None or y-len(wrapped)*size/72*1.35-(1.25 if text.startswith('Phase ') else .55)<.7:newpage()
            y-=.15
            for t in wrapped:textline(t,size,True,BLUE if level<3 else INK)
            y-=.13
        elif not line.strip():flush()
        elif line.startswith('- ') or re.match(r'^\d+\. ',line):flush();paragraph.append(line);flush()
        else:paragraph.append(line.strip())
    flush()
    with PdfPages(output) as pdfout:
        pdfout.infodict().update(Title='Kathryn - bowsprit and trailboard attachment gap analysis',Author='Project geometry review',Subject='Measured CAD defects, annotated original drawings, and staged correction plan')
        for f in pages:pdfout.savefig(f);plt.close(f)
    print(f'{output}: {len(pages)} pages')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sources-only',action='store_true');p.add_argument('--render',choices=list(VIEWS));p.add_argument('--figures',action='store_true');p.add_argument('--measure',action='store_true');p.add_argument('--pdf',action='store_true');a=p.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    if a.render:render_view(a.render)
    if a.measure:measure()
    if a.figures or a.sources_only:figures(a.sources_only)
    if a.pdf:pdf()
