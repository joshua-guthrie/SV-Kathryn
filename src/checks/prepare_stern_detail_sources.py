"""Derived native stern-detail crops; originals and baseline figures preserved."""
import json
from pathlib import Path
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[2]

def main():
    manifest=json.loads((ROOT/'references/drawing_package/manifest.json').read_text())
    for view_id,box,name in (
        ('S04-V02',(105,30,530,160),'stern-side-plan-controls'),
        ('S04-V01',(20,0,410,200),'stern-davit-profile-controls'),
    ):
        view=next(v for v in manifest['views'] if v['id']==view_id)
        sx,sy=[n/p for n,p in zip(view['native_size'],view['preview_size'])]
        bounds=tuple(round(v*(sx if i%2==0 else sy)) for i,v in enumerate(box))
        with Image.open(ROOT/'references/drawing_package'/view['native_image']) as source:
            image=source.crop(bounds).convert('RGB')
        image.thumbnail((2000,1400))
        draw=ImageDraw.Draw(image)
        for x in range(0,image.width,100):
            draw.line((x,0,x,image.height),fill='#c8d8ec')
            draw.text((x+2,2),str(x),fill='#004080',font_size=16)
        for y in range(0,image.height,100):
            draw.line((0,y,image.width,y),fill='#edcccc')
            draw.text((2,y+2),str(y),fill='#9c2020',font_size=16)
        image.save(ROOT/'renders'/f'{name}.png')
        print(view_id,dict(preview_size=view['preview_size'],native_size=view['native_size'],
                          crop_preview_box=box,display_size=image.size))

if __name__=='__main__':main()
