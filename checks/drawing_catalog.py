"""Located view bounds on a proportional 1440 x 960 grid of each ORIGINAL scan.

The builder converts these bounds to native pixels and records the exact crop
and transforms. Grid coordinates locate views; they are not dimensional scales.
"""

SHEET_TITLES = {
    1: 'Identity, history and bow ornament', 2: 'Lines, offsets and measurement method',
    3: 'Hull history, profile and rig', 4: 'General arrangement and deck equipment',
    5: 'Structural and hold plans, timber schedule',
    6: 'Frame sets 4/5 and structural conception',
    7: 'Frame set 13, cabin section and winder', 8: 'Sail plan (reference only)',
}


def view(sheet, suffix, title, box, kind='drawing', psm=3):
    return dict(id=f'S{sheet:02d}-{suffix}', sheet=sheet, title=title,
                grid_box=list(box), kind=kind, ocr_psm=psm)


VIEWS = [
    view(1, 'V01', 'Vessel name and identity', (100, 100, 580, 320)),
    view(1, 'V02', 'General vessel illustration', (445, 60, 1020, 600)),
    view(1, 'V03', 'Bow ornament and chains', (945, 85, 1338, 295)),
    view(1, 'N01', 'History and unusual construction', (105, 330, 445, 885), 'notes', 6),
    view(1, 'N02', 'Survey context and credits', (1030, 325, 1340, 725), 'notes', 6),
    view(1, 'T01', 'Official register dimensions', (1030, 735, 1340, 865), 'table', 6),
    view(1, 'V04', 'Location map', (440, 600, 1020, 914)),
    view(2, 'V01', 'Sheer plan and station locations', (90, 115, 1090, 335)),
    view(2, 'V02', 'Half-breadth plan', (135, 360, 1090, 527)),
    view(2, 'V03', 'Body plan and transom', (95, 550, 430, 765)),
    view(2, 'T01', 'Table of offsets', (470, 557, 1195, 792), 'table', 6),
    view(2, 'N01', 'Field method, corrected keel and uncertainty', (1090, 70, 1340, 535), 'notes', 6),
    view(2, 'R01', 'Feet/metre scale bars', (130, 802, 1315, 895), 'scale', 6),
    view(3, 'V01', 'Hull profile and rigging', (210, 85, 1155, 795)),
    view(3, 'V02', 'Aft rig view', (1170, 375, 1340, 785)),
    view(3, 'N01', 'Hull history, repairs and materials', (105, 60, 620, 590), 'notes'),
    view(3, 'N02', 'Rigging and running-gear key', (1090, 65, 1345, 425), 'notes'),
    view(3, 'R01', 'Feet/metre scale bars', (325, 797, 1125, 892), 'scale', 6),
    view(4, 'V01', 'Inboard profile', (245, 235, 1325, 465)),
    view(4, 'V02', 'Deck plan', (240, 500, 1325, 785)),
    view(4, 'V03', 'Port rail profile', (245, 55, 1070, 200)),
    view(4, 'V04', 'Cabin profile aft', (155, 465, 310, 560)),
    view(4, 'N01', 'Spars, fittings and deck notes', (1090, 60, 1340, 235), 'notes', 6),
    view(4, 'N02', 'Equipment, kingplank and steering key', (1080, 385, 1345, 595), 'notes', 6),
    view(4, 'N03', 'Aft equipment and modification key', (1080, 695, 1345, 790), 'notes', 6),
    view(4, 'R01', 'Feet/metre scale bars', (135, 805, 1310, 895), 'scale', 6),
    view(5, 'V01', 'Main deck structural plan', (135, 95, 1075, 365)),
    view(5, 'V02', 'Hold plan and interior arrangement', (135, 465, 1075, 720)),
    view(5, 'V03', 'Main beam register-mark detail A', (610, 380, 825, 460)),
    view(5, 'N01', 'Interior arrangement key', (835, 63, 1095, 175), 'notes', 6),
    view(5, 'N02', 'Ceiling and clamp notes 5/6', (835, 350, 1090, 460), 'notes', 6),
    view(5, 'N03', 'Deck, frames, keelson and fittings notes', (1090, 60, 1340, 800), 'notes', 6),
    view(5, 'N04', 'Deck-beam timber schedule note 7', (830, 650, 1090, 810), 'notes', 6),
    view(5, 'N05', 'Wood species and observed fastenings', (1090, 820, 1340, 900), 'notes', 6),
    view(5, 'R01', 'Feet/metre scale bars', (115, 805, 1085, 895), 'scale', 6),
    view(6, 'V01', 'Section at frame set 4, looking to bow', (205, 65, 580, 395)),
    view(6, 'V02', 'Section at frame set 5, looking aft to bulkhead', (120, 395, 680, 805)),
    view(6, 'V03', 'Structural conception, frame sets 13–16 starboard', (805, 70, 1335, 550)),
    view(6, 'N01', 'Survey access limitations and repair distinction', (580, 137, 808, 310), 'notes', 6),
    view(6, 'N02', 'Construction notes 1–7', (727, 565, 1035, 835), 'notes', 6),
    view(6, 'N03', 'Construction notes 8–19', (1030, 565, 1340, 895), 'notes', 6),
    view(6, 'R01', 'Feet/metre scale bars and printed scales', (130, 810, 825, 900), 'scale', 6),
    view(7, 'V01', 'Section at frame set 13, looking aft to cabin bulkhead', (120, 75, 705, 435)),
    view(7, 'V02', 'Section at cabin hatch, looking forward to cabin bulkhead', (130, 430, 665, 805)),
    view(7, 'V03', 'Winder construction detail', (900, 70, 1330, 555)),
    view(7, 'N01', 'Survey access and winder operation', (700, 60, 915, 270), 'notes', 6),
    view(7, 'N02', 'Construction notes 1–8', (705, 570, 1035, 795), 'notes', 6),
    view(7, 'N03', 'Construction and winder notes 9–19', (1030, 580, 1340, 895), 'notes', 6),
    view(7, 'R01', 'Feet/metre scale bars and printed scales', (130, 805, 825, 900), 'scale', 6),
    view(8, 'V01', 'Complete sail-plan reference', (100, 55, 1345, 805)),
    view(8, 'R01', 'Scale and footer reference', (130, 805, 1315, 895), 'scale', 6),
]
