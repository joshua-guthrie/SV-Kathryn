"""Actual-solid checks for the deck-to-cabin access path; run from project root."""
import math
import sys
from pathlib import Path

import cadquery as cq
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from parts import deck, hull, framing, interior,centreline,centreline_layout,hull_frames
from geometry_checks import Contains
from parts.access import companionway_access
from parts.params import (
    boat_point, COMPANIONWAY_AFT_FT, ACCESS_CLEAR_WIDTH_FT,
    ACCESS_WELL_AFT_FT, ACCESS_WELL_FORE_FT, ACCESS_WELL_WIDTH_FT,
    ACCESS_TREAD_COUNT,
)
from parts.primitives import block


def overlap(a,b):
    aa,bb=a.BoundingBox(),b.BoundingBox()
    if any(getattr(aa,f'{axis}max') <= getattr(bb,f'{axis}min')+1e-8 or
           getattr(bb,f'{axis}max') <= getattr(aa,f'{axis}min')+1e-8 for axis in 'xyz'):
        return 0.0
    return a.intersect(b).Volume()


def check():
    access = deck.access_geometry()
    cabin = {n: s for n, s, _ in deck.make_deckhouse_parts()}
    upper, lower = hull.make_hull()
    main_deck = hull.make_deck()
    fixed = {n: s for n, s in cabin.items()
             if ' door' not in n and ' hinge ' not in n}
    fixed.update({'Topsides': upper, 'Underwater hull': lower, 'Deck': main_deck})
    fixed.update({n: s for n, s, _ in framing.make_opening_frames()})
    enclosures={n:s for n,s,_ in interior.make_enclosure_parts()}
    fixed.update(enclosures)
    fixed.update({n:s for n,s,_ in centreline.make_centreline_parts()})
    fixed.update({n:s for maker in (hull_frames.make_frame_parts,hull_frames.make_support_parts) for n,s,_ in maker()})
    for name, shape in {**cabin, **fixed}.items():
        assert shape.isValid() and len(shape.Solids()) == 1, name

    # This crosses both walls AND the old main-roof lip, independently of
    # the cutting-tool shapes. The sill is at deck, not upper-house base.
    doorway = block(0, COMPANIONWAY_AFT_FT + .1, access.sill + .04,
                    ACCESS_CLEAR_WIDTH_FT - .1, .85,
                    access.head - access.sill - .08)
    for name, shape in fixed.items():
        assert overlap(doorway,shape) < 1e-7, ('blocked doorway', name)
    assert 0 < (access.sill - access.entry_deck) * 12 < 3
    assert abs(cabin['Port companionway door'].BoundingBox().zmin
               - cabin['Starboard companionway door'].BoundingBox().zmin) < 1e-7
    assert cabin['Port companionway door'].BoundingBox().zmin < access.entry_deck + .25
    print(f'PASS: continuous {ACCESS_CLEAR_WIDTH_FT * 12:.1f}-in doorway; '
          f'{(access.sill - access.entry_deck) * 12:.2f}-in sill, '
          f'{(access.head - access.sill) * 12:.2f}-in clear height.')

    # A stooping-height envelope follows the entry and each descending tread.
    # The actual roof and deck solids must clear it; no invisible closed slab.
    for index in range(1, ACCESS_TREAD_COUNT + 1):
        forward, top = access.tread(index)
        envelope = block(0, forward + .06, top + .025, 1.35, .15, 3.5)
        for name, shape in fixed.items():
            assert overlap(envelope,shape) < 1e-7, ('blocked stair', index, name)
        tread = cabin[f'Companionway tread {index}']
        for side in ('Port', 'Starboard'):
            stringer = cabin[f'{side} companionway stringer']
            assert tread.intersect(stringer).Volume() > 1e-6, ('unsupported tread', index, side)
    for side in ('Port', 'Starboard'):
        stringer = cabin[f'{side} companionway stringer']
        assert stringer.intersect(cabin['Companionway sill']).Volume() > 1e-7
        assert stringer.intersect(cabin['Companionway landing']).Volume() > 1e-7
    for label in ('aft','fore'):
        support=enclosures[f'Cabin sole {label} bearer and feet']
        assert overlap(cabin['Companionway landing'],support)>1e-6
        assert overlap(support,upper)+overlap(support,lower)>1e-6
    landing_f=access.tread(ACCESS_TREAD_COUNT)[0]+.65
    landing_clearance = block(0, landing_f, access.sole + .025, 1.35, .3, 5.7)
    for name, shape in fixed.items():
        assert overlap(landing_clearance,shape) < 1e-7, ('landing clearance', name)
    print(f'PASS: supported {ACCESS_TREAD_COUNT}-tread descent and landing; '
          f'four {access.riser * 12:.2f}-in risers; clear roof/deck passage.')

    # Verify preserved bottom planking under the LOCAL well, at its worst
    # corners as well as centreline. Distances are normal to the bottom panel.
    rows = np.array(hull.SECTIONS)
    wood=[Contains(s) for s in centreline.make_keelsons()]
    shell=[Contains(s) for s in (upper,lower)]
    for forward in np.linspace(ACCESS_WELL_AFT_FT, ACCESS_WELL_FORE_FT, 17):
        row = [float(np.interp(forward, rows[:, 0], rows[:, i])) for i in range(8)]
        _, width, _, _, _, bottom_width, bottom_z, rabbet = row
        keel_width = min(3.5 / 12, width * .25)
        slope = (bottom_z - rabbet) / (bottom_width - keel_width)
        for x in (-ACCESS_WELL_WIDTH_FT / 2, 0, ACCESS_WELL_WIDTH_FT / 2):
            bottom = rabbet + max(0, abs(x) - keel_width) * slope
            m=math.copysign(slope,x) if abs(x)>keel_width else 0
            norm=math.sqrt(1+m*m)
            def inside(d):
                p=boat_point(x-d*m/norm,forward,bottom+d/norm)
                return any(test(p) for test in shell)
            if x==0:
                p=boat_point(0,forward,bottom+2/12)
                assert inside(2/12) or any(test(p) for test in wood),('Missing centreline material',forward)
                z=centreline_layout.keelson_top(forward,hull.rabbet_height,access.sole)+.03
                assert not any(test(boat_point(0,forward,z)) for test in [*wood,*shell]),'Filler above aft keelson'
            else:
                assert inside(2/12),('thin planking',forward,x)
                assert not inside(4/12),('filled material beneath sole',forward,x)
    assert abs(upper.BoundingBox().xlen - 2 * max(s[1] for s in hull.SECTIONS)) < .05
    print('PASS: cabin bottom retains two-inch planking off-centre and actual keelson material on centreline; no filler above it.')

    # Hinges intentionally meet the leaves; test the rest of the stationary
    # assembly and opposite leaf at intermediate poses, not just closed/open.
    sweep_obstacles = {n: s for n, s in fixed.items() if 'stringer' not in n}
    sweep_obstacles.update({n: s for n, s, _ in deck.make_helm()})
    for angle in range(0, 91, 15):
        posed = {n: s for n, s, _ in deck.make_companionway_doors(angle)}
        for label in ('Port', 'Starboard'):
            leaf = posed[f'{label} companionway door']
            pane = posed[f'{label} companionway door window']
            assert leaf.intersect(pane).Volume() > 1e-7
            for name, shape in sweep_obstacles.items():
                assert overlap(leaf,shape) < 1e-7, ('door collision', angle, label, name)
        assert posed['Port companionway door'].intersect(
            posed['Starboard companionway door']).Volume() < 1e-7, ('leaf collision', angle)
    print('PASS: paired glazed leaves clear the enclosure, deck and helm over 0–90° (15° samples).')


if __name__ == '__main__':
    check()
