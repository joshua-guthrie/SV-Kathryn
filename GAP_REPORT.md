# Kathryn — model gap review

## Latest checkpoint — 2026-11-13: M5 cabin fit-out

Current model: **841 valid parts**, 1:1/mm, app build 347 s, no warnings.
The M4 deck is a 237-board standard-lumber schedule with beam-centred butts,
provisional waterway and kingplank scarf. The M5 cabin increment adds 49
source-qualified fit-out members (sole, settees, lining, stove, table, lockers);
`check_m5_cabin.py` passes. M4 side planking/individual side lining and the
measured waterway remain open; the whole-vessel M5 review is not complete.
Review artifacts: `milestones/M5.md`, `checks/m5_cabin_acceptance.json`,
`renders/m5-cabin-fitout-close.png`, `renders/m5-whole-vessel-cutaway.png`.


## Latest user-directed review — stern remedy required; other milestones held

The user rejected the remaining stern appearance after the local rake/helm
correction and requested a complete illustrated review and detailed remedy
specification. **`STERN_REVIEW_AND_REMEDY_SPEC.md` is now the governing report.**

- Current captured model: 446 parts, 1:1, build OK; overall stern not accepted.
- Confirmed remaining issues: slab/quarter deck projection, unverified counter
  anchor/surface, segmented round rear rails instead of timber rails, missing
  helm front opening/hydraulic mechanism, and missing/placeholder stern fittings.
- Current model deck projection aft of rail centre grows from16.9 in at centre
  to32.0 in near quarter. Existing S04 guides show a provisional12–13-in counter
  offset; guide roles/datum/geometry condition must be confirmed before remedy.
- Report includes11 embedded arrowed images, locked-scale plan/profile overlays,
  source/photographic comparisons, priorities R0–R9, work orders and15 independent
  acceptance criteria. Assets/provenance: `renders/stern_review/`;
  measurements: `checks/stern_review_measurements.json`.
- **M4/M5 remain on hold.** Earlier passes below are historical/local geometry
  evidence and do not close the reopened complete stern review.

## Historical result — M3 frame increment

**439 valid single-solid parts, no warnings**, current in SOMA and
`output/model.step`; latest complete build **304.0 s**. Source/member details,
acceptance and qualified reconstructions: `milestones/M3.md`.

| Finding | Correction / evidence | State |
|---|---|---|
| S-F01: no complete inspectable hull-frame construction | Registered independent schedule; 154 frame pieces, primary tenons, uninletted companions, two continuous under-keelson floors and 78 limbers. 15 additional structural supports. | M3 complete against checks; inaccessible/ambiguous details explicitly inferred |
| M3-R01: numbering/age could be silently generalized | Plan/caption/scarf registration; literal stern-knee conflict preserved. 22 older-marked bottom records remain **possibly** original; side ages unresolved. 24 interpreted repair-pattern companions, not 24 independently dated repairs. | Resolved evidence organization; fine pairing/date refinement retained |
| M3-S01: frame 1 did not seat on steep actual bow cavity | Final-bay frame profile taken from actual cavity section. All bottom/head bearings and 9,955 distinct exterior samples pass. | Resolved |
| M3-C01: local clamps depended on the old hull-only support | Extended full pine runs, seated on side heads; separate forward oak reinforcement. Header/carlings/clamp/frame checks pass. | Resolved |
| M3-D01: first added stanchion cap duplicated a nearby header | Reused actual after-hatch fore header; only two extra cap beams. | Resolved |
| M3-B01: source-locating Samson post exposed an inherited aft bowsprit extension | S04 deck/profile heel at F52.770, profile check F52.804. Post keeps proper section and stem-knee mortise; spar/heel chock/cross-timber/headrail seats pass. One additional bearing timber. | Resolved local interface; inherited forward rig references remain for M5 review |

Fixed registered frame-4 and frame-13 shell guides give **1.538 / 1.733-in RMS**;
scale and F are held, only named local Z references fitted. Five board poses,
three steering poses, actual voids, rounded repair knees, hatch/cover/support,
companionway/door and exterior/machinery checks pass. Original source hashes and
drawing-package calibration/crop/link checks pass.

Inspection: `renders/m3-review.png`, `m3-frame-pairings.png`,
`m3-forepeak-headwork.png`, `m3-section-S06-V01.png`, `m3-section-S07-V01.png`
under `renders/`. Machine records: `checks/m3_acceptance.json`,
`checks/m3_section_comparison.json`.

**Remaining:** inaccessible cabin/aft planes and stock, some individual secondary
pairings/dates, fine timber/deck/panel joints and corrected/as-surveyed vertical
differences remain source-qualified. M4 is individual boards and complete deck
integration; M5 is fit-out and final fidelity, including full board stowage and
remaining inherited fine rig/fitting coordinates.

## Historical result — M2 complete, centreline structure

**269 valid parts, no warnings**, current in SOMA and `output/model.step`.
Latest full build: **379.7 s**, below the application's 600-second limit.
Full member evidence, acceptance and source limits: `milestones/M2.md`.

| Finding | Correction / evidence | State |
|---|---|---|
| S-C01: missing keelson/trunk and true centreboard passage | Two complementary oak scarf sections; eight individual 2 × 11.5-in pine courses, rails/ends and continuous shoe/keel/shell/keelson slot. 30 sampled passage columns, actual stock sections and 44 adjacent air samples pass. | M2 complete |
| M2-J01: temporary pad / intersecting centreline supports | Mortised keelson, separate iron hoop, faceted mast/chocks, oak partners and lapped carlings; sole/partition relief and actual seating checks pass. | Resolved |
| M2-T01: trial raised board fouled hatch/deck | -17-degree trial rejected; -15-degree displayed pose plus three intermediates clear actual structure. Full historic stowage is not certified. | Clearance state verified; source refinement retained |
| M2-P01: new build hit 600-s application limit | Smooth trunk lofts, adaptive keelson sections and targeted exact-classifier checks reduce cost; dense source comparison gives 0.0562-in maximum keelson-base approximation. Final complete build 379.7 s. | Resolved |
| M2-L01: inherited worm-shoe widening did not follow actual slot | Widening now spans the source-located slot; actual pivot-plane shoe section is 10 in. | Resolved |

`checks/m2_acceptance.json` and `checks/m2_source_comparison.json` record the
checks. M1 enclosure, companionway/door poses, hatch supports/cover removal,
exterior/machinery and -35/0/+35 steering regressions pass. Original source hashes
and drawing-package validation pass. Inspected actual mesh overview, longitudinal
cutaway, mast supports and calibrated source-profile overlay:
`renders/m2-review.png`, `renders/m2-source-profile-comparison.png`.

**Remaining:** M3 full hull-frame numbering/planes, original mortised and later
uninletted sister/replacement construction; M4 individual boards/lining/deck
joints; M5 historic fit-out. Inaccessible aft keelson, exact scarf/mortise/trunk-end
rakes and board stowage/pin/hoisting details remain explicit source uncertainties.
The forward keelson is **possibly original**; no invented member dates are assigned.

## Historical result — M1 accepted, continuous hollow enclosure

**241 valid parts, no warnings**, current in SOMA and `output/model.step`.
M0/M1 are complete; M2 is next. Full acceptance, review history and remaining
source questions are in `milestones/M1.md`.

| Finding | Correction / evidence | State |
|---|---|---|
| S-V01: isolated wells left most of the hull filled | One continuous cavity; planking material is 7.63% of the equivalent filled exterior envelope. 105 distributed air samples, four actual transverse sections and full cutaways pass. | M1 resolved |
| I-M02: inherited datum/arrangement did not follow the source ledger | Source line stations and three hatch centres migrated; mast axis intersects the source deck point. Cabin/helm/equipment references located from sheet 4; lesser attachments transfer by hull-station correspondence. | Named source-coordinate migration complete; fine fitting/frame identity refinement continues in M3/M5 |
| M1-D01: underside of sheer strake mistaken for actual deck edge | Calibrated source picks add the missing 12.5–16.1-in upper band and outward flare. Raw offsets remain underside references. Actual-model deck height/width checks pass. | Resolved after section-gap review |
| M1-S01: landing/mast depended on embedded filler | Two real sole bearer/foot assemblies, localized mast bearing and hollow stock boxing added. Contacts, enclosure and shaft clearance pass. | Resolved for M1 local supports |
| M1-C01: narrow cabin aperture left a false deck-level floor | Full cabin deck opening, perimeter framing and two thin compartment partitions added; cabin/hold/forepeak spaces are inspectable. | Resolved |

### Source comparison and acceptance

- Initial shell overlays exposed M1-D01. Correcting the separately labelled
  Top-of-Deck reference improved representative shell-guide RMS from 4.31 to
  **1.13 in** on 6a and from 2.45 to **0.88 in** on 7a. Scale is retained;
  representative plane/vertical registration is inferred, not a confirmed frame
  station. Data and datum differences: `checks/m1_section_comparison.json`.
- Source picks: `drawing_package/sheer_band_measurements.json` and
  `renders/m1-sheer-band-source.png`. Current maximum beam is about **16.736 ft**;
  transom top width **11.46 ft**, nominal deck-to-bottom centre depth **2.9 ft**.
  The earlier 1.8-ft transom figure described the lower/undersheer reference,
  not the complete corrected deck-edge face.
- Body F bounds **-1.800 to 50.733 ft** are distinct from the 50-ft recorded-length
  witnesses. Do not compress the whole projected body/appendages into that interval.
- Actual-solid checks: 144 normal-ray material samples, thin transom closure,
  floor/mast bearings, hollow stock box, full cabin aperture, hatch seating/removal,
  door/stair/landing paths and 0–90° door poses pass. Machine enclosure record:
  `checks/m1_acceptance.json`.
- Exterior/bow/spar/strake contacts, eight body keel-depth checks, 35 actual
  aft-keel sections and -35/0/+35 steering including the new boxing pass.
  Aft-keel chord deviation is 0.232 in, with no reverse hollow.
- Final build: **241 parts**, no warnings (382.4 s). Open-interior, longitudinal,
  source-section and refreshed assembly/access views inspected.
- The equipment integration review found the inherited engine-cover length
  intersecting migrated clutch controls. Its source-plan envelope is about
  3.33 ft long; corrected hollow housing and lid clear all controls. The new
  persistent machinery contact/clearance regression and prior detail check pass.

Main review: `renders/m1-review.png`. In SOMA hide `Deck/Planking` and
`Deck/Cabin/Roofs`, plus covers/equipment as useful, retaining the planking and
interior groups. Normal STEP still contains the complete assembly.

### Remaining milestone gaps

M2 must complete the keelson, real centreboard slot/trunk and centreline joints.
M3 must establish actual hull-frame numbering/planes and model the repair members;
the source-section vertical/keel datum differences are preserved for that work.
M4/M5 cover individual boards, detailed partitions/lining and historic fit-out.
The continuous skin/partition envelopes and local bearing dimensions are not a
claim that those later member schedules are already complete.

## Current accepted goal — milestone roadmap

The user clarified that the boat still appears mostly solid and that the goal
is to inspect the **entire interior** accurately, especially following the
construction sections on sheets 6a/7a. The comprehensive plan is approved;
outcomes are called **milestones**. The user confirmed **include repairs** and
**accurate, inspectable historic CAD model**, and requested an initial milestone
to make the scanned references more useful for AI interpretation.

`INTERIOR_SPEC.md` is the governing specification. M0 prepares indexed lossless
views, searchable/checked notes and tables, calibrated coordinates and useful
checked vector/point traces. M1–M5 then cover the continuous hollow enclosure,
centreline structure, frames/repair members, boards/deck integration, and fit-out/
final review. **M0–M3 are complete**; M4/M5 remain. The current geometry is
the 439-part hollow enclosure with individual centreline/frame/repair structure.

| ID | Gap against the specification | Milestone |
|---|---|---|
| S-D01 | Indexed native views/tiles, searchable OCR, checked notes/table and calibration/trace demonstrations now form the reference package. | Resolved in M0 |
| I-M02 | Source data and principal hull/hatch/mast coordinates have been migrated; fine member/fitting identification continues in its relevant milestone. | M0/M1 principal migration complete |
| S-V01 | Continuous hollow enclosure replaces the broad filled regions; material, space, support and section checks pass. | M1 complete |
| S-C01 | Separate keelson/scarf, hollow trunk, real board passage and integrated mast supports pass; fine historical joint/stowage uncertainties are explicit. | M2 complete |
| S-F01 | Registered frame construction, qualified older bottoms and repair-pattern companions, real mortises/underpasses and supported clamps pass. Hidden planes, some pairings and fine joints remain explicit reconstruction limits. | M3 complete against checks |
| S-B01 | Deck planking is complete; individual side planking/lining and measured waterway remain open. | M4 |
| S-A01 | M5 cabin fit-out, inspection set, evidence list and whole-vessel cutaway complete; M4 side-board/waterway gaps are tracked under S-B01. | M5 complete |

Each milestone closes by its documented acceptance criteria and gap analysis;
multiple modification/review cycles may be needed within a milestone.

## M0 acceptance — AI-ready drawings and calibrated reference data

- **Package:** `drawing_package/index.html` (local searchable contact sheet),
  `INDEX.md`, manifest, per-view pages, 51 lossless native views and 498 native
  tiles covering all eight main-vessel sheets.
- **Text/data:** 4,623 OCR words with confidence and original pixel bounds;
  58 separate visually checked construction records, including all sheet-6/7
  note keys; complete 15-station/eight-row offset table. Raw OCR remains separate.
- **Scale:** six ruler calibrations agree with printed imperial scale/DPI within
  0.13%; max fit residual below 0.018 ft. Sheet 6 has a genuine conflicting
  metric 1:32 caption; the 3/4-inch imperial bar supports 1:16. This is retained
  as a source inconsistency, not silently normalized.
- **Registration:** canonical source convention declared from sheet 2's 50-ft
  recorded-length dimension. Homologous sheet-4/5 deck features fit within
  0.102 ft (declared pick uncertainty ±0.20 ft). The old CAD's hatch/mast placement
  deltas are listed for M1; no geometry was repositioned in M0.
- **Section evidence:** complete frame-set-4 and cabin-hatch demonstrations on
  sheets 6a/7a, with nine open boundary guides, calibrated local X/Z points,
  SVG/PNG source overlays, member/repair regions and linked checked note keys.
- **Validation:** eight original SHA-256 hashes unchanged; native crop/tile pixel
  samples and coordinate transforms verified; OCR/text search, source-table
  distinctions, scales, registration and section-guide data pass
  `python checks/check_drawing_package.py`. Machine result: `validation.json`.

Full acceptance and source-interpretation decisions are recorded in
`drawing_package/ACCEPTANCE.md`. M0's checked sources specifically distinguish
rounded replacement knees from grown knees, possible original frames from
certain originals, and projected fittings from cut-plane material. Sheet 5's
first-frame wording (*stern knee*) is preserved for the separate frame-number
interpretation in M3. Source limitations remain evidence questions, not invented
exact timber dimensions.

## Current resumed result — hatch/local-framing increment

The first board-level opening-support increment is built: **235 valid parts**,
no warnings, current in SOMA and `output/model.step`. The supplied Chapelle book
has been identified and its relevant construction sections reviewed. Kathryn's
HAER descriptive data is saved locally and its construction/alteration discussion
has been reviewed. Full member evidence and measurements are in
`INTERIOR_RECONSTRUCTION.md`.

| ID | Correction / finding | State |
|---|---|---|
| I-H01 | Replaced the three combined hatch solids with white-oak coamings, 15 separate removable cover boards and six retaining cleats. Opened the deck and local hull passages to the preserved bottom surface. | Resolved for the local openings; seating/removal/passage checks pass. |
| I-F01 | Added 35 individually registered support timbers: cambered headers/half beams, paired carlings, local clamps and companionway roof supports. Main/forepeak share forebody clamps. | Local support increment verified; complete boat framing schedule remains next-stage work. |
| I-M01 | Calibrated original sheet-4 ruler/footprints; 150.75 px/ft agrees within 0.5% with the printed 3/8-in scale at 400 dpi. Main hatch widened to a measured approximately 6.5 × 5.5-ft footprint; nearly flush forepeak follows vessel-specific alteration history. | Footprint calibration complete; JSON/pick coordinates retained. |
| I-M02 | The old normalized hull/mast/deck arrangement is not fully registered to raw scaled drawing positions. Current hatch centres are inherited reconstruction coordinates, not newly measured stations. | Open: resolve common longitudinal registration before the full interior member schedule. |
| I-R01 | Found `Reference Material/Migrations of an American Boat Type.pdf`; reviewed its relevant sharpie construction/development discussion and Kathryn HAER pp. 2–4. Kathryn has a fully framed fore-and-aft bottom, three narrow chine planks, no chine log, original inletted frames and later uninletted sisters. | Initial research complete; use these vessel-specific distinctions for subsequent framing. |
| I-B01 | Individual hatch cover boards and 35 support members are now inspectable components. | First board-level increment complete; full frames, lining, floors, bulkheads and furnishings remain staged work. |

Verification: hatch passage/cover removal, timber contacts/sections, roof support
seating, 75 normal-ray bottom-material samples and mast clearance pass. The
companionway checks include the new framing and pass. Prior detail, bow/spar/
strake, chine/transom, eight body-keel sections, 35 aft-keel sections and rudder
clearances at -35/0/+35° all pass. The first comprehensive hatch-check command
hit its execution limit; bounding-box rejection/compound cover checks reduced
redundant booleans, and the complete check then passed.

Inspected `renders/hatch-review.png`, `hatch-source-comparison.png`,
`hatch-scale-measurements.png` and the detailed closed/open/section/framing
views. Closed covers are the normal assembly; removed-cover/cutaway/isolated
framing images are inspection views. Overall/stern/side and companionway views
are refreshed.

## Previous goal / overnight checkpoint — 2026-11-07

The user has expanded the goal to a **board-level interior reconstruction**,
authorizing dimensions measured from the scaled drawings and asking that
skipjack construction references and a supplied book inform the work. Tonight's
stopping point is source review, before the hatch/framing geometry changes.
The verified model remains the **179-part** companionway checkpoint below.

| ID | Next-stage finding / need | State |
|---|---|---|
| I-H01 | All three hatches currently combine their cover/coaming in one solid, with no matching deck/below-deck passage. | Source review started; geometry correction pending. |
| I-F01 | Opening support beams, longitudinal framing and cabin/companionway support members need individual representation and contact checks. | Readable structural plan and timber notes retained; calibrated placement and implementation pending. |
| I-M01 | Transfer unlabelled geometry from scaled drawings using view-specific calibration and known dimensional references. | Measurement policy saved; new interior measurement ledger/calibration pending. |
| I-R01 | Consult the supplied book and suitable historical construction references. | E. C. Collier descriptive report reviewed; online museum overview reviewed and vessel-specific PDF leads located. The separate book has not been identified. |
| I-B01 | Model interior structure, lining/floors/bulkheads and furnishings as identifiable timbers/boards. | Saved as phased project goal; implementation pending. |

Details, citations, measurement rules and the exact resume point are in
`INTERIOR_RECONSTRUCTION.md` and `PASSDOWN.md`. Hatch source crops are
`renders/hatch-source-structural-plan.png`, `hatch-source-beam-notes.png`,
`hatch-source-deck-notes.png`, `hatch-source-deck-plan.png`,
`hatch-source-inboard-profile.png` and `hatch-source-cabin-roof-support.png`.
These are evidence crops, not completed hatch/CAD comparisons.

## Completed continuation — 2026-11-07, companionway access

The user authorized continued work after the completed six-pass cycle and
identified the door stranded on the upper box. That was a functional gap missed
by the exterior-only review: the door began at the main-roof level, while the
two cabin bodies, roof, deck and filled hull blocked descent.

Readable evidence: sheet 4's aft door swings in plan and steep companion steps
in the inboard profile; sheet 7's section at the cabin hatch shows the roof
opening. Original-sheet crops are retained as
`renders/kathryn-access-source-profile.png` and `kathryn-access-source-plan.png`.

| ID | Finding | Correction / verification | Status |
|---|---|---|---|
| A-C01 | The upper-only door required climbing onto the lower roof; the lower aft wall and roof lip remained closed. | Replaced it with two full-height glazed leaves, continuous jambs/lintel and a low sill. One shared aperture cuts both aft walls and the overhanging roof lip. A separate actual-solid doorway probe passes. | Resolved; unlabelled dimensions reconstructed |
| A-C02 | The roof/deck/filled hull contained no connected access passage or stairs. | Hollowed the two cabin enclosures, opened the main roof and deck, and cut a local below-deck well. Added three treads on two stringers, joined to the sill and landing. Passage, support contacts and landing clearance pass. | Resolved for the local access arrangement |
| A-C03 | New access geometry must preserve the bottom planking and avoid obstructing the doors/helm. | The well leaves at least 2.04 in of normal bottom material at the sampled sections, including the worst aft corners. Both leaves clear the enclosure, deck, helm and each other at 0–90° in 15° increments. | Verified |

### Dimensions and assumptions

The exterior cabin/raised-house envelope supplies the doorway head. The clear
opening is **19.8 in wide × 45.27 in high**, with its sill **2.16 in above the
local deck**; this is a low, stooping companionway. The landing is **27 in below
deck**, reached by three treads and four equal **7.29-in risers**, with **4.8-in
going**. The well is 2.2 ft wide. These small access dimensions, wall/hinge
details and tread count are proportional reconstruction choices, not labelled
historical measurements. The exterior drawing proportions and estimated
2-inch hull-strake constraint guide the reconstruction. Door sweep checks
verify the static geometry, not manufacture-ready scale hinge tolerances.

### Verified result

- `python -m soma build`: **179 valid single-solid parts**, no warnings;
  `output/model.step` and the live SOMA geometry are current at 1:32.
- `python checks/check_companionway.py`: continuous doorway and roof/deck
  passage, low sill, supported treads/stringers/landing, preserved bottom
  material, embedded glazing and door sweep all pass.
- Existing pass-6 detail checks, source chine/transom checks, bow/spar/strake
  attachments, eight body-keel sections, 35 aft-keel sections and rudder
  clearances at -35/0/+35° all pass.
- Inspected normal closed, open and cutaway views against the source. The
  default assembly has closed doors; open/cutaway pictures are inspection
  views. Overall assembly, profile and stern views are refreshed.
- Before/after overview: `renders/kathryn-companionway-review.png`.
  Source comparison: `renders/kathryn-companionway-source-comparison.png`.
  Detailed evidence: `renders/kathryn-cabin-detail.png`,
  `kathryn-companionway-open.png`, `kathryn-companionway-cutaway.png`.
  Reproduce the access views with `python checks/render_companionway.py`.

The local access well and descent are now represented; the broader internal
fit-out and timber/fastening schedules remain the separate construction-plan
work described below. Original TIFFs have not been modified.

## Previous review — 2026-11-06, maximum six passes

### Final result — six-pass cycle complete

Pass 5 completed the independent drawing audit. Pass 6 corrected its five
supported exterior findings and passed the final integration checks. The
current assembly has **163 valid parts**, builds without warnings, and is
current in SOMA and `output/model.step`. The six-pass limit is now reached.
The drawings needed for this work were readable throughout.

### Pass 5 audit / pass 6 corrections

The user authorized the final independent audit and supported corrections.
Orthographic side/plan comparisons are saved in
`renders/pass5-side-comparison.png` and `renders/pass5-plan-comparison.png`;
the earlier source/CAD transom comparison supplies the end-view sizing check.
The profile/plan images are normalized review views using the existing hull
datum, not a claim that every unlabelled arrangement dimension is printed.
Enlarged original sheets 1, 4 and 7 provide the detail evidence below and are readable.

| ID | Source / finding | Pass 6 correction | Status |
|---|---|---|---|
| P5-L01 | Sheet 4 item 10 is above centreline in the bow-right plan, but the model hatch appeared below. With bow -Y and up +Z, physical port is +X; the old side-label convention was reversed. | Added explicit `PORT_SIDE=1`, moved the hatch to the drawing-side position and applied consistent port/starboard names to symmetric parts. Final plan and actual registered hatch bbox agree. | Resolved |
| P5-C01 | Sheet 4's raised companionway front is raked, and its side glazing follows the sloped outline; the model was a vertical box with small rectangular panes. | Added a traced 0.75-ft roof-level front setback and shaped side openings with inset panes. Actual sections verify the rake and pane/frame seating. | Resolved as traced exterior |
| P5-C02 | Sheet 7's cabin section shows shallow transverse camber in both roofs; the model roofs were flat. | Added approximately 0.12-ft main-roof and 0.10-ft companionway-roof camber; wall/roof and upper-body/lower-roof contacts have positive overlap. | Resolved as traced exterior |
| P5-E01 | Sheet 7's winder has shouldered frames, top/cross bracing, axle bearings, perforated wheels and brake/clutch controls. The model used two pointed A-frames and plain drums. | Added the shouldered/cross-braced cage, perforated end plates, four bored bearings, two slotted drive wheels, two brake/lever assemblies and two clutch controls. Axle centres are shared; bearings, frame/skids and engine/control clearances pass. | Exterior gap resolved; manufacturing detail approximate |
| P5-B01 | Sheet 1's enlarged bow shows compact lettering with connected scrolling vine relief. Model letters were spread across too much of the board and the foliage was sparse/disconnected visually. | Compacted the name to a band under 3.3 ft long and added connected scrolling vine/leaf relief on both faces. Both names read normally and all relief/letters seat into the single board. | Exterior gap resolved; fine cuts approximate |

Exact machinery manufacturing dimensions, tooth profiles, hidden drivetrain and
hydraulic internals are not specified by these detail sketches. The corrections
are exterior reconstructions; they do not close the separate production-design
work of framing schedules, plank spiling, joints, fasteners and hardware sizing.

### Pass 6 final evidence

- **Build:** 163 parts, no warnings, all registered parts valid single solids.
  The exported assembly manifest includes all ten new winder components and
  places the forepeak hatch on the source-plan side.
- **New detail checks:** passed physical side handedness; actual low/high
  companionway sections; pane/frame overlap; roof camber from CAD sections;
  roof/wall contacts; bearing bores clear of the axles/wheels; drive wheels
  join the axles; brake bases meet the skids; controls clear the engine cover;
  compact names and connected vine relief on both sides.
- **Core regression:** source chine residuals and monotonicity, transom size,
  bow attachments, mast enclosure, rubbing-strake fit, eight body keel-depth
  sections, 35 aft-keel sections and -35/0/+35 rudder clearances all pass.
  The combined verification command reached its execution limit after the
  detail/body checks; the remaining aft-keel and steering checks were then run
  separately and passed. No intended check remains pending.
- **Visual comparison:** final source/model plan/profile images are
  `renders/pass6-plan-comparison.png` and `renders/pass6-side-comparison.png`.
  Pass-5 baseline comparisons are retained for before/after review. The prior
  transom source/CAD comparison remains the end-view sizing reference.
- **Detail views:** `renders/kathryn-cabin-detail.png`,
  `renders/kathryn-winder-detail.png`, `renders/kathryn-winder-isolated.png`,
  and `renders/kathryn-bow-carving.png`. The isolated winder view hides the
  engine cover only for inspection; the complete assembly retains the cover.

### Work still required for actual construction plans

The supported exterior audit findings are addressed. The current model remains
an exterior/reference reconstruction, not a complete set of building plans.
Production work still includes the internal frame/keelson schedule, full plank
spiling and cutting templates, rabbets/scarfs/joints, fastening patterns, and
dimensioned hardware/steering/drivetrain design. Irregular original timber sizes,
estimated strake thickness and unprinted machine/steel-rudder details require
further measurements or explicit design decisions. These are documented limits,
not dimensions silently invented during the final pass.

### Earlier completed passes

**Pass-4 result:** pass **4 of the six-pass cycle** corrected the aft-keel
indentation in markup `20261106-1840`. The keel/shoe now runs continuously from
the rudder heel to a tangent body join. The build passes at 153 parts, and
35 actual CAD sections confirm that the marked dip/hump is gone. The earlier
three-pass close-out remains historical, superseded for this finding.

**Goal:** review the drawings, correct supported gaps, compare the resulting
model against the drawings and construction again, and stop when the listed
gaps are resolved without regressions or after six passes. Stop and notify the
user if drawing evidence needed for a correction cannot be read. The original
400-dpi TIFFs, including their lumber notes, offsets and outlines, are readable.

Current trigger: `markup-20261106-1840.png`, following the earlier bow/chine,
rudder, transom and lumber-construction review. A valid solid alone is not a
drawing-fidelity acceptance test; this pass specifically checks the complete
longitudinal keel silhouette.

| ID | Evidence / discrepancy | Acceptance criterion | Status |
|---|---|---|---|
| R3-H01 | The old blend moved measured chine widths inward into an artificial V section, creating a shoulder and reverse-looking plank run. | Replaced it with bounded fair longitudinal runs fitted to the offsets. Plan widths decrease smoothly without hooking outward again. | Resolved |
| R3-H02 | Missing forward chine offsets were replaced by arbitrary fractions of the deck section, turning the chine upward toward the stem head. | Upper/lower chine runs now meet the lower stem at approximately 46.99 / 46.60 ft forward. Forward topside/bottom battens terminate progressively at the stem instead of being dragged up to the deck-height endpoint. | Resolved |
| R3-R01 | The previous rudder used approximate head-relative dimensions and was too large in the complete model. | Blade height reduced from 4.1 to 3.5 ft, with proportional head-drop/aft offsets (about 27% nominal planform-area reduction). Shaft head and 25-degree axis retained; blade, bearings, deadwood and clearance reviewed together. The size remains a proportional trace, not a printed dimension. | Resolved as approximate outline reconstruction |
| R3-T01 | Width compared closely, but the model's 1.35-ft centre face depth was shallow compared with the body-plan trace (about 1.8 ft, railwork excluded). | Retained 11.3-ft width; lowered the centre bottom to 4.8 ft, giving about 1.8-ft nominal face depth. Source/CAD comparison and stern regressions pass. | Resolved |
| R3-C01 | The prior review did not explicitly connect the hull surface to the recorded timber construction. | Recorded the actual timber notes below; reviewed continuous fore/aft bottom and topside batten runs, progressive stem termination and chine bend behaviour. | Construction-envelope review complete |
| R4-K01 | The aft-depth blend produced a dip near the heel, then an upward hump before falling back to the main keel. This indentation is absent from the drawing. | Replaced the blended depth with a directly faired, monotone heel-to-body run tangent to the body keel at station 5. Oak/shoe thicknesses retained; supporting deadwood follows the corrected run. Actual sections and profile comparison pass. | Resolved in pass 4 |

### Recorded construction constraints

| Component | Drawing evidence |
|---|---|
| Hull strakes | Sheet 7 note 10: estimated 2-inch thickness, highly irregular widths; mostly oak below the chine, pine above; oak chine. Sheet 1 explicitly describes fore-and-aft bottom planking and a rounded chine. |
| Frames | Sheets 5/6: oak, varying old/new members; generally about 5.5-inch square in the exposed frame sets. |
| Deck planks | Sheet 5 note 8: mainly fir/pine with oak replacements; 1.75 inches thick, commonly 3.5–4 inches wide, some inboard members 5–7 inches. |
| Ceiling | Sheet 6 note 1: approximately 1.75-inch pine, about 9-inch width. This is NOT a prescribed hull-strake width. |
| Transom | Sheet 5 note 27: oak; fore/aft frames average 3.75 x 4 inches, diagonal braces 6.75 x 2 inches, 8 x 6-inch side moulding rounded at the chine. |
| Keel/shoe | Sheets 6/7: 8-inch average keel width; 3 x 8-inch worm shoe, up to 10 inches at the centreboard. |
| Rudder | Sheet 4 item 23 identifies stainless steel; its complete fabrication thickness is not labelled. |

The construction check concerns a fair, plank-compatible hull envelope and
the recorded interfaces. This exterior assembly does not contain a complete
frame/fastener schedule or a shop-ready spiling/cutting list.

### Measurements and source agreement

- New fair forebody curves are fitted directly to the measured upper/lower
  chine runs from maximum breadth. The upper-curve width residual is at most
  about 0.6 inch at the sampled stations; the lower curve follows the surrounding
  offsets within about 1.3 inches while separately identifying the already-noted
  anomalous station 8.5 value. The source transcription stays intact.
- The upper/lower chine curves meet the rabbet at about 46.99 / 46.60 ft
  forward, not at the deck-height stem endpoint at 50 ft. Fitted plan bend
  radii exceed 28 ft. Topsides and bottom runs are shown in the construction view.
- Transom half-breadth traced from the body/half-breadth plan is approximately
  5.7 ft: about 11.4 ft overall, versus the model's 11.3 ft. No unsupported
  widening was indicated. The centre face depth was corrected separately.
- Rudder dimensions are not printed. The corrected blade size is a traced
  proportional reconstruction, not a new claim of an explicitly dimensioned
  historical part. The adopted 3.5-ft blade height and both outline offsets are
  scaled together about the existing shaft head. The reduced blade remains
  clear of the counter as it turns.

### Current pass log

| Pass | Changes | Drawing / construction review | Outcome |
|---|---|---|---|
| 1 of 6 | Removed the transverse collapse; fitted longitudinal chine runs and terminated them at the lower stem. Reduced the rudder blade from 4.1 to 3.5 ft high, scaling its outline consistently about the fixed shaft head. | 153-part build passed. Source residuals, monotonic runs, >28-ft plan bend radii, bow/keel attachments and -35/0/+35 steering clearances pass. Plank-run and profile views inspected. | Hull/rudder correction accepted for integration; separate transom review found shallow face. |
| 2 of 6 | Retained transom width and changed its centre bottom from 5.25 to 4.8 ft (nominal face depth 1.8 ft). | 153-part build passed. Rechecked actual CAD transom dimensions, source-run residuals, plank runs, stern stock passage, all attachments and steering clearances. | Corrected; no geometry regression found. |
| 3 of 6 | Independent review; no additional model change. | Compared bow/underside/plan/profile, source chine plot, steel-rudder/stock cutaway, transom source/CAD plot and fore/aft top/bottom battens with the original sheets and timber notes. | Closed at that stage; later markup reopened the aft-keel finding. |
| 4 of 6 | Corrected the aft-keel indentation in `20261106-1840`. Replaced the 12.5-ft cutoff with a direct heel-to-station-5 run joining the body at 25.625 ft. | 153-part build passes. 35 actual shoe sections rise without reverse slope; heel and body height/tangent match, contacts join, and -35/0/+35 steering clearances pass. Compared the complete keel silhouette with sheet 4. | Marked hollow removed; 4 passes used. |
| 5 of 6 | Independent complete-model drawing audit; no geometry change. | Matched plan/profile, transom end reference and enlarged sheets 1/4/7 exposed the mirrored hatch, side convention, cabin roof/front shapes, winder detail and carving/letter spacing. | Five supported exterior findings recorded for pass 6. |
| 6 of 6 | Coordinated correction of the five pass-5 findings. | 163-part build, new detail/contact/clearance checks, core hull/keel/steering regressions and final reference/detail views inspected. | Supported exterior findings corrected; construction-plan and unprinted-detail limits recorded. Six-pass cycle closed. |

### Passes 1–4 acceptance evidence — history

- `python -m soma build`: 163 parts, no warnings; one valid solid per part.
- **Pass 4 keel guard:** 35 actual CAD sections show no dip, hump or reverse
  slope between heel and body. The direct cubic run deviates at most 0.39 inch
  from its heel/body straight chord and matches the body tangent. A monotonicity
  assertion is retained in the model. The oak and shoe keep their existing
  thicknesses; the deadwood is the filling above the fair run.
- The nominal 9-inch hull-to-shoe projection applies from station 5
  (25.625 ft forward) into the main body, verified at eight sections. Aft of
  that join the keel follows the continuous heel run shown in the profile;
  the previous 12.5-ft cutoff is superseded.
- Source-run checks: maximum upper width/height residuals about 0.56/0.57 inch;
  lower width/height residuals about 1.34/0.34 inches, with station 8.5 explicitly
  separated as the retained measured outlier. Fair plan radii approximately
  28.23 / 28.46 ft; no forward width reversals.
- Original source offsets remain intact. The chine endpoint elevations and the
  transom/rudder outline sizes are traced reconstruction choices, identified as
  approximate rather than printed dimensions.
- Regression checks pass for keel/shoe depth at eight sections, mast heel
  enclosure, rubbing-strake contact, cross-bearer/walking-board contact,
  boom/gooseneck/crutch attachment, hatch/traveller/post placement and rudder
  motion at -35, 0 and +35 degrees.
- Geometry/output comparisons: `renders/kathryn-chine-comparison.png`,
  `renders/kathryn-planking-review.png`, `renders/kathryn-transom-comparison.png`,
  `renders/kathryn-bow-entry.png`, `renders/kathryn-hull-profile.png`, and
  `renders/kathryn-rudder-cutaway.png`.
- Aft keel evidence: `renders/kathryn-aft-keel-check.png` compares the old and
  corrected runs; `renders/kathryn-stern.png` and `kathryn-hull-profile.png`
  show the updated assembly silhouette.
- The gold topside and blue bottom lines in the planking-review image are
  illustrative longitudinal battens. Their spacing is not a prescribed strake
  width or cutting list; the dense transverse CAD loft edges are not plank joints.
- Remaining source limits: irregular hull-strake widths, exact unlabelled steel
  rudder fabrication details and fine carving cuts are not fully specified in
  the supplied sheets. These do not prevent reading/comparing the current
  exterior geometry; a full production timber/fastener schedule remains outside
  this exterior assembly.

## Earlier reviews — history

Review date: 2026-11-05. Baseline: 117-part exterior model at 1:32.
Iteration 1 closed at 151 parts. Iteration 2, prompted by markup
`20261105-2131` and the keel-depth feedback, is now built and checked at
**153 parts**. Its five findings below supersede the first hull/keel close-out.

## Iteration 2 — gap analysis and corrections

| ID | Priority | Evidence / gap | Required correction | Status |
|---|---|---|---|---|
| R2-B01 | High | The chine-to-flat-entry change was concentrated in only 4.375 ft; the latest markup still showed a shoulder. | The wider transverse blend still distorted the plank run; it was removed and replaced by R3-H01/R3-H02. | Superseded by current review |
| R2-K01 | High | The part called Keel filled to an independent low profile, creating an excessive external fin along the body. Sheets 6/7 show a keel adjacent to the rabbet and a separate 3-inch by 8-inch worm shoe. | The shallow main-body members are retained. The early 12.5-ft aft cutoff caused a hollow and is superseded by the direct heel run in R4-K01. | Main-body fix retained; aft run revised in pass 4 |
| R2-D01 | Medium | Sheet 4 item 10 places the small forepeak hatch to port and aft of the mast, not on the centreline. | Moved its centre to 2.75 ft port of centreline and 35.2 ft forward, following the plan proportions. | Resolved |
| R2-D02 | Medium | Sheet 4 item 14's jib-sheet traveller was missing from the foredeck. | Added the athwartship bar with two joined deck feet ahead of the mast. | Resolved |
| R2-D03 | Medium | Sheets 5/6 specify a Samson post tapering from a 5-inch-square foot to a 14-inch by 5-inch head; the model used an abrupt T cap. | Replaced the step with a tapered timber using those foot/head sizes. | Resolved |

The second review also rechecked the spar axes/attachments, cabin and companionway,
three hatches, rails, bow headwork, chain attachment points, winder/rollers and
stern steering arrangement against sheets 3–7. Existing simplified machinery,
hidden framing and omitted rope tackle remain the documented exterior-model scope.

**Keel evidence:** sheet 6 note 7 / sheet 7 note 11 identify the oak keel's
average width as 8 inches; sheet 6/7 note 19 gives the worm shoe as 3 by 8 inches
(approximately 10 inches wide at the centreboard). The oak's approximately
6-inch external moulding is read from the section, not an explicit depth label.
The internal 14-inch-wide keelson is not an external fin.

### Full-review coverage

| Assembly | Review result |
|---|---|
| Hull lines, chine and stem | Revisited sheet 2 plus the latest markup; longer blend implemented, flat forward sections retained, envelope/solid checks pass. |
| Keel, worm shoe and stern deadwood | Rebuilt against sheets 6/7; actual CAD sections verify shallow body projection. |
| Rudder and wheel box | Accepted stock axis retained; clearance regression includes the new shoe and passes at -35/0/+35 degrees. |
| Mast, boom, bowsprit and supports | Mast heel enclosure and the gooseneck/crutch/board support contacts rechecked and pass. |
| Bow carving, headrails and chains | Single centreline board retained; letters and both reliefs attach; shared chain attachment coordinates retained. |
| Cabin, companionway, hatches and helm | Exterior arrangement rechecked against sheet 4; forepeak hatch placement corrected. |
| Foredeck fittings | Added the missing traveller and corrected the recorded Samson-post taper. |
| Rails and rubbing strakes | Surface fit checked again on both sides after the wider hull blend. |
| Winder, rollers and engine cover | Rechecked against sheets 4/7; existing simplified exterior representation retained, without inventing hidden machinery. |

### Keel projection comparison

The old free-profile keel projected approximately 29.8 inches below the rabbet
at 12.5 ft forward, 17.4 inches at 21.25 ft, and 15.1 inches at 30 ft. The
revised keel plus shoe projects **9 inches at all three sections**. That limit
applies to the main body; the separate aft deadwood connects the rudder heel,
and the forefoot tapers into the stem.

## References and review method

- HAER MD-117 sheets 1–8, with sheet 1's enlarged decorated bow, sheet 2's
  lines/offsets, sheets 3/4's bow profiles and plan, and sheet 7's equipment.
- User references `photos/bow details.png`, `photos/rudder detail 3.png` and
  the supplied vessel photographs, especially the dockside bow photograph
  `photos/21440483420_4ec676fab5_z.jpg`.
- Checked the current CAD builders and SOMA mesh against the exterior silhouette,
  placement, attachment and visibility of the depicted components.
- The accepted wheel-box/rudder alignment is the stern reference for this review.
- Incorporated bow feedback in markups `2048`, `2049`, `2051` and `2102` on
  2026-11-05: flat entry with a smooth transition, one centreline decorated
  board below the bowsprit, and an enclosed mast heel.

## Iteration 1 findings — history

| ID | Priority | Finding | Correction | Status |
|---|---|---|---|---|
| B01 | High | Blunt stem face, hollow-looking entry and a visible shoulder in the transition. | Stem correction retained; the blend and keel treatment were revised further in R2-B01/R2-K01. | Superseded by iteration 2 |
| B02 | High | Decorative work was first represented by tiny vertical strips, then incorrectly separated into two projecting boards. | One 0.16-ft-thick centreline board directly under the bowsprit, with KATHRYN readable on both faces, contrasting borders, relief foliage and scrolls. Lettering begins forward of the cutwater so the stem does not hide it. | Resolved |
| B03 | High | Triangular headrails and cross-bearers absent. | Added converging port/starboard headrails, knees, three cross-bearers and bowsprit heel/stem-head fittings. | Resolved |
| B04 | High | Bow chains were plain cylinders with arbitrary attachment points. | Four alternating-link chains: two bobstays and two side stays. Added stem straps, side chainplates, eyes and shared bowsprit collars. | Resolved |
| B05 | Medium | Bowsprit heel and walking-board supports independently positioned. | One shared bowsprit axis and deck datum now drive the heel saddle, walking boards, cross-bearers and bands. | Resolved |
| M01 | Medium | Boom's fixed front coordinate did not follow the revised mast rake. | Attachment follows the mast at boom height through a gooseneck collar/pin; the aft crutch now meets the deck and boom underside. | Resolved |
| M02 | Medium | Rubbing strakes floated outside the narrowing topsides. | Inner edges follow the actual topside section, overlap the hull and taper into the stem. | Resolved |
| M03 | High | The mast heel protruded below the hull near the mast step. | Trimmed only the buried heel inside the hull, retaining the accepted mast axis, rake and head position. | Resolved |

### Bow-entry interpretation

The original sheet 2 cell at station 8.5 reads **2-7-4** and remains unchanged
in `CHINE_BOTTOM_WIDTHS` and `SOURCE_SECTIONS`. The current review fits fair
longitudinal runs, giving that isolated lower-curve hollow a separately stated
low weight. The previous transverse V-blending method is superseded. This is
an explicit reconstruction choice, not a silent source-table edit.

## Reference limits and deliberately omitted work

- Trailboard lettering and the major floral/scroll motifs are identifiable; the
  supplied images do not resolve every carving cut. Relief depth and the fine
  motif shapes are visual approximations, documented in `NOTES.md`.
- Photographs show different paint/maintenance states. The current overall
  hull palette remains the model's chosen state. The nameboard uses a dark
  red ground and warm ivory relief; exact paint shades are assumed.
- The chain links have small fused contact patches so each static chain is one
  valid registered solid. Their link section/contact detail is simplified.
- Sails and general rope/wire rigging remain excluded by the user's brief.
  The explicitly requested bow chains are included. The jib club therefore
  remains in its depicted sail-plan position without its omitted rope tackle.
- Internal framing, hidden hydraulic internals, the pushboat and manufacturing
  detail remain outside the established exterior-model scope. Cabin and dredging
  equipment are simplified exterior representations, as previously documented.
- The longitudinal station reconstruction remains approximate. The station 8.5
  fair-entry override is documented explicitly above.

## Verification and close-out

- **Build:** `python -m soma build` passed with 153 parts, no warnings; every
  registered part passes the existing one-valid-solid assertion.
- **Keel sections:** actual CAD-plane intersections at eight stations from
  12.5 to 43.125 ft verify 9-inch body projection, including the 3-inch shoe.
  The keel/shoe and keel/deadwood have positive joining overlap; aft deadwood
  is confined to the specified stern region. The registered assembly includes
  the separate worm shoe, not just the helper geometry.
- **Bow:** verified the single board's centreline symmetry/thickness; relief and
  all 14 letters intersect the board; the board seats into the bowsprit.
- **Entry:** flat-section collinearity checks pass; original station 8.5 source
  measurement remains intact. Inspected the final low bow-entry, side, plan and
  three-quarter renders.
- **Attachments:** each cross-bearer meets the bowsprit and both walking boards;
  boom/gooseneck and crutch/deck contacts have positive overlap.
- **Hull fit:** buried mast heel has no exposed volume below the local deck;
  rubbing-strake overlap was checked along both sides at seven positions.
- **Stern regression:** rudder + shaft still clear the hull, deck, wheel box,
  keel, worm shoe, sternpost and bearings at -35, 0 and +35 degrees.
- **Foredeck:** checked the hatch's actual CAD centre, the traveller's deck
  contact, and the Samson post's 5-inch foot / 14-inch head geometry.
- Current assembly: `output/model.step`. Review images:
  `renders/kathryn-bow-port.png`, `kathryn-bow-starboard.png`,
  `kathryn-bow-plan.png`, `kathryn-bow-entry.png`, `kathryn-bow.png`,
  `kathryn-side.png`, and `kathryn-iso.png`.
- Keel review evidence: `renders/kathryn-hull-profile.png` and
  `renders/kathryn-keel-section.png`. The section plot is made from actual
  CAD intersections, with the keel and shoe highlighted for identification.
