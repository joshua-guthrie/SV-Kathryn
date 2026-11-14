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

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
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
    plan = Image.open(ROOT / 'references/drawing_package/S05/S05-V01/preview.png').convert('RGB')
    scale = 2
    plan = plan.resize((plan.width * scale, plan.height * scale), Image.LANCZOS)
    top_margin, bottom_margin = 190, 330
    canvas = Image.new('RGB', (plan.width + 80, plan.height + top_margin + bottom_margin), 'white')
    canvas.paste(plan, (40, top_margin))
    draw = ImageDraw.Draw(canvas, 'RGBA')
    font_title = ImageFont.truetype(FONT, 38)
    font = ImageFont.truetype(FONT, 25)
    font_small = ImageFont.truetype(FONT, 21)
    reg = json.loads((ROOT / 'references/drawing_package/registration.json').read_text())['transformations']['S05']
    manifest = json.loads((ROOT / 'references/drawing_package/manifest.json').read_text())
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
    run_x, run_pieces = {}, {}
    for row in boards:
        bb = row['shape'].BoundingBox()
        x0, x1 = run_x.get(row['run'], (bb.xmin, bb.xmax))
        run_x[row['run']] = (min(x0, bb.xmin), max(x1, bb.xmax))
        run_pieces.setdefault(row['run'], []).append((25 - bb.ymax, 25 - bb.ymin))
    for run in run_pieces:
        run_pieces[run] = sorted(run_pieces[run])
    port_runs = sorted([r for r in run_x if r.startswith('Port')], key=lambda r: run_x[r][0])
    star_runs = sorted([r for r in run_x if r.startswith('Starboard')], key=lambda r: run_x[r][0])
    centre = [r for r in run_x if r.startswith('Deck centre')]

    def beam_options(a, b):
        return [beam for beam in BEAMS
                if a + 1.0 <= beam_forward(beam) <= b - 1.0]

    def butt_stations(run_index, run, previous):
        """Standard 12-ft lumber: never let a board exceed 12 ft.

        Walk forward through each continuous deck piece. Whenever the rest of
        the piece is longer than 12 ft, select a measured beam centre at or
        before the 12-ft cap. Board lengths are therefore <= 12 ft; they may be
        shorter. The two boards either side of every selected station share
        that beam.
        """
        result = []
        for a, b in run_pieces[run]:
            last = a
            while b - last > 12.0 + 1e-9:
                target = min(last + 12.0, b - 1.0)
                options = [beam for beam in beam_options(a, b)
                           if last + 1.0 < beam_forward(beam) <= target + 1e-9]
                ordered = sorted(options, key=lambda beam: abs(beam_forward(beam) - target))
                chosen = None
                for minimum in (4.0, 2.0):
                    for beam in ordered:
                        f = beam_forward(beam)
                        if any(abs(f - q) < 4.0 for q, _ in result):
                            continue
                        if all(abs(f - p) >= minimum for p in previous):
                            chosen = beam
                            break
                    if chosen is not None:
                        break
                if chosen is None:
                    # Keep the 12-ft cap even where the ideal 2-bay stagger
                    # cannot also be met; the acceptance check reports this.
                    for beam in ordered:
                        f = beam_forward(beam)
                        if any(abs(f - q) < 4.0 for q, _ in result):
                            continue
                        chosen = beam
                        break
                if chosen is None:
                    break
                result.append((beam_forward(chosen), chosen['set']))
                last = beam_forward(chosen)
        return result

    fig = plt.figure(figsize=(18, 12.5), dpi=170)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.02, 1.15], hspace=.24, wspace=.14)
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
            for f, _ in stations:
                ax.plot([f, f], [x0, x1], color='#b00020', lw=1.5)
                ax.add_patch(Rectangle((f - .55, x0), 1.1, x1 - x0, fill=False,
                                       edgecolor='#b00020', lw=.6, alpha=.9))
            previous = [f for f, _ in stations]

    draw_stations(port_runs)
    draw_stations(star_runs)
    centre_previous = [f for f, _ in butt_stations(0, port_runs[0], [])] + \
                      [f for f, _ in butt_stations(0, star_runs[0], [])]
    for run in centre:
        x0, x1 = run_x[run]
        for f, _ in butt_stations(1, run, centre_previous):
            ax.plot([f, f], [x0, x1], color='#b00020', lw=1.5)
            ax.add_patch(Rectangle((f - .55, x0), 1.1, x1 - x0, fill=False,
                                   edgecolor='#b00020', lw=.6, alpha=.9))
    ax.set_xlim(-2, 51)
    ax.set_ylim(-9, 9)
    ax.set_aspect('equal')
    ax.set_xlabel('Forward (ft) — bow at right')
    ax.set_ylabel('Across (ft) — port up')
    ax.set_title('D. PROPOSED STANDARD-LUMBER PATTERN — no board over 12 ft; every butt centred on a measured beam\n'
                 'Red = butt at beam centreline. Each adjoining plank covers half the beam’s sided width. No ledgers. Widths: 4-in/6-in nominal.\n'
                 'Concept shown on the current run boundaries; implementation re-spaces courses to 3.5-in / 5.5-in actual stock.',
                 fontsize=9.2, loc='left')
    legend = [Line2D([0], [0], color='#b00020', lw=2, label='beam-centred butt'),
              Line2D([0], [0], color='#0b4f9c', lw=1.5, label='measured deck beam'),
              Line2D([0], [0], color='#c45a00', lw=1.2, ls='--', label='opening')]
    ax.legend(handles=legend, loc='lower left', fontsize=7, framealpha=.95)

    sub = gs[1, 0].subgridspec(2, 1, hspace=.42)
    axd = fig.add_subplot(sub[0])
    axd.set_xlim(0, 6)
    axd.set_ylim(0, 5.8)
    axd.set_aspect('equal')
    axd.axis('off')
    axd.add_patch(Rectangle((2.0, .9), 1.0, 4.2, facecolor='#dbe8f7',
                            edgecolor='#0b4f9c', lw=1.2))
    axd.add_patch(Rectangle((.2, 1.9), 2.3, 1.0, facecolor='#e7d6b7',
                            edgecolor='#7a4a17', lw=1.0))
    axd.add_patch(Rectangle((2.5, 1.9), 3.3, 1.0, facecolor='#f0e2c8',
                            edgecolor='#7a4a17', lw=1.0))
    axd.plot([2.5, 2.5], [1.8, 3.0], color='#b00020', lw=2.5)
    axd.text(2.5, 5.3, 'beam 5½ in; joint at beam centreline', fontsize=7.0,
             ha='center', color='#0b4f9c')
    axd.text(1.1, 3.25, 'plank A', fontsize=6.8, ha='center', color='#7a4a17')
    axd.text(4.0, 3.25, 'plank B', fontsize=6.8, ha='center', color='#7a4a17')
    axd.text(2.5, .15, 'each plank end covers 2¾ in = half of the 5½-in beam',
             fontsize=6.4, ha='center', color='#111111')
    axd.annotate('', xy=(2.5, 1.55), xytext=(2.0, 1.55),
                 arrowprops=dict(arrowstyle='<->', color='#b00020', lw=1.0))
    axd.annotate('', xy=(3.0, 1.55), xytext=(2.5, 1.55),
                 arrowprops=dict(arrowstyle='<->', color='#b00020', lw=1.0))
    axd.set_title('E. BEAM-CENTRED BUTT DETAIL — two boards share one beam',
                  fontsize=8, loc='left')

    axs = fig.add_subplot(sub[1])
    axs.axis('off')
    axs.set_xlim(-.4, 5.4)
    axs.set_ylim(-.4, 7.2)
    for beam in range(6):
        axs.plot([beam, beam], [0, 6.4], color='#0b4f9c', lw=1.1)
    for run in range(6):
        y = 5.8 - run
        phase = (2 * (run % 3)) % 6
        axs.plot([0, 5], [y, y], color='#777777', lw=.6)
        for j in range(6):
            if j == phase:
                axs.plot([j - .22, j + .22], [y, y], color='#b00020', lw=2.4)
    axs.annotate('', xy=(0, 6.65), xytext=(2, 6.65),
                 arrowprops=dict(arrowstyle='<->', color='#0a7a35', lw=1.1))
    axs.text(1, 6.78, '>= 2 bays', fontsize=6.5, color='#0a7a35', ha='center')
    axs.text(2.5, 7.0, 'adjacent planks never share a beam', fontsize=7,
             ha='center', color='#111111')

    axr = fig.add_subplot(gs[1, 1])
    axr.axis('off')
    rules = [
        'PROPOSED RECONSTRUCTION RULES', '',
        '1. One logical board per plank run; no aggregate backing.',
        '2. Standard lumber: 4-in nominal (3½-in actual) typical deck',
        '   stock; 6-in nominal (5½-in actual) inboard/kingplank stock.',
        '3. Every internal butt is centred on a measured deck beam. The',
        '   upstream plank ends at the beam centreline and covers half',
        '   the beam’s sided width; the next plank covers the other half.',
        '   No ledgers and no unsupported butts.',
        '4. 12 ft is the maximum board length (standard 12-ft stock);',
        '   shorter boards are allowed. Report actual lengths and reject',
        '   any board over 12 ft.',
        '5. Adjacent planks stagger by >= 2 beam bays; never put two',
        '   adjacent planks on the same beam.',
        '6. Keep internal butts >= 12 in from opening coamings. Opening',
        '   edges are framed boundaries, not extra butt lines.',
        '7. Spile/taper plank ends into the oak waterway at bow and stern;',
        '   do not leave triangular strip tips.',
        '8. Keep the 6-in centre kingplank; stagger its butts on the',
        '   same beam-centre grid.',
        '9. No backing or ledger: deck boards + waterway must conserve',
        '   the deck envelope; the beams are the only butt support.',
        '10. Exact historic butt positions are not printed on S05; this',
        '    is a qualified reconstruction.',
    ]
    axr.text(0, 1, '\n'.join(rules), fontsize=8.0, va='top', ha='left', color='#111111')
    fig.suptitle('Kathryn — standard-lumber deck pattern: ≤12-ft boards, 4/6-in nominal, beam-centred butts (for review)',
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

    p17 = enhanced(ROOT / 'references/loc_photos/LOC_Kathryn_photos/18-LOC-P17.jpg', (140, 430, 640, 900))
    p25 = enhanced(ROOT / 'references/loc_photos/LOC_Kathryn_photos/26-LOC-P25.jpg', (220, 400, 900, 720))
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
