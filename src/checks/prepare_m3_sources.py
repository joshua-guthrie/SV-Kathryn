"""Lossless source crops/coordinate grids for the M3 member interpretation."""
import json
from pathlib import Path
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[2]
PACKAGE=ROOT/'references/drawing_package'
Image.MAX_IMAGE_PIXELS=None


def main():
    manifest=json.loads((PACKAGE/'manifest.json').read_text())
    records=[]
    for key in ('S05-V02','S06-V01','S06-V02','S06-V03','S07-V01'):
        view=next(v for v in manifest['views'] if v['id']==key)
        image=Image.open(PACKAGE/view['preview']).convert('RGB')
        draw=ImageDraw.Draw(image)
        for x in range(0,image.width,100):
            draw.line((x,0,x,image.height),fill='#dfaaaa')
            draw.text((x+2,4),str(x),fill='#a00000',font_size=18)
        for y in range(0,image.height,100):
            draw.line((0,y,image.width,y),fill='#aabddd')
            draw.text((4,y+3),str(y),fill='#004080',font_size=18)
        image.save(ROOT/'renders'/f'm3-{key}-grid.png')
    for key,box,name in (
        ('S05-V02',(560,205,1245,323),'m3-hold-frame-strip'),
        ('S05-V02',(1220,175,1700,345),'m3-forward-frame-strip'),
        ('S05-V02',(25,15,620,525),'m3-aft-frames'),
        ('S06-V03',(0,650,1770,1470),'m3-frame-conception'),
        ('S05-V02',(1470,220,1610,310),'m3-samson-post-plan'),
    ):
        view=next(v for v in manifest['views'] if v['id']==key)
        sx,sy=[n/p for n,p in zip(view['native_size'],view['preview_size'])]
        bounds=(round(box[0]*sx),round(box[1]*sy),round(box[2]*sx),round(box[3]*sy))
        with Image.open(PACKAGE/view['native_image']) as image:
            crop=image.crop(bounds).convert('RGB')
        crop.thumbnail((2400,1800),Image.Resampling.LANCZOS)
        crop.save(ROOT/'renders'/f'{name}.png')
        draw=ImageDraw.Draw(crop)
        for x in range(0,crop.width,100):
            draw.line((x,0,x,crop.height),fill='#dfaaaa')
            draw.text((x+2,3),str(x),fill='#a00000',font_size=18)
        for y in range(0,crop.height,100):
            draw.line((0,y,crop.width,y),fill='#aabddd')
            draw.text((3,y+3),str(y),fill='#004080',font_size=18)
        crop.save(ROOT/'renders'/f'{name}-grid.png')
        records.append(dict(id=name,view=key,view_native_box=bounds,
                            source_native_box=[bounds[0]+view['native_box'][0],bounds[1]+view['native_box'][1],
                                               bounds[2]+view['native_box'][0],bounds[3]+view['native_box'][1]],
                            preview_size=list(crop.size)))
    source=next(s for s in manifest['sources'] if s['id']=='S04')
    with Image.open(ROOT/source['path']) as image:
        box=(940,215,1080,440)
        bounds=tuple(round(v*(image.width/1440 if i%2==0 else image.height/960)) for i,v in enumerate(box))
        crop=image.crop(bounds).convert('RGB')
        crop.thumbnail((1600,1800),Image.Resampling.LANCZOS)
        crop.save(ROOT/'renders/m3-samson-post-profile.png')
        records.append(dict(id='m3-samson-post-profile',source='S04',source_native_box=bounds,preview_size=list(crop.size)))
        box=(1080,270,1150,330)
        bounds=tuple(round(v*(image.width/1440 if i%2==0 else image.height/960)) for i,v in enumerate(box))
        crop=image.crop(bounds).convert('RGB')
        draw=ImageDraw.Draw(crop)
        for y in range(270,331,5):
            yy=(y-270)*image.height/960
            draw.line((0,yy,crop.width,yy),fill='#b5c9e8')
            draw.text((2,yy+2),str(y),fill='#004080',font_size=17)
        crop.save(ROOT/'renders/m3-bowsprit-heel-profile-grid.png')
        records.append(dict(id='m3-bowsprit-heel-profile-grid',source='S04',source_native_box=bounds,preview_size=list(crop.size)))
    (PACKAGE/'m3_source_crops.json').write_text(json.dumps(records,indent=2)+'\n')


if __name__=='__main__':main()
