"""Actual M2 assembly inspection and calibrated source-profile comparison."""
import json
import sys
from pathlib import Path
import numpy as np
import cadquery as cq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image,ImageDraw,ImageOps

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from parts import hull,centreline,centreline_layout as layout
from parts.params import *
from render_m1 import render


def lines(shape):
    for edge in shape.Edges():
        points=[edge.positionAt(float(t)) for t in np.linspace(0,1,24 if edge.geomType()!='LINE' else 2)]
        yield np.array([(25-p.y,p.z) for p in points])


def source_comparison():
    data=CENTRELINE_SOURCE
    manifest=json.loads((ROOT/'drawing_package/manifest.json').read_text())
    registration=json.loads((ROOT/'drawing_package/registration.json').read_text())
    calibration=json.loads((ROOT/'drawing_package/calibration.json').read_text())
    source=next(s for s in manifest['sources'] if s['id']=='S04')
    image=Image.open(ROOT/'renders/m2-board-profile-source.png').convert('RGB')
    crop=(6231,2809,9698,4565)
    sx,sy=image.width/(crop[2]-crop[0]),image.height/(crop[3]-crop[1])
    a,b=registration['transformations']['S04']['grid_x_to_F']
    ppf=calibration['calibrated_sheets']['S04']['native_pixels_per_ft']
    pin=data['board_source_native_pivot']
    def xy(points):
        native_x=(points[:,0]-b)/a*source['native_size'][0]/1440
        native_y=pin[1]-(points[:,1]-CENTREBOARD_PIVOT_Z_FT)*ppf
        return (native_x-crop[0])*sx,(native_y-crop[1])*sy
    plane=cq.Face.makeFromWires(cq.Workplane('YZ').rect(80,40).val())
    fig,ax=plt.subplots(figsize=(16,8.5),dpi=150)
    ax.imshow(image)
    objects=[('Actual board, source lowered pose',layout.make_board(0),'#0876d0'),
             ('Actual trunk wall (port)',centreline.trunk_course(1,0),'#d47b13')]
    for index in range(1,TRUNK_COURSES):
        objects.append((None,centreline.trunk_course(1,index),'#d47b13'))
    # Board centre-plane section includes its real pivot bore. Trunk stock is
    # projected in profile to expose the separately modeled pine courses.
    for label,shape,color in objects:
        if label and label.startswith('Actual board'):shape=shape.intersect(plane)
        for i,points in enumerate(lines(shape)):
            x,y=xy(points)
            ax.plot(x,y,color=color,lw=1,label=label if i==0 else None)
    ax.set_xlim(0,image.width)
    ax.set_ylim(image.height,0)
    ax.axis('off')
    ax.legend(loc='upper left',fontsize=8)
    ax.set_title('M2 actual solids over calibrated S04 inboard profile',fontsize=13)
    fig.text(.5,.025,'Horizontal source registration retained. Vertical anchor: same-column keel/shoe witness at board pivot.\n'
             'Corrected/as-surveyed hull datum and ±0.15-ft outline picks remain explicit; raised stop is reconstructed.',
             ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.065,1,1))
    fig.savefig(ROOT/'renders/m2-source-profile-comparison.png',facecolor='white')
    plt.close(fig)
    # Independent dense evaluation of the optimized keelson base profile.
    positions=layout.keelson_positions(KEELSON_AFT_FT,KEELSON_FORE_FT,hull.rabbet_height)
    fs=np.linspace(KEELSON_AFT_FT,KEELSON_FORE_FT,4001)
    actual=np.interp(fs,positions,[hull.rabbet_height(f) for f in positions])
    error=float(max(abs(actual-np.array([hull.rabbet_height(f) for f in fs]))))
    assert error<KEELSON_PROFILE_TOLERANCE_FT*1.05
    record=dict(source_views=data['source_views'],keelson_base_max_linearization_error_inches=error*12,
                keelson_loft_sections=len(positions),source_pick_uncertainty_ft=data['board_pick_uncertainty_ft'],
                vertical_basis=data['board_vertical_basis'],board_pose_note=data['board_pose_note'],
                source_overlay='renders/m2-source-profile-comparison.png')
    (ROOT/'checks/m2_source_comparison.json').write_text(json.dumps(record,indent=2)+'\n')
    print('M2 optimized keelson base error:',error*12,'in;',len(positions),'sections',flush=True)


def main():
    render('m2-open-interior.png',mast_clip=106)
    render('m2-longitudinal-cutaway.png',True,mast_clip=106)
    render('m2-mast-supports.png',camera=((140,-60,190),(0,-151,64),65),mast_clip=106)
    source_comparison()
    canvas=Image.new('RGB',(1800,1810),'white')
    draw=ImageDraw.Draw(canvas)
    draw.text((25,18),'KATHRYN M2 - CENTRELINE STRUCTURE',fill='black',font_size=30)
    draw.text((25,65),'Inspection: deck/roofs and near-side planking hidden as applicable. Complete STEP remains assembled.',fill='black',font_size=19)
    for y,file,title,limit in ((105,'m2-open-interior.png','Two-section oak keelson, hollow pine trunk and mast foundations',(1750,1050)),
                                (1195,'m2-longitudinal-cutaway.png','Longitudinal cutaway: open board passage and raised-board pose',(1750,520))):
        image=ImageOps.contain(Image.open(ROOT/'renders'/file).convert('RGB'),limit)
        draw.text((25,y),title,fill='black',font_size=22)
        canvas.paste(image,((1800-image.width)//2,y+35))
    canvas.save(ROOT/'renders/m2-review.png')


if __name__=='__main__':main()
