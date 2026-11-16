"""Capture the current trailboards, annotate primary sources, and typeset the review.

This is an evidence tool. It never changes CAD, app parameters, or references.
Run --capture once, --render NAME in a fresh process for each view, --sources,
then --pdf. The frozen source/build hashes reject later geometry silently
replacing this as-found review. The PDF uses the installed matplotlib backend.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import textwrap

os.environ.setdefault('MPLCONFIGDIR', '/tmp/kathryn-trailboard-matplotlib')
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/images/trailboard_review'
CACHE = Path('/tmp/kathryn-trailboard-sources')
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'src/checks')]
from PIL import Image, ImageDraw, ImageFont, ImageOps

INK = '#173044'
RED = '#be3037'
BLUE = '#086d9f'
GREEN = '#187447'
AMBER = '#976000'
PURPLE = '#7836a1'
COLORS = [RED, BLUE, GREEN, PURPLE]
FONTS = '/usr/share/fonts/truetype/dejavu/'
MANIFEST = ROOT / 'references/drawing_package/manifest.json'
LEDGER = ROOT / 'references/drawing_package/bow_remedy_registration.json'


def font(size, bold=False):
    return ImageFont.truetype(FONTS + ('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'), size)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def source_files():
    files = [ROOT / 'model.py', *sorted((ROOT / 'src/parts').glob('*.py')), LEDGER]
    if (ROOT / 'parameters.json').exists():
        files.append(ROOT / 'parameters.json')
    return {str(p.relative_to(ROOT)): sha(p) for p in files}


def guard():
    record = json.loads((OUT / 'provenance.json').read_text())
    changed = [name for name, digest in record['model_files'].items() if sha(ROOT / name) != digest]
    changed += [name for name, digest in record['build_files'].items() if sha(ROOT / name) != digest]
    if (OUT / 'sources.json').exists():
        for evidence in json.loads((OUT / 'sources.json').read_text()).values():
            if 'source' in evidence and sha(ROOT / evidence['source']) != evidence['source_sha256']:
                changed.append(evidence['source'])
            if 'crop_sha256' in evidence and sha(OUT / evidence['crop_file']) != evidence['crop_sha256']:
                changed.append(evidence['crop_file'])
    if changed:
        raise RuntimeError('Frozen as-found review changed; use a new evidence directory: ' + ', '.join(changed))
    return record


def capture():
    if (OUT / 'provenance.json').exists():
        guard()
        return
    from soma.measure import Model
    from parts import bow
    from parts.bow_layout import LONGHEAD
    build = json.loads((ROOT / '.soma/build.json').read_text())
    assert build['status'] == 'ok' and not build['warnings']
    assert len(build['parts']) == 928
    assert not [name for name in source_files() if (ROOT / name).stat().st_mtime > build['started']], 'Sources newer than export'
    model = Model(ROOT / '.soma')
    records = {p['name']: p for p in model.map['parts']}
    names = [n for n in records if any(k in n.lower() for k in ('trailboard', 'longhead', 'scrollwork'))]
    names += ['Port projecting headrail', 'Starboard projecting headrail', 'Bowsprit']
    shapes = {n: model.shape(records[n]['id']).scale(1 / 304.8) for n in names}
    bounds = {}
    for n, s in shapes.items():
        b = s.BoundingBox()
        bounds[n] = dict(valid=s.isValid(), solids=len(s.Solids()), volume_ft3=s.Volume(),
                         across_ft=[b.xmin, b.xmax], forward_ft=[25 - b.ymax, 25 - b.ymin],
                         height_ft=[b.zmin, b.zmax])
    contacts = {}
    for label in ('Port', 'Starboard'):
        board = shapes[label + ' trailboard board']
        for other in ('Longhead trailboard backing', label + ' projecting headrail'):
            contacts[label + ' board / ' + other] = dict(
                separation_mm=board.distance(shapes[other]) * 304.8,
                common_ft3=board.intersect(shapes[other]).Volume())
    samples = []
    for f in (51, 52, 54, 56, 58, 60, LONGHEAD['body_tip_f']):
        samples.append(dict(forward_ft=f, upper_ft=bow.panel_top(f), lower_ft=bow.panel_bottom(f),
                            depth_in=12 * (bow.panel_top(f) - bow.panel_bottom(f))))
    files = ['.soma/build.json', '.soma/model.glb', '.soma/model.map.json', 'output/model.step']
    record = dict(review_date='2026-11-15', head=subprocess.check_output([str(ROOT / 'project-git'), 'rev-parse', 'HEAD'], text=True).strip(),
                  basis='928-part working-tree export; CAD source changes are not committed at capture',
                  build_finished=datetime.datetime.fromtimestamp(build['finished'], datetime.timezone.utc).isoformat(),
                  parts=len(build['parts']), warnings=build['warnings'], model_files=source_files(),
                  build_files={n: sha(ROOT / n) for n in files}, units='full-size feet; exported BREP divided by 304.8',
                  geometry=bounds, contacts=contacts, board_depth_samples=samples,
                  capture_status='geometry evidence only; no historical-shape acceptance asserted')
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'provenance.json').write_text(json.dumps(record, indent=2) + '\n')
    print('Captured', len(bounds), 'exported solids; contacts:', contacts, flush=True)


def plate(image, title, subtitle, marks, notes, name):
    """Numbered leaders point to evidence; explanations occupy a separate band."""
    width = 1800
    ratio = width / image.width
    im = image.convert('RGB').resize((width, round(image.height * ratio)), Image.Resampling.LANCZOS)
    header, footer = 110, 290
    canvas = Image.new('RGB', (width, im.height + header + footer), 'white')
    canvas.paste(im, (0, header))
    draw = ImageDraw.Draw(canvas)
    draw.text((28, 15), title, font=font(29, True), fill=INK)
    draw.text((28, 63), subtitle, font=font(20), fill='#526473')
    for i, (point, offset) in enumerate(marks):
        x, y = point[0] * ratio, point[1] * ratio + header
        tx = max(24, min(width - 24, x + offset[0]))
        ty = max(header + 24, min(header + im.height - 24, y + offset[1]))
        c = COLORS[i % 4]
        draw.ellipse((x - 7, y - 7, x + 7, y + 7), outline=c, width=3)
        draw.line((x, y, tx, ty), fill=c, width=3)
        draw.ellipse((tx - 19, ty - 19, tx + 19, ty + 19), fill='white', outline=c, width=3)
        draw.text((tx, ty), str(i + 1), font=font(23, True), fill=c, anchor='mm')
    for i, note in enumerate(notes):
        col, row = i % 2, i // 2
        text = '\n'.join(textwrap.wrap(f'{i + 1}. {note}', width=67))
        draw.multiline_text((28 + col * 890, header + im.height + 18 + row * 113), text,
                            font=font(24), fill=COLORS[i % 4], spacing=5)
    draw.text((28, canvas.height - 29), 'KATHRYN / TRAILBOARD REVIEW / AS FOUND 15 NOV 2026 / Annotation numbers are local to each figure', font=font(15), fill='#526473')
    canvas.save(OUT / name)
    print(name, flush=True)


VIEWS = {
    'context': ((-1, 0, 0), (0, -31.0, 9.1), 7.6),
    'starboard': ((-1, 0, 0), (0, -31.5, 9.0), 4.9),
    'port': ((1, 0, 0), (0, -31.5, 9.0), 4.9),
    'quarter': ((-.75, -.55, .48), (0, -31.0, 9.3), 6.2),
    'plan': ((0, 0, 1), (0, -31.5, 9.0), 7.2),
    'head': ((-1, 0, 0), (0, -36.7, 10.4), 1.35),
}


def render(name):
    guard()
    import build_bow_gap_assets as renderer
    renderer.HILITE.clear()
    scene = renderer.ModelScene()
    from parts.params import boat_point
    allnames = [p['name'] for p in scene.parts]
    ornaments = [n for n in allnames if any(k in n.lower() for k in ('trailboard', 'longhead', 'scrollwork'))]
    hide = ['Jib sail (S08 demonstration)', 'Main sail (S08 demonstration)']
    if name in ('starboard', 'port', 'head'):
        label = 'Port' if name == 'port' else 'Starboard'
        show = {n for n in ornaments if n.startswith(label)}
        hide = [n for n in allnames if n not in show]
    elif name == 'plan':
        show = set(ornaments + ['Port projecting headrail', 'Starboard projecting headrail', 'Bowsprit stem-head extension'])
        hide = [n for n in allnames if n not in show]
    direction, focus, scale = VIEWS[name]
    side = 1 if name == 'port' else -1
    witnesses = [boat_point(side * .37, 50.40591, 7.55), boat_point(side * .40, 54.4, 8.45),
                 boat_point(side * .40, 58, 9.4), boat_point(side * .40, 62.05, 10.65)]
    notes = ['Aft edge is a square station cut; compare the oblique return in D1.',
             'Untraced DejaVu Serif glyphs and fixed tilt need comparison with both drawing and photo.',
             'Repeated sine-wave vine and leaf shapes substitute for the traced scroll pattern.',
             'Polygonal nose and one eye omit the hooked beak, jaw and feather details.']
    title = {'context': 'C1 / Current bow profile: placement and ornament are separate questions',
             'starboard': 'C2 / Current starboard face: actual exported carving, isolated',
             'port': 'C3 / Current port face: lettering reads outward on this side too',
             'quarter': 'C4 / Current quarter view: constant-width central backing',
             'plan': 'C5 / Current plan: backing and side boards with spar hidden',
             'head': 'C6 / Current forward head: eye present, carved anatomy absent'}[name]
    if name == 'quarter':
        notes = ['Both decorated faces sit on a common central backing; this is not the old floating-board version.',
                 'The aft board termination must be checked against the hull and the ornament drawing together.',
                 'Uniform extrusion makes the ornament read as raised graphic strips.',
                 'The head has no traced beak opening or feather cuts.']
    if name == 'plan':
        witnesses = [boat_point(-.37, 54, 9), boat_point(.37, 58, 10), boat_point(0, 56, 9), boat_point(-1.6, 53, 10)]
        notes = ['Starboard board is 1.44 in thick at a constant transverse offset.',
                 'Port face is symmetric in location; this does not by itself validate historic thickness.',
                 'Backing is 6.00 in wide; total timber stack is 8.88 in before relief.',
                 'Headrails converge separately and continue aft outside this crop. Source does not dimension facing thickness.']
    if name == 'head':
        witnesses = [boat_point(-.40, 62.17, 10.68), boat_point(-.40, 62.50, 10.70),
                     boat_point(-.40, 61.70, 10.48), boat_point(-.40, 60.8, 10.1)]
        notes = ['An eye is modeled: do not report it as wholly missing.',
                 'The outline ends in straight segments; the source has a hooked, open beak.',
                 'No feather scallops or jaw separator reproduce the drawing detail.',
                 'A generic scroll approaches the head; source-specific carving topology is absent.']
    im, pts = scene.render(direction, (0, 1, 0) if name == 'plan' else (0, 0, 1), focus, scale,
                           hide=tuple(hide), points=witnesses)
    marks = [(p, ((-80 if i % 2 else 70), -80 if i < 2 else 75)) for i, p in enumerate(pts)]
    if name == 'head':
        marks = list(zip(pts, [(-70, -90), (65, -80), (70, 75), (-70, 75)]))
    assert all(8 < p[0] < im.width - 8 and 8 < p[1] < im.height - 8 for p, _ in marks), 'Witness outside view'
    plate(im, title, '928-part completed SOMA export / native materials / orthographic camera / sails hidden',
          marks, notes, 'model-' + name + '.png')


def sources():
    guard()
    manifest = json.loads(MANIFEST.read_text())
    records = {}
    def drawing(key, box):
        view = next(v for v in manifest['views'] if v['id'] == key)
        path = ROOT / 'references/drawing_package' / view['native_image']
        im = Image.open(path).convert('RGB').crop(box)
        records[key + str(box)] = dict(source=str(path.relative_to(ROOT)), source_sha256=sha(path),
                                      crop_native_view_px=box, native_view_to_sheet_translation=view['native_box'][:2],
                                      original_sheet_sha256=view['source_sha256'])
        return im
    im = drawing('S01-V03', (0, 0, 3960, 1450))
    plate(im, 'D1 / Original HAER Sheet 1: the ornament actually drawn',
          'S01-V03 / original line work / unscaled pictorial detail: use for motif and proportions',
          [((255, 1100), (-55, -80)), ((1600, 885), (-10, -85)), ((2700, 650), (0, 100)), ((3570, 420), (50, 95))],
          ['The aft end is an oblique cut with a framed return, not a vertical rectangular plaque.',
           'The name occupies a reserved field. Drawn glyph boundaries do not prove hollow painted lettering.',
           'Broad curling stems and leaves follow distinct source paths; the border turns with the panel.',
           'An eagle-like head includes eye, hooked open beak and layered feather cuts.'], 'drawing-ornament.png')
    im = drawing('S01-V03', (3000, 245, 3820, 745))
    plate(im, 'D2 / Original head detail: features to trace as separate regions',
          'Native S01-V03 crop (3000,245)-(3820,745) / enlargement, no geometric redraw',
          [((575, 135), (-80, -65)), ((704, 145), (50, 75)), ((625, 180), (50, 100)), ((430, 190), (-75, 80))],
          ['Eye and brow establish the head orientation; retain their relation to the beak.',
           'Beak hooks down and surrounds a visible opening; a pointed polygon is insufficient.',
           'Jaw and throat have separate contours instead of one uninterrupted slab.',
           'Feather divisions bridge the neck into the vine without inventing a stock emblem.'], 'drawing-head.png')
    im = drawing('S01-V03', (1050, 700, 2200, 1090))
    plate(im, 'D3 / Original name field: stroke shape, spacing and clear border',
          'Native S01-V03 crop (1050,700)-(2200,1090) / no font substitution',
          [((355, 240), (-100, -70)), ((730, 145), (45, -65)), ((1020, 95), (0, 100)), ((330, 285), (-40, 70))],
          ['Trace glyph boundaries and counters. The photo also shows serif-like details; reconcile both sources.',
           'Baseline follows the reserved name field; letter tilt and spacing need individual control.',
           'Scroll terminals frame the name rather than running through the letters.',
           'Keep the field inside its frame; preserve the continuous lower border.'], 'drawing-name.png')
    # Locked Sheet 4 registration: original scale plus the existing spar/post datum.
    from soma.measure import Model
    model = Model(ROOT / '.soma')
    parts = {p['name']: p for p in model.map['parts']}
    ledger = json.loads(LEDGER.read_text())
    a, b = ledger['registration']['F_from_S04_grid_x']
    unit = ledger['registration']['profile_grid_height_ft_per_unit']
    from parts.hull import deck_height
    from parts.params import BOW_POST_FORWARD_FT
    deck = deck_height(BOW_POST_FORWARD_FT)
    for mode, key, gb in [('profile', 'S04-V01', (1040, 285, 1255, 360)), ('plan', 'S04-V02', (1040, 600, 1255, 675))]:
        view = next(v for v in manifest['views'] if v['id'] == key)
        src = next(s for s in manifest['sources'] if s['id'] == 'S04')
        sx, sy = src['native_size'][0] / 1440, src['native_size'][1] / 960
        box = tuple(round(g * (sx if i % 2 == 0 else sy)) - view['native_box'][i % 2] for i, g in enumerate(gb))
        im = drawing(key, box)
        im.save(OUT / ('source-s04-' + mode + '-clean.png'))
        draw = ImageDraw.Draw(im)
        import numpy as np
        for name, color in [('Starboard trailboard board', RED), ('Starboard projecting headrail', BLUE)]:
            shape = model.shape(parts[name]['id']).scale(1 / 304.8)
            for edge in shape.Edges():
                points = []
                for t in np.linspace(0, 1, 2 if edge.geomType() == 'LINE' else 25):
                    p = edge.positionAt(float(t))
                    gx = ((25 - p.y) - b) / a
                    gy = 318.5 - (p.z - deck) / unit if mode == 'profile' else 636.5 - p.x / unit
                    points.append((gx * sx - view['native_box'][0] - box[0], gy * sy - view['native_box'][1] - box[1]))
                draw.line(points, fill=color, width=4)
        notes = (['Red is the actual board outline; its broad-body position broadly follows this existing registration.',
                  'The nose is a coarse polygon. Compare the black eagle outline beneath the red trace.',
                  'Blue is the separate headrail; projected overlap is not automatically a solid collision.',
                  'The red aft return is vertical; the source return is oblique. Common registration is inherited, not an independent fit.']
                 if mode == 'profile' else
                 ['The red lines show the current constant-width board stack, partly hidden beneath the spar in this plan.',
                  'The blue headrail is a separate converging timber; do not spread the boards to follow it without evidence.',
                  'This drawing supplies no direct facing-board thickness dimension. Current 1.44 in faces remain a modeling assumption.',
                  'Keep the common scale and datum for all components; do not fit each overlay independently.'])
        from parts import bow
        def at(f, z, x=0):
            gx = (f - b) / a
            gy = 318.5 - (z - deck) / unit if mode == 'profile' else 636.5 - x / unit
            return (gx * sx - view['native_box'][0] - box[0], gy * sy - view['native_box'][1] - box[1])
        if mode == 'profile':
            xr, zr = bow.headrail_point(-1, 56)
            marks = [(at(54, bow.panel_top(54)), (-65, 60)), (at(62.50, 10.70), (-35, 80)),
                     (at(56, zr), (-30, -55)), (at(bow.TRAILBOARD_ROOT_FT, bow.panel_bottom(bow.TRAILBOARD_ROOT_FT)), (40, 65))]
        else:
            xr, zr = bow.headrail_point(-1, 56)
            marks = [(at(54, 9, -.37), (-65, 60)), (at(56, zr, xr), (35, 75)),
                     (at(58, 9, .37), (-30, -70)), (at(53, 9, 0), (50, 55))]
        plate(im, 'D4 / Locked Sheet 4 profile overlay' if mode == 'profile' else 'D5 / Locked Sheet 4 plan overlay',
              'Black = original scan / red = exported board / blue = exported headrail / inherited common registration',
              marks, notes, 'drawing-' + mode + '-overlay.png')
    photo_manifest = json.loads((ROOT / 'references/loc_photos/LOC_Kathryn_photos/manifest.json').read_text())
    for identity, box, title, points, notes in [
        ('LOC-P06', (620, 1890, 1250, 2200), 'P1 / Port trailboard in the original HAER photograph',
         [(195, 145), (410, 232), (560, 280), (385, 160)],
         ['The head is forward, to the left in this photograph; the image has not been mirrored.',
          'Light lettering and ornament sit within a dark field; the name and vines remain visually distinct.',
          'The aft field returns toward the hull instead of reading as an isolated hanging sign.',
          'Rope, rail and paint wear obscure details. Use the drawing for fine motif geometry, not enlarged photo pixels.']),
        ('LOC-C01', (3000, 2030, 3570, 2250), 'P2 / Starboard trailboard in the LOC color transparency',
         [(110, 153), (270, 115), (442, 63), (210, 135)],
         ['A dark, narrow decorated field is visible along the forward longhead.',
          'Light ornament contrasts with the dark field; exact paint values cannot be sampled reliably from this small, aged image.',
          'The forward end rises toward the head under the bowsprit; preserve its anatomical outline.',
          'The opposite face also carries KATHRYN. Perspective and possible paint-state differences are not orthographic dimensions.'])]:
        record = next(r for r in photo_manifest['photos'] if r['id'] == identity)
        path = CACHE / record['master_file']
        clean = OUT / ('source-' + identity.lower() + '-crop.png')
        context = OUT / ('source-' + identity.lower() + '-context.png')
        if path.exists():
            full = Image.open(path).convert('RGB')
            full.crop(box).save(clean)
            context_im = full.copy()
            ImageDraw.Draw(context_im).rectangle(box, outline='#ed3838', width=12)
            context_im.thumbnail((1600, 1200))
            context_im.save(context)
            records[identity] = dict(url=record['master_url'], catalog=record['page_url'], caption=record['title'],
                                     original_sha256=sha(path), original_size=list(full.size), crop_original_px=box,
                                     crop_file=clean.name, crop_sha256=sha(clean), context_file=context.name,
                                     treatment='native crop, RGB conversion only; no mirroring, enhancement or invented detail')
        else:
            assert clean.exists(), 'Original photo cache absent; restore the recorded master or keep the existing clean crop'
            records[identity] = json.loads((OUT / 'sources.json').read_text())[identity]
        im = Image.open(clean)
        plate(im, title, identity + ' / original master crop / perspective witness; not a dimensional measurement',
              [(p, (-50 if i % 2 == 0 else 45, -70 if i < 2 else 70)) for i, p in enumerate(points)], notes,
              'photo-' + identity.lower() + '.png')
    (OUT / 'sources.json').write_text(json.dumps(records, indent=2) + '\n')


def pdf(source=None, target=None, footer=None, title=None):
    """Searchable PDF of the Markdown, with full-page figures for legible labels."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    from matplotlib.font_manager import FontProperties
    from matplotlib.textpath import TextToPath
    matplotlib.rcParams['pdf.fonttype'] = 42
    matplotlib.rcParams['figure.max_open_warning'] = 0
    source = Path(source) if source else ROOT / 'docs/TRAILBOARD_GAP_ANALYSIS.md'
    target = Path(target) if target else ROOT / 'docs/trailboard-gap-analysis.pdf'
    footer = footer or '15 November 2026 | Review snapshot and correction specification | See document status'
    title = title or 'Kathryn - trailboard gap analysis and implementation specification'
    pages, page, y = [], None, 0
    metrics = TextToPath()
    def newpage():
        nonlocal page, y
        page = plt.figure(figsize=(8.5, 11), facecolor='white')
        pages.append(page)
        y = 10.06
        page.text(.065, .96, 'KATHRYN / TRAILBOARDS / SOURCE EVIDENCE AND MODEL VERIFICATION', fontsize=8.2, weight='bold', color=INK)
        page.text(.065, .032, footer, fontsize=7.7, color='#526473')
        page.text(.935, .032, str(len(pages)), fontsize=8, ha='right', color='#526473')
    def clean(text):
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        return text.replace('**', '').replace('`', '').replace('\u2014', '-').replace('\u2013', '-')
    def wrap(text, size=10.2, bold=False):
        prop = FontProperties(family='DejaVu Sans', size=size, weight='bold' if bold else 'normal')
        result, current = [], ''
        for word in text.split():
            # Break hashes and long schema field names instead of overrunning the margin.
            chunks = [word[i:i+65] for i in range(0, len(word), 65)]
            for chunk in chunks:
                candidate = (current + ' ' + chunk).strip()
                if current and metrics.get_text_width_height_descent(candidate, prop, ismath=False)[0] > 521:
                    result.append(current)
                    current = chunk
                else:
                    current = candidate
        if current:
            result.append(current)
        return result
    def paragraph(text, size=10.2, bold=False, reserve=0):
        nonlocal y
        lines = wrap(clean(text), size, bold)
        h = size / 72 * 1.38
        if page is None or y - h * len(lines) - reserve < .70:
            newpage()
        for line in lines:
            page.text(.065, y / 11, line, fontsize=size, weight='bold' if bold else 'normal', va='top', color=INK)
            y -= h
        y -= .10
        # Retain usable primary-source references in the standalone PDF too.
        for label, url in re.findall(r'\[([^\]]+)\]\((https?://[^)]+)\)', text):
            for linkline in wrap(label + ': ' + url, size=8):
                if y - .16 < .70:
                    newpage()
                page.text(.075, y / 11, linkline, fontsize=8, color=BLUE, va='top', url=url)
                y -= .16
            y -= .06
    pending = []
    def flush():
        if pending:
            paragraph(' '.join(pending))
            pending.clear()
    source_lines = source.read_text().splitlines()
    for index, line in enumerate(source_lines):
        if line.startswith('!['):
            flush()
            match = re.fullmatch(r'!\[(.*?)\]\((.*?)\)', line)
            assert match, line
            newpage()
            im = Image.open(source.parent / match.group(2))
            w = 7.45
            h = w * im.height / im.width
            if h > 8.45:
                h = 8.45
                w = h * im.width / im.height
            ax = page.add_axes([(.5 + (7.5 - w) / 2) / 8.5, (9.92 - h) / 11, w / 8.5, h / 11])
            ax.imshow(im)
            ax.axis('off')
            y = 9.77 - h
            paragraph(match.group(1), size=8.8)
            page = None
        elif line.startswith('#'):
            flush()
            level = len(line) - len(line.lstrip('#'))
            following = []
            for candidate in source_lines[index + 1:]:
                if not candidate.strip():
                    if following:
                        break
                    continue
                if candidate.startswith(('#', '![')):
                    break
                following.append(candidate.strip())
            reserve = max(.60, len(wrap(clean(' '.join(following)))) * 10.2 / 72 * 1.38 + .10)
            paragraph(line.lstrip('# '), size={1:20, 2:14, 3:11.5}.get(level, 10.5), bold=True, reserve=reserve)
        elif not line.strip():
            flush()
        elif line.startswith('- ') or re.match(r'^\d+\. ', line):
            flush()
            paragraph(line)
        else:
            pending.append(line.strip())
    flush()
    with PdfPages(target) as handle:
        handle.infodict().update(Title=title,
                                Author='Kathryn project review', Subject='Annotated original drawings, photographs, exported CAD, and correction acceptance criteria')
        for fig in pages:
            handle.savefig(fig)
            plt.close(fig)
    print(target, len(pages), 'pages', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture', action='store_true')
    parser.add_argument('--render', choices=VIEWS)
    parser.add_argument('--sources', action='store_true')
    parser.add_argument('--pdf', action='store_true')
    args = parser.parse_args()
    if args.capture:
        capture()
    if args.render:
        render(args.render)
    if args.sources:
        sources()
    if args.pdf:
        pdf()
