"""Archive official LOC Kathryn catalog/resource metadata and photo references."""
import json
import hashlib
import urllib.request
import re
import html
import sys
import time
from http.client import IncompleteRead
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'Reference Material/LOC_Kathryn_photos'
URLS={
    'item':'https://www.loc.gov/item/md1454/?fo=json',
    'resource':'https://www.loc.gov/resource/hhh.md1454.photos/?sp=24&fo=json',
}


def fetch(url):
    request=urllib.request.Request(url,headers={'User-Agent':'Kathryn-CAD-reference-review/1.0'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request,timeout=90) as response:return response.read()
        except (OSError,IncompleteRead):
            if attempt==2:raise
            time.sleep(attempt+1)


def main():
    OUT.mkdir(exist_ok=True)
    if '--masters' in sys.argv:
        manifest=json.loads((OUT/'manifest.json').read_text())
        wanted=set(sys.argv[sys.argv.index('--masters')+1:])
        selected=[r for r in manifest['photos'] if r['id'] in wanted]
        for row in selected:
            path=OUT/row['master_file']
            if not path.exists():path.write_bytes(fetch(row['master_url']))
            row['master_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
            with Image.open(path) as image:
                row['master_size']=list(image.size)
                detail=image.convert('RGB')
                detail.thumbnail((2400,2000),Image.Resampling.LANCZOS)
                detail.save(OUT/f'{row["id"]}-detail.jpg',quality=96)
            print(row['id'],'master',row['master_size'],flush=True)
            (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        return
    for name,url in URLS.items():
        target=OUT/f'{name}.json'
        if not target.exists():
            data=json.loads(fetch(url))
            target.write_text(json.dumps(data,indent=2)+'\n')
        else:data=json.loads(target.read_text())
    item=json.loads((OUT/'item.json').read_text())
    resource=next(r for r in item['resources'] if 'photos' in r.get('url',''))
    records=[]
    for page,files in enumerate(resource['files'],1):
        caption=next(f for f in files if f.get('use')=='caption')
        title=caption['title'].split(' - KATHRYN')[0]
        printed=re.match(r'^(\d+)\.',title)
        identity=f'LOC-P{int(printed.group(1)):02d}' if printed else 'LOC-C01'
        review=max((f for f in files if f['mimetype'] in ('image/jpeg','image/jpg')),key=lambda f:f.get('width',0))
        master=next(f for f in files if f['mimetype']=='image/tiff')
        records.append(dict(id=identity,page=page,title=title,
            page_url=f'https://www.loc.gov/resource/hhh.md1454.photos/?sp={page}',
            caption_url=caption['aka'],review_url=review['url'],master_url=master['url'],
            review_file=f'{page:02d}-{identity}.jpg',master_file=f'{page:02d}-{identity}.tif',
            review_size=[review.get('width'),review.get('height')]))
    def download(row):
        path=OUT/row['review_file']
        if not path.exists():path.write_bytes(fetch(row['review_url']))
        row['review_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
        print(row['id'],row['title'],flush=True)
    with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(download,records))
    manifest=dict(collection_url='https://www.loc.gov/item/md1454/',
                  requested_url='https://www.loc.gov/resource/hhh.md1454.photos/?sp=24&st=text',
                  retrieval='Official catalog/resource JSON; ordinary HTML returned HTTP 403.',
                  collection_title=item['item']['title'],
                  rights=item['item'].get('rights_advisory'),
                  dating=item['item'].get('created_published'),
                  source_use='Vessel-specific visual QA. Perspective, lens and temporary survey removals are not calibrated plan dimensions.',
                  photos=records)
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    for sheet,start in enumerate(range(0,len(records),12),1):
        canvas=Image.new('RGB',(1800,1520),'white')
        draw=ImageDraw.Draw(canvas)
        draw.text((20,12),f'KATHRYN - Library of Congress HAER MD-117 photos / sheet {sheet}',fill='black',font_size=24)
        for index,row in enumerate(records[start:start+12]):
            x=(index%3)*600;y=55+(index//3)*360
            image=ImageOps.contain(Image.open(OUT/row['review_file']).convert('RGB'),(580,285))
            canvas.paste(image,(x+(600-image.width)//2,y))
            draw.text((x+10,y+289),f'{row["id"]} / LOC page {row["page"]}',fill='black',font_size=18)
            title=row['title']
            for line in range(2):draw.text((x+10,y+311+line*19),title[line*49:(line+1)*49],fill='black',font_size=14)
        canvas.save(OUT/f'contact-{sheet:02d}.jpg',quality=92)
    cards='\n'.join(f'<section><h2>{html.escape(r["id"]+" — "+r["title"])}</h2>'
        f'<img src="{r["review_file"]}" loading="lazy" style="max-width:100%">'
        f'<p><a href="{r["page_url"]}">LOC page {r["page"]}</a> · '
        f'<a href="{r["master_url"]}">Original TIFF</a></p></section>' for r in records)
    (OUT/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Kathryn LOC photo references</title>'
        '<style>body{font:16px sans-serif;max-width:1100px;margin:2em auto}section{border-top:1px solid #aaa;margin-top:2em}</style>'
        '<h1>Kathryn — HAER MD-117 Library of Congress photographs</h1>'
        '<p>31 black-and-white photos plus one color transparency. Caption numbers differ from gallery page numbers.</p>'+cards)


if __name__=='__main__':main()
