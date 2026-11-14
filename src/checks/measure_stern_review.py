"""Native traceable stern/helm review crops and canonical longitudinal picks."""
import json
import math
from pathlib import Path
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[2]
PACKAGE=ROOT/'references/drawing_package'


def main():
    manifest=json.loads((PACKAGE/'manifest.json').read_text())
    registration=json.loads((PACKAGE/'registration.json').read_text())
    records=[]
    measurements=[]
    for key,box,name in (
        ('S04-V02',(40,100,330,410),'stern-deck-source'),
        ('S04-V01',(50,115,300,305),'stern-profile-source'),
        ('S02-V01',(85,120,360,385),'stern-lines-source'),
    ):
        view=next(v for v in manifest['views'] if v['id']==key)
        sx,sy=[n/p for n,p in zip(view['native_size'],view['preview_size'])]
        bounds=tuple(round(v*(sx if i%2==0 else sy)) for i,v in enumerate(box))
        with Image.open(PACKAGE/view['native_image']) as image:crop=image.crop(bounds).convert('RGB')
        crop.thumbnail((2000,2000),Image.Resampling.LANCZOS)
        crop.save(ROOT/'renders'/f'{name}.png')
        draw=ImageDraw.Draw(crop)
        for x in range(0,crop.width,100):
            draw.line((x,0,x,crop.height),fill='#dfaaaa')
            draw.text((x+2,3),str(x),fill='#a00000',font_size=17)
        for y in range(0,crop.height,100):
            draw.line((0,y,crop.width,y),fill='#aabddd')
            draw.text((3,y+3),str(y),fill='#004080',font_size=17)
        crop.save(ROOT/'renders'/f'{name}-grid.png')
        records.append(dict(id=name,view=key,preview_box=box,view_native_box=bounds,
                            display_size=list(crop.size),source_sha256=view['source_sha256']))
        source=next(s for s in manifest['sources'] if s['id']==key[:3])
        a,b=registration['transformations'][key[:3]]['grid_x_to_F']
        ratio=crop.width/(bounds[2]-bounds[0])
        picks=( [('counter upper',[223,397]),('counter lower',[1015,828]),('stock at deck',[736,408])] if key=='S04-V01' else
                [('deck aft centre',[162,840]),('upper rail aft centre',[380,840]),
                 ('helm box aft',[595,840]),('helm box fore',[1110,840]),('wheel hub',[1160,840])] if key=='S04-V02' else
                [('counter upper',[182,159]),('counter junction',[870,555])] )
        for label,p in picks:
            native=[view['native_box'][0]+bounds[0]+p[0]/ratio,
                    view['native_box'][1]+bounds[1]+p[1]/ratio]
            value=a*native[0]/source['native_size'][0]*1440+b
            measurements.append(dict(view=key,label=label,source_native_point=native,canonical_F_ft=value,display_pick=p))
            print(key,label,'F',value)
    view=next(v for v in manifest['views'] if v['id']=='S04-V02')
    source=next(s for s in manifest['sources'] if s['id']=='S04')
    a,b=registration['transformations']['S04']['grid_x_to_F']
    def F(px):
        native=view['native_box'][0]+px*view['native_size'][0]/view['preview_size'][0]
        return a*native/source['native_size'][0]*1440+b
    for label,x in [('transom centre',75),('helm box aft',149),('helm box fore',243),('wheel',251)]:
        print(label,'preview X',x,'canonical F',F(x))
    (PACKAGE/'stern_review_crops.json').write_text(json.dumps(records,indent=2)+'\n')
    (PACKAGE/'stern_review_picks.json').write_text(json.dumps(measurements,indent=2)+'\n')
    def value(view,label):return next(r['canonical_F_ft'] for r in measurements if r['view']==view and r['label']==label)
    aft=value('S04-V02','helm box aft');fore=value('S04-V02','helm box fore')
    stock_deck=value('S04-V01','stock at deck')
    data=dict(source_views=['S02-V01','S04-V01','S04-V02'],
        source_hashes={s['id']:s['sha256'] for s in manifest['sources'] if s['id'] in ('S02','S04')},
        photo_qa=['LOC-P28','LOC-P29','LOC-P30'],
        transom_forward_per_vertical_ft=1.8,
        rake_basis='Scaled counter guides in S02/S04, approximately 1.74/1.84 forward per vertical foot; rounded to 1.8. Upper deck length reference retained.',
        helm_box_aft_ft=aft,helm_box_fore_ft=fore,helm_box_width_ft=289/149.9803,
        helm_wheel_forward_ft=value('S04-V02','wheel hub'),
        rudder_stock_at_deck_ft=stock_deck,
        rudder_head_forward_ft=stock_deck-.5*math.tan(math.radians(25)),
        helm_basis='Native S04 deck-plan box faces and wheel, independent inboard-profile stock/deck crossing. Case height and fine wheel details reconstructed with LOC-P28/29.',
        aft_top_rail_above_deck_ft=308/149.9803,
        aft_lower_rail_above_deck_ft=198/149.9803,
        rear_rail_centre_ft=value('S04-V02','upper rail aft centre'),
        rear_rail_shoulder_ft=1.0,rear_rail_halfwidth_ft=5.0,
        rail_basis='Inboard-profile vertical rail/deck witnesses and inset curved rail in S04 deck plan; shoulder blending reconstructed. Rail is distinct from aftmost deck edge.',
        pick_uncertainty_ft=.20)
    (PACKAGE/'stern_helm_registration.json').write_text(json.dumps(data,indent=2)+'\n')


if __name__=='__main__':main()
