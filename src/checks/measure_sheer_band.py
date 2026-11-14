"""M1 source review: Top of Deck is above Underside of Sheer Strake.

Picks are from the two explicitly labelled curves in S02-V01/V02, avoiding
station strokes. Original offset-table readings are not changed.
"""
import json
from pathlib import Path
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'references/drawing_package'


def main():
    manifest=json.loads((OUT/'manifest.json').read_text())
    source=next(s for s in manifest['sources'] if s['id']=='S02')
    scale=json.loads((OUT/'calibration.json').read_text())['calibrated_sheets']['S02']['native_pixels_per_ft']
    reg=json.loads((OUT/'registration.json').read_text())
    stations={r['lines_station']:r['canonical_forward_ft'] for r in reg['line_stations']}
    sx,sy=source['native_size'][0]/1440,source['native_size'][1]/960
    # station, sampled grid x, TopDeck Y, underside Y, half-breadth Top/underside Y
    picks=[(0,252.5,192.36,209.35,None,None),
           (2,385,196.84,215.83,387.56,390.55),
           (3,449.5,196.84,215.88,382.18,385.91),
           (4,515.5,195.15,214.53,378.64,382.87),
           (6,646.5,188.32,208.36,383.02,388.36),
           (8,778.5,179.10,197.54,416.51,420.75),
           (10,908.5,167.59,183.19,480.15,485.78)]
    records=[]
    for station,x,top,under,btop,bunder in picks:
        records.append(dict(lines_station=station,forward_ft=stations[station],
            profile_native_points=dict(top_of_deck=[x*sx,top*sy],underside_sheer_strake=[x*sx,under*sy]),
            band_height_ft=(under-top)*sy/scale,
            half_breadth_native_points=(dict(top_of_deck=[x*sx,btop*sy],underside_sheer_strake=[x*sx,bunder*sy]) if btop is not None else None),
            outward_flare_ft=(bunder-btop)*sy/scale if btop is not None else .16,
            flare_basis='scale-measured' if btop is not None else 'closure reconstruction near transom'))
    data=dict(added_in_milestone='M1',source_views=['S02-V01','S02-V02','S02-T01'],
              source_sha256=source['sha256'],native_pixels_per_ft=scale,
              interpretation='Offset-table Sheer reference is the underside of sheer strake; Top of Deck is a separately labelled higher/wider curve.',
              point_pick_uncertainty_inches=1.5,
              measurements=records,
              closures=[dict(forward_ft=-1.8,band_height_ft=1.1,outward_flare_ft=.08,basis='transom closure reconstruction'),
                        dict(forward_ft=(939-178)/15,band_height_ft=1.0,outward_flare_ft=0,basis='fine planked-stem closure reconstruction')])
    (OUT/'sheer_band_measurements.json').write_text(json.dumps(data,indent=2)+'\n')
    view=next(v for v in manifest['views'] if v['id']=='S02-V01')
    image=Image.open(OUT/view['preview']).convert('RGB')
    draw=ImageDraw.Draw(image)
    px=image.width/view['native_size'][0]
    py=image.height/view['native_size'][1]
    for r in records:
        p=r['profile_native_points']
        coords=[((point[0]-view['native_box'][0])*px,(point[1]-view['native_box'][1])*py) for point in (p['top_of_deck'],p['underside_sheer_strake'])]
        draw.line(coords,fill='#cd2727',width=4)
        for x,y in coords: draw.ellipse((x-4,y-4,x+4,y+4),fill='#cd2727')
        draw.text((coords[0][0]+7,coords[0][1]-24),f"{r['band_height_ft']*12:.1f} in",fill='#b00000',font_size=17,stroke_width=1,stroke_fill='white')
    image.save(ROOT/'renders/m1-sheer-band-source.png')
    print([(r['lines_station'],round(r['band_height_ft']*12,2),round(r['outward_flare_ft']*12,2)) for r in records])


if __name__=='__main__': main()
