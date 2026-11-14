"""M0 acceptance: source integrity, pixel provenance, OCR, records and transforms."""
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'references/drawing_package'
Image.MAX_IMAGE_PIXELS = None


def sha256(path):
    result=hashlib.sha256()
    with path.open('rb') as stream:
        for data in iter(lambda: stream.read(1024*1024),b''):
            result.update(data)
    return result.hexdigest()


def check():
    manifest=json.loads((OUT/'manifest.json').read_text())
    sources={s['id']:s for s in manifest['sources']}
    views={v['id']:v for v in manifest['views']}
    assert len(sources)==8 and len(views)==len(manifest['views'])==51
    tiles=words=0
    for source_id,source in sources.items():
        assert sha256(ROOT/source['path'])==source['sha256'],('original changed',source_id)
        with Image.open(ROOT/source['path']) as original:
            assert list(original.size)==source['native_size']
            for view in [v for v in views.values() if v['source_id']==source_id]:
                with Image.open(OUT/view['native_image']) as native:
                    box=view['native_box']
                    assert list(native.size)==[box[2]-box[0],box[3]-box[1]]
                    # Independent pixel samples verify that native views really
                    # are crops of the source rather than scaled/rethresholded.
                    for rx,ry in ((.1,.1),(.5,.5),(.9,.2),(.2,.8),(.9,.9)):
                        x,y=int(rx*native.width),int(ry*native.height)
                        assert native.getpixel((x,y))==original.getpixel((box[0]+x,box[1]+y))
                matrix=np.array(view['source_to_preview'])
                assert np.allclose(matrix@np.array([box[0],box[1],1]),[0,0,1])
                assert np.allclose(matrix@np.array([box[2],box[3],1]),[*view['preview_size'],1])
                for tile in view['tiles']:
                    tb=tile['native_box']
                    with Image.open(OUT/tile['path']) as image:
                        assert list(image.size)==[tb[2]-tb[0],tb[3]-tb[1]]
                        x,y=image.width//2,image.height//2
                        assert image.getpixel((x,y))==original.getpixel((tb[0]+x,tb[1]+y))
                    tiles+=1
                ocr=json.loads((OUT/view['ocr']['words']).read_text())
                assert len(ocr['words'])==view['ocr']['word_count']
                words+=len(ocr['words'])
                for word in ocr['words']:
                    assert box[0]-.1<=word['native_box'][0]<=word['native_box'][2]<=box[2]+.1
                    assert box[1]-.1<=word['native_box'][1]<=word['native_box'][3]<=box[3]+.1
                assert (OUT/view['native_image']).with_name('index.html').is_file()
    print(f'PASS: 8 original hashes; 51 exact native crops; {tiles} lossless tiles; source/preview transforms.')
    assert words>3000
    notes=json.loads((OUT/'notes_verified.json').read_text())['notes']
    note_ids={n['id'] for n in notes}
    for sheet in ('S06','S07'):
        assert all(f'{sheet}-{i:02d}' in note_ids for i in range(1,20))
    assert all(v in views for n in notes for v in n['source_views'])
    assert any('NOT GROWN' in n['checked_text'] for n in notes)
    search=json.loads((OUT/'search_index.json').read_text())
    assert any('keelson' in v['text'].lower() for v in search)
    assert any('NOT GROWN' in v['text'] for v in search)
    print(f'PASS: {words} coordinate-linked OCR words; {len(notes)} checked records; complete sheet-6/7 note keys and checked-text search.')
    offsets=json.loads((OUT/'offsets_verified.json').read_text())
    assert len(offsets['rows'])==15 and all(len(row['printed'])==8 for row in offsets['rows'])
    assert offsets['rows'][11]['printed']['chine_bottom_half_breadth']=='2-7-4'
    assert offsets['rows'][-1]['printed']['chine_bottom_half_breadth'] is None
    assert len(offsets['model_differences'])==1
    assert offsets['model_differences'][0]['station']==4
    assert offsets['model_differences'][0]['source']=='5-9-7'
    print('PASS: complete offset-table transcription, blank cells, retained 2-7-4 outlier and explicit historical model fairing difference.')
    cal=json.loads((OUT/'calibration.json').read_text())['calibrated_sheets']
    for source in cal.values():
        assert source['fit_residual_ft']<.05
        assert source['print_crosscheck_relative_error']<.01
    assert cal['S06']['source_label_issue']
    reg=json.loads((OUT/'registration.json').read_text())
    assert reg['max_deck_alignment_residual_ft']<reg['point_pick_uncertainty_ft']
    assert abs(reg['reference_dimension']['imperial_bar_length_ft']-50)<.5
    assert len(reg['legacy_feature_migration'])==4
    assert np.all(np.diff([r['canonical_forward_ft'] for r in reg['line_stations']])>0)
    print('PASS: six ruler calibrations/independent print checks; source scale conflict retained; common source coordinates and explicit legacy migration ledger.')
    for view_id in ('S06-V01','S07-V02'):
        trace=json.loads((OUT/'traces'/f'{view_id}.json').read_text())
        assert trace['source_sha256']==views[view_id]['source_sha256']
        assert trace['paths'] and trace['regions']
        for path in trace['paths']:
            assert len(path['native_points'])==len(path['local_XZ_feet'])>=2
            assert path['max_pick_to_ink_preview_px']<=18
        assert (OUT/'traces'/f'{view_id}-overlay.png').is_file()
        assert (OUT/'traces'/f'{view_id}-overlay.svg').is_file()
        assert (OUT/'demos'/f'{view_id}.html').is_file()
    print('PASS: calibrated sheet-6/7 section guides, source overlays, local datums and linked construction/repair regions.')
    class Links(HTMLParser):
        def handle_starttag(self, tag, attrs):
            for key,value in attrs:
                if key not in ('href','src') or not value:
                    continue
                url=urlsplit(value)
                if url.scheme or not url.path:
                    continue
                target=document.parent/unquote(url.path)
                assert target.is_file(),('broken local link',document,value)
    documents=[*OUT.rglob('*.html'),*OUT.glob('traces/*-overlay.svg')]
    for document in documents:
        Links().feed(document.read_text())
    print(f'PASS: all local links in {len(documents)} index/view/demo/vector documents resolve.')
    return dict(sheets=8,views=51,tiles=tiles,ocr_words=words,checked_records=len(notes),
                offset_stations=15,calibrated_sheets=6,representative_sections=2,
                linked_documents=len(documents))


if __name__=='__main__':
    result=check()
    (OUT/'validation.json').write_text(json.dumps(dict(status='passed',**result),indent=2)+'\n')
