"""Locate exposed hull-frame edges from native hold-plan ink; reviewed picks only."""
import json
import sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
PACKAGE=ROOT/'drawing_package'

# Reviewed timber edge pairs in the 2000-pixel S05-V02 preview. These transform
# back to native scan pixels before registration. 'o' is the explicit older
# stipple; 'p' primary age unresolved; 'r' additional unmarked repair-pattern.
PORT={
 20:[(594,605,'o')],19:[(637.64,648.44,'r'),(648.44,657.13,'o')],
 18:[(684.89,691.46,'r'),(691.46,700.78,'o'),(700.78,712.02,'r')],
 17:[(736.17,747.09,'r'),(747.09,757.05,'o'),(757.05,766.90,'r')],
 16:[(788.73,797.84,'r'),(797.84,809.07,'o'),(809.07,820.72,'r')],
 15:[(844.14,851.66,'r'),(851.66,862.58,'o')],14:[(900.40,908.46,'r'),(908.46,919.05,'o')],
 13:[(965.99,976.05,'o')],12:[(1018.22,1025.85,'p')],11:[(1069.72,1079.25,'o')],
 10:[(1113.37,1121.85,'r'),(1121.85,1131.38,'o')],9:[(1173.13,1181.08,'p')],
 8:[(1216.15,1224,'p')],7:[(1242.64,1261.39,'p'),(1277.50,1287.98,'r')],
 6:[(1328.14,1340.54,'p')],5:[(1392.99,1403.79,'p'),(1403.79,1413.44,'r')],
 4:[(1440.03,1453.59,'p')],3:[(1488.03,1505.62,'o')],2:[(1534.65,1544.92,'p')],
 1:[(1599,1611,'p')],
}
STARBOARD={
 20:[(594,605,'o')],19:[(638.91,648.44,'r'),(648.44,658.40,'o')],
 18:[(695.06,703.22,'o'),(703.22,713.18,'r')],
 17:[(737.23,744.65,'r'),(744.65,755.14,'o'),(755.14,766.05,'r')],
 16:[(792.54,799.96,'r'),(799.96,811.40,'o')],
 15:[(843.93,852.41,'r'),(852.41,865.44,'o')],
 14:[(892.14,900.40,'r'),(900.40,911,'r'),(911,919.90,'o')],
 13:[(949.57,959.10,'r'),(959.10,967.15,'r'),(967.15,976.48,'o')],
 12:[(1018.22,1030.30,'p')],11:[(1070.99,1080.53,'o')],10:[(1123.33,1133.08,'o')],
 9:[(1172.07,1178.85,'p')],8:[(1215.41,1224.09,'p')],
 7:[(1242.64,1261.39,'p'),(1277.50,1287.98,'r')],6:[(1328.14,1340.54,'p')],
 5:[(1392.99,1403.79,'p'),(1403.79,1413.44,'r')],4:[(1440.03,1453.59,'p')],
 3:[(1489.30,1506.15,'o')],2:[(1534.65,1544.18,'p')],1:[(1599,1611,'p')],
}


def make_ledger(manifest,view):
    registration=json.loads((PACKAGE/'registration.json').read_text())
    source=next(s for s in manifest['sources'] if s['id']=='S05')
    a,b=registration['transformations']['S05']['grid_x_to_F']
    def native(px):return view['native_box'][0]+px*view['native_size'][0]/view['preview_size'][0]
    def forward(px):return a*native(px)/source['native_size'][0]*1440+b
    s4=next(s for s in manifest['sources'] if s['id']=='S04')
    deck=next(v for v in manifest['views'] if v['id']=='S04-V02')
    a4,b4=registration['transformations']['S04']['grid_x_to_F']
    heel_px=1588.0
    heel_native=deck['native_box'][0]+heel_px*deck['native_size'][0]/deck['preview_size'][0]
    bowsprit_heel=a4*heel_native/s4['native_size'][0]*1440+b4
    cal=json.loads((PACKAGE/'calibration.json').read_text())
    heel_above_post=(318.5-292.0)*s4['native_size'][1]/960/cal['calibrated_sheets']['S04']['native_pixels_per_ft']
    members=[]
    image=Image.open(PACKAGE/view['preview']).convert('RGB')
    draw=ImageDraw.Draw(image)
    for side,rows in ((1,PORT),(-1,STARBOARD)):
        for number,spans in rows.items():
            for index,(left,right,kind) in enumerate(spans):
                primary=kind!='r'
                centre=(left+right)/2
                mirrored=side<0 and number<=7
                basis=('construction-inferred position against the stem knee' if number==1 else
                       'opposite-side continuation; hidden by lining' if mirrored else
                       'scale-measured exposed plan edges')
                f=forward(centre)
                members.append(dict(id=f'F{number:02d}-{("P" if side>0 else "S")}-{index+1}',
                    set=number,side=side,forward_ft=f,sided_ft=forward(right)-forward(left),
                    preview_edges=[left,right],source_native_edges=[native(left),native(right)],
                    source_view='S05-V02',dimension_basis=basis,
                    role='primary' if primary else 'repair-pattern',
                    older_graphic=kind=='o',
                    older_graphic_scope='identified exposed bottom only; associated side-futtock age unresolved',
                    age=('older, possibly original' if kind=='o' else 'unresolved'),
                    repair_basis=('additional member at an existing set; 1954 newer-frame family S06-11, individual date unresolved' if not primary else None),
                    pairing_basis=('unmarked companion interpreted from narrow plan edge pairs; individual grouping/history is not independently certified' if not primary else 'primary member / older graphic where shown'),
                    keelson_joint=('underpass' if number in (19,20) and primary else
                                   'mortised' if primary and number>1 else 'butt'),
                    molded_ft=(3 if primary else 3.5)/12,
                    molded_basis='S07-08 3-in average at keelson; S06-11 newer frames generally 0.5 in larger',
                    position_uncertainty_ft=.5 if number==1 else .20))
                y=246 if side>0 else 289
                color='#9b541f' if kind=='o' else '#0876d0' if primary else '#d74632'
                draw.line((centre,y-20,centre,y+20),fill=color,width=2)
                if primary:draw.text((centre-8,y-36 if side>0 else y+22),str(number),fill=color,font_size=13)
    # Known survey gaps remain identifiable inference, never numbered as
    # observed sets 21+. Two aft sets are reported but their exact planes are
    # obscured; the inaccessible cabin continuation is reconstructed separately.
    for name,f in [('AFT-A',3.25),('AFT-B',5.15),('CAB-1',7.10),('CAB-2',8.85),
                   ('CAB-3',10.60),('CAB-4',12.50),('CAB-5',14.20)]:
        for side in (1,-1):
            members.append(dict(id=f'{name}-{("P" if side>0 else "S")}',set=name,side=side,
                forward_ft=f,sided_ft=3.5/12,source_view='S05-V02',
                dimension_basis='construction-inferred in inaccessible/obscured bay',
                role='primary',older_graphic=False,age='unresolved',repair_basis=None,
                keelson_joint='mortised' if name.startswith('CAB') else 'none',molded_ft=3/12,
                molded_basis='S07-08; individual inaccessible stock unresolved',position_uncertainty_ft=.75))
    ledger=dict(source_hashes={s['id']:s['sha256'] for s in manifest['sources'] if s['id'] in ('S04','S05','S06','S07')},
        numbering=dict(interpretation='bow-to-aft numbered exposed sets 1–20',
            printed_note='First set fitted against stern knee.',
            conflict='Printed stern-knee clause conflicts with from-bow exposure, sections 4/5/13 and the scarf between 15–20; retained verbatim.',
            checks=['F4/F5 bracket mast area shown in S06','F13 lies forward of the winder shown looking aft in S07',
                    'located scarf lies between F15 and F20'],
            frame1='stem-knee abutment is a reconstruction, not an independently readable frame plane'),
        bowsprit_heel_ft=bowsprit_heel,
        bowsprit_heel_above_post_deck_ft=heel_above_post,
        bowsprit_heel_source=dict(view='S04-V02',preview_x=heel_px,native_x=heel_native,
                                  profile_grid_axis=[1102,292],profile_grid_post_deck=[996,318.5],
                                  profile_forward_ft=a4*1102+b4,plan_profile_delta_ft=bowsprit_heel-(a4*1102+b4),
                                  basis='visible rounded spar heel at stem head; profile height anchored to post deck. Native ruler retained; inherited aft extension crossed Samson post'),
        members=members,source_limited_regions=['cabin inaccessible','two aft exposed sets not individually located',
                                              'forward starboard lining obscures some edge pairs',
                                              'some multi-member pairing assignments lack independent exposure'],
        inferred_joinery=dict(primary_chine_taper_inches=2,limber_width_inches=2,limber_height_inches=1.25,
                             tenon_inches=1.5,chine_joint_seating_allowance_ft=.008,
                             chine_joint_note='Separate bottom/knee and side futtock with contacting lands; exact historic laps unresolved'),
        supports=dict(stanchion_plan_preview_x=[686,759,815],stanchion_section_inches=5.5,
                      strongback_forward_ft=forward(251),strongback_top_inches=5,strongback_center_depth_inches=15,
                      clamp_oak_reinforcement_aft_ft=forward(971),
                      basis='S05-06/23/24; strongback and reinforcement limits scale/construction-inferred'))
    (PACKAGE/'m3_frame_schedule.json').write_text(json.dumps(ledger,indent=2)+'\n')
    image.save(ROOT/'renders/m3-frame-numbering-source.png')
    print('Reviewed ledger:',len(members),'half-frame members;',
          len([r for r in members if r['role']=='repair-pattern']),'separate repair-pattern additions')
    print('Source bowsprit heel F:',bowsprit_heel)
    for number in (4,5,13,15,20):
        row=next(r for r in members if r['set']==number and r['side']==1 and r['role']=='primary')
        print('Set',number,'F',row['forward_ft'])


def main():
    manifest=json.loads((PACKAGE/'manifest.json').read_text())
    view=next(v for v in manifest['views'] if v['id']=='S05-V02')
    make_ledger(manifest,view)
    if '--candidates' not in sys.argv:return
    with Image.open(PACKAGE/view['native_image']) as image:
        image=image.convert('L')
        sx,sy=[n/p for n,p in zip(view['native_size'],view['preview_size'])]
        for row,limits in ((230,(575,1680)),(235,(575,1680)),(300,(575,1680))):
            pixels=np.array(image.crop((0,round((row-5)*sy),image.width,round((row+5)*sy))))<128
            hits=np.mean(pixels,axis=0)>.94
            indices=np.flatnonzero(hits)
            groups=np.split(indices,np.flatnonzero(np.diff(indices)>1)+1)
            picks=[round(float(g.mean()/sx),2) for g in groups if len(g) and limits[0]<g.mean()/sx<limits[1]]
            print('Plan preview frame-edge candidates, row',row,':',picks)
            if row==235:
                for a,b in zip(picks[:-1],picks[1:]):
                    if 4<b-a<18:
                        box=(round((a+1.7)*sx),round(231*sy),round((b-1.7)*sx),round(242*sy))
                        ink=float(np.mean(np.array(image.crop(box))<128))
                        print('  span',a,b,'interior ink',round(ink,3))


if __name__=='__main__':main()
