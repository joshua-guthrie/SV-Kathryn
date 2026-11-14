"""Complete sheet-6/7 reference demonstrations and registration audit card."""
import html
import json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'references/drawing_package'


def main():
    manifest=json.loads((OUT/'manifest.json').read_text())
    views={v['id']:v for v in manifest['views']}
    cal=json.loads((OUT/'calibration.json').read_text())['calibrated_sheets']
    notes=json.loads((OUT/'notes_verified.json').read_text())['notes']
    folder=OUT/'demos'
    folder.mkdir(exist_ok=True)
    for view_id in ('S06-V01','S07-V02'):
        view=views[view_id]
        sheet=view_id[:3]
        trace=json.loads((OUT/'traces'/f'{view_id}.json').read_text())
        rows=''
        for note in [n for n in notes if n['id'].startswith(sheet+'-')]:
            links=' '.join(f'<a href="../{views[v]["native_image"].replace("native.png","index.html")}">{v}</a>' for v in note['source_views'])
            dims=html.escape(json.dumps(note['dimensions_inches'],ensure_ascii=False))
            rows+=f'<tr><td>{note["id"]}</td><td>{html.escape(note["checked_text"])}</td><td>{dims}</td><td>{links}</td></tr>'
        region_rows=''.join(f'<li><b>{r["note"]}</b>: {html.escape(r["kind"])}</li>' for r in trace['regions'])
        caption_issue=cal[sheet]['source_label_issue'] or 'No conflicting printed scale caption identified.'
        page=f'''<!doctype html><meta charset="utf-8"><title>{view_id} checked section</title>
<style>body{{font:17px sans-serif;max-width:1450px;margin:2em auto;padding:0 1em}}img{{max-width:100%}}
td,th{{border:1px solid #ccd2da;padding:.5em;vertical-align:top}}table{{border-collapse:collapse}}code{{white-space:pre-wrap}}
.box{{background:#eef3f8;padding:1em}}a{{color:#17569a}}</style><a href="../index.html">Drawing index</a>
<h1>{html.escape(view_id+' — '+view['title'])}</h1>
<p><a href="../{view['native_image']}">Full native view</a> · <a href="../traces/{view_id}.json">Calibrated point/region data</a> ·
<a href="../traces/{view_id}-overlay.svg">Vector/source overlay</a> · <a href="../{view['ocr']['text']}">Unreviewed OCR</a></p>
<div class="box"><b>Calibration:</b> {cal[sheet]['native_pixels_per_ft']:.4f} original pixels/full-size foot.
<p>{html.escape(caption_issue)}</p><p><b>Trace datum:</b> {html.escape(trace['vertical_datum'])}.
Positive X is port; this section looks forward. These are open boundary guides, not finished member cutting templates.</p>
<p>Section names/frame numbers identify a view, not its longitudinal location. Lines stations, deck-beam numbers and hull-frame numbers must remain distinct.</p></div>
<img src="../traces/{view_id}-overlay.png"><h2>Visible construction and repair regions</h2><ul>{region_rows}</ul>
<h2>Checked sheet note key</h2><p>The sheet key includes objects seen beyond the cut plane as well as cut members.
Preserve the distinction between a projected fitting and a timber actually cut at the section.</p>
<table><tr><th>Note</th><th>Checked meaning</th><th>Dimensions (inches)</th><th>Source notes</th></tr>{rows}</table>
<h2>Scale source</h2><img src="../{views[sheet+'-R01']['preview']}">'''
        (folder/f'{view_id}.html').write_text(page)
    reg=json.loads((OUT/'registration.json').read_text())
    chart=Image.new('RGB',(1700,700),'white')
    draw=ImageDraw.Draw(chart)
    draw.text((28,20),'KATHRYN - SOURCE / LEGACY-PLACEMENT AUDIT',fill='black',font_size=28)
    draw.text((28,66),'Full-size feet in the declared source convention; CAD migration is M1 work.',fill='black',font_size=20)
    for i,record in enumerate(reg['legacy_feature_migration']):
        y=135+i*125
        draw.text((28,y),record['name'],fill='black',font_size=22)
        draw.text((28,y+30),f"Legacy {record['legacy_model_forward_ft']:.2f} ft  |  source {record['canonical_forward_ft']:.2f} ft  |  delta {record['delta_ft']:+.2f} ft",fill='black',font_size=19)
        lo=min(record['legacy_model_forward_ft'],record['canonical_forward_ft'])-1
        hi=max(record['legacy_model_forward_ft'],record['canonical_forward_ft'])+1
        def x(f): return 690+(f-lo)/(hi-lo)*920
        draw.line((690,y+34,1610,y+34),fill='#bbc1c9',width=3)
        for value,colour,label in ((record['legacy_model_forward_ft'],'#5d6570','legacy'),
                                   (record['canonical_forward_ft'],'#08774a','source')):
            px=x(value)
            draw.line((px,y+17,px,y+50),fill=colour,width=5)
            draw.text((px-30,y+55),label,fill=colour,font_size=18)
    draw.text((28,654),f"Sheet 4/5 deck-landmark alignment max residual: {reg['max_deck_alignment_residual_ft']:.3f} ft; declared pick uncertainty ±0.20 ft.",fill='black',font_size=19)
    chart.save(folder/'registration-audit.png')
    print('Two complete section demonstrations and registration-audit.png written.')


if __name__=='__main__':
    main()
