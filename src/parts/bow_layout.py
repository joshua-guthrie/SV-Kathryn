"""Shared source-controlled bow stations; full-size feet, independent of CAD."""
import json
from pathlib import Path

SOURCE = json.loads((Path(__file__).resolve().parents[2] /
                     'references/drawing_package/bow_remedy_registration.json').read_text())
SPAR = SOURCE['spar']
HEADWORK = SOURCE['headwork']
LONGHEAD = SOURCE['longhead']
RIG = SOURCE['rig']


def axis_height(forward):
    return SPAR['heel_z'] + (forward-SPAR['heel_f'])*SPAR['slope']


def radius_at(forward):
    t=max(0,min(1,(forward-SPAR['round_start_f'])/(SPAR['end_f']-SPAR['round_start_f'])))
    return SPAR['round_radius_ft'] + t*(SPAR['tip_radius_ft']-SPAR['round_radius_ft'])


def half_depth_at(forward):
    if forward <= SPAR['shoulder_f']:return SPAR['square_depth_ft']/2
    if forward >= SPAR['round_start_f']:return radius_at(forward)
    t=(forward-SPAR['shoulder_f'])/(SPAR['round_start_f']-SPAR['shoulder_f'])
    return SPAR['square_depth_ft']/2*(1-t)+SPAR['round_radius_ft']*t
