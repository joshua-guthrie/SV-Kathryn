"""Actual-solid opening, removable-cover, timber-seat and hull-skin checks."""
import math
import sys
from pathlib import Path
import cadquery as cq
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from parts import beam_layout,deck,deck_beams,hull,framing,spars,centreline,centreline_layout,hull_frames
from parts.openings import hatch_openings, framed_openings
from parts.params import (boat_point,DECK_BEAM_SIDED_FT,DECK_BEAM_DEPTH_FT,
                          KEELSON_AFT_FT,KEELSON_FORE_FT,CB_SLOT_AFT_FT,CB_SLOT_FORE_FT,
                          TRUNK_GAP_FT)
from parts.primitives import block


def overlap(a, b):
    aa, bb = a.BoundingBox(), b.BoundingBox()
    if any(getattr(aa, f'{axis}max') <= getattr(bb, f'{axis}min') + 1e-8 or
           getattr(bb, f'{axis}max') <= getattr(aa, f'{axis}min') + 1e-8
           for axis in 'xyz'):
        return 0.0
    return a.intersect(b).Volume()


def check():
    upper, lower = hull.make_hull()
    main_deck = hull.make_deck()
    hatches = {n: s for n, s, _ in deck.make_hatches()}
    frames = {n: s for n, s, _ in framing.make_opening_frames()}
    frames.update({n: s for n, s, _ in deck_beams.make_deck_beam_parts()})
    hull_members={n:s for maker in (hull_frames.make_frame_parts,hull_frames.make_support_parts) for n,s,_ in maker()}
    hull_sides=[s for n,s in hull_members.items() if n.endswith('side futtock')]
    for name, shape in {**hatches, **frames, 'upper': upper, 'lower': lower,
                        'deck': main_deck}.items():
        assert shape.isValid() and len(shape.Solids()) == 1, name
    fixed = {**frames, **{o.name: hatches[o.name] for o in hatch_openings()},
             **hull_members,'deck': main_deck, 'upper hull': upper, 'lower hull': lower}
    for opening in hatch_openings():
        print('Checking', opening.name, flush=True)
        _, top = opening.coaming_levels(hull.deck_height)
        base = hull.deck_height(opening.forward, opening.across) - 2.3
        probe = block(opening.across, opening.forward, base,
                      opening.clear_width - .08, opening.clear_length - .08,
                      top + .05 - base)
        for name, shape in fixed.items():
            assert overlap(probe, shape) < 1e-7, ('blocked hatch', opening.name, name)
        coaming = hatches[opening.name]
        assert coaming.intersect(main_deck).Volume() > 1e-6, ('floating coaming', opening.name)
        for lift in (0, .05, .5, 1.5):
            covers = {n: s for n, s, _ in deck.make_hatch_covers(lift)
                      if n.startswith(opening.name + ' cover')}
            assembly = cq.Compound.makeCompound(list(covers.values()))
            if lift > 0:
                for obstacle, obj in fixed.items():
                    assert overlap(assembly, obj) < 1e-7, ('cover removal', lift, opening.name, obstacle)
            for name, shape in covers.items():
                if lift == 0 and 'board' in name:
                    assert shape.intersect(coaming).Volume() > 1e-7, ('unseated board', name)
            if lift == 0:
                cleats = [s for n, s in covers.items() if 'cleat' in n]
                for name, board in covers.items():
                    if 'board' in name:
                        assert all(board.intersect(cleat).Volume() > 1e-7 for cleat in cleats), name
        print(f'PASS: {opening.name}: {opening.clear_width * 12:.1f} x '
              f'{opening.clear_length * 12:.1f} in clear; coaming seated and boards lift clear.')

    for opening in framed_openings():
        print('Checking supports for', opening.name, flush=True)
        name = opening.name
        all_clamps = [s for n, s in frames.items() if n.endswith('clamp')]
        for side in ('port', 'starboard'):
            carling = frames[f'{name} {side} carling']
            clamp_name = 'Forebody' if name in ('Main hold hatch', 'Forepeak hatch') else name
            clamp = frames[f'{clamp_name} {side} clamp']
            for end in ('aft', 'fore'):
                header_name = beam_layout.beam_name(beam_layout.opening_support(name, end))
                header = frames[header_name]
                assert header.intersect(carling).Volume() > 1e-6, ('header/carling', name, side, end)
                assert any(header.intersect(other).Volume() > 1e-6 for other in all_clamps), \
                    ('header/clamp', name, side, end)
                assert any(overlap(clamp,s)>1e-7 for s in hull_sides), ('clamp/frame bearing', name, side)
            halves = [s for n, s in frames.items()
                      if n.startswith(f'{name} {side} half beam')]
            for half in halves:
                assert half.intersect(carling).Volume() > 1e-6, ('half/carling', name, side)
                assert half.intersect(clamp).Volume() > 1e-6, ('half/clamp', name, side)
                assert half.intersect(main_deck).Volume() > 1e-6, ('beam/deck', name, side)
        # Section dimensions, not an axis-aligned bbox of a cambered member.
        # Measure away from the centreline centreboard clearance notch.
        beam = frames[beam_layout.beam_name(beam_layout.opening_support(name, 'aft'))]
        face = cq.Face.makeFromWires(cq.Workplane('YZ').rect(100, 40).val())
        section = beam.intersect(face.translate(cq.Vector(1.0, 0, 0))).BoundingBox()
        assert abs(section.ylen - DECK_BEAM_SIDED_FT) < 1e-5
        assert abs(section.zlen - DECK_BEAM_DEPTH_FT) < 1e-5
    print('PASS: paired side members, headers, cambered half beams and hull-seated clamps join; '
          'actual beam sections are 5.5 in square.')

    cabin = {n: s for n, s, _ in deck.make_deckhouse_parts()}
    roof_frames = {n: s for n, s in frames.items() if 'roof' in n}
    for name, shape in roof_frames.items():
        assert shape.intersect(cabin['Main cabin roof']).Volume() > 1e-7, ('roof seat', name)
    for label in ('Port', 'Starboard'):
        carling = frames[f'{label} companionway roof carling']
        for header in ('Companionway roof fore header', f'{label} companionway roof aft half header'):
            assert carling.intersect(frames[header]).Volume() > 1e-7
        assert frames[f'{label} companionway roof aft half header'].intersect(cabin['Main cabin']).Volume() > 1e-7
    print('PASS: roof carlings join split aft/fore headers and seat under the cambered roof.')

    rows = np.array(hull.SECTIONS)
    keelsons=centreline.make_keelsons()
    skin_samples=0
    centreline_samples=0
    def inside(point):
        point = cq.Vector(*point)
        return upper.isInside(point, 1e-6) or lower.isInside(point, 1e-6)
    for opening in hatch_openings():
        for f in np.linspace(opening.aft + .08, opening.fore - .08, 5):
            row = [float(np.interp(f, rows[:, 0], rows[:, i])) for i in range(8)]
            kw = min(3.5 / 12, row[1] * .25)
            slope = (row[6] - row[7]) / (row[5] - kw)
            for x in np.linspace(opening.across - opening.clear_width / 2 + .12,
                                 opening.across + opening.clear_width / 2 - .12, 5):
                bottom = row[7] + max(0, abs(x) - kw) * slope
                m = math.copysign(slope, x) if abs(x) > kw else 0
                norm = math.sqrt(1 + m * m)
                def at(d):
                    return boat_point(x - d * m / norm, f, bottom + d / norm)
                if KEELSON_AFT_FT<f<KEELSON_FORE_FT and abs(x)<centreline_layout.keelson_width(f)/2+.02:
                    # The centreline is now actual oak or the documented open
                    # board slot, rather than uniformly thin bottom planking.
                    occupied=inside(at(2/12)) or any(s.isInside(cq.Vector(*at(2/12)),1e-6) for s in keelsons)
                    slot=CB_SLOT_AFT_FT<f<CB_SLOT_FORE_FT and abs(x)<TRUNK_GAP_FT/2
                    assert occupied!=slot,('Keelson/slot material',opening.name,f,x)
                    centreline_samples+=1
                else:
                    assert inside(at(2.0 / 12)), ('thin bottom', opening.name, f, x)
                    assert not inside(at(2.95 / 12)), ('bottom passage not hollow', opening.name, f, x)
                    skin_samples+=1
    mast = spars.make_mast()
    for name, shape in frames.items():
        assert mast.intersect(shape).Volume() < 1e-7, ('mast/frame collision', name)
    print(f'PASS: {skin_samples} bottom-skin rays and {centreline_samples} keelson/slot rays preserve the actual material interfaces; '
          'framing clears the accepted mast.')


if __name__ == '__main__':
    check()
