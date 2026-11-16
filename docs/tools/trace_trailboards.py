"""Trace HAER line-work into a provenance-rich ornament ledger (no CAD writes).

White connected regions delineated by original ink provide the carving and
letter contours. Small enclosed stipple is removed, while deliberate counters
and mouth regions are retained/classified. The source is never modified.
"""
import hashlib
import json
from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/kathryn-trailboard-traces-mpl')
import numpy as np
from scipy import ndimage as ndi
from PIL import Image, ImageDraw, ImageFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'references/drawing_package/trailboard_traces'
DATA = ROOT / 'references/drawing_package/trailboard_targets.json'
IMAGE = ROOT / 'references/drawing_package/S01/S01-V03/native.png'
SHEAR, V0 = .19, 900


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_svg(features):
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="3960" height="2107" viewBox="0 0 3960 2107">',
         '<image href="../S01/S01-V03/native.png" width="3960" height="2107"/>']
    for feature in features:
        for island, polygon in enumerate(feature['polygons'], 1):
            for ring, points in enumerate([polygon['outer'], *polygon.get('holes', [])]):
                coords=' '.join(f'{x},{y}' for x,y in points)
                ring_id=f'{feature["id"]}-island-{island}-ring-{ring}'
                svg.append(f'<polygon id="{ring_id}" points="{coords}" fill="none" stroke="red" stroke-width="2"/>')
    svg.append('</svg>')
    (OUT/'source-trace-overlay.svg').write_text('\n'.join(svg)+'\n')


def rdp(points, tolerance=1.4):
    p = np.asarray(points, float)
    if len(p) <= 2:
        return p
    d = p[-1] - p[0]
    if np.linalg.norm(d) < 1e-10:
        distance = np.linalg.norm(p - p[0], axis=1)
    else:
        t = np.clip(((p - p[0]) @ d) / (d @ d), 0, 1)
        distance = np.linalg.norm(p - p[0] - t[:, None] * d, axis=1)
    k = int(np.argmax(distance))
    if distance[k] <= tolerance:
        return p[[0, -1]]
    return np.vstack((rdp(p[:k + 1], tolerance)[:-1], rdp(p[k:], tolerance)))


def native(points):
    p = np.asarray(points, float).copy()
    p[:, 1] += V0 - SHEAR * p[:, 0]
    return np.round(p, 3).tolist()


def paths(mask):
    ys, xs = np.where(mask)
    if not len(xs):
        return []
    x0, x1, y0, y1 = xs.min() - 2, xs.max() + 3, ys.min() - 2, ys.max() + 3
    x0, y0 = max(0, x0), max(0, y0)
    fig, ax = plt.subplots()
    contour = ax.contour(mask[y0:y1, x0:x1].astype(float), levels=[.5])
    loops = []
    for vertices in contour.allsegs[0]:
        if len(vertices) < 5:
            continue
        p = vertices + [x0, y0]
        # Split a ring away from its start so the closed simplifier is stable.
        p = np.vstack((p[:-1], p[:1]))
        far = int(np.argmax(np.linalg.norm(p - p[0], axis=1)))
        p = np.vstack((rdp(p[:far + 1])[:-1], rdp(p[far:])[:-1]))
        if len(p) < 3:
            continue
        area = .5 * np.sum(p[:, 0] * np.roll(p[:, 1], -1) - np.roll(p[:, 0], -1) * p[:, 1])
        loops.append((float(area), p))
    plt.close(fig)
    loops.sort(key=lambda item: abs(item[0]), reverse=True)
    if not loops:
        return []
    sign = np.sign(loops[0][0])
    from matplotlib.path import Path as MplPath
    return [{'outer': native(p), 'holes': [native(q) for a, q in loops[1:] if np.sign(a) != sign and MplPath(p).contains_point(q.mean(axis=0))]}
            for a, p in loops if np.sign(a) == sign]


def fill_small_holes(mask, max_area=35):
    holes = ndi.binary_fill_holes(mask) & ~mask
    labels, count = ndi.label(holes)
    sizes = np.bincount(labels.ravel())
    keep = sizes <= max_area
    keep[0] = False
    return mask | keep[labels]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    im = Image.open(IMAGE).convert('L')
    flat = im.transform((3960, 500), Image.Transform.AFFINE,
                        (1, 0, 0, -SHEAR, 1, V0), resample=Image.Resampling.NEAREST, fillcolor=255)
    white = np.asarray(flat) > 128
    labels, _ = ndi.label(white)
    slices = ndi.find_objects(labels)
    glyphs = {'K': 6004, 'A': 6034, 'T': 5988, 'H': 6035, 'R': 5992, 'Y': 6038, 'N': 6113}
    # Original native source has this precise hash; these region IDs are tied
    # to that raster and the declared shear, not an OCR/font reconstruction.
    assert sha(IMAGE) == '1055509566f971f1d0d6c6542abb8607e47c8a4dc5c5e331a452955255e0d772'
    regions = {}
    for k, sl in enumerate(slices, 1):
        if sl is None:
            continue
        yy, xx = sl
        if xx.start < 170 or xx.stop > 3712 or yy.start < 125 or yy.stop > 411:
            continue
        a = labels[sl] == k
        area = int(a.sum())
        if area < 120:
            continue
        filled = ndi.binary_fill_holes(a)
        fraction = float((filled & ~a).sum() / filled.sum())
        if fraction > .02 and k != 3213 and k not in glyphs.values():
            continue
        if xx.start > 1190 and xx.stop < 1995 and yy.start > 242 and k not in glyphs.values():
            continue
        if k in (3800, 4484, 4759):  # eye, beak and mouth negatives are classified separately
            continue
        regions[k] = (area, fraction)
    features = []
    classed = np.zeros((*white.shape, 3), np.uint8)
    classed[:] = [46, 28, 23]
    for k, (area, fraction) in regions.items():
        mask = labels == k
        char = next((c for c, label in glyphs.items() if label == k), None)
        if char:
            # Half of the printed boundary stroke belongs to the visible glyph.
            # Three native pixels stay within the approved six-pixel trace budget.
            mask = ndi.binary_dilation(mask, iterations=3)
            mask = fill_small_holes(mask)
            if char == 'R':
                mask &= ~ndi.binary_dilation(labels == 6122, iterations=1)
            fid, role = 'glyph-' + char, 'letter'
        else:
            mask = fill_small_holes(mask, 250 if k == 3213 else 35)
            fid = {3621: 'border-upper', 5467: 'border-lower', 3463: 'head-face',
                   3213: 'neck-ground', 5441: 'aft-scroll-name-enclosure',
                   5567: 'name-enclosure-upper', 6259: 'name-enclosure-lower',
                   5151: 'aft-leaf-upper', 5896: 'aft-leaf-lower'}.get(k, f'carving-region-{k}')
            role = 'border' if k in (3621, 5467) else 'head' if k >= 3213 and k <= 5060 and  slices[k-1][1].start > 3200 else 'ornament'
        polygons = paths(mask)
        if not polygons:
            continue
        yy, xx = np.where(labels == k)
        seed = [int(xx[len(xx)//2]), int(yy[len(yy)//2])]
        feature = dict(id=fid, source_id='S01-V03', source_sha256=sha(IMAGE),
                       native_points=polygons[0]['outer'], closed=True, holes=polygons[0]['holes'],
                       polygons=polygons, role=role, evidence_class='traced original scan',
                       mapping_id='S01-to-S04-common-surface', region_seed_native=native([seed])[0],
                       region_pixels=area, removed_stipple_fraction=fraction,
                       notes='Printed boundary half-stroke included' if char else 'Small closed stipple excluded; contours retained')
        if char:
            feature['character'] = char
        features.append(feature)
        classed[mask] = [232, 207, 142] if role != 'letter' else [250, 230, 170]
    eye = fill_small_holes(ndi.binary_dilation(labels == 3800, iterations=2))
    features.append(dict(id='eye', source_id='S01-V03', source_sha256=sha(IMAGE), native_points=paths(eye)[0]['outer'],
                         closed=True, holes=[], polygons=paths(eye), role='eye', evidence_class='traced original scan',
                         mapping_id='S01-to-S04-common-surface', notes='Dark eye follows the observed eye contour; depth remains a representation assumption'))
    classed[eye] = [15, 20, 23]
    # White mouth is a recessed/painted negative, not an unproven through-hole.
    mouth = fill_small_holes(ndi.binary_dilation(labels == 4759, iterations=1))
    features.append(dict(id='mouth', source_id='S01-V03', source_sha256=sha(IMAGE), native_points=paths(mouth)[0]['outer'],
                         closed=True, holes=[], polygons=paths(mouth), role='recess', evidence_class='traced original scan',
                         mapping_id='S01-to-S04-common-surface', notes='Mouth separator represented as a dark recessed region, not a through-cut'))
    classed[mouth] = [18, 21, 22]
    # Trace the frame's actual outer curves, retaining the source's canted return.
    def boundary(k, which):
        points = []
        for x in range(340, 3301, 12):
            y = np.where(labels[:, x] == k)[0]
            if len(y):
                points.append([x, float(y.min() - 2 if which == 'top' else y.max() + 2)])
        return points
    top, bottom = boundary(3621, 'top'), boundary(5467, 'bottom')
    head = [(3332,174),(3343,149),(3352,139),(3350,126),(3335,110),
            (3390,132),(3450,148),(3508,155),(3540,155),(3520,145),(3515,125),
            (3532,136),(3560,140),(3580,138),(3600,145),(3620,157),
            (3655,157),(3680,162),(3698,172),(3710,185),(3713,196),
            (3706,196),(3699,185),(3685,180),(3675,192),(3660,213),
            (3635,223),(3580,231),(3500,235),(3430,244),(3370,251),(3300,256)]
    outer = [[315,145], *top, *head, *reversed(bottom), [195,375],[171,359]]
    source_outer = native(outer)
    features.insert(0, dict(id='outer-facing', source_id='S01-V03', source_sha256=sha(IMAGE),
                            native_points=source_outer, closed=True, holes=[], polygons=[{'outer':source_outer,'holes':[]}],
                            role='outline', evidence_class='traced original scan; neck/chain occlusion qualified',
                            mapping_id='S01-to-S04-common-surface', notes='Canted aft return; native frame edges; head anchors follow original ink, not the old CAD polygon'))
    cap = native([(315,145),(329,150),(295,195),(215,318),(195,375),(171,359)])
    features.append(dict(id='aft-frame-return', source_id='S01-V03', source_sha256=sha(IMAGE), native_points=cap,
                         closed=True, holes=[], polygons=[{'outer':cap,'holes':[]}], role='border', evidence_class='traced original scan',
                         mapping_id='S01-to-S04-common-surface', notes='Source oblique bevel/return, independently traced from the outline'))
    inner_top, inner_bottom = [], []
    for x in range(340,3301,12):
        t, b = np.where(labels[:,x]==3621)[0], np.where(labels[:,x]==5467)[0]
        if len(t) and len(b):
            inner_top.append([x,float(t.max()+2)])
            inner_bottom.append([x,float(b.min()-2)])
    field=native([[295,195],*inner_top,[3360,229],*reversed(inner_bottom),[215,318]])
    features.append(dict(id='paint-field',source_id='S01-V03',source_sha256=sha(IMAGE),native_points=field,
                         closed=True,holes=[],polygons=[{'outer':field,'holes':[]}],role='field',evidence_class='traced original scan',
                         mapping_id='S01-to-S04-common-surface',notes='Field follows the observed inner frame edges; no uniform global inset'))
    # Bound the classification by the observed facing. This excludes small
    # white patches on the foreground rail/chain from becoming floating carving.
    outer_mask=Image.new('L',flat.size,0);ImageDraw.Draw(outer_mask).polygon(outer,fill=255)
    inside=np.asarray(outer_mask)>0
    kept=[];excluded=[]
    for feature in features:
        if feature['role']=='outline':kept.append(feature);continue
        raster=Image.new('L',flat.size,0);draw=ImageDraw.Draw(raster)
        for polygon in feature['polygons']:
            p=np.asarray(polygon['outer']);p[:,1]-=V0-SHEAR*p[:,0]
            draw.polygon([tuple(v) for v in p],fill=255)
            for hole in polygon.get('holes',[]):
                p=np.asarray(hole);p[:,1]-=V0-SHEAR*p[:,0]
                draw.polygon([tuple(v) for v in p],fill=0)
        clipped=(np.asarray(raster)>0)&inside
        polygons=paths(clipped)
        if not polygons:
            excluded.append(feature['id']);continue
        feature.update(polygons=polygons,native_points=polygons[0]['outer'],holes=polygons[0]['holes'])
        kept.append(feature)
    features=kept
    # The source guide controls the mapping for every motif together.
    guide = []
    for x in range(340, 3301, 12):
        a, b = np.where(labels[:,x] == 3621)[0], np.where(labels[:,x] == 5467)[0]
        if len(a) and len(b):
            guide.append([x, float(a.min()-2), float(b.max()+2)])
    source = json.loads((ROOT/'references/drawing_package/bow_remedy_registration.json').read_text())
    reg = source['registration'];a,b=reg['F_from_S04_grid_x'];unit=reg['profile_grid_height_ft_per_unit']
    deck = source['spar']['heel_z']-(318.5-310.1)*unit
    top_grid = [[1066,330.25],[1100,322.625],[1120,318.24],[1150,312.21],[1180,306.08],[1210,298.70],[1230,291.70]]
    bottom_grid = [[1066,344.40],[1100,336.78],[1120,331.20],[1150,325.02],[1180,316.65],[1210,306.03],[1230,298.01]]
    fy = lambda points:[[a*x+b,deck+(318.5-y)*unit] for x,y in points]
    physical = dict(registration=reg, deck_anchor_z_ft=deck, upper_grid_points=top_grid, lower_grid_points=bottom_grid,
                    upper_fz=fy(top_grid),lower_fz=fy(bottom_grid),
                    headrail_profile_centres_grid=[[1015,320.75],[1190,295.60]],
                    headrail_plan_grid=[[1015,681],[1112,661.5],[1152,652.5],[1190,645]],
                    handoff='Short fitted transition to the unchanged accepted hull-rail root; concealed handoff is inferred')
    held=[]
    for gx,gy,role in [(1075,329.05,'upper'),(1110,320.33,'upper'),(1135,315.15,'upper'),
                        (1165,309.17,'upper'),(1200,301.25,'upper'),(1220,296.11,'upper'),
                        (1110,334.04,'lower'),(1135,329.98,'lower'),(1165,320.73,'lower'),
                        (1200,309.57,'lower'),(1220,302.04,'lower'),
                        (1100,308.575,'rail'),(1150,301.70,'rail'),(1180,297.16,'rail')]:
        held.append(dict(source_id='S04-V01',grid_xy=[gx,gy],forward_ft=a*gx+b,height_ft=deck+(318.5-gy)*unit,
                         role=role,used_in_fit=False,uncertainty_ft=.20))
    data=dict(schema_version=1,target_state='HAER drawing arrangement and S01 ornament; vessel photos as cross-checks',
              sources={'S01-V03':{'path':str(IMAGE.relative_to(ROOT)),'sha256':sha(IMAGE),'native_size':list(im.size)},
                       'S04':source['source_files']['S04']},physical_transforms=physical,
              surface_mapping=dict(id='S01-to-S04-common-surface',flat_shear=SHEAR,flat_vertical_offset_px=V0,
                  source_body_guides_flat=guide,source_root_x=315,source_tip_x=3713,
                  physical_root_f=a*1066+b,physical_tip_f=a*1248.2+b,
                  head_anchor_native=[3713,195+V0-SHEAR*3713],head_anchor_grid=[1248.2,289.20],
                  head_blend_flat_x=[3050,3300],letter_reflection_flat_x=[1250,1910],
                  description='Common longitudinal/depth transfer for all features; smoothly joins a uniform native head mapping. No per-leaf or per-letter fitting.'),
              features=features,held_out_landmarks=held,excluded_foreground_regions=excluded,
              uncertainty_masks=[{'source_id':'S01-V03','native_box':[3250,350,3470,620],'reason':'Neck/chain overlap; visible feather boundaries retained, concealed continuation is reconstructed'},
                                 {'source_id':'S04-V01','grid_box':[1050,330,1070,350],'reason':'Aft facing return partly hidden by stem; S01 determines its obliquity'}],
              assumptions={'facing_thickness_ft':.12,'backing_width_ft':.5,'relief_extrusion_ft':.035,'relief_embed_ft':.005,
                           'fastener_height_fraction':.14,'fastener_placement':'Unprinted fitting detail; lower band keeps holes and heads clear of the name',
                           'palette':'Retain current green/maroon/pale gold; not calibrated historic paint values',
                           'mouth':'Dark recess boundary, not an unsupported through-cut',
                           'lettering':'S01 traced glyph boundaries; filled strokes, with counters; serif-like P06 photo state recorded separately',
                           'hidden_handoff':'Short source/hull transition remains a fitted reconstruction'},
              review_status='Native contours inspected; physical held-out tests and exported-solid checks required before acceptance')
    DATA.write_text(json.dumps(data,indent=2)+'\n')
    classed[np.asarray(outer_mask)==0]=[237,241,246]
    Image.fromarray(classed).save(OUT/'classified-source.png')
    overlay=flat.convert('RGB');d=ImageDraw.Draw(overlay)
    for feature in features:
        color='#e02035' if feature['role']=='outline' else '#087eaa' if feature['role']=='letter' else '#168b53'
        for poly in feature['polygons']:
            points=np.array(poly['outer']);points[:,1]-=V0-SHEAR*points[:,0]
            d.line([tuple(p) for p in np.vstack((points,points[:1]))],fill=color,width=2)
    overlay.save(OUT/'source-trace-overlay.png')
    write_svg(features)
    print('Features:',len(features),'carving regions:',sum(f['role'] in ('border','ornament','head') for f in features),flush=True)


if __name__=='__main__':main()
