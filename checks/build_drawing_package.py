"""Build indexed, source-traceable images and OCR for milestone M0.

Run from any directory; no CAD or original reference files are modified.
"""
import argparse
import csv
import hashlib
import html
import io
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image, ImageDraw

from drawing_catalog import SHEET_TITLES, VIEWS
from ocr_tesseract import Tesseract

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'drawing_package'
Image.MAX_IMAGE_PIXELS = None
MODEL_URL = 'https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/main/eng.traineddata'


def digest(path):
    hasher = hashlib.sha256()
    with path.open('rb') as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b''):
            hasher.update(data)
    return hasher.hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def relative(path):
    return str(path.relative_to(OUT))


def images():
    manifest = {'schema_version': 1, 'originals_modified': False,
                'coordinate_system': 'original scan pixels; x right, y down',
                'sources': [], 'views': []}
    for sheet, title in SHEET_TITLES.items():
        path = ROOT / '2d model' / f'master-pnp-habshaer-md-md1400-md1454-sheet-{sheet:05d}a.tif'
        folder = OUT / f'S{sheet:02d}'
        folder.mkdir(parents=True, exist_ok=True)
        with Image.open(path) as source:
            width, height = source.size
            source_meta = dict(id=f'S{sheet:02d}', title=title,
                               path=str(path.relative_to(ROOT)), sha256=digest(path),
                               native_size=[width, height], mode=source.mode,
                               dpi=[float(v) for v in source.info.get('dpi', (0, 0))])
            overview = source.convert('L')
            overview.thumbnail((1800, 1200), Image.Resampling.LANCZOS)
            overview = overview.convert('RGB')
            draw = ImageDraw.Draw(overview)
            for spec in [v for v in VIEWS if v['sheet'] == sheet]:
                bounds = tuple(round(v * (width / 1440 if i % 2 == 0 else height / 960))
                               for i, v in enumerate(spec['grid_box']))
                x0, y0, x1, y1 = bounds
                assert 0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height
                view_folder = folder / spec['id']
                view_folder.mkdir(exist_ok=True)
                crop = source.crop(bounds)
                native = view_folder / 'native.png'
                crop.save(native)
                preview = crop.convert('L')
                preview.thumbnail((2000, 1600), Image.Resampling.LANCZOS)
                preview.save(view_folder / 'preview.png')
                px, py = preview.width / crop.width, preview.height / crop.height
                entry = {**spec, 'source_id': source_meta['id'],
                         'source_sha256': source_meta['sha256'],
                         'native_box': list(bounds), 'native_size': list(crop.size),
                         'native_image': relative(native),
                         'preview': relative(view_folder / 'preview.png'),
                         'preview_size': list(preview.size),
                         'source_to_preview': [[px, 0, -x0 * px], [0, py, -y0 * py], [0, 0, 1]],
                         'tiles': []}
                # Original-resolution overlapping tiles retain exact pixel data.
                for row, ty in enumerate(range(0, crop.height, 1472)):
                    for col, tx in enumerate(range(0, crop.width, 1472)):
                        box = (tx, ty, min(crop.width, tx + 1600), min(crop.height, ty + 1600))
                        filename = f'tile-{row:02d}-{col:02d}.png'
                        tile_path = view_folder / filename
                        crop.crop(box).save(tile_path)
                        entry['tiles'].append(dict(path=relative(tile_path),
                            native_box=[x0 + box[0], y0 + box[1], x0 + box[2], y0 + box[3]]))
                manifest['views'].append(entry)
                q = (x0 * overview.width / width, y0 * overview.height / height,
                     x1 * overview.width / width, y1 * overview.height / height)
                colour = '#ba2929' if spec['kind'] in ('notes', 'table') else '#125da8'
                draw.rectangle(q, outline=colour, width=2)
                draw.text((q[0] + 4, q[1] + 3), spec['id'], fill=colour, font_size=15,
                          stroke_width=1, stroke_fill='white')
            overview.save(folder / 'overview.png')
            source_meta['overview'] = relative(folder / 'overview.png')
            manifest['sources'].append(source_meta)
        print(f'S{sheet:02d}: native views and tiles complete', flush=True)
    write_json(OUT / 'manifest.json', manifest)
    return manifest


def ocr_one(spec, tessdata):
    folder = (OUT / spec['native_image']).parent
    with Image.open(OUT / spec['native_image']) as source:
        image = source.convert('L')
    original_size = image.size
    image.thumbnail((3600, 3600), Image.Resampling.LANCZOS)
    sx, sy = image.width / original_size[0], image.height / original_size[1]
    with Tesseract(tessdata) as engine:
        text, tsv = engine.recognize(image, spec['ocr_psm'], dpi=max(70, round(400 * sx)))
        version = engine.version
    (folder / 'ocr.txt').write_text(text)
    (folder / 'ocr.tsv').write_text(tsv)
    words = []
    fields = 'level page_num block_num par_num line_num word_num left top width height conf text'.split()
    reader = csv.DictReader(io.StringIO(tsv), delimiter='\t',
                            fieldnames=None if tsv.startswith('level\t') else fields)
    for row in reader:
        if row.get('level') != '5' or not row.get('text', '').strip():
            continue
        x, y, w, h = [float(row[key]) for key in ('left', 'top', 'width', 'height')]
        x0, y0 = spec['native_box'][:2]
        words.append(dict(text=row['text'], engine_confidence=float(row['conf']),
                          native_box=[x0 + x / sx, y0 + y / sy,
                                      x0 + (x + w) / sx, y0 + (y + h) / sy]))
    record = dict(view_id=spec['id'], review_status='unreviewed OCR',
                  engine='Tesseract C API', version=version, language='eng',
                  psm=spec['ocr_psm'], ocr_size=list(image.size),
                  source_to_ocr=[[sx, 0, -spec['native_box'][0] * sx],
                                 [0, sy, -spec['native_box'][1] * sy], [0, 0, 1]], words=words)
    write_json(folder / 'ocr_words.json', record)
    print(f"{spec['id']}: OCR {len(words)} words", flush=True)
    return spec['id'], {'text': relative(folder / 'ocr.txt'),
                        'tsv': relative(folder / 'ocr.tsv'),
                        'words': relative(folder / 'ocr_words.json'),
                        'word_count': len(words), 'review_status': 'unreviewed OCR'}


def ocr(manifest, tessdata, jobs):
    model = tessdata / 'eng.traineddata'
    if not model.is_file():
        raise FileNotFoundError(f'English model required in {tessdata}; see package README')
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        results = dict(pool.map(lambda spec: ocr_one(spec, tessdata), manifest['views']))
    for spec in manifest['views']:
        spec['ocr'] = results[spec['id']]
    manifest['ocr_model'] = dict(source_url=MODEL_URL, sha256=digest(model),
                                 license='Apache-2.0, tessdata_fast repository')
    write_json(OUT / 'manifest.json', manifest)


def index(manifest):
    cards = []
    rows = []
    checked_path = OUT / 'notes_verified.json'
    checked = json.loads(checked_path.read_text())['notes'] if checked_path.is_file() else []
    for spec in manifest['views']:
        folder = (OUT / spec['native_image']).parent
        text = (OUT / spec['ocr']['text']).read_text() if 'ocr' in spec else ''
        verified = [n for n in checked if spec['id'] in n['source_views']]
        checked_html = ''.join(f'<h3>{html.escape(n["id"])}</h3><p>{html.escape(n["checked_text"])}</p>'
                               for n in verified)
        escape = html.escape
        tiles = '\n'.join(f'<li><a href="{Path(t["path"]).name}">{Path(t["path"]).name}</a> '
                          f'{t["native_box"]}</li>' for t in spec['tiles'])
        body = f'''<!doctype html><meta charset="utf-8"><title>{spec['id']}</title>
<style>body{{font:16px sans-serif;max-width:1400px;margin:2em auto}}img{{max-width:100%}}
pre{{white-space:pre-wrap;background:#f3f4f6;padding:1em}}a{{color:#17569a}}</style>
<a href="../../index.html">Package index</a><h1>{escape(spec['id']+' '+spec['title'])}</h1>
<p>Original scan pixels: {spec['native_box']}; source SHA-256: {spec['source_sha256']}.</p>
<p><a href="native.png">Native lossless view</a> · <a href="ocr.txt">Raw OCR</a> ·
<a href="ocr_words.json">Word coordinates/confidence</a> · <a href="../../manifest.json">Manifest</a></p>
<img src="preview.png"><h2>Checked construction records</h2>{checked_html}
<h2>Raw OCR — requires review</h2><pre>{escape(text)}</pre>
<h2>Original-resolution tiles and native bounds</h2><ul>{tiles}</ul>'''
        (folder / 'index.html').write_text(body)
        entry = dict(id=spec['id'], sheet=spec['source_id'], title=spec['title'],
                     kind=spec['kind'], page=relative(folder / 'index.html'),
                     preview=spec['preview'], text=text+'\n'+'\n'.join(n['id']+' '+n['checked_text'] for n in verified))
        cards.append(entry)
        rows.append(f"- [{spec['id']} — {spec['title']}]({entry['page']}) ({spec['kind']})")
    # Embed records for local file:// search; no web server or remote script needed.
    data = json.dumps(cards, ensure_ascii=False).replace('<', '\\u003c')
    overview = ''.join(f'<a href="{s["overview"]}"><img width="250" src="{s["overview"]}" '
                       f'alt="{html.escape(s["title"])}"></a>' for s in manifest['sources'])
    page = '''<!doctype html><meta charset="utf-8"><title>Kathryn drawing index</title>
<style>body{font:16px sans-serif;max-width:1450px;margin:2em auto;padding:0 1em;background:#f7f8fa}
input{font:inherit;padding:.6em;width:70%}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:1em}
article{background:white;padding:1em;border:1px solid #ccd2da}article img{width:100%;height:190px;object-fit:contain}
a{color:#17569a}.overview img{border:1px solid #ccd2da;margin:4px}small{color:#555}</style>
<h1>Kathryn — indexed drawing reference package</h1>
<p>Original TIFFs remain authoritative. Raw OCR is unreviewed; checked notes/tables and calibrated geometry have separate evidence records.</p>
<p><a href="manifest.json">Source/pixel manifest</a> · <a href="notes_verified.json">Checked construction notes</a> ·
<a href="offsets_verified.json">Checked offset table</a> · <a href="calibration.json">Scale calibrations</a> ·
<a href="registration.json">Coordinate registration</a> · <a href="ACCEPTANCE.md">M0 acceptance</a></p>
<p><b>Checked section demonstrations:</b> <a href="demos/S06-V01.html">Sheet 6 / frame set 4</a> ·
<a href="demos/S07-V02.html">Sheet 7 / cabin hatch</a> · <a href="demos/registration-audit.png">Source/legacy placement audit</a></p>
<div class="overview">OVERVIEWS</div><h2>Search views, notes and raw OCR</h2>
<input id="q" placeholder="Try keelson, sister, 5-1/2, cabin, S06, frame set…"><p id="count"></p><div id="results" class="grid"></div>
<script>const views=DATA;function show(){const q=document.querySelector('#q').value.toLowerCase();
const rows=views.filter(v=>(v.id+' '+v.title+' '+v.kind+' '+v.text).toLowerCase().includes(q));
document.querySelector('#count').textContent=rows.length+' views';const root=document.querySelector('#results');root.replaceChildren();
for(const v of rows){const a=document.createElement('article'),link=document.createElement('a'),im=document.createElement('img'),h=document.createElement('h3'),s=document.createElement('small');
link.href=v.page;im.src=v.preview;im.loading='lazy';h.textContent=v.id+' — '+v.title;link.append(im,h);s.textContent=v.kind+'; OCR requires review';a.append(link,s);root.append(a)}}
document.querySelector('#q').addEventListener('input',show);show();</script>'''.replace('OVERVIEWS', overview).replace('DATA', data)
    (OUT / 'index.html').write_text(page)
    (OUT / 'INDEX.md').write_text('# Kathryn indexed views\n\n' + '\n'.join(rows) + '\n')
    write_json(OUT / 'search_index.json', cards)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', choices=('images', 'ocr', 'index', 'all'), default='all')
    parser.add_argument('--tessdata', type=Path, default=Path('/tmp/opencode/tessdata'))
    parser.add_argument('--jobs', type=int, default=2)
    args = parser.parse_args()
    manifest = images() if args.stage in ('images', 'all') else json.loads((OUT / 'manifest.json').read_text())
    if args.stage in ('ocr', 'all'):
        ocr(manifest, args.tessdata, args.jobs)
    index(manifest)
    print(f"Package: {len(manifest['sources'])} sheets, {len(manifest['views'])} views", flush=True)


if __name__ == '__main__':
    main()
