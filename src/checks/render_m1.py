"""M1 actual-mesh inspection and calibrated source/actual-solid section overlays."""
import json
import sys
from pathlib import Path
import numpy as np
import vtk
from PIL import Image,ImageDraw,ImageOps
from scipy.optimize import minimize
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from parts import hull
from parts.params import CABIN_AFT_FT,CABIN_FORE_FT,LINE_STATIONS_FT


def render(filename,cutaway=False,camera=None,mast_clip=78,hide_groups=(),show_names=()):
    parts=json.loads((ROOT/'.soma/model.map.json').read_text())['parts']
    from parts.deck import make_bow_post
    post=next(p for p in parts if p['name']=='Samson post')
    source_height=make_bow_post().BoundingBox().zlen
    view_scale=(post['bbox'][1][2]-post['bbox'][0][2])/source_height/(304.8/32)
    imp=vtk.vtkGLTFImporter()
    imp.SetFileName(str(ROOT/'.soma/model.glb'))
    imp.Update()
    ren=imp.GetRenderer()
    ren.SetBackground(.92,.94,.97)
    actors=ren.GetActors()
    actors.InitTraversal()
    collection=[actors.GetNextActor() for _ in range(actors.GetNumberOfItems())]
    assert len(collection)==2*len(parts)
    side=vtk.vtkPlane()
    side.SetOrigin(0,0,0)
    side.SetNormal(1,0,0)
    mast=vtk.vtkPlane()
    mast.SetOrigin(0,0,mast_clip*view_scale)
    mast.SetNormal(0,0,-1)
    for i,part in enumerate(reversed(parts)):
        name,group=part['name'],part['group']
        pair=collection[2*i:2*i+2]
        assert abs(pair[0].GetBounds()[2]-part['bbox'][0][1])<.1,name
        for actor in pair:
            actor.GetProperty().SetAmbient(.45)
            actor.GetProperty().SetDiffuse(.55)
            hide=(group.startswith('Deck/Planking') or group=='Deck/Cabin/Roofs'
                  or group.startswith('Deck/Equipment') or group.startswith('Deck/Rails')
                  or group.startswith('Deck/Foredeck') or group.startswith('Spars')
                  or 'hatch cover' in name
                  or name in ('Steering pedestal','Helm wheel','Wheel shaft','Rudder upper bearing'))
            if name=='Mast':
                hide=False
                actor.GetMapper().AddClippingPlane(mast)
            hide=hide or any(group.startswith(prefix) for prefix in hide_groups)
            if name in show_names:hide=False
            actor.SetVisibility(not hide)
            if cutaway:
                actor.GetMapper().AddClippingPlane(side)
            if group=='Interior/Enclosure and bearings':
                if 'bulkhead' in name:
                    actor.GetProperty().SetColor(.80,.76,.61)
                else:
                    actor.GetProperty().SetColor(.70,.40,.16)
    win=vtk.vtkEGLRenderWindow()
    win.SetOffScreenRendering(True)
    win.SetSize(*( (2000,850) if cutaway else (1800,1200) ))
    win.AddRenderer(ren)
    kit=vtk.vtkLightKit()
    kit.SetKeyLightIntensity(1)
    kit.AddLightsToRenderer(ren)
    cam=ren.GetActiveCamera()
    cam.ParallelProjectionOn()
    cam.SetViewUp(0,0,1)
    if cutaway:
        cam.SetPosition(-700,0,70)
        cam.SetFocalPoint(0,0,43)
        cam.SetParallelScale(115)
    else:
        cam.SetPosition(420,520,480)
        cam.SetFocalPoint(0,0,38)
        cam.SetParallelScale(206)
    if camera:
        position,focus,scale=camera
        cam.SetPosition(*position)
        cam.SetFocalPoint(*focus)
        cam.SetParallelScale(scale)
    cam.SetPosition(*(v*view_scale for v in cam.GetPosition()))
    cam.SetFocalPoint(*(v*view_scale for v in cam.GetFocalPoint()))
    cam.SetParallelScale(cam.GetParallelScale()*view_scale)
    direction=np.array(cam.GetDirectionOfProjection())
    if abs(direction[2])>.99:cam.SetViewUp(0,1,0)
    ren.ResetCameraClippingRange()
    win.Render()
    capture=vtk.vtkWindowToImageFilter()
    capture.SetInput(win)
    capture.Update()
    writer=vtk.vtkPNGWriter()
    writer.SetFileName(str(ROOT/'renders'/filename))
    writer.SetInputConnection(capture.GetOutputPort())
    writer.Write()
    win.Finalize()
    print(filename,flush=True)


def edge_segments(shape):
    segments=[]
    for edge in shape.Edges():
        samples=[edge.positionAt(float(t)) for t in np.linspace(0,1,20 if edge.geomType()!='LINE' else 2)]
        p=np.array([(v.x,v.z) for v in samples])
        segments.extend(zip(p[:-1],p[1:]))
    return np.array(segments)


def point_distances(points,segments):
    a,b=segments[:,0],segments[:,1]
    direction=b-a
    norm=np.maximum(np.sum(direction*direction,axis=1),1e-12)
    delta=points[:,None,:]-a[None,:,:]
    t=np.clip(np.sum(delta*direction[None,:,:],axis=2)/norm[None,:],0,1)
    closest=a[None,:,:]+t[:,:,None]*direction[None,:,:]
    return np.sqrt(np.min(np.sum((points[:,None,:]-closest)**2,axis=2),axis=1))


def section_overlay(view_id,limits):
    package=ROOT/'references/drawing_package'
    manifest=json.loads((package/'manifest.json').read_text())
    view=next(v for v in manifest['views'] if v['id']==view_id)
    trace=json.loads((package/'traces'/f'{view_id}.json').read_text())
    source=np.array([p for path in trace['paths'] if 'outer_planking' in path['id']
                     for p in path['local_XZ_feet']])
    data=np.array(hull.SECTIONS)
    def wire(f):
        row=tuple(float(np.interp(f,data[:,0],data[:,i])) for i in range(8))
        return hull.hull_wire(row)
    def loss(v):
        f,z=v
        points=source+np.array([0,z])
        d=point_distances(points,edge_segments(wire(f)))
        return float(np.mean(d*d))
    starts=[(f,hull.keel_bottom(f)) for f in np.linspace(*limits,5)]
    fits=[minimize(loss,start,bounds=[limits,(-2,5)],method='Powell',
                   options={'xtol':.002,'ftol':1e-8}) for start in starts]
    best=min(fits,key=lambda fit:fit.fun)
    f,z=map(float,best.x)
    rms=float(np.sqrt(best.fun))
    assert rms*12<1.5,('M1 shell/source guide mismatch',view_id,rms*12)
    upper,lower=hull.make_hull()
    plane=hull.cq.Face.makeFromWires(hull.section_plane(f).rect(30,25).val())
    sections=[s.intersect(plane) for s in (upper,lower)]
    image=Image.open(package/view['preview']).convert('RGB')
    sx=view['native_size'][0]/image.width
    sy=view['native_size'][1]/image.height
    ppf=trace['native_pixels_per_ft']
    fig,ax=plt.subplots(figsize=(12,10),dpi=160)
    ax.imshow(image)
    for shape in sections:
        for a,b in edge_segments(shape):
            xy=np.array([a,b])
            px=trace['origin_preview_pixels'][0]-xy[:,0]*ppf/sx
            py=trace['origin_preview_pixels'][1]-(xy[:,1]-z)*ppf/sy
            ax.plot(px,py,color='#0876d0',lw=1.25)
    ax.set_xlim(0,image.width)
    ax.set_ylim(image.height,0)
    ax.axis('off')
    ax.set_title(f'{view_id}: actual M1 planking section in blue\n'
                 f'Shape-registered representative plane F={f:.2f} ft; shell-guide RMS={rms*12:.2f} in',fontsize=11)
    fig.text(.5,.015,'Calibrated scale retained. Section-plane identity is inferred here; exact frame-number registration is M3 work.\n'
             'Source shows additional framing/fit-out; M1 blue overlay represents the hollow planking enclosure only.',
             ha='center',fontsize=8)
    fig.tight_layout(rect=(0,.055,1,1))
    filename=f'm1-section-{view_id}.png'
    fig.savefig(ROOT/'renders'/filename,facecolor='white')
    plt.close(fig)
    print(filename,'RMS',rms*12,'in',flush=True)
    return dict(source_view=view_id,representative_F_ft=f,
                plane_basis='calibrated outline shape registration; NOT confirmed hull-frame station',
                local_datum_global_Z_ft=z,keel_shoe_global_Z_ft=hull.keel_bottom(f),
                local_datum_difference_ft=z-hull.keel_bottom(f),
                outline_RMS_inches=rms*12,scope='actual planking cross-section; detailed source frames/fit-out pending M2–M5')


def main():
    render('m1-open-interior.png')
    render('m1-longitudinal-cutaway.png',True)
    result=[section_overlay('S06-V01',(LINE_STATIONS_FT[7],LINE_STATIONS_FT[9])),
            section_overlay('S07-V02',(CABIN_AFT_FT+.3,CABIN_FORE_FT-.3))]
    (ROOT/'src/checks/m1_section_comparison.json').write_text(json.dumps(result,indent=2)+'\n')
    canvas=Image.new('RGB',(1800,1780),'white')
    draw=ImageDraw.Draw(canvas)
    draw.text((24,18),'KATHRYN M1 - CONTINUOUS OPEN INTERIOR',fill='black',font_size=30)
    draw.text((24,65),'Inspection: deck, roofs, hatch covers and equipment hidden; near side removed in cutaway.',fill='black',font_size=20)
    for y,file,caption,limit in (
        (105,'m1-open-interior.png','Continuous hollow shell, cabin/hold/forepeak spaces and real supports',(1760,1050)),
        (1195,'m1-longitudinal-cutaway.png','Longitudinal inspection cutaway - thin planking and partitions',(1760,520))):
        image=ImageOps.contain(Image.open(ROOT/'renders'/file).convert('RGB'),limit)
        draw.text((24,y),caption,fill='black',font_size=21)
        canvas.paste(image,((1800-image.width)//2,y+35))
    canvas.save(ROOT/'renders/m1-review.png')
    print('m1-review.png',flush=True)


if __name__=='__main__':
    main()
