"""One declared S01 surface transfer and independent S04 physical references."""
import json
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator

TARGET_PATH=Path(__file__).resolve().parents[2]/'references/drawing_package/trailboard_targets.json'
TARGET=json.loads(TARGET_PATH.read_text())
ENVELOPE_PATH=Path(__file__).resolve().parents[2]/'references/drawing_package/longhead_envelope.json'
ENVELOPE=json.loads(ENVELOPE_PATH.read_text())
MAPPING=TARGET['surface_mapping']
PHYSICAL=TARGET['physical_transforms']
FEATURES={f['id']:f for f in TARGET['features']}
GUIDE=np.asarray(MAPPING['source_body_guides_flat'])
SCALE=(MAPPING['physical_tip_f']-MAPPING['physical_root_f'])/(MAPPING['source_tip_x']-MAPPING['source_root_x'])
_upper=PchipInterpolator(*np.asarray(PHYSICAL['upper_fz']).T)
_lower=PchipInterpolator(*np.asarray(PHYSICAL['lower_fz']).T)
_outer_upper=PchipInterpolator(*np.asarray(ENVELOPE['picks']['outer_upper_fz']).T)
_outer_lower=PchipInterpolator(*np.asarray(ENVELOPE['picks']['outer_lower_fz']).T)
ENVELOPE_ROOT_F=ENVELOPE['picks']['aft_root_f_ft']
ENVELOPE_TIP_F=ENVELOPE['picks']['forward_head_f_ft']
_a,_b=PHYSICAL['registration']['F_from_S04_grid_x']
_unit=PHYSICAL['registration']['profile_grid_height_ft_per_unit']
_deck=PHYSICAL['deck_anchor_z_ft']
_gx,_gy=MAPPING['head_anchor_grid']
_head_z=_deck+(318.5-_gy)*_unit


def panel_top(f):return float(_upper(f))
def panel_bottom(f):return float(_lower(f))
def outer_top(f):return float(_outer_upper(f))
def outer_bottom(f):return float(_outer_lower(f))


def source_guides(x):
    return np.interp(x,GUIDE[:,0],GUIDE[:,1]),np.interp(x,GUIDE[:,0],GUIDE[:,2])


def native_to_fz(points,reflect_name=False):
    p=np.asarray(points,float);x=p[:,0].copy();v=p[:,1]-MAPPING['flat_vertical_offset_px']+MAPPING['flat_shear']*x
    if reflect_name:
        top,bottom=source_guides(x)
        depth=(v-top)/(bottom-top)
        x=sum(MAPPING['letter_reflection_flat_x'])-x
        top,bottom=source_guides(x)
        v=top+depth*(bottom-top)
    f=MAPPING['physical_root_f']+(x-MAPPING['source_root_x'])*SCALE
    top,bottom=source_guides(x)
    body=_upper(f)-(v-top)/(bottom-top)*(_upper(f)-_lower(f))
    raw_y=v+MAPPING['flat_vertical_offset_px']-MAPPING['flat_shear']*x
    head=_head_z+(MAPPING['head_anchor_native'][1]-raw_y)*SCALE
    start,end=MAPPING['head_blend_flat_x']
    t=np.clip((x-start)/(end-start),0,1);weight=t*t*(3-2*t)
    z=(1-weight)*body+weight*head
    return np.column_stack((f,z))


def fz_to_native(points):
    """Inverse of the common transfer, used on actual exported edge samples."""
    p=np.asarray(points,float);f,z=p[:,0],p[:,1]
    x=MAPPING['source_root_x']+(f-MAPPING['physical_root_f'])/SCALE
    y0=MAPPING['flat_vertical_offset_px']-MAPPING['flat_shear']*x
    z0=native_to_fz(np.column_stack((x,y0)))[:,1]
    z1=native_to_fz(np.column_stack((x,y0+1)))[:,1]
    return np.column_stack((x,y0+(z-z0)/(z1-z0)))


def source_headrail_points(side):
    plan=np.asarray(PHYSICAL['headrail_plan_grid'])
    centres=np.asarray(PHYSICAL['headrail_profile_centres_grid'])
    out=[]
    for gx,gy in plan:
        f=_a*gx+_b
        profile_y=float(np.interp(gx,centres[:,0],centres[:,1]))
        z=_deck+(318.5-profile_y)*_unit
        out.append([side*(gy-PHYSICAL['registration']['plan_centreline_grid_y'])*_unit,f,z])
    return out
