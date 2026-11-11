"""Verify model-map and STEP full-size millimetres, independently of UI labels."""
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from parts import deck,hull
from parts.params import *


def check():
    build=json.loads((ROOT/'.soma/build.json').read_text())
    mapping=json.loads((ROOT/'.soma/model.map.json').read_text())
    assert build['status']=='ok' and not build['warnings']
    parts=mapping['parts']
    post=next(p for p in parts if p['name']=='Samson post')
    actual=(post['bbox'][1][2]-post['bbox'][0][2])/deck.make_bow_post().BoundingBox().zlen
    assert abs(actual-MODEL_MM_PER_FOOT)<.001,('Incorrect full-size transform',actual)
    assert MODEL_SCALE==1 and abs(actual-304.8)<.001
    upper=next(p for p in parts if p['name']=='Painted topsides')
    length=upper['bbox'][1][1]-upper['bbox'][0][1]
    # Physical wood bounds are distinct from the recorded reference witnesses.
    expected=hull.make_hull()[0].BoundingBox().ylen*304.8
    assert abs(length-expected)<.1,('Body export length',length,expected)
    body=[p for p in parts if p['name'] in ('Painted topsides','Underwater hull','Cambered deck')
          or p['group']=='Hull/Stern moulding']
    physical_span=max(p['bbox'][1][1] for p in body)-min(p['bbox'][0][1] for p in body)
    with (ROOT/'output/model.step').open() as f:header=f.read(20000)
    assert 'SI_UNIT(.MILLI.,.METRE.)' in header,'STEP lacks explicit millimetre units'
    result=dict(status='passed',scale='1:1',cad_units='mm',millimetres_per_source_foot=actual,
                body_length_mm=physical_span,body_length_ft=physical_span/304.8,
                topsides_component_length_mm=length,
                recorded_50ft_reference_mm=50*304.8,parts=len(parts),
                viewer_units='Installed SOMA measurement display is fixed to millimetres; no feet/inches display switch found.')
    (ROOT/'checks/model_scale_acceptance.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f'PASS: 1:1, {actual:.6f} mm/ft; wood body {physical_span:.2f} mm; 50-ft reference 15,240 mm; {len(parts)} parts; STEP explicitly mm.')


if __name__=='__main__':check()
