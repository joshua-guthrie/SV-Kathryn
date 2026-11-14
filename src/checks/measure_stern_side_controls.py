"""Extend the independent stern observations through the visible S04 shoulder."""
import json
import sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))

def main():
    package=ROOT/'references/drawing_package'
    data=json.loads((package/'stern_remedy_targets.json').read_text())
    manifest=json.loads((package/'manifest.json').read_text())
    view=next(v for v in manifest['views'] if v['id']=='S04-V02')
    source=next(s for s in manifest['sources'] if s['id']=='S04')
    a,b=json.loads((package/'registration.json').read_text())['transformations']['S04']['grid_x_to_F']
    ppf=json.loads((package/'calibration.json').read_text())['calibrated_sheets']['S04']['native_pixels_per_ft']
    sx,sy=[n/p for n,p in zip(view['native_size'],view['preview_size'])]
    def observation(point):
        px=105+point[0]*425/2000
        py=30+point[1]*130/612
        native=[view['native_box'][0]+px*sx,view['native_box'][1]+py*sy]
        return dict(derived_crop_point=list(point),source_native_point=native,
                    across_ft=(data['local_image_centre']['source_native_y']-native[1])/ppf,
                    forward_ft=a*native[0]/source['native_size'][0]*1440+b)
    # Reviewed ring centres and the separately visible curved outside wood
    # stroke, not the straight diagonal davit projection crossing that stroke.
    rail=[observation(p) for p in [(363,311),(549,259),(727,226),(912,192),
                                  (1104,163),(1303,138),(1503,114),(1698,93),(1885,73)]]
    wood=[observation(p) for p in [(700,181),(900,137),(1100,105),(1300,78),
                                  (1500,50),(1700,26),(1900,4)]]
    data['side_rail_observations']=rail
    data['side_wood_observations']=wood
    old=[p for p in data['fitted_outer_wood_controls'] if p[0]<6]
    wood_fit=old+[[p['across_ft'],p['forward_ft']] for p in wood]
    from parts.hull import SECTIONS,topside_halfwidth,deck_thickness
    from parts.params import RAIL_WIDTH_FT,RAIL_THICKNESS_FT
    row=[float(np.interp(18,[s[0] for s in SECTIONS],[s[i] for s in SECTIONS])) for i in range(8)]
    z=min(row[2]-.38,row[2]-deck_thickness(row[2],row[4])-RAIL_THICKNESS_FT/2)
    outside=topside_halfwidth(18,z)+RAIL_WIDTH_FT-.035
    wood_fit.extend([[outside,18],[25,100]])
    data['moulding_handoff']=dict(forward_ft=18,outer_halfwidth_ft=outside,
        basis='Inferred fair runout into retained side rubbing stock; outside radius comes from the actual section at F18, not an arbitrary aft-quarter squeeze.')
    data['fitted_outer_wood_controls']=wood_fit
    data['fitted_rail_controls']=[p for p in data['fitted_rail_controls'] if p[0]<5]+[
        [p['across_ft'],p['forward_ft']] for p in rail]
    data['fit_notes']='Paired aft controls averaged within source allowance. Original asymmetric picks retained. Port shoulder controls measured independently; mirrored to starboard. Final forward handoff and hidden joints inferred.'
    data['side_control_crop']=dict(file='renders/stern-side-plan-controls.png',
        view='S04-V02',preview_box=[105,30,530,160],display_size=[2000,612],
        pick_uncertainty_ft=.20)
    image=Image.open(ROOT/'renders/stern-side-plan-controls.png').convert('RGB')
    draw=ImageDraw.Draw(image)
    for points,color in ((rail,'#0078ce'),(wood,'#dc2525')):
        for p in points:
            x,y=p['derived_crop_point'];draw.ellipse((x-12,y-12,x+12,y+12),outline=color,width=3)
    image.save(ROOT/'renders/stern-side-plan-picked.png')
    (package/'stern_remedy_targets.json').write_text(json.dumps(data,indent=2)+'\n')
    print('Side rail X/F:',[(round(p['across_ft'],3),round(p['forward_ft'],3)) for p in rail])
    print('Side wood X/F:',[(round(p['across_ft'],3),round(p['forward_ft'],3)) for p in wood])

if __name__=='__main__':main()
