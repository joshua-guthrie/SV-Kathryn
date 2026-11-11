"""Build the annotated M4 deck-planking gap-analysis figures.

Run from the project root:
    python checks/build_deck_planking_gap_assets.py

The figures are written to renders/ and are intentionally not versioned.
They document the current partition, the source pattern, the photo check and
the proposed staggered/supported pattern.  No model geometry is changed.
"""
import json
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

from parts import deck_beams, framing
from parts.beam_layout import BEAMS, forward as beam_forward
from parts.deck_planking import deck_boards
from parts.openings import framed_openings

FIG = ROOT / 'renders'
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'


def build_current(boards):
    run_extent = {}
    for run in {row['run'] for row in boards}:
        rows = [row for row in boards if row['run'] == run]
        ymin = min(row['shape'].BoundingBox().ymin for row in rows)
        ymax = max(row['shape'].BoundingBox().ymax for row in rows)
        run_extent[run] = (25 - ymax, 25 - ymin)
    longest = sorted(run_extent, key=lambda run: run_extent[run][1] - run_extent[run][0],
                     reverse=True)[:6]
    highlight = {run: plt.cm.tab10(i) for i, run in enumerate(longest)}

    def plot(ax, fmin=None, fmax=None):
        for row in boards:
            for edge in row['shape'].Edges():
                pts = np.array([[p.x, p.y, p.z] for p in
                                (edge.positionAt(float(t)) for t in np.linspace(0, 1, 6))])
                f = 25 - pts[:, 1]
                if fmin is not None and (f.max() < fmin or f.min() > fmax):
                    continue
                ax.plot(f, pts[:, 0], color=highlight.get(row['run'], '#777777'),
                        lw=.65 if row['run'] in highlight else .35,
                        alpha=.95 if row['run'] in highlight else .55)

    def decorate(ax, fmin, fmax, xlim):
        for beam in BEAMS:
            f = beam_forward(beam)
            if fmin - 1 <= f <= fmax + 1:
                span = framing.clamp_outer(f)
                ax.plot([f, f], [-span, span], color='#0b4f9c', lw=.7, alpha=.9)
                ax.text(f, span + .12, f"S{beam['set']}", fontsize=4.6,
                        color='#0b4f9c', ha='center', va='bottom')
        for opening in framed_openings():
            if opening.fore < fmin or opening.aft > fmax:
                continue
            ax.add_patch(Rectangle((opening.aft, -opening.clear_width / 2),
                                   opening.fore - opening.aft, opening.clear_width,
                                   fill=False, edgecolor='#c45a00', lw=1.1, ls='--'))
            ax.text(opening.forward, opening.clear_width / 2 + .18, opening.name,
                    fontsize=5.8, color='#c45a00', ha='center', va='bottom')
            for f in (opening.aft, opening.fore):
                ax.axvline(f, color='#b00020', lw=.8, ls=':', alpha=.85)
        ax.set_xlim(fmin, fmax)
        ax.set_ylim(*xlim)
        ax.set_aspect('equal')
        ax.grid(False)

    fig = plt.figure(figsize=(18, 11), dpi=170)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.15, 1], hspace=.28, wspace=.16)
    ax = fig.add_subplot(gs[0, :])
    plot(ax)
    decorate(ax, -2.5, 51, (-9, 9))
    ax.set_xlabel('Forward (ft) — bow at right')
    ax.set_ylabel('Across (ft) — port up')
    ax.set_title('A. CURRENT STATE — long parallel strips, split only at openings\n'
                 '109 segments / 53 runs. Highlighted: six longest runs. Dotted red = common transverse end lines; '
                 'no supported staggered butts.', fontsize=10, loc='left')
    axb = fig.add_subplot(gs[1, 0])
    plot(axb, 40, 51)
    decorate(axb, 40, 51, (-6, 6))
    axb.set_title('B. BOW DETAIL — every strip is cut by the hull outline into a triangular tip;\n'
                  'seams stay parallel instead of tapering/spiling to the waterway.', fontsize=8, loc='left')
    axb.set_xlabel('Forward (ft)')
    axb.set_ylabel('Across (ft)')
    axc = fig.add_subplot(gs[1, 1])
    plot(axc, 4, 15)
    decorate(axc, 4, 15, (-5, 5))
    axc.set_title('C. CABIN OPENING — many adjacent planks end on the same transverse lines;\n'
                  'the model introduces no stagger and no butt blocks.', fontsize=8, loc='left')
    axc.set_xlabel('Forward (ft)')
    axc.set_ylabel('Across (ft)')
    fig.suptitle('Kathryn — M4 deck planking: current geometry vs required staggered/spiled pattern',
                 fontsize=12, x=.01, ha='left')
    fig.savefig(FIG / 'm4-deck-planking-gap-current.png', bbox_inches='tight')
    plt.close(fig)


def build_source():
    plan = Image.open(ROOT / 'drawing_package/S05/S05-V01/preview.png').convert('RGB')
    scale = 2
    plan = plan.resize((plan.width * scale, plan.height * scale), Image.LANCZOS)
    top_margin, bottom_margin = 190, 330
    canvas = Image.new('RGB', (plan.width + 80, plan.height + top_margin + bottom_margin), 'white')
    canvas.paste(plan, (40, top_margin))
    draw = ImageDraw.Draw(canvas, 'RGBA')
    font_title = ImageFont.truetype(FONT, 38)
    font = ImageFont.truetype(FONT, 25)
    font_small = ImageFont.truetype(FONT, 21)
    reg = json.loads((ROOT / 'drawing_package/registration.json').read_text())['transformations']['S05']
    manifest = json.loads((ROOT / 'drawing_package/manifest.json').read_text())
    view = next(v for v in manifest['views'] if v['id'] == 'S05-V01')
    source = next(s for s in manifest['sources'] if s['id'] == 'S05')
    a, b = reg['grid_x_to_F']

    def preview_x(forward_ft):
        native = (forward_ft - b) / a / 1440 * source['native_size'][0]
        return (native - view['native_box'][0]) / view['native_size'][0] * view['preview_size'][0]

    for beam in BEAMS:
        px = preview_x(beam_forward(beam)) * scale + 40
        draw.line((px, top_margin + 70 * scale, px, top_margin + 500 * scale),
                  fill=(20, 80, 180, 105), width=2)
        draw.text((px - 8, top_margin + 45 * scale), str(beam['set']),
                  font=font_small, fill=(20, 80, 180, 235))

    def box(x0, y0, x1, y1, color, width=5):
        draw.rectangle((40 + x0 * scale, top_margin + y0 * scale,
                        40 + x1 * scale, top_margin + y1 * scale), outline=color, width=width)

    box(1510, 155, 1830, 450, (20, 130, 60, 255))
    box(110, 120, 390, 460, (20, 130, 60, 255))
    for box_ in ((420, 165, 705, 475), (735, 165, 1015, 475), (1040, 165, 1290, 465)):
        box(*box_, (200, 90, 0, 255))

    def card(x, y, lines, color):
        widths = [draw.textlength(line, font=font) for line in lines]
        w = max(widths) + 26
        h = 34 * len(lines) + 16
        draw.rounded_rectangle((x, y, x + w, y + h), radius=10,
                               fill=(255, 255, 255, 235), outline=color, width=3)
        yy = y + 8
        for line in lines:
            draw.text((x + 13, yy), line, font=font, fill=color)
            yy += 34

    card(60, 18, ['S05-V01 main deck structural plan — observed planking pattern',
                  'Blue = reconciled S05-07 deck-beam sets 1–23; green = tapered/staggered end zones; orange = openings.'],
         (0, 0, 0, 255))
    card(60, top_margin + plan.height + 20,
         ['BOW (green): seams converge and terminate at the curved waterway at different stations.',
          'The planks are spiled/tapered; their ends are staggered, not one common transverse line.'],
         (20, 110, 55, 255))
    card(60, top_margin + plan.height + 105,
         ['STERN (green): plank ends follow the counter, helm and cabin boundaries at different stations.',
          'Openings (orange) interrupt individual planks; no single transverse butt line crosses the deck.'],
         (20, 110, 55, 255))
    card(60, top_margin + plan.height + 190,
         ['Sheet 5 shows the tapered/staggered layout but does not dimension individual butt positions.',
          'The supported-butt rule in the proposed pattern is therefore a qualified reconstruction.'],
         (120, 60, 40, 255))
    draw.line((150, top_margin + plan.height + 80, 40 + 1640 * scale, top_margin + 300 * scale),
              fill=(20, 110, 55, 220), width=4)
    draw.line((150, top_margin + plan.height + 165, 40 + 250 * scale, top_margin + 380 * scale),
              fill=(20, 110, 55, 220), width=4)
    canvas.save(FIG / 'm4-deck-planking-gap-source.png')


def build_proposal(boards):
    run_x, run_f = {}, {}
    for row in boards:
        bb = row['shape'].BoundingBox()
        x0, x1 = run_x.get(row['run'], (bb.xmin, bb.xmax))
        run_x[row['run']] = (min(x0, bb.xmin), max(x1, bb.xmax))
        f0, f1 = run_f.get(row['run'], (25 - bb.ymax, 25 - bb.ymin))
        run_f[row['run']] = (min(f0, 25 - bb.ymax), max(f1, 25 - bb.ymin))
    port_runs = sorted([r for r in run_x if r.startswith('Port')], key=lambda r: run_x[r][0])
    star_runs = sorted([r for r in run_x if r.startswith('Starboard')], key=lambda r: run_x[r][0])
    centre = [r for r in run_x if r.startswith('Deck centre')]

    def near_opening(beam):
        return any(o.aft - 1.2 < beam_forward(beam) < o.fore + 1.2 for o in framed_openings())

    def butt_stations(run_index, run, previous):
        f0, f1 = run_f[run]
        length = f1 - f0
        if length < 12:
            return []
        count = max(1, int(round(length / 18.0)))
        targets = np.linspace(f0 + 3.0, f1 - 3.0, count)
        phase = ((run_index % 3) - 1) * 4.0
        usable = [beam for beam in BEAMS
                  if beam['role'] != 'split' and not near_opening(beam)
                  and f0 + 2.0 < beam_forward(beam) < f1 - 2.0]
        result = []
        for target in targets:
            f = min(f1 - 3.0, max(f0 + 3.0, float(target) + phase))
            options = []
            nearest = min(usable, key=lambda beam: abs(beam_forward(beam) - f), default=None)
            if nearest is not None and abs(beam_forward(nearest) - f) < 1.5:
                options.append((beam_forward(nearest), 'beam'))
            for shift in (0.0, 4.0, -4.0, 8.0, -8.0):
                g = f + shift
                if f0 + 3.0 <= g <= f1 - 3.0:
                    options.append((g, 'ledger'))
            for g, support in options:
                if all(abs(g - p) >= 4.0 for p in previous):
                    result.append((g, support))
                    break
        return result

    fig = plt.figure(figsize=(18, 11), dpi=170)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.12, 1], hspace=.26, wspace=.14)
    ax = fig.add_subplot(gs[0, :])
    for row in boards:
        for edge in row['shape'].Edges():
            pts = np.array([[p.x, p.y, p.z] for p in
                            (edge.positionAt(float(t)) for t in np.linspace(0, 1, 6))])
            ax.plot(25 - pts[:, 1], pts[:, 0], color='#bbbbbb', lw=.3, alpha=.8)
    for beam in BEAMS:
        f = beam_forward(beam)
        span = framing.clamp_outer(f)
        ax.plot([f, f], [-span, span], color='#0b4f9c', lw=.55, alpha=.7)
    for opening in framed_openings():
        ax.add_patch(Rectangle((opening.aft, -opening.clear_width / 2),
                               opening.fore - opening.aft, opening.clear_width,
                               fill=False, edgecolor='#c45a00', lw=1.0, ls='--'))

    def draw_stations(runs, offset=0):
        previous = []
        for index, run in enumerate(runs):
            x0, x1 = run_x[run]
            stations = butt_stations(index + offset, run, previous)
            for f, support in stations:
                color = '#b00020' if support == 'beam' else '#b35a00'
                ax.plot([f, f], [x0, x1], color=color, lw=1.5)
                ax.add_patch(Rectangle((f - .55, x0), 1.1, x1 - x0, fill=False,
                                       edgecolor=color, lw=.6, alpha=.9))
            previous = [f for f, _ in stations]

    draw_stations(port_runs)
    draw_stations(star_runs)
    # Centre kingplank: keep its butts clear of both adjacent first runs.
    centre_previous = [f for f, _ in butt_stations(0, port_runs[0], [])] + \
                      [f for f, _ in butt_stations(0, star_runs[0], [])]
    for run in centre:
        x0, x1 = run_x[run]
        for f, support in butt_stations(1, run, centre_previous):
            color = '#b00020' if support == 'beam' else '#b35a00'
            ax.plot([f, f], [x0, x1], color=color, lw=1.5)
            ax.add_patch(Rectangle((f - .55, x0), 1.1, x1 - x0, fill=False,
                                   edgecolor=color, lw=.6, alpha=.9))
    ax.set_xlim(-2, 51)
    ax.set_ylim(-9, 9)
    ax.set_aspect('equal')
    ax.set_xlabel('Forward (ft) — bow at right')
    ax.set_ylabel('Across (ft) — port up')
    ax.set_title('D. PROPOSED PATTERN — butts only over supported members, staggered between adjacent planks\n'
                 'Red = butt over beam; amber = butt over 12-in ledger/block. Every plank is an individual board.',
                 fontsize=9.5, loc='left')
    legend = [Line2D([0], [0], color='#b00020', lw=2, label='butt over beam'),
              Line2D([0], [0], color='#b35a00', lw=2, label='butt over 12-in ledger/block'),
              Line2D([0], [0], color='#0b4f9c', lw=1.5, label='measured deck beam'),
              Line2D([0], [0], color='#c45a00', lw=1.2, ls='--', label='opening')]
    ax.legend(handles=legend, loc='lower left', fontsize=7, framealpha=.95)

    axz = fig.add_subplot(gs[1, 0])
    axz.axis('off')
    axz.set_xlim(-.4, 5.4)
    axz.set_ylim(-.6, 9.0)
    for beam in range(6):
        axz.plot([beam, beam], [0, 8], color='#0b4f9c', lw=1.4)
        axz.text(beam, -.25, f'beam\n{beam+1}', fontsize=6.2, color='#0b4f9c', ha='center', va='top')
    for run in range(8):
        y = 7.5 - run
        phase = (2 * (run % 3)) % 6
        axz.plot([0, 5], [y, y], color='#777777', lw=.7)
        for j in range(6):
            if j == phase:
                axz.plot([j - .38, j + .38], [y, y], color='#b00020', lw=3.0)
                axz.add_patch(Rectangle((j - .38, y - .22), .76, .44, fill=False,
                                        edgecolor='#b00020', lw=.9))
    axz.annotate('', xy=(0, 8.55), xytext=(2, 8.55),
                 arrowprops=dict(arrowstyle='<->', color='#0a7a35', lw=1.4))
    axz.text(1, 8.65, '>= 2 bays', fontsize=7, color='#0a7a35', ha='center')
    axz.text(2.5, 9.0, 'SCHEMATIC ZOOM — 8 planks / 6 beams', fontsize=8.2, ha='center', va='bottom')
    axz.text(-.35, 8.2, 'adjacent butts never share a beam', fontsize=7.2, color='#111111')

    axr = fig.add_subplot(gs[1, 1])
    axr.axis('off')
    rules = [
        'PROPOSED RECONSTRUCTION RULES', '',
        '1. One logical board per plank run segment; no aggregate backing.',
        '2. Butt only over a deck beam, or over a 12-in butt block/ledger that',
        '   spans to two adjacent beams; no unsupported butt in a span.',
        '3. Target 16–20-ft plank lengths (reconstruction) with a three-phase',
        '   stagger; adjacent butts >= 2 bay widths apart; never align adjacent planks.',
        '4. Keep butts >= 12 in from opening coamings and plank ends;',
        '   no butt at a hatch/cabin corner.',
        '5. Spile/taper plank ends into the oak waterway at bow and stern;',
        '   do not leave triangular strip tips.',
        '6. Keep the 6-in centre kingplank; stagger its butts on the same grid.',
        '7. Butt blocks/ledgers are extra material below the deck (not carved from it);',
        '   deck boards + waterway must still conserve the deck envelope.',
        '8. Exact historic butt positions are not printed on S05;',
        '   this pattern is a qualified reconstruction.',
    ]
    axr.text(0, 1, '\n'.join(rules), fontsize=8.2, va='top', ha='left', color='#111111')
    fig.suptitle('Kathryn — proposed staggered, beam-supported deck planking pattern (for review)',
                 fontsize=12, x=.01, ha='left')
    fig.savefig(FIG / 'm4-deck-planking-gap-proposal.png', bbox_inches='tight')
    plt.close(fig)


def build_photos():
    font_title = ImageFont.truetype(FONT, 40)
    font = ImageFont.truetype(FONT, 24)

    def enhanced(path, box):
        im = Image.open(path).convert('L').crop(box)
        return ImageOps.autocontrast(im, cutoff=1).filter(
            ImageFilter.UnsharpMask(radius=2, percent=160, threshold=3))

    p17 = enhanced(ROOT / 'Reference Material/LOC_Kathryn_photos/18-LOC-P17.jpg', (140, 430, 640, 900))
    p25 = enhanced(ROOT / 'Reference Material/LOC_Kathryn_photos/26-LOC-P25.jpg', (220, 400, 900, 720))
    height = 620
    p17 = p17.resize((int(p17.width * height / p17.height), height), Image.LANCZOS)
    p25 = p25.resize((int(p25.width * height / p25.height), height), Image.LANCZOS)
    gap, margin, top, cap = 40, 40, 150, 190
    canvas = Image.new('RGB', (margin * 2 + p17.width + gap + p25.width, top + height + cap), 'white')
    canvas.paste(p17, (margin, top))
    canvas.paste(p25, (margin + p17.width + gap, top))
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 35), 'LOC deck views — appearance check, not a measured butt layout',
              font=font_title, fill='black')

    def caption(x, y, head, body, width_chars):
        draw.text((x, y), head, font=font, fill='black')
        yy = y + 34
        for line in textwrap.wrap(body, width_chars):
            draw.text((x, yy), line, font=font, fill=(70, 70, 70))
            yy += 30

    caption(margin, top + height + 16, 'LOC-P17 — foredeck view',
            'Faint longitudinal seams are visible under the painted finish; individual butt ends are not resolvable.', 44)
    caption(margin + p17.width + gap, top + height + 16, 'LOC-P25 — aft deck view',
            'Painted finish; no reliable butt-joint pattern is visible at this scale. Photos are perspective views, not calibrated plan dimensions.', 80)
    draw.text((margin, top + height + cap - 42),
              'Sheet 5 remains the authority for the plank layout; the photos only corroborate the painted longitudinal finish.',
              font=font, fill=(70, 70, 70))
    canvas.save(FIG / 'm4-deck-planking-gap-photos.png')


if __name__ == '__main__':
    boards = deck_boards()
    FIG.mkdir(exist_ok=True)
    build_current(boards)
    build_source()
    build_proposal(boards)
    build_photos()
    print('Wrote deck-planking gap figures to', FIG)
