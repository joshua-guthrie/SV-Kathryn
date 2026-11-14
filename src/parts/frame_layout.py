"""M3 checked member schedule and shared joint tools, without CAD import cycles."""
from functools import lru_cache
import json
import math
from pathlib import Path
from .params import *
from .centreline_layout import keelson_width
from .primitives import block

SOURCE=FRAME_SOURCE
MEMBERS=SOURCE['members']


def stem_knee_top(f,deck,rabbet):
    return min(deck(f)-.70,rabbet(f)+STEM_KNEE_RISE_FT)


def samson_heel(deck,rabbet):
    return stem_knee_top(BOW_POST_FORWARD_FT,deck,rabbet)-.22


def source_plan_forward(px):
    # The transformation is retained in the measurement ledger through native
    # picks; this convenience uses the same S05 view's linear registration.
    row=next(r for r in MEMBERS if r['id']=='F13-P-1')
    left,right=row['preview_edges']
    slope=row['sided_ft']/(right-left)
    return row['forward_ft']+(px-(left+right)/2)*slope


def underpass_rows():
    return [r for r in MEMBERS if r['side']==1 and r['keelson_joint']=='underpass']


@lru_cache(maxsize=2)
def underpass_tools(bottom):
    result=[]
    for row in underpass_rows():
        f=row['forward_ft']
        top=max(bottom(f+d,0) for d in (-row['sided_ft']/2,row['sided_ft']/2))+OLD_FRAME_MOLDED_FT+.025
        result.append(block(0,f,-5,keelson_width(f)+.08,row['sided_ft']+.035,top+5))
    return tuple(result)


@lru_cache(maxsize=2)
def mortise_tools(bottom):
    result=[]
    for row in MEMBERS:
        if row['keelson_joint']!='mortised':continue
        f,side=row['forward_ft'],row['side']
        half=keelson_width(f)/2
        low=min(bottom(f+d,side*(half-FRAME_TENON_FT)) for d in (-row['sided_ft']/2,row['sided_ft']/2))-.06
        high=max(bottom(f+d,side*half) for d in (-row['sided_ft']/2,row['sided_ft']/2))+OLD_FRAME_MOLDED_FT*1.2+.035
        result.append(block(side*(half-FRAME_TENON_FT/2),f,low,
                            FRAME_TENON_FT+.06,row['sided_ft']+.012,high-low))
    return tuple(result)
