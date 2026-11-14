"""Scale-aware actual-mesh stern review plus measured-source/photo witnesses."""
import json
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
from render_m1 import render

ROOT=Path(__file__).resolve().parents[2]


def main():
    parts=json.loads((ROOT/'.soma/model.map.json').read_text())['parts']
    visible=tuple(p['name'] for p in parts if p['group'].startswith('Deck/Rails') or
                  p['group']=='Deck/Planking' or p['name'].startswith('Helm lid') or
                  p['name'] in ('Steering pedestal','Helm wheel','Wheel shaft','Main cabin roof','Companionway roof'))
    render('stern-corrected-perspective.png',camera=((180,430,240),(0,220,65),85),mast_clip=106,show_names=visible)
    render('stern-corrected-plan.png',camera=((0,225,650),(0,225,0),75),mast_clip=106,show_names=visible)
    render('stern-corrected-cutaway.png',True,camera=((-500,200,85),(0,205,50),65),mast_clip=106,show_names=visible)
    canvas=Image.new('RGB',(2000,1940),'white')
    draw=ImageDraw.Draw(canvas)
    draw.text((22,15),'KATHRYN - DRAWING-BASED STERN / HELM CORRECTION, FULL-SIZE 1:1',fill='black',font_size=27)
    for file,xy,limit,title in (
        ('renders/stern-corrected-perspective.png',(15,75),(1150,850),'Actual CAD: corrected rail, longer helm case, wood lid'),
        ('references/loc_photos/LOC_Kathryn_photos/LOC-P28-detail.jpg',(1200,75),(780,850),'LOC-P28: helm / stern reference'),
        ('renders/stern-corrected-cutaway.png',(15,1010),(1150,700),'Actual CAD section: raked counter and stock clearance'),
        ('renders/stern-profile-source.png',(1200,1010),(780,700),'S04 inboard profile: controlling geometry'),
    ):
        image=ImageOps.contain(Image.open(ROOT/file).convert('RGB'),limit)
        draw.text(xy,title,fill='black',font_size=20)
        canvas.paste(image,(xy[0],xy[1]+32))
    draw.text((25,1820),'Measured S04 helm case: about 3 ft 5 in long; rear case-to-rail clearance: about 1 ft 5 in.',fill='black',font_size=22)
    draw.text((25,1860),'Drawings govern dimensions. Photographs cross-check appearance; perspective is not an absolute scale.',fill='black',font_size=20)
    canvas.save(ROOT/'renders/stern-helm-review.png')


if __name__=='__main__':main()
