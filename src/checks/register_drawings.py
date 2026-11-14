"""Checked data, calibrated coordinates and representative vector section guides."""
import ast
import hashlib
import html
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt

from drawing_evidence import NOTES, STATIONS, OFFSETS, OCR_CORRECTIONS

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'references/drawing_package'
Image.MAX_IMAGE_PIXELS = None


def save(name, obj):
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def feet(value):
    f, i, e = map(int, value.split('-'))
    return f + i / 12 + e / 96


def checked_data():
    save('notes_verified.json', dict(status='checked transcription; retain survey uncertainty',
                                   notes=NOTES, ocr_corrections=OCR_CORRECTIONS))
    rows = []
    for i, station in enumerate(STATIONS):
        row = dict(station=station, printed={}, feet={})
        for key, text in OFFSETS.items():
            tokens = text.split()
            value = tokens[i] if i < len(tokens) else None
            row['printed'][key] = value
            row['feet'][key] = feet(value) if value else None
        rows.append(row)
    # Compare source readings with the current parameter transcription WITHOUT
    # importing CAD/SOMA. Source and intentional model fairing remain separate.
    names = ['SHEER_HEIGHTS','CHINE_TOP_HEIGHTS','CHINE_BOTTOM_HEIGHTS','RABBET_HEIGHTS',
             'SHEER_WIDTHS','CHINE_TOP_WIDTHS','CHINE_BOTTOM_WIDTHS']
    keys = list(OFFSETS)[:7]
    values = {}
    for node in ast.parse((ROOT / 'src/parts/params.py').read_text()).body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id in names:
                values[node.targets[0].id] = ast.literal_eval(node.value.func.value).split()
    differences = []
    for name, key in zip(names, keys):
        for i, model in enumerate(values[name]):
            source = rows[i]['printed'][key]
            if source != model:
                differences.append(dict(station=STATIONS[i], field=key, source=source, model=model,
                    disposition='existing deliberate sheer fairing; source retained' if name == 'SHEER_HEIGHTS' and STATIONS[i] == 4 else 'requires review'))
    save('offsets_verified.json', dict(source_view='S02-T01', notation='feet-inches-eighths of inch',
        review_status='visually checked source table', blanks='null = not recorded; never filled silently',
        rows=rows, model_differences=differences,
        retained_outlier=dict(station=8.5, field='chine_bottom_half_breadth', printed='2-7-4',
                              note='Keep the measured value distinct from the existing faired model.')))
    (OUT / 'checked_notes.md').write_text('# Checked construction notes\n\n' + '\n\n'.join(
        f"## {n['id']}\n\n{n['checked_text']}\n\nSource views: {', '.join(n['source_views'])}."
        for n in NOTES) + '\n')


# Approximate grid x locations are refined to the strongest native tick stroke.
RULERS = {
    2: dict(view='S02-R01', ticks={0:162.0,10:313.0,50:909.0}, y=(828,842), inches_per_ft=.375),
    3: dict(view='S03-R01', ticks={0:351.5,20:550.5,50:850.0}, y=(821,835), inches_per_ft=.25),
    4: dict(view='S04-R01', ticks={0:163.5,20:462.5,50:911.0}, y=(835,848), inches_per_ft=.375),
    5: dict(view='S05-R01', ticks={0:147.5,20:447.5,50:895.5}, y=(827,841), inches_per_ft=.375),
    6: dict(view='S06-R01', ticks={0:178.0,10:476.5,20:774.5}, y=(834,849), inches_per_ft=.75),
    7: dict(view='S07-R01', ticks={0:176.0,10:474.5,20:773.0}, y=(828,841), inches_per_ft=.75),
}


def calibrate(manifest):
    result = {}
    for sheet, spec in RULERS.items():
        source = next(s for s in manifest['sources'] if s['id'] == f'S{sheet:02d}')
        w, h = source['native_size']
        sx, sy = w / 1440, h / 960
        with Image.open(ROOT / source['path']) as image:
            samples = []
            for distance, x in spec['ticks'].items():
                box = (round((x - 2) * sx), round(spec['y'][0] * sy),
                       round((x + 2) * sx), round(spec['y'][1] * sy))
                a = np.asarray(image.crop(box).convert('L')) < 100
                strengths = a.sum(axis=0)
                hits = np.flatnonzero(strengths >= strengths.max() * .98)
                picked = box[0] + float(np.median(hits))
                samples.append(dict(feet=distance, native_x=picked))
        fit = np.polyfit([p['feet'] for p in samples], [p['native_x'] for p in samples], 1)
        residual = max(abs(p['native_x'] - np.polyval(fit, p['feet'])) for p in samples) / fit[0]
        expected = source['dpi'][0] * spec['inches_per_ft']
        result[source['id']] = dict(source_view=spec['view'], native_pixels_per_ft=float(fit[0]),
            ruler_ticks=samples, fit_residual_ft=float(residual),
            printed_inches_per_ft=spec['inches_per_ft'], print_dpi_crosscheck_px_per_ft=expected,
            print_crosscheck_relative_error=float(abs(fit[0] / expected - 1)),
            point_pick_uncertainty_ft=.08 if sheet >= 6 else .15,
            policy='Imperial bar is primary; view scale must be declared separately.',
            source_label_issue='Imperial 3/4-inch scale = 1:16 conflicts with printed metric caption 1:32.' if sheet == 6 else None)
        print(source['id'], 'px/ft', round(fit[0], 4), 'residual ft', round(residual, 4), flush=True)
    save('calibration.json', dict(coordinates='original scan pixels', calibrated_sheets=result,
        unscaled_views=['S01 illustration/map/ornament unless separately dimensioned',
                        'S08 illustrative sail details explicitly marked not to scale',
                        'S06-V03 perspective structural conception is not a metric projection'],
        metric_caption_resolution='S06 1:32 caption is a source inconsistency. Use calibrated imperial bar and 3/4-inch caption; do not apply a factor-of-two rescale.'))
    return result


def registration(manifest, calibration):
    sources = {s['id']:s for s in manifest['sources']}
    # S02's explicitly drawn 50-ft recorded-length dimension is the canonical
    # longitudinal reference. It is NOT the extent of every projected appendage.
    a2, b2 = 178.0, 928.0
    sx2 = sources['S02']['native_size'][0] / 1440
    # Homologous outline junctions; small drafting/pick differences are retained.
    s2_ends = np.array([151.0, 939.0])
    s5_ends = np.array([151.5, 937.0])
    m5, b5 = np.polyfit(s5_ends, s2_ends, 1)
    # Independent deck landmarks register sheets 4 and 5. No forced fit to the
    # old CAD hatch/mast positions is used.
    homologues = [
        ('after hatch centre', 562.5, 429.0),
        ('main hold hatch centre',795.5,661.5),
        ('mast at deck',914.0,781.5),
        ('forward cabin edge',520.0,389.5),
    ]
    x4 = np.array([r[1] for r in homologues])
    x5 = np.array([r[2] for r in homologues])
    m4, b4 = np.polyfit(x4,x5,1)
    def f2(x):
        return (x - a2) * 50 / (b2 - a2)
    def f5(x):
        return f2(m5 * x + b5)
    def f4(x):
        return f5(m4 * x + b4)
    residuals = [dict(feature=r[0], sheet4_grid_x=r[1], sheet5_grid_x=r[2],
                      residual_ft=float((m4*r[1]+b4-r[2])*m5*50/(b2-a2))) for r in homologues]
    station_x = [251,284,317,350,383,448,514,579,645,711,777,810,842,875,907]
    rows = [dict(lines_station=s, sheet2_grid_x=x, canonical_forward_ft=float(f2(x)),
                 legacy_model_forward_ft=50*(.075+.0875*s)) for s,x in zip(STATIONS,station_x)]
    features = []
    for name, source_x, legacy in [('After deck hatch',562.5,17.5),('Main hold hatch',795.5,31.1),
                                  ('Forepeak hatch',876,35.2),('Mast at deck',914,37.5)]:
        features.append(dict(name=name, source_view='S04-V02', grid_x=source_x,
                             canonical_forward_ft=float(f4(source_x)),
                             legacy_model_forward_ft=legacy,
                             delta_ft=float(f4(source_x)-legacy),
                             disposition='M1 migration input; old CAD geometry not moved during M0'))
    record = dict(status='source-coordinate convention established; geometry migration assigned to M1',
        canonical_frame=dict(F='forward from aft witness of the S02 50-ft recorded-length dimension',
            X='positive port; plan pixels upward from centreline',
            Z='up from lines-plan baseline; transverse traces retain a named local vertical datum until section station is established',
            units='full-size feet', source_view='S02-V01'),
        reference_dimension=dict(native_x=[a2*sx2,b2*sx2], feet=50,
            imperial_bar_length_ft=float((b2-a2)*sx2/calibration['S02']['native_pixels_per_ft']),
            note='Dimension witnesses define F=0/50. Projections beyond them are not silently compressed into that interval.'),
        transformations=dict(
            S02=dict(grid_x_to_F=[50/(b2-a2),-a2*50/(b2-a2)], baseline_grid_y=303.0),
            S05=dict(grid_x_to_F=[float(m5*50/(b2-a2)),float((b5-a2)*50/(b2-a2))],
                     centreline_grid_y=232.0, method='planked-hull aft edge and forward planking/stem junction aligned with S02'),
            S04=dict(grid_x_to_F=[float(m5*m4*50/(b2-a2)),float((m5*b4+b5-a2)*50/(b2-a2))],
                     centreline_grid_y=640.0, method='four independently picked deck landmarks fitted to S05')),
        homologous_deck_landmarks=residuals,
        max_deck_alignment_residual_ft=max(abs(r['residual_ft']) for r in residuals),
        point_pick_uncertainty_ft=.20,
        line_stations=rows, legacy_feature_migration=features,
        numbering_rules=['Lines stations 0–10 are NOT deck-beam numbers or hull-frame set numbers.',
                         'Sheet 5 deck beams are keyed from bow; split side members count as a set.',
                         'Sheet 5 note 10 says the first hull-frame set is against the stern knee; preserve this wording and establish its independent numbering before assigning section positions.',
                         'Hull frame-set numbers in section captions need their own member schedule; do not equate to line stations.'],
        decision='Source coordinates above govern new members. M1 explicitly migrates the inherited normalized CAD using the recorded deltas and regression evidence; no force-fit of source dimensions to the old CAD.',
        source_conditions=['S02 lines are corrected to a straight keel; historical hogging/deadrise distortions are documented separately.',
                           'Deck/hold arrangements and repair sections depict the surveyed vessel. Record differences rather than inventing exact agreement.'])
    save('registration.json', record)
    print('Deck landmark residual:', record['max_deck_alignment_residual_ft'], 'ft')


TRACES = {
    'S06-V01': dict(origin=[917,1410], port_direction=-1,
        datum='local Z=0 at bottom of external keel/shoe section; not the lines-plan baseline',
        paths={
            'port_outer_planking':[[198,516],[340,1057],[351,1079],[367,1097],[500,1162],[650,1232],[800,1304],[863,1333]],
            'starboard_outer_planking':[[1656,518],[1435,1077],[1414,1103],[1275,1170],[1120,1244],[970,1315]],
            'deck_underside':[[200,514],[500,503],[800,495],[1100,497],[1400,507],[1655,519]],
        },
        regions=[dict(note='S06-08',box=[810,1140,1025,1380],kind='cut keelson region'),
                 dict(note='S06-17',box=[835,165,1005,1065],kind='forward projected Sampson post; NOT a cut frame at this station'),
                 dict(note='S06-11',box=[995,850,1420,1210],kind='replacement frame region'),
                 dict(note='S06-15',box=[1040,1120,1435,1325],kind='older frame region')]),
    'S07-V02': dict(origin=[987,1250], port_direction=-1,
        datum='local Z=0 at bottom of external shoe in the section; not the lines-plan baseline',
        paths={
            'port_outer_planking':[[225,564],[270,755],[284,802],[300,824],[326,838],[500,881],[700,925],[960,972]],
            'starboard_outer_planking':[[1750,570],[1695,762],[1680,806],[1662,829],[1640,841],[1400,897],[1200,943],[1015,975]],
            'port_deck_surface':[[225,540],[400,536],[574,530]],
            'starboard_deck_surface':[[1400,539],[1570,549],[1750,554]],
            'port_roof_surface':[[512,251],[556,233],[820,224]],
            'starboard_roof_surface':[[1147,231],[1417,240],[1474,263]],
        },
        regions=[dict(note='S07-08',box=[220,560,565,835],kind='frame/lining region; molded depth average 3 in at keelson'),
                 dict(note='S07-01',box=[300,600,575,788],kind='individual ceiling/lining boards'),
                 dict(note='S07-12',box=[952,960,1018,1100],kind='keelson region'),
                 dict(note='S07-07',box=[1120,280,1310,626],kind='projected electrical boxes; not bulk solid hull')]),
}


def trace_sections(manifest, calibration):
    folder = OUT / 'traces'
    folder.mkdir(exist_ok=True)
    views = {v['id']:v for v in manifest['views']}
    for view_id, spec in TRACES.items():
        view = views[view_id]
        image = Image.open(OUT / view['preview']).convert('RGB')
        pixels = np.asarray(image.convert('L')) < 95
        distance, nearest = distance_transform_edt(~pixels, return_indices=True)
        draw = ImageDraw.Draw(image)
        sx, sy = view['native_size'][0]/image.width, view['native_size'][1]/image.height
        ppf = calibration[view['source_id']]['native_pixels_per_ft']
        paths, svg_paths = [], []
        colours = ['#e12d25','#0089ba','#8e28b8','#13913a','#dd8c00','#bf2671']
        for i,(name, picks) in enumerate(spec['paths'].items()):
            snapped, gaps = [], []
            for x,y in picks:
                gap = float(distance[y,x])
                gaps.append(gap)
                if gap > 18:
                    raise AssertionError((view_id,name,[x,y],gap,'pick too far from drawn ink'))
                yy,xx = nearest[:,y,x]
                snapped.append([int(xx),int(yy)])
            native = [[view['native_box'][0]+x*sx, view['native_box'][1]+y*sy] for x,y in snapped]
            local = [[spec['port_direction']*(x-spec['origin'][0])*sx/ppf,
                      (spec['origin'][1]-y)*sy/ppf] for x,y in snapped]
            paths.append(dict(id=name, native_points=native, local_XZ_feet=local,
                              source_pick_preview_pixels=picks, snapped_preview_pixels=snapped,
                              max_pick_to_ink_preview_px=max(gaps),
                              review='section boundary guide; trace overlay checked separately'))
            colour=colours[i%len(colours)]
            draw.line(snapped,fill=colour,width=4)
            for x,y in snapped:
                draw.ellipse((x-4,y-4,x+4,y+4),fill=colour)
            pts=' '.join(f'{x-view["native_box"][0]:.2f},{y-view["native_box"][1]:.2f}' for x,y in native)
            svg_paths.append(f'<polyline id="{name}" points="{pts}" fill="none" stroke="{colour}" stroke-width="8"/>')
        for region in spec['regions']:
            draw.rectangle(region['box'],outline='#d37b00',width=2)
            draw.text((region['box'][0]+3,region['box'][1]+3),region['note'],fill='#b06000',font_size=16,stroke_width=1,stroke_fill='white')
        image.save(folder/f'{view_id}-overlay.png')
        record=dict(view_id=view_id, units='full-size feet', origin_preview_pixels=spec['origin'],
                    vertical_datum=spec['datum'], positive_X='port', viewing_direction='forward',
                    source_sha256=view['source_sha256'], native_pixels_per_ft=ppf,
                    shape_role='open boundary guides, not finished cutting templates or complete member outlines',
                    paths=paths, regions=spec['regions'])
        save(f'traces/{view_id}.json',record)
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{view["native_size"][0]}" height="{view["native_size"][1]}" viewBox="0 0 {view["native_size"][0]} {view["native_size"][1]}">'\
            f'<image href="../{view["native_image"]}" width="100%" height="100%"/>'+''.join(svg_paths)+'</svg>'
        (folder/f'{view_id}-overlay.svg').write_text(svg)
        print(view_id, 'section guides:', len(paths), flush=True)


def main():
    manifest=json.loads((OUT/'manifest.json').read_text())
    checked_data()
    calibration=calibrate(manifest)
    registration(manifest,calibration)
    trace_sections(manifest,calibration)


if __name__=='__main__':
    main()
