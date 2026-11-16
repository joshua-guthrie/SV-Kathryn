"""Build after views, source overlay and sections for the longhead envelope fix.

Runs against the completed SOMA build.  The images are documentation only; the
acceptance numbers are in src/checks/check_longhead_envelope.py.
"""
from pathlib import Path
import argparse
import json
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
import cadquery as cq

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/images/trailboard_envelope_gap'
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'src/checks')]
from build_bow_gap_assets import ModelScene
from soma.measure import Model
from parts.trailboard_layout import ENVELOPE, outer_top, outer_bottom, panel_top, panel_bottom

FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans'
COLORS = {'backing': '#086d9f', 'board': '#c81e2b', 'headrail': '#0b8b8b',
          'upper': '#187447', 'lower': '#c46b00', 'spar': '#3f3f46', 'stem': '#777777'}
FT = 304.8


def font(size, bold=False):
    return ImageFont.truetype(FONT + ('-Bold' if bold else '') + '.ttf', size)


def plate(im, title, subtitle, notes, path):
    width = 1800
    ratio = width / im.width
    im = im.convert('RGB').resize((width, round(im.height * ratio)), Image.Resampling.LANCZOS)
    header, footer = 110, 200
    out = Image.new('RGB', (width, im.height + header + footer), 'white')
    out.paste(im, (0, header))
    d = ImageDraw.Draw(out)
    d.text((28, 15), title, font=font(28, True), fill='#173044')
    d.text((28, 62), subtitle, font=font(19), fill='#526473')
    for i, note in enumerate(notes):
        d.text((28, header + im.height + 20 + i * 34), note, font=font(20), fill='#173044')
    d.text((28, out.height - 28), 'KATHRYN / LONGHEAD ENVELOPE / ACTUAL COMPLETED EXPORT / source depth and hidden joints remain qualified',
           font=font(14), fill='#526473')
    out.save(OUT / path)
    print(path, flush=True)


def render(name):
    scene = ModelScene()
    names = [p['name'] for p in scene.parts]
    sails = ['Jib sail (S08 demonstration)', 'Main sail (S08 demonstration)']
    if name in ('starboard', 'port'):
        label = 'Port' if name == 'port' else 'Starboard'
        show = {n for n in names if n.startswith(label + ' trailboard') or
                n in ('Longhead trailboard backing', 'Longhead upper shoulder') or
                n.startswith(label + ' projecting headrail') or n == label + ' longhead eagle eye'}
        hide = tuple(n for n in names if n not in show)
    elif name == 'plan':
        show = {n for n in names if any(s in n.lower() for s in
                ('trailboard', 'longhead', 'projecting headrail', 'stem-head extension', 'bowsprit'))}
        hide = tuple(n for n in names if n not in show)
    elif name == 'underside':
        show = {n for n in names if ('Longhead' in n or 'trailboard board' in n or
                'projecting headrail' in n or 'headrail knee' in n or 'trailboard fixing' in n or
                n in ('Bowsprit stem-head extension', 'Painted stem and cutwater',
                      'Bowsprit heel bearing cross-timber'))}
        hide = tuple(n for n in names if n not in show)
    elif name == 'head':
        show = {n for n in names if n.startswith('Starboard trailboard') or
                n in ('Longhead trailboard backing', 'Longhead upper shoulder') or
                n == 'Starboard longhead eagle eye'}
        hide = tuple(n for n in names if n not in show)
    else:
        hide = tuple(sails)
    views = {
        'profile': ((-1, 0, 0), (0, 0, 1), (0, -31, 9.1), 7.6),
        'quarter': ((-.85, .55, .5), (0, 0, 1), (0, -30, 9.0), 7.0),
        'starboard': ((-1, 0, 0), (0, 0, 1), (0, -31.2, 9.0), 4.9),
        'port': ((1, 0, 0), (0, 0, 1), (0, -31.2, 9.0), 4.9),
        'plan': ((0, 0, 1), (0, 1, 0), (0, -31, 9.0), 7.8),
        'underside': ((-.8, .2, -.4), (0, 0, 1), (0, -29.5, 8.4), 6.5),
        'head': ((-1, 0, 0), (0, 0, 1), (0, -36.8, 10.5), 1.45),
    }
    direction, up, focus, scale = views[name]
    im, _ = scene.render(direction, up, focus, scale, hide=hide)
    titles = {
        'profile': 'Expanded longhead/trailboard timber envelope in the completed export',
        'quarter': 'Quarter view: the enlarged headwork now supports the full decorated fascia',
        'starboard': 'Isolated starboard assembly: upper shoulder, carved fascia and deep lower body',
        'port': 'Isolated port assembly: mirrored timber envelope with the outward-reading name',
        'plan': 'Plan with the decorated faces and backing: centreline longhead and separate headrails',
        'underside': 'Underside: full-width backing and fitted stem/head extension',
        'head': 'Forward head: the envelope follows the source head and supports the eagle'
    }
    notes = {
        'profile': ['Upper wood rises to the source-controlled line beneath the bowsprit with a measured gap.',
                    'Lower wood follows the solid S04 boundary above the chain/cable and fairs into the stem.'],
        'quarter': ['The decorated face remains nested on the enlarged timber; its contours and scale are unchanged.',
                    'The headrails remain separate, fitted timbers.'],
        'starboard': ['The white margin around the ornament is the newly exposed solid timber.',
                      'The upper shoulder and lower body are valid registered solids, not a render silhouette.'],
        'port': ['The structural envelope is mirror-consistent; only the documented name reflection differs.',
                 'The face still reads KATHRYN outward.'],
        'plan': ['The common backing remains a half-foot-wide solid; the source does not independently dimension it.',
                 'Headrails converge independently and are not used as the upper wood boundary.'],
        'underside': ['The backing is cut against the stem, cross-timber and stem-head extension with matching fitted faces.',
                      'No zero-thickness sheet or floating ornament remains.'],
        'head': ['The forward closure follows the source head silhouette and contains the S01 eagle.',
                 'The lower body carries aft into the stem/head root.']
    }
    plate(im, titles[name], f'{len(scene.parts)} registered parts / native materials / completed SOMA export',
          notes[name], 'after-' + name + '.png')


def sections():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon
    model = Model(ROOT / '.soma')
    recs = {p['name']: p for p in model.map['parts']}
    shapes = {n: model.shape(recs[n]['id']).scale(1 / 304.8)
              for n in ('Longhead trailboard backing', 'Starboard trailboard board')}
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.6), sharey=True)
    for ax, f in zip(axes, (53.0, 56.0, 60.0)):
        plane = cq.Face.makeFromWires(
            cq.Workplane(cq.Plane(origin=(0, 25 - f, 0), xDir=(1, 0, 0),
                                  normal=(0, 1, 0))).rect(10, 30).val())
        for key, color, label in (('Longhead trailboard backing', '#c9b28a', 'timber'),
                                  ('Starboard trailboard board', '#234f7c', 'S01 fascia')):
            sec = shapes[key].intersect(plane)
            for face in sec.Faces():
                for wire in [face.outerWire(), *face.innerWires()]:
                    pts = []
                    for edge in wire.Edges():
                        n = max(2, int(edge.Length() / 0.08) + 2)
                        for t in np.linspace(0, 1, n):
                            p = edge.positionAt(float(t))
                            pts.append((p.x, p.z))
                    pts = np.asarray(pts, float)
                    if len(pts) > 2:
                        centre = np.mean(pts, axis=0)
                        angles = np.arctan2(pts[:, 1] - centre[1], pts[:, 0] - centre[0])
                        pts = pts[np.argsort(angles)] if hasattr(pts, 'shape') else [p for _, p in sorted(zip(angles, pts))]
                        ax.add_patch(Polygon(pts, closed=True, facecolor=color,
                                             edgecolor='#173044' if 'fascia' in label else '#6b5634',
                                             lw=0.7, alpha=1.0 if 'fascia' in label else 0.55,
                                             label=label))
        ax.axhline(panel_top(f), color='#c81e2b', lw=1.0, ls='--')
        ax.axhline(panel_bottom(f), color='#c81e2b', lw=1.0, ls='--')
        ax.set_title(f'F = {f:.0f} ft', fontsize=11)
        ax.set_xlim(-0.55, 0.55)
        ax.set_ylim(6.6, 10.8)
        ax.set_aspect('equal')
        ax.grid(alpha=.2)
        ax.set_xlabel('X (ft)')
        ax.text(-.52, panel_top(f) + .05, 'timber above face', color='#187447', fontsize=8)
        ax.text(-.52, panel_bottom(f) - .18, 'timber below face', color='#187447', fontsize=8)
    axes[0].set_ylabel('Z (ft)')
    handles = [plt.Line2D([], [], color='#c9b28a', lw=8, label='solid backing timber'),
               plt.Line2D([], [], color='#234f7c', lw=3, label='decorated S01 fascia'),
               plt.Line2D([], [], color='#c81e2b', lw=1, ls='--', label='fascia upper/lower')]
    fig.legend(handles=handles, loc='lower center', ncol=3, frameon=False, fontsize=9)
    fig.tight_layout(rect=(0, .08, 1, 1))
    fig.savefig(OUT / 'sections.png', dpi=180)
    plt.close(fig)
    print('sections.png', flush=True)


def overlay():
    manifest = json.loads((ROOT / 'references/drawing_package/manifest.json').read_text())
    view = next(v for v in manifest['views'] if v['id'] == 'S04-V01')
    source = next(s for s in manifest['sources'] if s['id'] == 'S04')
    sx, sy = source['native_size'][0] / 1440, source['native_size'][1] / 960
    gb = (1000, 280, 1270, 365)
    box = tuple(round(g * (sx if i % 2 == 0 else sy)) - view['native_box'][i % 2]
                for i, g in enumerate(gb))
    im = Image.open(ROOT / 'references/drawing_package' / view['native_image']).convert('RGB').crop(box)
    d = ImageDraw.Draw(im, 'RGBA')
    reg = ENVELOPE['registration']; a, b = reg['F_from_S04_grid_x']
    unit = reg['profile_grid_height_ft_per_unit']; deck = reg['deck_anchor_z_ft']
    def xy(f, z):
        gx = (f - b) / a; gy = 318.5 - (z - deck) / unit
        return ((gx - gb[0]) * sx, (gy - gb[1]) * sy)
    # Declared source envelope curves.
    for key, color, shift in (('outer_upper_fz', COLORS['upper'], -3),
                              ('outer_lower_fz', COLORS['lower'], 3)):
        pts = [xy(*p) for p in ENVELOPE['picks'][key]]
        pts = [(x, y + shift) for x, y in pts]
        d.line(pts, fill=color, width=5)
        for x, y in pts:
            d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=color)
    model = Model(ROOT / '.soma')
    recs = {p['name']: p for p in model.map['parts']}
    for name, color, width in [('Longhead trailboard backing', COLORS['backing'], 3),
                               ('Starboard trailboard board', COLORS['board'], 3),
                               ('Starboard projecting headrail', COLORS['headrail'], 3),
                               ('Bowsprit', COLORS['spar'], 2),
                               ('Painted stem and cutwater', COLORS['stem'], 2)]:
        shape = model.shape(recs[name]['id']).scale(1 / 304.8)
        for edge in shape.Edges():
            pts = []
            for t in np.linspace(0, 1, 2 if edge.geomType() == 'LINE' else 18):
                p = edge.positionAt(float(t))
                pts.append(xy(25 - p.y, p.z))
            d.line(pts, fill=color, width=width)
    legend = [
        ('#187447', 'outer upper timber'),
        ('#c46b00', 'outer lower timber'),
        ('#c81e2b', 'S01 decorated face'),
        ('#086d9f', 'backing envelope'),
        ('#0b8b8b', 'item-11 headrail'),
        ('#3f3f46', 'bowsprit / stem'),
    ]
    width = 1800
    fitted = im.resize((width, round(im.height * width / im.width)), Image.Resampling.LANCZOS)
    out = Image.new('RGB', (width, fitted.height + 225), 'white')
    out.paste(fitted, (0, 100))
    dd = ImageDraw.Draw(out)
    dd.text((28, 15), 'Source classification and completed export over S04-V01', font=font(28, True), fill='#173044')
    dd.text((28, 62), 'Black = original scan / coloured = declared source envelope and actual exported edges', font=font(18), fill='#526473')
    for i, (color, label) in enumerate(legend):
        x = 28 + (i % 3) * 590
        y = fitted.height + 115 + (i // 3) * 38
        dd.rectangle((x, y, x + 28, y + 16), fill=color)
        dd.text((x + 38, y - 4), label, fill='#173044', font=font(19))
    dd.text((28, fitted.height + 195), 'S04-V01: solid wood edges used; dashed cable, chain hardware and foreground rigging excluded.',
            fill='#526473', font=font(17))
    out.save(OUT / 'source-profile-envelope.png')
    print('source-profile-envelope.png', flush=True)


def comparison():
    before = Image.open(OUT / 'current-profile.png').convert('RGB')
    after = Image.open(OUT / 'after-profile.png').convert('RGB')
    width = 1800
    def fit(im):
        return im.resize((width, round(im.height * width / im.width)), Image.Resampling.LANCZOS)
    before, after = fit(before), fit(after)
    out = Image.new('RGB', (width, before.height + after.height + 150), 'white')
    d = ImageDraw.Draw(out)
    d.text((28, 15), 'Before / after: trailboard timber envelope', font=font(28, True), fill='#173044')
    d.text((28, 62), 'The decorated face and headrails are unchanged; the surrounding solid timber is added.', font=font(19), fill='#526473')
    y = 100
    d.text((28, y), 'BEFORE - thin decorated strip, no upper or lower timber', font=font(21, True), fill='#9b1c1c')
    out.paste(before, (0, y + 30)); y += before.height + 50
    d.text((28, y), 'AFTER - full source-envelope timber, face nested and supported', font=font(21, True), fill='#187447')
    out.paste(after, (0, y + 30))
    out.save(OUT / 'comparison-before-after.png')
    print('comparison-before-after.png', flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--render', choices=['profile', 'quarter', 'starboard', 'port', 'plan', 'underside', 'head', 'all'])
    p.add_argument('--sections', action='store_true')
    p.add_argument('--overlay', action='store_true')
    p.add_argument('--comparison', action='store_true')
    a = p.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if a.render:
        for name in (['profile', 'quarter', 'starboard', 'port', 'plan', 'underside', 'head']
                     if a.render == 'all' else [a.render]):
            render(name)
    if a.sections:
        sections()
    if a.overlay:
        overlay()
    if a.comparison:
        comparison()
