"""Independent classified S04 observations for the stern remedy.

Cap-rail fastener centres are native-image ring picks (>0.90 ring score in
extract_stern_controls.py). Wood-edge controls are reviewed adjacent contour
strokes, separate from the two straight projected lines and item18 traveller.
"""
import json
import math
import sys
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
PACKAGE=ROOT/'references/drawing_package'


def main():
    m=json.loads((PACKAGE/'manifest.json').read_text())
    reg=json.loads((PACKAGE/'registration.json').read_text())
    cal=json.loads((PACKAGE/'calibration.json').read_text())
    s=next(s for s in m['sources'] if s['id']=='S04')
    v=next(v for v in m['views'] if v['id']=='S04-V02')
    crop=next(r for r in json.loads((PACKAGE/'stern_review_crops.json').read_text()) if r['view']=='S04-V02')
    a,b=reg['transformations']['S04']['grid_x_to_F'];ppf=cal['calibrated_sheets']['S04']['native_pixels_per_ft']
    # Two independent symmetric observations agree: helm-case mid-breadth and
    # midpoint of outermost rear-cap fasteners. This refines the local image
    # centre by about1.4 in, within M0's pick allowance, without moving boat X0.
    centre_crop_y=841.5
    def F(x):return a*(v['native_box'][0]+crop['view_native_box'][0]+x)/s['native_size'][0]*1440+b
    def X(y):return (centre_crop_y-y)/ppf
    circles=[(556,103),(425,303),(395,493),(377,732),(379,925),(394,1159),(440,1406),(487,1491),(568,1580)]
    edge_x=[478,354.5,314,300.5,299.5,306,355.5,401.5,497]
    rail=[dict(native_crop_point=list(p),across_ft=X(p[1]),forward_ft=F(p[0])) for p in circles]
    wood=[dict(native_crop_point=[x,p[1]],across_ft=X(p[1]),forward_ft=F(x)) for p,x in zip(circles,edge_x)]
    # Continue the same wood contour through the shoulder; covered portions
    # are faired between these controls, not copied from davit projections.
    for x,y in [(672.5,0),(612,34),(547,69)]:wood.append(dict(native_crop_point=[x,y],across_ft=X(y),forward_ft=F(x)))
    def fit_controls(points,centre,extras):
        buckets={0:[centre]}
        for p in points:buckets.setdefault(round(abs(p['across_ft']),3),[]).append(p['forward_ft'])
        initial=[[x,float(np.mean(values))] for x,values in sorted(buckets.items())]
        result=[]
        for point in initial:
            if result and point[0]-result[-1][0]<.25 and point[0]>0:
                result[-1]=[(result[-1][0]+point[0])/2,(result[-1][1]+point[1])/2]
            else:result.append(point)
        result.extend(extras)
        result=sorted(result)
        # Sub-pick asymmetry/line weight is retained in observations; this
        # fitted visible envelope is symmetrized within the0.20-ft allowance.
        values=np.maximum.accumulate([p[1] for p in result])
        return [[p[0],float(y)] for p,y in zip(result,values)]
    wood_fit=fit_controls(wood,F(298.5),[[6.15,6.2],[6.8,10.0],[7.4,12.0],[25,12.0]])
    rail_fit=fit_controls(rail,F(377.8),[])
    # Correct the first review's deck anchor:374–381 is the upper deck stroke;
    #401–409 is the lower stroke. Rake is a separate source observation.
    profile=next(r for r in json.loads((PACKAGE/'stern_review_crops.json').read_text()) if r['view']=='S04-V01')
    pv=next(v for v in m['views'] if v['id']=='S04-V01')
    def pf(px):return a*(pv['native_box'][0]+profile['view_native_box'][0]+px)/s['native_size'][0]*1440+b
    top_y=377.5
    upper_stock_x=736-(408-top_y)*math.tan(math.radians(25))
    stock_deck_f=pf(upper_stock_x)
    from parts import hull
    from parts.params import HULL_AFT_FT,DECK_THICKNESS_FT
    anchor_z=hull.deck_height(stock_deck_f)
    upper=(pf(223),anchor_z+(top_y-397)/ppf)
    lower=(pf(1015),anchor_z+(top_y-828)/ppf)
    rake=(lower[0]-upper[0])/(upper[1]-lower[1])
    ref_z=hull.deck_height(HULL_AFT_FT)-DECK_THICKNESS_FT
    intercept=upper[0]-rake*(ref_z-upper[1])
    data=dict(source_views=['S04-V01','S04-V02','S05-V01','S05-V02'],source_sha256=s['sha256'],
        condition='Surveyed HAER arrangement/repair condition, locally registered to the retained S02 source coordinate frame; corrected offsets are not overwritten.',
        local_image_centre=dict(view='S04-V02',native_crop_y=centre_crop_y,
            source_native_y=v['native_box'][1]+crop['view_native_box'][1]+centre_crop_y,
            basis='Case mid-breadth and outer fastener midpoint agree; local image centre refinement, not a model translation.'),
        rail_fastener_observations=rail,outer_wood_observations=wood,
        fitted_outer_wood_controls=wood_fit,fitted_rail_controls=rail_fit,
        counter=dict(rake_forward_per_vertical_ft=rake,anchor_forward_ft=intercept,anchor_height_ft=ref_z,
            guide_controls=[dict(F_ft=f,Z_ft=z) for f,z in (upper,lower)],
            upper_deck_anchor_crop_point=[upper_stock_x,top_y],upper_deck_anchor_F_ft=stock_deck_f,
            upper_deck_anchor_Z_ft=anchor_z,basis='Actual upper-deck stroke, not the lower deck/clamp line used in the preliminary review.'),
        rudder_head_forward_ft=stock_deck_f-.5*math.tan(math.radians(25)),
        source_stock=dict(rail_inches=[3.5,1.75],moulding_inches=[8,6],transom_frame_sided_inches=3.75,
            transom_brace_inches=[6.75,2],stern_deck_timber_inches=[4,3.5],stern_d_inches=[6,3]),
        pick_uncertainty_ft=.20,fit_notes='Median corresponding side controls; original side picks preserved. Fore shoulder handoff and hidden joins are construction inferences.',
        traveller=dict(forward_ft=.35,span_ft=2.2,height_above_deck_ft=.32,basis='S04 item18 short rod immediately aft of helm; section/feet inferred.'),
        rail_heights=dict(top_ft=(377.5-77)/ppf,lower_ft=(377.5-187)/ppf,
                         basis='S04 profile upper deck line and separate upper/lower rail strokes'),
        geometry_state='accepted input for source-comparison implementation; final acceptance requires actual CAD comparisons')
    (PACKAGE/'stern_remedy_targets.json').write_text(json.dumps(data,indent=2)+'\n')
    # Complete the separately reviewed side controls and fair handoff, rather
    # than silently restoring the superseded inferred shoulder on regeneration.
    from measure_stern_side_controls import main as measure_sides
    measure_sides()
    image=Image.open(ROOT/'renders/stern-deck-source.png').convert('RGB');draw=ImageDraw.Draw(image)
    for p,x in zip(circles,edge_x):
        draw.ellipse((p[0]-16,p[1]-16,p[0]+16,p[1]+16),outline='#0876d0',width=3)
        draw.ellipse((x-7,p[1]-7,x+7,p[1]+7),outline='#d22b26',width=3)
    image.save(ROOT/'renders/stern-remedy-source-controls.png')
    print('Counter:',data['counter'],'head F',data['rudder_head_forward_ft'])
    print('Wood controls:',wood_fit,'rail controls:',rail_fit)


if __name__=='__main__':main()
