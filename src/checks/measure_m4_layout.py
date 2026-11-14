"""Measured S05 deck-beam schedule reconciled with the opening frames.

The printed S05-07 note gives 23 deck-beam sets plus a *separate* group of
stern timbers aft of the rudder box.  This script keeps the original scale
picks, proves which sets are split half-beam pairs around an opening by
sampling the drawing itself, and records the stern timbers.  It is the
measurement source for parts/beam_layout.py; it does not build geometry.
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / 'references/drawing_package'
sys.path.insert(0, str(ROOT / 'src'))
from parts.openings import framed_openings

# Reviewed edge pairs in the existing 2000-pixel preview, bow to stern.
# These are deck-beam set IDs, not hull-frame or lines-station numbers.
BEAM_EDGES = [
    (1608, 1620), (1545, 1558), (1482, 1496), (1407, 1425),
    (1322, 1338), (1262, 1275), (1200, 1215), (1144, 1157),
    (1089, 1102), (1024, 1038), (949, 964), (877, 892),
    (807, 822), (750, 764), (678, 692), (603, 616),
    (528, 543), (468, 481), (400, 413), (330, 343),
    (273, 285), (213, 226), (175, 188),
]

# S05-07: which printed opening each beam set frames.  A set outside the
# clear opening is a full header beam; the note calls the two sides of an
# interrupted member one set.
HEADER_ROLES = {
    5: ('Forepeak hatch', 'fore'),
    6: ('Forepeak hatch', 'aft'),
    7: ('Main hold hatch', 'fore'),
    10: ('Main hold hatch', 'aft'),
    15: ('After deck hatch', 'fore'),
    17: ('Cabin deck opening', 'fore'),
    21: ('Cabin deck opening', 'aft'),
}

# The drawing proves these sets cross an opening only as paired half beams:
# at each picked edge the line is absent across the clear opening width.
SPLIT_SETS = {8, 9, 16, 18, 19, 20}

# Stern timbers aft of the rudder box (S05-07c).  The note prints the oak
# stock but no count, and no member is lettered on the plan.  The full
# transverse timber at the rudder-box aft face measures about 4 in in plan,
# matching the 4 x 3 1/2-in oak class.  A separate 6 x 3-in pine "d" cannot be
# identified without inventing stock, so it is left as an explicit open item.
# Picks are line centres from the native plan scan.
STERN_TIMBER_PICKS = [
    dict(id='1', label='Stern oak deck timber 1 (S05-07c)', preview_edges=[111.89, 125.13],
         sided_inches=4, molded_inches=3.5, material='oak',
         basis='S05-07(c); full transverse timber at the rudder-box aft face'),
]
# The seven-C leader also touches a transverse line near preview X 59.  At
# that station the counter is solid and the line lies outside the interior
# air volume, so it cannot be a standard deck beam; it is retained only as an
# open source identification, not as invented beam geometry.
UNRESOLVED_STERN_LINE = dict(preview_edges=[52.87, 65.48])


def measure():
    manifest = json.loads((PACKAGE / 'manifest.json').read_text())
    source = next(row for row in manifest['sources'] if row['id'] == 'S05')
    view = next(row for row in manifest['views'] if row['id'] == 'S05-V01')
    registration = json.loads((PACKAGE / 'registration.json').read_text())
    a, b = registration['transformations']['S05']['grid_x_to_F']

    def native(x):
        return view['native_box'][0] + x * view['native_size'][0] / view['preview_size'][0]

    def forward(x):
        return a * native(x) / source['native_size'][0] * 1440 + b

    native_image = Image.open(PACKAGE / view['native_image']).convert('L')
    pixels = np.asarray(native_image)
    sx = pixels.shape[1] / view['preview_size'][0]
    sy = pixels.shape[0] / view['preview_size'][1]
    ft_per_preview_px = a * (view['native_size'][0] / view['preview_size'][0]) / source['native_size'][0] * 1440
    centreline_preview_y = (registration['transformations']['S05']['centreline_grid_y'] / 1440
                            * source['native_size'][0] - view['native_box'][1]) / sy

    def dark_fraction(edges, across_half_ft):
        # Allow for slight scan skew: in each row, look for the line within
        # two preview pixels of the picked edge.  A real opening has no line
        # anywhere in that window.
        values = []
        for x in edges:
            column = int(x * sx)
            window = max(1, int(2 * sx))
            rows = np.arange(int((centreline_preview_y - across_half_ft / ft_per_preview_px) * sy),
                             int((centreline_preview_y + across_half_ft / ft_per_preview_px) * sy))
            values.append(float((pixels[rows, column - window:column + window + 1].min(axis=1) < 128).mean()))
        return values

    def expected_opening(forward_ft):
        for opening in framed_openings():
            if opening.aft <= forward_ft <= opening.fore:
                return opening
        return None

    members = []
    image = Image.open(PACKAGE / view['preview']).convert('RGB')
    draw = ImageDraw.Draw(image)
    for number, (left, right) in enumerate(BEAM_EDGES, 1):
        # S05-07(a): the first three are 6 x 4 3/4-in with the 4 3/4-in in
        # plan, i.e. 6-in molded.  S05-07(b): the rest average 5 1/2 square.
        sided, depth = (4.75 / 12, 6 / 12) if number <= 3 else (5.5 / 12, 5.5 / 12)
        material = 'oak' if 12 <= number <= 15 else 'pine'
        opening = expected_opening(forward((left + right) / 2))
        role = 'full'
        if number in HEADER_ROLES:
            role = 'header_' + HEADER_ROLES[number][1]
            assert opening is None, ('Header set lies inside an opening', number)
        elif number in SPLIT_SETS:
            assert opening is not None, ('Split set is not inside an opening', number)
            role = 'split'
            fractions = dark_fraction((left, right), opening.clear_width / 2 * .88)
            assert max(fractions) < .10, ('Split set has a continuous beam line', number, fractions)
        source_forward = forward((left + right) / 2)
        build_forward = source_forward
        if role.startswith('header_'):
            opening_obj = next(o for o in framed_openings()
                               if o.name == HEADER_ROLES[number][0])
            if role == 'header_aft':
                build_forward = min(build_forward, opening_obj.aft - sided / 2)
            else:
                build_forward = max(build_forward, opening_obj.fore + sided / 2)
            # Use only the stated pick allowance to preserve the measured
            # clear opening; do not silently move a source member further.
            assert abs(build_forward - source_forward) <= .20 + 1e-9, (number, build_forward, source_forward)
        members.append(dict(
            set=number, forward_ft=source_forward, build_forward_ft=build_forward,
            preview_edges=[left, right],
            source_native_edges=[native(left), native(right)],
            observed_sided_ft=forward(right) - forward(left),
            sided_ft=sided, molded_ft=depth, material=material,
            role=role, opening=(HEADER_ROLES[number][0] if number in HEADER_ROLES else
                                opening.name if opening is not None else None),
            dimension_basis='S05 note 7 printed stock; first-three orientation checked against projected plan widths',
            position_basis='scale-measured S05-V01 timber edges; opposite half members form one set',
            uncertainty_ft=.20))
        if role != 'split':
            fractions = dark_fraction((left, right), 2.0)
            assert max(fractions) > .25, ('Full beam line is absent', number, fractions)
        x = (left + right) / 2
        draw.line((x, 15, x, 535), fill=('#a04d18' if material == 'oak' else '#0876bd'), width=2)
        draw.text((x - 7, 22 + (number % 2) * 18), str(number),
                  fill=('#a04d18' if material == 'oak' else '#0876bd'), font_size=14)

    assert len(members) == 23
    assert all(a['forward_ft'] > b['forward_ft'] for a, b in zip(members, members[1:]))
    assert {m['set'] for m in members if m['role'] == 'split'} == SPLIT_SETS
    assert {m['set'] for m in members if m['role'].startswith('header_')} == set(HEADER_ROLES)

    stern_timbers = []
    for pick in STERN_TIMBER_PICKS:
        left, right = pick['preview_edges']
        stern_timbers.append(dict(
            id=pick['id'], label=pick['label'],
            forward_ft=forward((left + right) / 2),
            preview_edges=[left, right],
            source_native_edges=[native(left), native(right)],
            observed_sided_ft=forward(right) - forward(left),
            sided_ft=pick['sided_inches'] / 12,
            molded_ft=pick['molded_inches'] / 12,
            material=pick['material'], basis=pick['basis'], uncertainty_ft=.20))
    assert len(stern_timbers) == 1 and 0 < stern_timbers[0]['forward_ft'] < 2.0
    assert 3 / 12 < stern_timbers[0]['observed_sided_ft'] < 7 / 12
    left, right = UNRESOLVED_STERN_LINE['preview_edges']
    unresolved_stern = dict(
        forward_ft=forward((left + right) / 2), preview_edges=[left, right],
        reason='Transverse line touched by the 7c leader, but it lies in the solid counter/transom edge and outside the interior air; not a standard deck beam.',
        status='unresolved; not a geometry input')

    result = dict(
        status='reconciled for M4 integration; source for deck beams and stern timbers',
        review_required=[
            'The printed note gives stern-timber stock but no count; only the two distinguishable 4 x 3 1/2-in oak members are modelled.',
            'Member d (6 x 3-in pine) is not lettered on the plan and cannot be identified without inventing stock; it remains unresolved.',
            'The 7c leader also touches a line in the solid counter near F=-1.05; it is not a standard deck beam and is retained as an unresolved source line.',
            'The after-deck hatch has no separate aft header set; its carlings bear on the cabin fore header (set 17) and fore header (set 15).',
        ],
        source_view='S05-V01', source_sha256=source['sha256'],
        native_view_sha256=hashlib.sha256((PACKAGE / view['native_image']).read_bytes()).hexdigest(),
        source_note='S05-07', members=members, stern_timbers=stern_timbers,
        unresolved_stern_line=unresolved_stern,
        split_set_test='The picked edge lines are absent across the clear opening width, so these sets are paired half beams, not continuous beams.',
        deck_planks=dict(thickness_ft=1.75 / 12, typical_width_ft=3.75 / 12,
                         inboard_width_ft=6 / 12, material='mostly fir; individual pine replacement identities unresolved'),
        ceiling=dict(thickness_ft=1.75 / 12, nominal_width_ft=9 / 12,
                     width_allowance_ft=1 / 12, material='pine',
                     limber_boards='Absent alongside keelson in main hold; survey removal is not permanent absence'),
        inferences=['fine beam end joints and concealed laps',
                    'individual plank runs, spiling, and staggered butt positions',
                    'exact pine replacement-board identities',
                    'stern-timber count beyond the two visibly distinguishable members'])
    (PACKAGE / 'm4_deck_schedule.json').write_text(json.dumps(result, indent=2) + '\n')
    image.save(ROOT / 'renders/m4-deck-beam-source.png')
    print('Saved reconciled 23-set deck schedule and two stern timbers; split sets proved from the drawing.')
    return result


if __name__ == '__main__':
    measure()
