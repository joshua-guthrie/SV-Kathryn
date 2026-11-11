"""Provisional S05 deck-beam picks; reconcile stern IDs before geometry use."""
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'drawing_package'

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

    members = []
    image = Image.open(PACKAGE / view['preview']).convert('RGB')
    draw = ImageDraw.Draw(image)
    for number, (left, right) in enumerate(BEAM_EDGES, 1):
        # The narrower projected sided dimension of 1-3 agrees with 4.75 in;
        # their remaining printed 6-in dimension is the molded depth.
        sided, depth = (4.75 / 12, 6 / 12) if number <= 3 else (5.5 / 12, 5.5 / 12)
        material = 'oak' if 12 <= number <= 15 else 'pine'
        members.append(dict(set=number, forward_ft=forward((left + right) / 2),
                            preview_edges=[left, right],
                            source_native_edges=[native(left), native(right)],
                            observed_sided_ft=forward(right) - forward(left),
                            sided_ft=sided, molded_ft=depth, material=material,
                            dimension_basis='S05 note 7 printed stock; first-three orientation checked against projected plan widths',
                            position_basis='scale-measured S05-V01 timber edges; opposite half members form one set',
                            uncertainty_ft=.20))
        x = (left + right) / 2
        draw.line((x, 15, x, 535), fill=('#a04d18' if material == 'oak' else '#0876bd'), width=2)
        draw.text((x - 7, 22 + (number % 2) * 18), str(number),
                  fill=('#a04d18' if material == 'oak' else '#0876bd'), font_size=14)
    assert len(members) == 23
    assert all(a['forward_ft'] > b['forward_ft'] for a, b in zip(members, members[1:]))
    result = dict(status='provisional; not a geometry input',
                  review_required=['Reconcile the 23-set numbering with existing stern oak timbers at preview X182/220 and member d before integration.'],
                  source_view='S05-V01', source_sha256=source['sha256'],
                  native_view_sha256=hashlib.sha256((PACKAGE / view['native_image']).read_bytes()).hexdigest(),
                  source_note='S05-07', members=members,
                  deck_planks=dict(thickness_ft=1.75 / 12, typical_width_ft=3.75 / 12,
                                   inboard_width_ft=6 / 12, material='mostly fir; individual pine replacement identities unresolved'),
                  ceiling=dict(thickness_ft=1.75 / 12, nominal_width_ft=9 / 12,
                               width_allowance_ft=1 / 12, material='pine',
                               limber_boards='Absent alongside keelson in main hold; survey removal is not permanent absence'),
                  inferences=['fine beam end joints and concealed laps',
                              'individual plank runs, spiling, and staggered butt positions',
                              'exact pine replacement-board identities'])
    (PACKAGE / 'm4_deck_schedule.json').write_text(json.dumps(result, indent=2) + '\n')
    image.save(ROOT / 'renders/m4-deck-beam-source.png')
    print('Saved 23 provisional deck-beam picks; stern numbering/material reconciliation remains open before geometry use.')
    return result


if __name__ == '__main__':
    measure()
