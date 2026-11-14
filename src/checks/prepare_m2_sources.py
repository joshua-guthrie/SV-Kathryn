"""Readable, source-traceable centreline review details for M2."""
import json
from pathlib import Path
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'drawing_package'
Image.MAX_IMAGE_PIXELS=None


def main():
    manifest=json.loads((OUT/'manifest.json').read_text())
    for key in ('S04-V01','S05-V01','S05-V02','S06-V02','S07-V01'):
        view=next(v for v in manifest['views'] if v['id']==key)
        image=Image.open(OUT/view['preview']).convert('RGB')
        draw=ImageDraw.Draw(image)
        for x in range(0,image.width,100):
            draw.line((x,0,x,image.height),fill='#e0aaaa')
            draw.text((x+2,2),str(x),fill='#a00000',font_size=17)
        for y in range(0,image.height,100):
            draw.line((0,y,image.width,y),fill='#aabde0')
            draw.text((2,y+3),str(y),fill='#004080',font_size=17)
        image.save(ROOT/'renders'/f'm2-{key}-grid.png')
        print(key,view['native_box'],view['preview_size'])
    for sheet,box,name in (
        (4,(620,280,965,455),'m2-board-profile-source.png'),
        (5,(380,560,830,620),'m2-keelson-trunk-plan-source.png'),
        (5,(705,192,835,272),'m2-mast-partners-source.png'),
        (7,(365,190,430,392),'m2-trunk-section-source.png')):
        path=ROOT/'2d model'/f'master-pnp-habshaer-md-md1400-md1454-sheet-{sheet:05d}a.tif'
        with Image.open(path) as image:
            native=tuple(round(v*(image.width/1440 if i%2==0 else image.height/960)) for i,v in enumerate(box))
            crop=image.crop(native).convert('L')
            crop.thumbnail((2000,1800),Image.Resampling.LANCZOS)
            crop.save(ROOT/'renders'/name)
            if name=='m2-board-profile-source.png':
                annotated=crop.convert('RGB')
                draw=ImageDraw.Draw(annotated)
                for x in range(0,annotated.width,100):
                    draw.line((x,0,x,annotated.height),fill='#ddaaaa')
                    draw.text((x+2,2),str(x),fill='#a00000',font_size=19)
                for y in range(0,annotated.height,100):
                    draw.line((0,y,annotated.width,y),fill='#aabddd')
                    draw.text((2,y+3),str(y),fill='#004080',font_size=19)
                annotated.save(ROOT/'renders/m2-board-profile-grid.png')
            print(name,native)


if __name__=='__main__':main()
