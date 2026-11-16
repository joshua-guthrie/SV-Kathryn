"""Annotated after views and source comparisons from a completed SOMA export."""
from pathlib import Path
import argparse
import json
import sys
import textwrap
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/images/trailboard_correction'
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'src/checks')]
COLORS=['#086d9f','#187447','#976000','#7836a1']


def font(size,bold=False):
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold' if bold else '')+'.ttf',size)


def plate(im,title,subtitle,points,notes,path,offsets=None):
    width=1800;ratio=width/im.width
    im=im.convert('RGB').resize((width,round(im.height*ratio)),Image.Resampling.LANCZOS)
    header,footer=110,300
    out=Image.new('RGB',(width,im.height+header+footer),'white');out.paste(im,(0,header));d=ImageDraw.Draw(out)
    d.text((28,15),title,font=font(28,True),fill='#173044')
    d.text((28,62),subtitle,font=font(20),fill='#526473')
    offsets=offsets or [(-75,-70),(70,-75),(-70,75),(70,75)]
    for i,((x,y),delta) in enumerate(zip(points,offsets)):
        x,y=x*ratio,y*ratio+header
        assert 0<x<width and header<y<header+im.height,(path,i,x,y)
        tx=max(24,min(width-24,x+delta[0]));ty=max(header+24,min(header+im.height-24,y+delta[1]))
        c=COLORS[i%4];d.line((x,y,tx,ty),fill=c,width=3)
        d.ellipse((x-6,y-6,x+6,y+6),outline=c,width=3)
        d.ellipse((tx-19,ty-19,tx+19,ty+19),fill='white',outline=c,width=3)
        d.text((tx,ty),str(i+1),anchor='mm',font=font(23,True),fill=c)
    for i,note in enumerate(notes):
        col,row=i%2,i//2
        d.multiline_text((28+col*890,header+im.height+20+row*113),textwrap.fill(f'{i+1}. {note}',67),font=font(23),fill=COLORS[i%4],spacing=5)
    d.text((28,out.height-29),'KATHRYN / TRAILBOARD CORRECTION / ACTUAL COMPLETED EXPORT / Source depth, palette and concealed handoff remain qualified',font=font(15),fill='#526473')
    OUT.mkdir(parents=True,exist_ok=True);out.save(OUT/path);print(path,flush=True)


VIEWS={
    'profile':((-1,0,0),(0,-31,9.1),7.6),
    'starboard':((-1,0,0),(0,-31.1,9),4.8),
    'port':((1,0,0),(0,-31.1,9),4.8),
    'head':((-1,0,0),(0,-36.8,10.6),1.25),
    'name':((-1,0,0),(0,-29.9,8.7),1.5),
    'quarter':((-.85,.55,.5),(0,-30,9.0),7.0),
    'plan':((0,0,1),(0,-31,9),7.8),
    'underside':((-.8,.2,-.4),(0,-29.5,8.4),6.5),
}


def render(name):
    import build_bow_gap_assets as renderer
    from parts.trailboard_layout import FEATURES,native_to_fz
    from parts.params import boat_point
    from parts import bow
    renderer.HILITE.clear();scene=renderer.ModelScene()
    names=[p['name'] for p in scene.parts]
    hide=['Jib sail (S08 demonstration)','Main sail (S08 demonstration)']
    if name in ('starboard','port','head','name'):
        label='Port' if name=='port' else 'Starboard'
        show=[n for n in names if n.startswith(label+' trailboard') or n==label+' longhead eagle eye']
        hide=[n for n in names if n not in show]
    if name=='plan':
        show=[n for n in names if any(s in n.lower() for s in ('trailboard','longhead','projecting headrail','stem-head extension'))]
        hide=[n for n in names if n not in show]
    if name=='underside':
        show=[n for n in names if ('Longhead' in n or 'Starboard trailboard board'==n or
                                  'projecting headrail' in n or 'headrail knee' in n or 'trailboard fixing' in n or
                                  n in ('Bowsprit stem-head extension','Painted stem and cutwater','Bowsprit heel bearing cross-timber'))]
        hide=[n for n in names if n not in show]
    side=1 if name=='port' else -1
    def point(key):
        f,z=native_to_fz(FEATURES[key]['native_points']).mean(axis=0)
        return boat_point(side*.39,float(f),float(z))
    points=[boat_point(side*.37,50.3,7.4),point('glyph-H'),point('carving-region-5636'),point('eye')]
    notes=['The aft return is oblique and fitted to the longhead, rather than a square plaque edge.',
           'The name enclosure and all seven glyphs are traced from S01; both outward faces read KATHRYN.',
           'The broad curling stems and unequal leaves follow the original regions, replacing repeated waves.',
           'The hooked beak, eye, jaw and feather transitions follow the documented head.']
    if name=='head':
        points=[point('eye'),point('mouth'),point('neck-ground'),boat_point(side*.39,62.5,10.8)]
        notes=['The eye follows the source contour and is seated against the facing.',
               'The mouth/jaw negative is a dark shallow region; no unsupported through-hole is invented.',
               'Separate source feather contours join the neck; drawing stipple is excluded.',
               'The head has its hooked profile; no stock emblem or pointed leaf substitutes for it.']
    if name=='name':
        points=[point('glyph-K'),point('glyph-A'),point('name-enclosure-upper'),boat_point(side*.39,56,bow.board_fastener_centre(56))]
        notes=['Source letter contours replace the DejaVu font approximation.',
               'Counters and independent stroke shapes are preserved as filled glyph faces.',
               'The drawn enclosure and its two scroll terminals frame the name.',
               'The inferred fixings are in the lower band, clear of the letters.']
    if name=='plan':
        points=[boat_point(-.37,54,9),boat_point(.37,58,9),boat_point(0,56,9),
                boat_point(bow.headrail_point(-1,54)[0],54,bow.headrail_point(-1,54)[1])]
        notes=['Starboard facing remains 1.44 in thick, provisionally.',
               'Port facing uses the same thickness; the source does not independently dimension it.',
               'The common backing remains 6 in wide, with coordinated fixing passages.',
               'The headrail plan follows item 11; the short after handoff fits the accepted hull.']
    if name=='underside':
        points=[boat_point(0,55,8.3),boat_point(-.37,56,bow.board_fastener_centre(56)),
                boat_point(0,50.5,7.6),boat_point(bow.headrail_point(-1,54)[0],54,bow.headrail_point(-1,54)[1])]
        notes=['One decorated face is hidden to expose the common backing and receiving structure.',
               'The relocated shaft passages and visible lower-band heads retain the face-to-backing attachment.',
               'The longhead still meets the previously fitted stem-head structure.',
               'The lowered source rail and its knee are separate from the decorated face.']
    direction,focus,scale=VIEWS[name]
    im,display=scene.render(direction,(0,1,0) if name=='plan' else (0,0,1),focus,scale,hide=tuple(hide),points=points)
    titles={'profile':'Corrected bow profile: traced ornament and source-located headrails',
            'starboard':'Corrected starboard face: source composition in the exported CAD',
            'port':'Corrected port face: the name reads outward on both sides',
            'head':'Corrected head: hooked beak, eye, jaw and feather contours',
            'name':'Corrected name field: source glyphs and shaped enclosure',
            'quarter':'Corrected quarter view: fitted facing, headwork and full spar',
            'plan':'Corrected plan with spar hidden: facing stack and headrails',
            'underside':'Exposed backing and attachments: one facing hidden'}
    offsets=[(-70,-90),(65,-80),(70,80),(-70,75)] if name=='head' else None
    plate(im,titles[name],f'{len(scene.parts)} registered parts / native materials / completed SOMA export / dimensions remain full-size feet',display,notes,'after-'+name+'.png',offsets)


def overlays():
    from soma.measure import Model
    from parts.trailboard_layout import PHYSICAL,fz_to_native
    model=Model(ROOT/'.soma');parts={p['name']:p for p in model.map['parts']}
    manifest=json.loads((ROOT/'references/drawing_package/manifest.json').read_text())
    reg=PHYSICAL['registration'];a,b=reg['F_from_S04_grid_x'];unit=reg['profile_grid_height_ft_per_unit'];deck=PHYSICAL['deck_anchor_z_ft']
    for mode,key,gb in [('profile','S04-V01',(980,280,1258,355)),('plan','S04-V02',(980,590,1258,690))]:
        view=next(v for v in manifest['views'] if v['id']==key);source=next(s for s in manifest['sources'] if s['id']=='S04')
        sx,sy=source['native_size'][0]/1440,source['native_size'][1]/960
        box=tuple(round(g*(sx if i%2==0 else sy))-view['native_box'][i%2] for i,g in enumerate(gb))
        im=Image.open(ROOT/'references/drawing_package'/view['native_image']).convert('RGB').crop(box);d=ImageDraw.Draw(im)
        for name,color in [('Starboard trailboard board','#d12538'),('Starboard projecting headrail','#087eaa')]:
            shape=model.shape(parts[name]['id']).scale(1/304.8)
            for edge in shape.Edges():
                pts=[]
                for t in np.linspace(0,1,2 if edge.geomType()=='LINE' else 25):
                    p=edge.positionAt(float(t));gx=((25-p.y)-b)/a
                    gy=318.5-(p.z-deck)/unit if mode=='profile' else reg['plan_centreline_grid_y']-p.x/unit
                    pts.append((gx*sx-view['native_box'][0]-box[0],gy*sy-view['native_box'][1]-box[1]))
                d.line(pts,fill=color,width=4)
        plate(im,'After / Original Sheet 4 '+mode+' with exported solids',
              'Black = original scan / red = current board / blue = corrected headrail / one inherited physical registration',[],
              ['The red board is exported geometry, including the oblique return and source head.',
               'The visible blue rail follows the independent item-11 picks; its short after handoff is qualified.',
               'Held-out source stations are checked separately from the target control points.',
               'No component is independently moved or scaled to make this overlay appear to fit.'],
              'source-'+mode+'-after.png')
    original=Image.open(ROOT/'references/drawing_package/S01/S01-V03/native.png').convert('RGB').crop((0,0,3960,1450));d=ImageDraw.Draw(original)
    for name,p in parts.items():
        if not (name.startswith('Starboard trailboard') or name=='Starboard longhead eagle eye'):continue
        if 'painted field' in name or 'fixing' in name:continue
        color='#d12538' if 'letter' in name else '#087eaa' if name.endswith(' board') else '#15865b'
        shape=model.shape(p['id']).scale(1/304.8)
        for edge in shape.Edges():
            fz=[]
            for t in np.linspace(0,1,3 if edge.geomType()=='LINE' else 12):
                q=edge.positionAt(float(t));fz.append((25-q.y,q.z))
            points=fz_to_native(fz)
            d.line([tuple(q) for q in points],fill=color,width=2)
    plate(original,'After / Original ornament with actual CAD contours returned to source pixels',
          'Blue = board / green = carving / red = glyphs / inverse of the declared common S01-to-S04 surface mapping',[],
          ['The glyphs, scrolls, frame and head are actual exported edges, rather than redrawn witness sketches.',
           'Pixel fidelity is checked in both directions, with recorded occlusion/fixing masks.',
           'This inverse surface comparison is distinct from the independent physical S04 checks.',
           'The port face is checked with its declared name reflection so the text stays readable.'],
          'source-ornament-after.png')


def comparisons():
    pairs=[('drawing',ROOT/'references/drawing_package/S01/S01-V03/native.png',(150,330,3750,1270),'starboard'),
           ('photo',ROOT/'docs/images/trailboard_review/source-loc-p06-crop.png',None,'port')]
    for label,path,box,view in pairs:
        original=Image.open(path).convert('RGB')
        if box:original=original.crop(box)
        current=Image.open(OUT/f'after-{view}.png').convert('RGB')
        # Crop just the model object from the after view; its separately linked
        # annotated plate remains intact in the report.
        body=current.crop((0,110,current.width,current.height-300))
        a=np.asarray(body);ys,xs=np.where(np.min(a,axis=2)<200)
        current=body.crop((max(0,int(xs.min())-20),max(0,int(ys.min())-20),
                           min(body.width,int(xs.max())+21),min(body.height,int(ys.max())+21)))
        canvas=Image.new('RGB',(1800,1450),'white');d=ImageDraw.Draw(canvas)
        d.text((28,20),'Original '+('HAER ornament drawing' if label=='drawing' else 'LOC-P06 port photograph'),font=font(28,True),fill='#173044')
        original=ImageOps.contain(original,(1740,510));canvas.paste(original,((1800-original.width)//2,70))
        d.text((28,605),'Current exported '+view+' face',font=font(28,True),fill='#173044')
        current=ImageOps.contain(current,(1740,720));canvas.paste(current,((1800-current.width)//2,650))
        d.text((28,1410),'Appearance comparison / source illustration and photo perspective are not independent dimensional scales',font=font(18),fill='#526473')
        canvas.save(OUT/f'comparison-{label}.png');print('comparison-'+label+'.png',flush=True)


def write_report():
    result=json.loads((OUT/'acceptance.json').read_text())
    checks={c['id']:c for c in result['checks']}
    assert all(checks[f'AC-{n:02d}']['status']=='pass' for n in range(1,10))
    proof=json.loads((OUT/'committed-build.json').read_text())
    if proof.get('status')=='passed':
        state=f"**implemented and verified from committed tree {proof['model_commit'][:7]}**"
        commit_note=f"The geometry commit **{proof['model_commit'][:7]}** was rebuilt from an archive without app state, output files or geometry caches. The clean build and its scale, deck, bow and trailboard checks passed. Later documentation checkpoints retain the same model-source hashes."
    else:
        state='**implemented; working-export checks passed; clean committed-tree gate pending**'
        commit_note='The completed working export has passed its source and attachment checks. A fresh archive build of the geometry commit is required before this package is pushed. Its result is recorded in the linked committed-build record.'
    physical=checks['AC-02']['actual']['maximum_residual_ft']
    outer=checks['AC-03']['actual']['outer_profile_trace_error_px']
    ornament=checks['AC-05']['actual']['maximum_ornament_error_px']
    glyph=checks['AC-06']['actual']['maximum_glyph_error_px']
    rail=checks['AC-09']['actual']['source_profile_residual_ft']
    text=f'''# Trailboard correction: implementation and verification

15 November 2026. Status: {state}. The current model contains **{result['part_count']} registered parts**. This report implements the approved [gap analysis and specification](TRAILBOARD_GAP_ANALYSIS.md); its before figures remain preserved as the 928-part review snapshot. An [illustrated PDF](trailboard-correction.pdf) is provided beside this file.

The square plaque-like return, pointed head and generic leaf pattern have been replaced with the composition traced from HAER Sheet 1. The boards now have an oblique aft return, broad unequal curls, a shaped enclosure around KATHRYN, the original glyph contours, and a hooked head with eye, mouth/jaw and feather regions. The separate headrails now follow their identified Sheet 4 profile and plan positions.

## What changed

- The ornament comes from original native scan regions, not a substituted font, stock bird or repeated sine wave. Small enclosed stipple is excluded. White regions on foreground objects outside the facing are excluded, including the incidental fragment found in the first build.

- Source border and painted-field boundaries replace the old uniform offsets. Each legitimate separate carving island is registered. A clipped region that splits into two pieces retains both, rather than dropping the smaller piece or adding an invented connecting bridge.

- Seven traced glyphs and their counters form the name. The port-side word uses a declared reflection within the reserved name field so that both outward faces read KATHRYN. The original name enclosure and its two scroll terminals are present.

- The eye and mouth separator are seated on the facing. The mouth remains a shallow dark negative region; the drawing does not establish a through-opening in the timber. The inferred fixing stations remain F = 51.5, 56.0 and 60.0 ft, but their vertical positions are in the lower band, clear of the name. Matching passages in facing, backing and relief move together.

- The visible headrail spans follow the identified item-11 plan and profile picks. Their after ends retain a short fitted transition to the accepted hull rails. The related knees and walking-board bearer feet follow the corrected rails. The hidden transition remains an explicitly inferred detail.

- The model has 96 more registered parts than the 928-part baseline because the actual source ornament islands are retained separately. The accepted hull, stern, mast, complete spar, Samson-post station and jib geometry retain their baseline bounds. **893 fixed-part witnesses** were compared.

![Current complete bow profile with source-derived ornament and corrected headrails.](images/trailboard_correction/after-profile.png)

## Source tracing and coordinate transfer

The [target ledger](../references/drawing_package/trailboard_targets.json) records native source pixels, source hashes, semantic roles, closed paths, holes, region seeds, assumptions, physical transforms, held-out landmarks and occlusion masks. The [SVG overlay](../references/drawing_package/trailboard_traces/source-trace-overlay.svg) and [lossless trace overlay](../references/drawing_package/trailboard_traces/source-trace-overlay.png) retain the relationship to the original scan. The extraction is reproducible with `python docs/tools/trace_trailboards.py` and does not modify the originals.

Sheet 4 controls the physical body envelope and rail placement. Sheet 1 supplies ornament contours and proportions. The whole design uses one declared longitudinal/depth transfer, blending into a uniform native mapping at the head; individual leaves and letters are not independently fitted. The original common drawing registration is retained. Source geometry is in full-size feet; registered geometry is in millimetres at 304.8 mm per foot.

Fourteen source stations were held out of the fit: independent upper/lower body points and rail points. Native trace error, historical source uncertainty and CAD contact tolerance are checked separately. The inverse S01 overlay below checks the declared surface transfer; it does not replace the independent physical S04 comparisons.

![Original ornament with actual exported CAD contours returned through the inverse common source mapping.](images/trailboard_correction/source-ornament-after.png)

![Actual board and headrail over the original Sheet 4 profile, at the common physical registration.](images/trailboard_correction/source-profile-after.png)

![Actual board and headrail over the original Sheet 4 plan. The after handoff to the accepted hull remains qualified.](images/trailboard_correction/source-plan-after.png)

## Corrected faces and details

The two isolated faces below use matching camera scales. They show the actual completed export in its native materials, with the remainder of the boat hidden. The name reflection affects the lettering placement and orientation; the head and decorative design still face forward on each side.

![Corrected starboard face: traced frame, scrolls, name enclosure, letters and head.](images/trailboard_correction/after-starboard.png)

![Corrected port face: the name reads outward while the head still points forward.](images/trailboard_correction/after-port.png)

![Corrected head close-up, with the eye, hooked beak, dark mouth/jaw region and feather contours identified.](images/trailboard_correction/after-head.png)

![Corrected name enclosure and traced glyphs, with the lower-band fixing clear of the letters.](images/trailboard_correction/after-name.png)

## Comparison with the drawing and photograph

These are appearance comparisons. The source illustration has no independent dimensional scale, and the photograph is in perspective. The actual physical residuals are reported separately below. The original [LOC-P06 crop and full-frame context](images/trailboard_review/source-loc-p06-context.png), [color transparency context](images/trailboard_review/source-loc-c01-context.png), captions and master hashes remain in the [review source record](images/trailboard_review/sources.json).

The source line work outlines the glyphs; this does not prove hollow physical lettering. The implementation uses the traced drawing-state contours as filled glyph strokes with counters. The serif-like appearance in the port photograph remains a documented photo-state observation, rather than a reason to claim that a generic font is an exact match.

![Original HAER ornament above the current starboard face. This comparison shows composition, not an independent physical scale.](images/trailboard_correction/comparison-drawing.png)

![Original LOC-P06 port photograph above the current port face. Perspective and paint-state qualifications remain explicit.](images/trailboard_correction/comparison-photo.png)

## Assembly and retained assumptions

Facing thickness remains **1.44 in**, common backing width **6.00 in**, and net relief stand-off approximately **0.36 in**. The green/maroon/pale-gold palette is retained. These are provisional reconstruction values, not newly measured historical dimensions or calibrated paint specifications. Source ink roughness is bounded by the native trace tolerance; it is not interpreted as a field of chisel marks or drilled stipple.

The body and its source-traced return fit the existing longhead/stem structure. Fixing passages and visible lower-band heads are coordinated. The fitted source rail/hull transition and unprinted fastening dimensions remain declared assumptions. Neither the facing nor a favorable rendering is used to conceal a missing primary spar attachment.

![Current quarter view of the completed bow, with the full spar and fitted decorative assembly.](images/trailboard_correction/after-quarter.png)

![Current plan with spar hidden to show the facing stack and independently placed headrails.](images/trailboard_correction/after-plan.png)

![Exposed backing and attachments with one facing hidden.](images/trailboard_correction/after-underside.png)

## Verification results

- Completed SOMA build: **{result['part_count']} valid registered parts**, status OK and zero warnings. The current model STEP and viewer cache were regenerated by the official build.

- **AC-01:** 893 accepted fixed-part bounding witnesses agree within the 0.1 mm check tolerance. The source drawing hashes are checked against the pinned originals.

- **AC-02:** maximum held-out physical source residual **{physical:.6f} ft**, or **{physical*12:.3f} in**, against the provisional **0.20 ft** historical envelope. No component is independently moved to improve an overlay.

- **AC-03:** actual exported outer-profile contour error **{outer:.3f} original pixels**, against the six-pixel digital trace limit.

- **AC-04/05:** the head and all source carving regions are present. Maximum ornament contour error **{ornament:.3f} original pixels**. Region checks run in both directions against native contours, outside the recorded occlusion and inferred-fixing masks.

- **AC-06:** fourteen glyphs compared across both faces, maximum error **{glyph:.3f} original pixels**. No unintended fixing-to-letter contact was found.

- **AC-07:** every checked region is a valid solid and contacts its board; maximum region-to-board separation **0.000 mm**. No unintended board-to-spar, board-to-headrail or board-to-backing common volume exceeded the stated limit. Paint and relief embed remain classified separately from timber interference.

- **AC-08:** thickness, depth, palette, photo state and hidden fitting assumptions are retained explicitly in the target and acceptance records.

- **AC-09:** maximum independent rail-profile residual **{rail:.6f} ft**. Both modeled rail handoffs contact their accepted hull rails, with measured separation **0.000 mm**.

- **AC-10:** {commit_note}

The [complete machine-readable acceptance](images/trailboard_correction/acceptance.json) contains per-region errors, contact measurements, held-out point residuals and the disposition of every TB finding. The [committed-build record](images/trailboard_correction/committed-build.json) identifies the independently rebuilt geometry commit and its image/source fingerprints. The previously pending bow-remedy source and checks are included with the geometry so that a repository checkout contains all required dependencies.

All eleven [README gallery images](../README.md) and the images in the [bow implementation note](BOWSPRIT_REMEDY_IMPLEMENTATION.md) are regenerated from this completed model. The original 928-part review figures remain before evidence and are labeled accordingly in the gap analysis.

## Reproduction

Run `soma build`, then `python src/checks/check_trailboards.py`, `python src/checks/check_bow_attachment.py` and the repository's scale/deck/rigging regressions. `python docs/tools/build_trailboard_correction.py --render VIEW` creates each of profile, starboard, port, head, name, quarter, plan and underside in a fresh process. Run `--overlays` and `--comparisons` for the source witnesses, and `python src/checks/render_readme_images.py` for the README gallery. The source-derived JSON is a model input and must be present in a clean checkout.

The [original gap analysis](TRAILBOARD_GAP_ANALYSIS.md), original scans and archived photographs remain the source specification. This implementation closes the identified visual composition defects while retaining the stated limits of the evidence.
'''
    (ROOT/'docs/TRAILBOARD_CORRECTION.md').write_text(text)
    print('TRAILBOARD_CORRECTION.md',flush=True)


def pdfs():
    import importlib.util
    spec=importlib.util.spec_from_file_location('trailboard_review_pdf',ROOT/'docs/tools/build_trailboard_review.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.pdf(ROOT/'docs/TRAILBOARD_CORRECTION.md',ROOT/'docs/trailboard-correction.pdf',
               '15 November 2026 | Implemented trailboard correction | Qualified dimensions and source states remain recorded',
               'Kathryn - trailboard correction and exported-model verification')
    module.pdf()


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--render',choices=VIEWS)
    p.add_argument('--overlays',action='store_true');p.add_argument('--comparisons',action='store_true')
    p.add_argument('--report',action='store_true');p.add_argument('--pdf',action='store_true');a=p.parse_args()
    if a.render:render(a.render)
    if a.overlays:overlays()
    if a.comparisons:comparisons()
    if a.report:write_report()
    if a.pdf:pdfs()
