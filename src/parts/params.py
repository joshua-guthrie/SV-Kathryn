"""Source dimensions in feet; registered parts are converted to millimetres."""
from soma import param
from .datum import (HULL_AFT_FT, HULL_FORE_FT, LINE_STATIONS_FT, source_forward,
                    legacy_forward, sheer_band_height, sheer_band_flare, CENTRELINE_SOURCE,FRAME_SOURCE,STERN_SOURCE,STERN_REMEDY_SOURCE)

# Recorded vessel dimensions drive the geometry. The origin is on the
# centreline amidships; the bow faces -Y, and Z is up from the lines-plan datum.
MODEL_SCALE = param(
    1, "Model scale denominator", min=1, max=64, step=1, group="Display",
    help="1 is full-size 1:1 in millimetres; 32 is 1:32. Source dimensions remain full-size feet.",
)
MM_PER_FOOT = 304.8
MODEL_MM_PER_FOOT = MM_PER_FOOT / MODEL_SCALE
HULL_LENGTH_FT = 50.0  # Recorded-length reference, not the extent of every projection.
DECK_CAMBER_FT = 0.14
DECK_THICKNESS_FT = 1.75 / 12
DECK_PLANK_NOMINAL_IN = 4
DECK_PLANK_WIDTH_FT = 3.5 / 12  # 4-in nominal (3.5-in dressed) fir/pine boards.
DECK_KINGPLANK_NOMINAL_IN = 6
DECK_CENTRE_PLANK_WIDTH_FT = 5.5 / 12  # 6-in nominal (5.5-in dressed) kingplank stock.
DECK_MAX_BOARD_LENGTH_FT = 12.0  # Hard maximum from standard 12-ft lumber.
DECK_BUTT_TOLERANCE_FT = 1 / 16 / 12  # Half-beam joint check tolerance.
DECK_STAGGER_FT = 4.0  # At least two beam bays between adjacent plank butts.
DECK_BUTT_EDGE_CLEARANCE_FT = 1.0  # Keep internal butts clear of opening coamings.
DECK_MIN_BOARD_LENGTH_FT = 0.5  # Avoid sliver boards; <4-ft closures are reported.
DECK_SCARF_LENGTH_FT = 14 / 12  # Visible kingplank scarf, 8:1 over 1.75-in thickness.
DECK_SCARF_MIN_BOARD_FT = 8.0  # Scarf only where stock length requires a joint.
WATERLINE_FT = 4.35
MAST_DECK_FORWARD_FT = source_forward('S04', 914.0)
MAST_POSITION_FT = MAST_DECK_FORWARD_FT + 1.05  # Approximate heel datum; spars solves the actual axis.
MAST_DIAMETER_FT = 13.5 / 12
MAST_HEIGHT_FT = 62.5  # Sheet 3: mast height 62'-6".
MAST_STEP_HEIGHT_FT = 2.5
MAST_RAKE_FT = 14.0  # skipjack masts rake aft strongly (~12-13 deg)
BOOM_AFT_POSITION_FT = legacy_forward(-10.5)
RIG_HEIGHT_RISE_FT = sheer_band_height(legacy_forward(42.0))
BOOM_FRONT_HEIGHT_FT = 11.0 + sheer_band_height(MAST_DECK_FORWARD_FT)
BOOM_AFT_HEIGHT_FT = 12.0 + sheer_band_height(legacy_forward(1.5))
# Full spar and headwork share the new original-drawing registration.
from .bow_layout import SPAR as BOW_SPAR, HEADWORK as BOW_HEADWORK, LONGHEAD as BOW_LONGHEAD
BOWSPRIT_END_FT = BOW_SPAR['end_f']
BOWSPRIT_HEEL_FT = BOW_SPAR['heel_f']
BOWSPRIT_HEEL_RADIUS_FT = BOW_SPAR['square_depth_ft']/2
BOWSPRIT_TIP_RADIUS_FT = BOW_SPAR['tip_radius_ft']
BOWSPRIT_TIP_HEIGHT_FT = BOW_SPAR['heel_z']+(BOWSPRIT_END_FT-BOWSPRIT_HEEL_FT)*BOW_SPAR['slope']
HEADRAIL_ROOT_FT = BOW_HEADWORK['headrail_root_f']
HEADRAIL_TIP_FT = BOW_HEADWORK['headrail_tip_f']
TRAILBOARD_ROOT_FT = BOW_LONGHEAD['root_f']
TRAILBOARD_TIP_FT = BOW_LONGHEAD['body_tip_f']
TRAILBOARD_THICKNESS_FT = BOW_LONGHEAD['board_thickness_ft']

IVORY = (.88, .88, .83)
WOOD = (.57, .38, .20)
IRON = (.18, .21, .22)
GLASS = (.10, .18, .21)
TRAILBOARD_PAINT = (.25, .045, .035)
CARVED_IVORY = (.91, .80, .53)
# With bow -Y and up +Z, the port side is +X (right-handed world frame).
PORT_SIDE = 1

# Visible deck arrangements reconstructed from sheet 4, dimensions in feet.
CABIN_AFT_FT = source_forward('S04', 398.0)
CABIN_FORE_FT = source_forward('S04', 520.0)
CABIN_FORWARD_FT = (CABIN_AFT_FT + CABIN_FORE_FT) / 2
CABIN_WIDTH_FT = 7.4  # S07 cabin section, scale-measured envelope (approximate).
CABIN_LENGTH_FT = CABIN_FORE_FT - CABIN_AFT_FT
CABIN_HEIGHT_FT = 2.7
COMPANIONWAY_LENGTH_FT = source_forward('S04', 453.0) - CABIN_AFT_FT
COMPANIONWAY_FORWARD_FT = CABIN_AFT_FT + COMPANIONWAY_LENGTH_FT / 2
COMPANIONWAY_WIDTH_FT = 4.6
COMPANIONWAY_HEIGHT_FT = 1.8
COMPANIONWAY_FRONT_SETBACK_FT = .75  # traced rake, not a printed dimension
CABIN_ROOF_CAMBER_FT = .12
COMPANIONWAY_ROOF_CAMBER_FT = .10
CABIN_ROOF_THICKNESS_FT = .16
CABIN_ROOF_OVERHANG_FT = .60
# Sheet 4 shows paired aft doors and a steep descending companion ladder;
# sheet 7 shows the roof opening. Small access dimensions are reconstructed,
# not printed historical measurements. The model normally shows closed doors.
CABIN_WALL_FT = .14
COMPANIONWAY_AFT_FT = COMPANIONWAY_FORWARD_FT - COMPANIONWAY_LENGTH_FT / 2
ACCESS_CLEAR_WIDTH_FT = 1.65
ACCESS_WELL_WIDTH_FT = 2.85  # S07 cabin-hatch roof opening, scale-measured (approximate).
ACCESS_WELL_AFT_FT = COMPANIONWAY_AFT_FT + CABIN_WALL_FT
ACCESS_WELL_FORE_FT = CABIN_FORE_FT - CABIN_WALL_FT
ACCESS_SILL_HEIGHT_FT = .18
ACCESS_SOLE_DROP_FT = 2.75  # Scale-derived cabin section drop, subject to actual bottom clearance.
ACCESS_TIMBER_FT = .14
ACCESS_TREAD_COUNT = 3  # Three treads, then the landing: four equal risers.
ACCESS_TREAD_GOING_FT = .4
ACCESS_TREAD_DEPTH_FT = .48
ACCESS_DOOR_THICKNESS_FT = .06
ACCESS_DOOR_GAP_FT = .025
ACCESS_DOOR_OPEN_DEG = 0.0  # Static pose; outward travel checked over 0–90°.
HATCHES_FT = [
    ("After deck hatch", source_forward('S04', 562.5), 3.2, 3.4),
    ("Main hold hatch", source_forward('S04', 795.5), 6.5, 5.5),
    ("Forepeak hatch", source_forward('S04', 876.0), 2.0, 2.0),
]
HATCH_ACROSS_FT = {"Forepeak hatch": PORT_SIDE * 2.75}  # Sheet 4 item 10, port of kingplank.
# Coaming/cover details are traced or construction-inferred, not printed sizes.
# Kathryn HAER data pp. 3–4: white-oak coamings; forepeak cut nearly flush in 1981.
HATCH_WALL_FT = 3.5 / 12
HATCH_HEIGHTS_FT = {"After deck hatch": .75, "Main hold hatch": .9,
                    "Forepeak hatch": .06}
HATCH_COVER_COUNTS = {"After deck hatch": 4, "Main hold hatch": 8, "Forepeak hatch": 3}
HATCH_COVER_THICKNESS_FT = 1.5 / 12
HATCH_COVER_GAP_FT = .006
HATCH_COVER_OVERHANG_FT = .04
HATCH_COVER_LIFT_FT = 0.0  # Removable boards; check vertical removal, not a hinged lid.
DECK_BEAM_SIDED_FT = 5.5 / 12  # Sheet 5 note 7, average for beams 4–23.
DECK_BEAM_DEPTH_FT = 5.5 / 12
DECK_CLAMP_SIDED_FT = 2.75 / 12  # Sheet 5 note 6: pine clamp 5.5 × 2.75 in.
DECK_CLAMP_DEPTH_FT = 5.5 / 12
INTERIOR_SKIN_FT = 2.24 / 12  # Retain a margin over the estimated 2-in hull strakes.
ROOF_BEAM_SIDED_FT = .20  # Traced roof supports; dimensions unlabelled.
ROOF_BEAM_DEPTH_FT = .22
JIB_TRAVELLER_FORWARD_FT = source_forward('S04', 934.0)
WINCH_FORWARD_FT = source_forward('S04', 690.0)
ENGINE_FORWARD_FT = source_forward('S04', 635.0)
ENGINE_COVER_LENGTH_FT = source_forward('S04', 660.0)-source_forward('S04', 610.0)  # Traced plan envelope.
BOW_POST_FORWARD_FT = source_forward('S05',862.0)  # Located Samson post, not inherited stern-normalized position.
FOREPEAK_BULKHEAD_FT = source_forward('S04', 843.0)
BULKHEAD_THICKNESS_FT = 1.75 / 12  # Interim plank-panel reconstruction; individual boards M4.
RAIL_TOP_FT = .98
RAIL_LOWER_FT = .36
RAIL_WIDTH_FT = 3.5 / 12
RAIL_THICKNESS_FT = 1.75 / 12

# Sheet 4 / photos/rudder detail 3.png: trace the dashed stock centreline,
# not the sloping hull outline. It rises AFT into the existing wheel box.
# The stock's traced run/rise gives approximately 25 degrees from vertical.
# The blade is a proportional reconstruction registered to the hull, not a
# separately dimensioned fabrication drawing. Its revised 3.5-ft height is
# used consistently for the outline, head drop and aft offsets.
HELM_FORWARD_FT = STERN_REMEDY_SOURCE['rudder_head_forward_ft']  # Independent upper-deck/stock datum.
HELM_BOX_FORWARD_FT = (STERN_SOURCE['helm_box_aft_ft']+STERN_SOURCE['helm_box_fore_ft'])/2
HELM_BOX_LENGTH_FT = STERN_SOURCE['helm_box_fore_ft']-STERN_SOURCE['helm_box_aft_ft']
HELM_BOX_WIDTH_FT = STERN_SOURCE['helm_box_width_ft']
HELM_WHEEL_FORWARD_FT = STERN_SOURCE['helm_wheel_forward_ft']
HELM_WHEEL_RADIUS_FT = 1.0  # Rim; handles extend to 1.23 ft. Scaled/photo-qualified.
HELM_HANDLE_RADIUS_FT = 1.23
HELM_WHEEL_HEIGHT_FT = 1.45
HELM_BOX_HEIGHT_FT = 1.85
HELM_STOCK_HEAD_ABOVE_DECK_FT = .5
RUDDER_RAKE_DEG = 25.0
RUDDER_BLADE_HEIGHT_FT = 3.5
_RUDDER_OUTLINE_SCALE = RUDDER_BLADE_HEIGHT_FT / 4.1
RUDDER_BLADE_TOP_DROP_FT = 3.55 * _RUDDER_OUTLINE_SCALE + sheer_band_height(HELM_FORWARD_FT)
RUDDER_AFT_EDGE_FROM_HELM_FT = -.2 * _RUDDER_OUTLINE_SCALE
RUDDER_AFT_BULGE_FT = .85 * _RUDDER_OUTLINE_SCALE
RUDDER_THICKNESS_FT = .18
RUDDER_POST_RADIUS_FT = .13
RUDDER_RUNNING_CLEARANCE_FT = .06
RUDDER_BLADE_CORNER_RADIUS = .18
RUDDER_GUDGEON_FRACTIONS = (.25, .9)
STERNPOST_DEPTH_FT = .24
STERN_RAKE_FT_PER_FT = STERN_REMEDY_SOURCE['counter']['rake_forward_per_vertical_ft']
STERN_BLEND_END_FT = 14.0
STERN_MOULDING_DEPTH_FT = 8/12
STERN_MOULDING_NORMAL_FT = 6/12

# Sheets 6/7: 8-inch oak keel and a separate 3 x 8-inch worm shoe.
# The oak's external depth is traced from the section (approximate), not the
# 10.5-inch internal keelson depth. Only the stern has a deadwood filling.
KEEL_THICKNESS_FT = 8 / 12
KEEL_EXPOSED_DEPTH_FT = 6 / 12
WORM_SHOE_DEPTH_FT = 3 / 12
WORM_SHOE_MAX_WIDTH_FT = 10 / 12
# Carry the heel run into the fair body at station 5. Ending the filling at
# 12.5 ft forced the keel up to the still-falling rabbet and made a hollow.
STERN_DEADWOOD_END_FT = LINE_STATIONS_FT[5]

# M2: printed stock sizes and located source layout; fine joinery/pose details
# are reconstruction choices retained in the centreline measurement ledger.
KEELSON_AFT_FT = CABIN_AFT_FT + .5  # Inaccessible cabin continuation, inferred.
KEELSON_FORE_FT = CENTRELINE_SOURCE['keelson_fore_ft']
KEELSON_AFT_WIDTH_FT = CENTRELINE_SOURCE['keelson_aft_width_ft']
KEELSON_FORE_WIDTH_FT = CENTRELINE_SOURCE['keelson_fore_width_ft']
KEELSON_ABOVE_GARBOARD_FT = CENTRELINE_SOURCE['keelson_height_above_garboard_ft']
KEELSON_FOOT_FT = CENTRELINE_SOURCE['keelson_lower_foot_ft']
KEELSON_PROFILE_TOLERANCE_FT = .005  # CAD interpolation, not source uncertainty.
KEELSON_SCARF_FORE_FT = CENTRELINE_SOURCE['scarf_fore_ft']
KEELSON_SCARF_AFT_FT = KEELSON_SCARF_FORE_FT-CENTRELINE_SOURCE['scarf_length_ft']
KEELSON_TAPER_START_FT = CENTRELINE_SOURCE['keelson_taper_start_ft']
KEELSON_TIP_WIDTH_FT = CENTRELINE_SOURCE['keelson_tip_width_ft']
TRUNK_AFT_FT = CENTRELINE_SOURCE['trunk_outer_aft_ft']
TRUNK_FORE_FT = CENTRELINE_SOURCE['trunk_outer_fore_ft']
TRUNK_END_FT = CENTRELINE_SOURCE['trunk_end_length_ft']
TRUNK_GAP_FT = CENTRELINE_SOURCE['trunk_gap_ft']
TRUNK_WALL_FT = CENTRELINE_SOURCE['trunk_wall_ft']
TRUNK_COURSE_FT = CENTRELINE_SOURCE['trunk_course_height_ft']
TRUNK_COURSES = CENTRELINE_SOURCE['trunk_courses']
TRUNK_OUTER_WIDTH_FT = TRUNK_GAP_FT+2*TRUNK_WALL_FT
CB_SLOT_AFT_FT = TRUNK_AFT_FT+TRUNK_END_FT
CB_SLOT_FORE_FT = TRUNK_FORE_FT-TRUNK_END_FT
CENTREBOARD_THICKNESS_FT = CENTRELINE_SOURCE['board_thickness_ft']
CENTREBOARD_ANGLE_DEG = CENTRELINE_SOURCE['board_raised_angle_degrees']
CENTREBOARD_PIVOT_FT,CENTREBOARD_PIVOT_Z_FT = CENTRELINE_SOURCE['board_pivot_FZ']
CENTREBOARD_PIN_RADIUS_FT = .5/12
MAST_PARTNER_SIDED_FT,MAST_PARTNER_DEPTH_FT = CENTRELINE_SOURCE['mast_partner_section_ft']
MAST_PARTNER_SPAN_FT = CENTRELINE_SOURCE['mast_partner_span_ft']
MAST_CHOCK_FT = CENTRELINE_SOURCE['mast_chock_radial_ft']
MAST_FORWARD_SUPPORT_FT = CENTRELINE_SOURCE['mast_fore_support_ft']

# M3 hull-frame sections are independent of the deck-beam averages above.
OLD_FRAME_MOLDED_FT = 3/12  # S07-08 at keelson; irregular individual timbers.
REPAIR_FRAME_MOLDED_FT = 3.5/12  # S06-11 generally 0.5 in larger.
FRAME_HEAD_MOLDED_FT = 3.5/12  # Fitted clamp bearing; reconstruction.
FRAME_TENON_FT = 1.5/12  # Fine mortise dimensions unrecorded.
FRAME_SHELL_BEARING_FT = .015
FRAME_LIMBER_WIDTH_FT = 2/12
FRAME_LIMBER_HEIGHT_FT = 1.25/12
STEM_KNEE_AFT_FT = source_forward('S05',845.0)
STEM_KNEE_FORE_FT = HULL_FORE_FT-1.1
STEM_KNEE_WIDTH_FT = 8/12  # Scaled/inferred; source specifies oak, not a section.
STEM_KNEE_RISE_FT = 1.8  # Located profile approximation above the garboard.


def boat_point(across, forward, height):
    """Source feet in the M0 recorded-length datum; bow -Y, port +X."""
    return (across, HULL_LENGTH_FT / 2 - forward, height)


def offset(value):
    """HAER offsets are feet-inches-eighths of an inch."""
    feet, inches, eighths = map(int, value.split("-"))
    return feet + (inches + eighths / 8) / 12


# Sheet 2, table of offsets, stations 0 through 10.
STATIONS = [0, .5, 1, 1.5, 2, 3, 4, 5, 6, 7, 8, 8.5, 9, 9.5, 10]
SHEER_HEIGHTS = "6-4-4 6-2-2 6-0-4 6-0-0 6-0-0 6-0-0 6-0-0 6-1-4 6-4-0 6-7-6 7-0-2 7-3-2 7-6-0 7-8-4 8-0-0".split()
CHINE_TOP_HEIGHTS = "5-9-4 5-3-6 4-11-6 4-7-0 4-3-4 3-11-5 3-10-0 4-0-0 4-2-0 4-5-4 4-8-0 4-9-0 4-10-0".split()
CHINE_BOTTOM_HEIGHTS = "5-4-0 4-11-4 4-5-4 4-0-2 3-8-3 3-4-0 3-2-5 3-4-4 3-7-4 3-10-0 4-0-0 4-1-0 4-2-6".split()
RABBET_HEIGHTS = "4-3-2 3-8-7 3-2-2 2-8-6 2-4-0 1-11-4 1-10-6 2-0-4 2-2-4 2-4-0 2-6-4 2-7-1 2-8-0 3-0-0 5-8-0".split()
SHEER_WIDTHS = "6-4-0 6-8-6 7-0-0 7-3-0 7-6-0 7-10-0 8-1-0 7-11-4 7-7-2 6-10-2 5-8-0 4-8-4 3-7-4 2-6-4 1-3-0".split()
CHINE_TOP_WIDTHS = "6-1-0 6-4-2 6-8-2 6-10-0 7-1-0 7-5-4 7-7-4 7-5-4 7-1-0 6-4-4 5-1-4 4-1-4 2-11-4".split()
CHINE_BOTTOM_WIDTHS = "5-9-6 5-11-6 6-2-0 6-5-0 6-8-2 7-0-2 7-1-2 7-0-0 6-6-2 5-11-0 4-9-0 2-7-4 2-6-0".split()
