"""Bound M4 loft optimization against the existing dense measured geometry."""
import json
import sys
import time
from pathlib import Path
import numpy as np
import cadquery as cq
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from parts import hull,stern_layout
from parts.params import *
from parts.board_tools import segmented_loft,split_material,plane_x


def main():
    start=time.time()
    reference=stern_layout.reference_height(hull.deck_height)
    old_outer=hull.solid_envelope()
    outer=segmented_loft([hull.hull_wire(s) for s in hull.SECTIONS]).intersect(stern_layout.keep(reference))
    print('Outer loft:',len(old_outer.Faces()),'->',len(outer.Faces()),'faces;',time.time()-start,flush=True)
    aft=hull.SECTIONS[0][0]+INTERIOR_SKIN_FT
    fore=hull.SECTIONS[-1][0]-.05
    while True:
        try:hull.shell_inner_profile(fore);break
        except ValueError:fore-=.025
    positions=np.unique(np.concatenate((np.linspace(aft,fore,int((fore-aft)/.5)+2),
        [s[0] for s in hull.SOURCE_SECTIONS if aft<s[0]<fore],
        np.linspace(max(aft,fore-2),fore,20),
        [f for f in (hull._chine_bottom_end,hull._chine_top_end) if aft<f<fore])))
    inner=segmented_loft([hull.shell_inner_profile(float(f)) for f in positions]).intersect(
        stern_layout.keep(reference,INTERIOR_SKIN_FT))
    print('Cavity loft:',len(inner.Faces()),'faces;',time.time()-start,flush=True)
    outer_shell=cq.Shell.makeShell(outer.Faces())
    distances=[]
    for f in np.linspace(LINE_STATIONS_FT[1],HULL_FORE_FT-.08,48):
        row=tuple(float(np.interp(f,[s[0] for s in hull.SECTIONS],[s[i] for s in hull.SECTIONS])) for i in range(8))
        for edge in hull.hull_wire(row).Edges():
            for t in (.25,.75):
                p=edge.positionAt(t)
                distances.append(outer_shell.distance(cq.Vertex.makeVertex(p.x,p.y,p.z)))
    error=max(distances)
    print('Maximum dense source-boundary deviation',error*12,'in; elapsed',time.time()-start,flush=True)
    assert error<.01,('Cubic source deviation exceeds 0.12 in',error*12)
    relative=abs(outer.Volume()-old_outer.Volume())/old_outer.Volume()
    print('Envelope volume comparison',relative,'elapsed',time.time()-start,flush=True)
    assert relative<.001,('Envelope volume drift',relative)
    planking=outer.cut(inner,hull.rudder_stock_passage(),hull.keelson_seating_tool())
    from parts.centreline_layout import centreboard_slot
    planking=planking.cut(centreboard_slot())
    assert planking.isValid() and len(planking.Solids())==1
    print('Planking',len(planking.Faces()),'faces; volume',planking.Volume(),'elapsed',time.time()-start,flush=True)
    (ROOT/'src/checks/m4_loft_prototype.json').write_text(json.dumps(dict(
        source_boundary_max_deviation_inches=error*12,envelope_relative_volume_difference=relative,
        old_outer_faces=len(old_outer.Faces()),new_outer_faces=len(outer.Faces()),new_planking_faces=len(planking.Faces()),
        source_boundary_samples=len(distances)),indent=2)+'\n')


if __name__=='__main__':main()
