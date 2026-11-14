"""Visually checked transcription records. Raw OCR remains a separate artifact.

Dimension values are full-size inches unless a field explicitly states otherwise.
Statements of uncertainty in the historical survey are retained.
"""


def note(key, views, text, dimensions=None, material=None, repair=None):
    return dict(id=key, source_views=views.split(), checked_text=text,
                dimensions_inches=dimensions or {}, material=material,
                repair_evidence=repair, review_status='visually checked against source crop')


NOTES = [
    note('S02-METHOD', 'S02-N01', 'Seventeen field stations were placed irregularly between railway blocks, closer at bow and stern; the keel bottom centreline was the primary datum. The drawings were replotted into ten-section format.'),
    note('S02-CORRECTION', 'S02-N01', 'Lines are based on a corrected/straight keel. The existing keel is dashed in the sheer plan. Stern sag about 8 inches and midship hollow deadrise about 3 inches port/2 inches starboard were left out of the lines for clarity.', {'stern_sag_approx':8, 'port_hollow_approx':3, 'starboard_hollow_approx':2}),
    note('S02-UNCERTAINTY', 'S02-N01', 'Stated accuracy of field notes is plus/minus 1/8 inch.', {'field_note_accuracy_plus_minus':.125}),
    note('S05-05', 'S05-N02', 'Ceiling timbers: 1-3/4-inch pine. Forward timbers end at the chain locker; stern timbers end at the stern frame. Limber boards along the keelson are not present in the main hold. Ceiling members were removed by the recording team to inspect frames.', {'thickness':1.75}, 'pine'),
    note('S05-06', 'S05-N02', 'Clamp: 5-1/2 x 2-3/4-inch pine; reinforced forward with 5-1/2 x 2-3/4-inch oak.', {'section':[5.5,2.75]}, 'pine with forward oak reinforcement'),
    note('S05-07', 'S05-N04', 'Deck beams are keyed in reference to the bow. Members to either side of hatches/cabin are counted as a set. Beams 1–3 are 6 x 4-3/4-inch pine. Beams 4–23 average 5-1/2-inch square, plus/minus 1/2 inch, pine except 12–15 oak under winders. Stern timbers aft of rudder box are 4 x 3-1/2-inch oak except member d, 6 x 3-inch pine.', {'beams_1_3':[6,4.75], 'beams_4_23':[5.5,5.5], 'variation_plus_minus':.5, 'stern_oak':[4,3.5], 'stern_d_pine':[6,3]}),
    note('S05-08', 'S05-N03', 'Deck planks are mostly fir with some pine replacements, parallel to centreline, ends tapered to waterway. Thickness 1-3/4 inches; typical widths 3-1/2 to 4 inches, some inboard members 5 to 7 inches.', {'thickness':1.75,'usual_width_range':[3.5,4],'inboard_width_range':[5,7]}, 'mostly fir, some pine replacements'),
    note('S05-10', 'S05-N03', 'Frames are oak; dimensions and pairing are highly irregular with old and new timbers. Twenty sets exposed from bow, inaccessible under main cabin; two more aft of main cabin. The printed note says first set against STERN knee. Sets 2–18 mortised into keelson; sets 19/20 pass under keelson. Preserve the printed wording; frame numbering must be interpreted separately from deck-beam numbering.', material='oak', repair='mixed older and replacement members'),
    note('S05-11', 'S05-N03', 'Hull strakes predominantly oak at/below chine; pine replacement noted under ceiling aft of main cabin. Above-chine strakes are pine.', material='oak below/pine above, with documented replacement', repair='pine replacement aft of main cabin'),
    note('S05-12', 'S05-N03', 'Oak keelson, aft section inaccessible. Forward of main cabin it has two sections scarfed between frame sets 15 and 20. Aft section 1 foot 2 inches wide; forward section 1 foot 4 inches wide x 10-1/2 inches at garboard, tapered at bow.', {'aft_width':14,'forward_width':16,'forward_depth_at_garboard':10.5}, 'oak'),
    note('S05-13', 'S05-N03', 'Knight heads: 11 x 4-inch oak.', {'section':[11,4]}, 'oak'),
    note('S05-16', 'S05-N03', 'Only a few timbers could positively be identified as older, possibly original, by wear and structural characteristics: forward keelson and several frames, mostly below chine. The survey uses a graphic designation.', repair='possibly original; do not assert certainty'),
    note('S05-18', 'S05-N03', 'Rudder box interior inaccessible; composite oak front and pine.', material='oak front and pine'),
    note('S05-19', 'S05-N03', 'Sampson post: oak, 1 foot 2 inches x 5 inches at head, tapering to 5 x 5-inch foot; mortised into stem knee. Replaced by owner in 1995.', {'head':[14,5],'foot':[5,5]}, 'oak', 'owner replacement 1995'),
    note('S05-23', 'S05-N03', 'Interior stanchions: oak, 5-1/2-inch square.', {'section':[5.5,5.5]}, 'oak'),
    note('S05-24', 'S05-N03', 'Strong back: composite pine. Top piece 5-inch square; bottom piece 1 foot 3 inches at centre, tapered to sheer and beam. See sheet 4 side section.', {'top_section':[5,5],'bottom_depth_at_centre':15}, 'pine'),
    note('S05-27', 'S05-N03', 'Transom: all oak. Fore/aft frames average 3-3/4 inches SIDED; molded dimension referred to sheet 4. Diagonal braces 6-3/4 x 2 inches; side molding 8 x 6 inches, rounded at chine.', {'fore_aft_frame_sided':3.75,'diagonal_brace':[6.75,2],'side_molding':[8,6]}, 'oak'),
    note('S05-FASTENINGS', 'S05-N05', 'Drawing wood names refer to white oak, pine and fir. Keelson sections fastened with drift pins; all hull fastenings observed by the HAER team were nails.'),
    note('S06-SURVEY', 'S06-N01', 'Fiberglass prevented measurement above/around chine except where ceiling was removed. Structural conception is based on partial ceiling removal, measured probing and nail patterns. New frames replaced in 1954 (11), versus older possibly original frames (15).', repair='1954 replacements versus possibly original frames'),
    note('S06-01', 'S06-N02', 'Ceiling: 1-3/4-inch pine; approximately 9 inches wide plus/minus 1 inch. Not shown in bow section to expose forward frames.', {'thickness':1.75,'width':9,'width_variation_plus_minus':1}, 'pine'),
    note('S06-02', 'S06-N02', 'Centerboard trunk: pine; see sheet 7.', material='pine'),
    note('S06-03', 'S06-N02', 'Clamp: 5-1/2 x 2-3/4-inch pine, reinforced forward with the same section in oak.', {'section':[5.5,2.75]}, 'pine/forward oak reinforcement'),
    note('S06-04', 'S06-N02', 'Deck: mostly fir with pine replacements, 1-3/4 inches thick; widths 3-1/2 to 4 inches, some inboard 5 to 7 inches.', {'thickness':1.75,'width_range':[3.5,4],'inboard_width_range':[5,7]}, 'fir with pine replacements'),
    note('S06-05', 'S06-N02', 'Deck beams mostly pine, average 5-1/2-inch square plus/minus 1 inch. Beams in structural conception detail are oak. Sheet 5 gives the more specific schedule.', {'section':[5.5,5.5],'variation_plus_minus':1}, 'mostly pine, oak in detail'),
    note('S06-06', 'S06-N02', 'Hull strakes: estimated 2 inches thick, highly irregular widths; mostly oak below chine with some pine replacements (sheet 5 note 11). Chine oak; examined above-chine timbers pine.', {'thickness_estimate':2}, 'oak/pine', 'pine replacements noted'),
    note('S06-07', 'S06-N02 S06-N03', 'Keel: oak, average width 8 inches plus/minus 1 inch. Traditionally separate from keelson; dotted line indicates probable seam below rabbet for more watertight construction.', {'width':8,'variation_plus_minus':1}, 'oak'),
    note('S06-08', 'S06-N03', 'Keelson: oak; average 1 foot 4 inches wide x 10-1/2 inches at garboard. See sheet 5 note 12.', {'section_at_garboard':[16,10.5]}, 'oak'),
    note('S06-09', 'S06-N03', 'Kingplank wood type not determined due to heavy paint.'),
    note('S06-10', 'S06-N03', 'Limber holes.'),
    note('S06-11', 'S06-N03', 'New frames: oak, NOT mortised into keelson. Knees are ROUNDED, NOT GROWN, at chine. Highly irregular dimensions; generally molded 1/2 inch larger than older frames (15).', {'molded_increase_approx':.5}, 'oak', 'replacement frames; rounded rather than grown knees'),
    note('S06-12', 'S06-N03', 'Mast: 1 foot 1-1/2 inches, pine; iron hoop at foot, traditionally mortised into keelson (mortise dimensions not determined). Sides at/below deck faceted for chocks.', {'diameter':13.5}, 'pine'),
    note('S06-13', 'S06-N03', 'Mast chocks: 2-inch pine, faceted between mast, deck and partners.', {'thickness':2}, 'pine'),
    note('S06-14', 'S06-N03', 'Mast partners: 3-1/2 x 11-inch oak.', {'section':[3.5,11]}, 'oak'),
    note('S06-15', 'S06-N03', 'Old frames: oak, mortised into keelson, tapered at chine; highly irregular dimensions.', material='oak', repair='older members, possibly original'),
    note('S06-16', 'S06-N03', 'Rails: 3-1/2 x 1-3/4-inch oak fastened with iron stanchions.', {'section':[3.5,1.75]}, 'oak'),
    note('S06-17', 'S06-N03', 'Sampson post: 1 foot 2 inches x 5-inch head, 5 x 5-inch foot, mortised into stem knee.', {'head':[14,5],'foot':[5,5]}, 'oak'),
    note('S06-18', 'S06-N03', 'Waterway: oak.', material='oak'),
    note('S06-19', 'S06-N03', 'Worm shoe: traditionally pine, average 3 x 8 inches plus/minus 1 inch; maximum width at centerboard 10 inches.', {'section':[3,8],'variation_plus_minus':1,'max_width_at_centerboard':10}, 'traditionally pine'),
    note('S07-SURVEY', 'S07-N01', 'Fiberglass obscured hull strakes except where ceiling was removed. Winder is a Hettinger Engine Company unit; separate references describe dredge operation.'),
    note('S07-01', 'S07-N02', 'Ceiling: 1-3/4-inch pine, approximately 9 inches wide plus/minus 1 inch; omitted in bow section to expose frames.', {'thickness':1.75,'width':9,'variation_plus_minus':1}, 'pine'),
    note('S07-02', 'S07-N02', 'Ceiling member removed by HAER team for access to frames and outer strakes. This is a survey-access condition, not proof of a permanent missing board.'),
    note('S07-03', 'S07-N02', 'Centerboard trunk cuts through keel and keelson. Walls constructed of 2 x 11-1/2-inch pine.', {'wall_stock':[2,11.5]}, 'pine'),
    note('S07-04', 'S07-N02', 'Clamp: 5-1/2 x 2-3/4-inch pine.', {'section':[5.5,2.75]}, 'pine'),
    note('S07-05', 'S07-N02', 'Deck mostly fir with pine replacements, 1-3/4-inch thick; usual widths 3-1/2 to 4 inches, some inboard 5 to 7 inches.', {'thickness':1.75,'width_range':[3.5,4],'inboard_width_range':[5,7]}, 'fir with pine replacements'),
    note('S07-06', 'S07-N02', 'Deck beams mostly pine, average 5-1/2-inch square plus/minus 1 inch; oak under winders; see sheet 5 schedule.', {'section':[5.5,5.5],'variation_plus_minus':1}, 'mostly pine, oak under winders'),
    note('S07-07', 'S07-N02', 'Electrical boxes.'),
    note('S07-08', 'S07-N02', 'Frames: oak, highly irregular sided dimensions. Molded dimension averages 3 inches at keelson. Frames in section 13 are possibly original; compare newer frames on sheet 6.', {'molded_at_keelson_average':3}, 'oak', 'section 13 possibly original; not asserted certain'),
    note('S07-09', 'S07-N03', 'Fuse box.'),
    note('S07-10', 'S07-N03', 'Hull strakes estimated 2 inches thick; highly irregular widths. Mostly oak below chine with pine replacements, oak chine; examined above-chine members pine.', {'thickness_estimate':2}, 'oak/pine'),
    note('S07-11', 'S07-N03', 'Keel: oak, width 8 inches plus/minus 1 inch; traditionally separate from keelson, probable seam shown below rabbet.', {'width':8,'variation_plus_minus':1}, 'oak'),
    note('S07-12', 'S07-N03', 'Keelson: oak, average 1 foot 4 inches wide x 10-1/2 inches at garboard; see sheet 5 note 12.', {'section_at_garboard':[16,10.5]}, 'oak'),
    note('S07-13', 'S07-N03', 'Limber holes.'),
    note('S07-14', 'S07-N03', 'Rails: 3-1/2 x 1-3/4-inch oak on iron stanchions.', {'section':[3.5,1.75]}, 'oak'),
    note('S07-15', 'S07-N03', 'Roller bars.'),
    note('S07-16', 'S07-N03', 'Waterway: oak.', material='oak'),
    note('S07-17', 'S07-N03', 'Winder brake controls dredge payout; outboard position pulls iron strap around forward wheel.'),
    note('S07-18', 'S07-N03', 'Winder clutch hauls dredge; outboard position shifts cable barrel backward into gear. Releasing handle lets bottom weight pull winders out of gear.'),
    note('S07-19', 'S07-N03', 'Worm shoe traditionally pine, average 3 x 8 inches plus/minus 1 inch; maximum width at centerboard 10 inches.', {'section':[3,8],'variation_plus_minus':1,'max_width_at_centerboard':10}, 'traditionally pine'),
]

STATIONS = [0,.5,1,1.5,2,3,4,5,6,7,8,8.5,9,9.5,10]
OFFSETS = {
    'sheer_height': '6-4-4 6-2-2 6-0-4 6-0-0 6-0-0 6-0-0 5-9-7 6-1-4 6-4-0 6-7-6 7-0-2 7-3-2 7-6-0 7-8-4 8-0-0',
    'chine_top_height': '5-9-4 5-3-6 4-11-6 4-7-0 4-3-4 3-11-5 3-10-0 4-0-0 4-2-0 4-5-4 4-8-0 4-9-0 4-10-0',
    'chine_bottom_height': '5-4-0 4-11-4 4-5-4 4-0-2 3-8-3 3-4-0 3-2-5 3-4-4 3-7-4 3-10-0 4-0-0 4-1-0 4-2-6',
    'rabbet_height': '4-3-2 3-8-7 3-2-2 2-8-6 2-4-0 1-11-4 1-10-6 2-0-4 2-2-4 2-4-0 2-6-4 2-7-1 2-8-0 3-0-0 5-8-0',
    'sheer_half_breadth': '6-4-0 6-8-6 7-0-0 7-3-0 7-6-0 7-10-0 8-1-0 7-11-4 7-7-2 6-10-2 5-8-0 4-8-4 3-7-4 2-6-4 1-3-0',
    'chine_top_half_breadth': '6-1-0 6-4-2 6-8-2 6-10-0 7-1-0 7-5-4 7-7-4 7-5-4 7-1-0 6-4-4 5-1-4 4-1-4 2-11-4',
    'chine_bottom_half_breadth': '5-9-6 5-11-6 6-2-0 6-5-0 6-8-2 7-0-2 7-1-2 7-0-0 6-6-2 5-11-0 4-9-0 2-7-4 2-6-0',
    'rabbet_half_breadth': ' '.join(['0-3-4'] * 15),
}

OCR_CORRECTIONS = [
    {'source_view':'S06-N02','raw_example':'1-374','checked':'1-3/4','reason':'fraction slash misrecognized'},
    {'source_view':'S06-N02','raw_example':'5-172','checked':'5-1/2','reason':'fraction slash misrecognized'},
    {'source_view':'S06-N02','raw_example':'Sheet 5, note 17','checked':'Sheet 5, note 11','reason':'source cross-reference checked visually'},
    {'source_view':'S05-N03','raw_example':'stern knee','checked':'stern knee (preserve as printed)','reason':'Do not silently change this to stem or assume hull-frame numbering follows the bow-keyed deck-beam schedule.'},
    {'source_view':'S06-N02','raw_example':'+ 1','checked':'plus/minus 1','reason':'OCR drops lower stroke of tolerance symbol'},
    {'source_view':'S06-R01','raw_example':'METERS: 1:32','checked':'caption conflicts with 3/4-inch imperial scale; use measured bars','reason':'the conflicting caption is in the SOURCE, not an OCR correction'},
]
