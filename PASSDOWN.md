# Passdown — Kathryn sailboat

## LATEST — 2026-11-11: M4 deck planking implemented and verified

**Current verified assembly: 792 valid parts, 1:1 CAD/STEP in millimetres, no
warnings.** The deck is now a standard-lumber plank schedule, not a material
partition.

- **237 deck boards in 55 runs**: 4-in nominal (3½-in actual) field stock and a
  6-in nominal (5½-in actual) kingplank. **Hard 12-ft maximum**; max 11.909 ft;
  min 0.163 ft (existing bow/stern closures); 31 boards under 4 ft reported.
- **123 internal butts**, every one on a measured S05-07 beam centreline. The
  two adjoining boards end/start at the beam centre and share the beam, each
  covering half its sided width. No ledger, block or unsupported butt.
- Six adjacent-run pairs fall below the 4-ft stagger target, minimum **2.095
  ft**, where the split-beam/opening grid prevents a full two-bay offset; no
  adjacent pair shares a beam. This is the approved “report the reduced stagger”
  outcome.
- **Waterway**: provisional 4-solid oak margin outboard of the accepted clamp;
  its measured section is still outstanding. **Kingplank**: continuous within
  each continuous deck piece; one visible 14-in scarf in the longest piece
  (`Deck/Scarfs/Kingplank`).
- Material: 83.621459 ft³ field + 7.150006 ft³ waterway = 90.771459 ft³ deck
  envelope; conservation 0.064 ppm.
- Final build stages **417.8 s** (model 241.0, STEP 13.3, GLB 149.2), under the
  600-s stage budget; wall 600.4 s. Earlier wall times of 694–837 s included
  waiting for the app warm process.
- Passing: `checks/check_m4_deck_pattern.py`, `check_registered_deck.py`,
  `prototype_deck_boards.py`, `check_m4_beams.py`, `check_model_scale.py`, plus
  the M1/M2/M3/stern/hatch/companionway/mast regressions.
- Review artifacts: `M4_DECK_PLANKING_GAP_ANALYSIS.md`, `milestones/M4.md`,
  `renders/m4-deck-planking-top.png`, `renders/m4-kingplank-scarf-close.png`,
  and the 237-row cut list `checks/m4_deck_board_schedule.json`.
- Git: model `453adc5`, pattern QA/repair `0eaea33`, validation docs `207651f`,
  resolved decisions `de38400`. Use `./project-git`; `.git` is read-only.
  No remote.

### Next work

1. **Side planking** (same support/stagger/standard-lumber logic):
   - The separate `parts/planking.py` prototype is **not live** and still fails
     its starboard completeness assertion: 17 cells, missing courses 11 and 14;
     boundaries 12/15 fail. Sequential partition takes ~459 s; the one-shot
     split + profile-classification approach previously timed out at ~30 min.
   - Tested this evening: a one-shot split of the starboard half with all 15
     `longitudinal_cutters` seam surfaces **failed conservation** (29.130 ft³
     returned from an 86.018-ft³ half). Do not repeat that exact approach.
     The sequential solid-slab partition still returns 17 cells with starboard
     courses 11/14 missing. Next candidates are a per-cell continuation of the
     two failed boundary cuts, or a different closed cutting solid; classify
     every cell by `identify_course` and add a post-pass for any cell spanning
     two courses. Do not register side boards until the 16-course completeness,
     12-ft limit, frame-centred half-frame joints, stagger and volume checks pass.
2. Measure/finalize the oak waterway section; the current clamp-margin piece is
   provisional.
3. Spiled/tapered edge treatment and remaining bow/stern closures.
4. Build-time/part-count pass before side boards are added.

## HISTORICAL — 2026-11-11: 650-part stopping point

**Superseded by the latest section above.** Current verified assembly: **792
valid parts** (was 650). The historical text below is retained.

**User requested a stop and passdown.** Current verified assembly: **650 valid
single-solid parts, 1:1/mm, no warnings**. The first M4 increment replaces the
aggregate deck with109 solid segments in53 runs. Material conserved to0.0695 ppm;
actual exported deck bounds unchanged and no missing deck mesh faces. Mast repair
and three-scale mesh checks pass. All final images were opened and inspected.

Implementation checkpoint `9d7103b`; final validation/passdown follows it in Git.
Use `./project-git`. Detailed status, commands, evidence, outstanding questions,
and exact next steps: **`PASSDOWN_2026-11-11.md`**. M4 is incomplete; M5 is not
implemented. The provisional23-pick beam ledger must be reconciled with existing
stern-timber numbering/materials before geometry use. No next increment started.

## LATEST — 2026-11-11 independent stern review passes; M4/M5 authorized

User is away and explicitly authorized the agent's independent stern review,
then continuation through remaining milestones. **No further user appearance
approval is required.** `STERN_INDEPENDENT_REVIEW.md` closes that gate using
fresh actual-CAD checks, fixed-scale source overlays and archived LOC photos.
Retain the accepted stern geometry and rerun regressions during M4.

Local repository baseline: `60b5c3d`; use `./project-git` because `.git` is mounted
read-only. Metadata lives in `.local-git`. Frequent detailed commits authorized;
no remote. See `VERSION_HISTORY.md` and the folder-owned AGENTS.md addition.

Mast repair is built and visually verified: the conical side formerly had zero
viewer triangles despite a valid solid. `.toNURBS()` preserves exact material;
actual full-size GLB now includes the side (390,748 triangles). Three-scale mesh
checks pass at 1/32/64 with no missing faces. Full build: 542 parts, no warnings,
325.22 s recorded stages (CLI395.9 s included waiting). Inspected restored mast
in `renders/current-full-vessel-side.png`. `checks/render_vessel.py` works without
the live app bridge and does not clip the mast. M2 bearing/trunk/board, full
companionway and scale regressions subsequently passed on that542-part envelope.

## LATEST — stern implementation built and checked; user review next

**Read `STERN_REMEDY_IMPLEMENTATION.md` first.** It supersedes the partial-work
state in `TONIGHT_PASSDOWN.md`. Current assembly: **542 valid parts, 1:1/mm**, no
warnings, captured successful415.49-s build. Full source/mesh hashes and stage times are
in `renders/stern_remedy/provenance.json`. Original baseline images are preserved.

The moulding is now correctly registered as three individual timber sections;
the Null TopoDS_Shape and crosswise-beam failures are resolved. Rails are fair
rectangular timber, with measured posts; helm opening/hydraulics, traveller,
davits/struts/winches/tackle, bumper, controls, cleat and speaker are implemented.
Unprinted sections, hidden joints and fine mechanism details remain qualified
reconstruction, not observed historical facts.

User markup `.soma/feedback/markup-20261110-2259.png` called out BOTH concave aft
quarters. Measured side controls replace the old inferred squeeze; an F18 fair
runout and exact shared rubbing-stock section remove the gaps/wing terminations.
Actual source/quarter/material/support/steering checks pass, including37 raw
wood/rail observations. Full companionway door sweep passes0–90° at15° samples.
The M3 frame/repair/limber/board checks and actual export-scale check also pass.

Next action is **the user's stern appearance review** of the new images/overlays
in `renders/stern_remedy/`. **M4/M5 remain held** until that is resolved. Use
`checks/check_stern_remedy.py` for current stern acceptance; the older
`check_stern_helm.py` describes the superseded preliminary checkpoint.
The required new source input is `drawing_package/stern_remedy_targets.json`.
Everything below retains earlier source research, baseline findings and history.

Checkpoint updated: 2026-11-09.

## Historical baseline report — superseded implementation state; milestones held

User's final steering: **focus on stern before going further; complete review;
generate a detailed remedy report saved as `.md`; include pictures with arrows
to model problems and reference comparisons; hold remaining milestones.**

Delivered governing report: **`STERN_REVIEW_AND_REMEDY_SPEC.md`** (root). It has
11 embedded annotated images, additional linked annotated views, matched-scale
plan/profile overlays, source/photo citations, actual model measurements,
priorities R0–R9, ordered remedy work orders and15 acceptance criteria.
**Overall stern status is remedy required / not accepted.** Do not resume the
unregistered M4 board prototypes until the stern has been resolved.

### Findings and evidence

- Captured live geometry: **446 parts, 1:1**, build OK/no warnings. GLB hash
  `77f270ab0a15833419914c1c9ebda2a0c0515565cec43fabe9ebebd7eb47db25`.
  No new model remedy was applied while producing this report.
- Source/CAD quantitative evidence: `checks/stern_review_measurements.json`.
  Actual deck projection aft of current rail centre is16.9 /21.6 /32.0 in at
  X0 /2.5 /4.5 ft. Current deck is nearly straight-backed while rail turns fore.
  Do not treat the17-in case-to-rail check as whole-stern acceptance.
- Existing S04 counter picks under fixed review deck anchor suggest the current
  plane is12.3 /13.2 in aft. **Provisional**, not certified trim targets: confirm
  planked edge identity, datum and corrected/as-surveyed condition first. Slope
  is close, but its inherited HULL_AFT anchor is not independently established.
- S04 item18's actual leader points to the **short transverse main-sheet
  traveller immediately aft of helm**, not automatically the furthest-aft long
  straight line. The report explicitly avoids that mistaken identification.
  Resolve hull/deck/waterway/moulding/rail/fitting layers before new geometry.
- Rear rails are14 round segments per rail, radius.09 ft; source is3.5 x1.75-in
  oak timber. Corner path/post pattern and paint details need source reconstruction.
- Helm footprint is improved, but lower front opening and hydraulic replacement
  equipment are missing. Report shows actual isolated shafts/bearing vs LOC-P29.
  Traveller/bumper/local controls missing; iron davits/stainless struts remain
  bent-rod placeholders. Substantial8 x6-in transom moulding and distinct local
  framing schedules require their own source-led representation.
- Preserve measured helm/wheel/stock/cabin chain; do not move/scale it to hide
  bad hull outline. Do not force final body bounds to an old bbox assertion if
  newly classified source wood bounds disagree. Global recorded50-ft datum and
  physical wood/fitting extents are separate concepts.

### Report artifacts

- `checks/build_stern_report_assets.py` generates evidence only, no model edits.
- All derived PNGs: `renders/stern_review/`. Red=model defects, blue=reference
  features, amber=unresolved interpretation, green=improvement to retain.
  Matplotlib overlays retain source scale/F; profile has one documented local
  deck anchor, no unconstrained fit shift. Source-photo perspective is not a ruler.
- Images/provenance and snapshot hashes: `image_provenance.json`,
  `photo_provenance.json` in that image directory. Originals untouched.
- Sources: M0 native S02/S04/S05/S06/S07 views plus archived LOC-P07/P25/P28/P29/
  P30/P31. All32 review photos and selected masters available locally. P07/P25
  masters were added for the report. Gallery page24 is printed photo23 (bow).
- `STERN_CORRECTION_PLAN.md` is explicitly superseded as preliminary history.
  Earlier local material/clearance passes are not overall visual acceptance.
- Preserve these baseline images when implementing remedy; save after-remedy
  validation separately. **All general M4/M5 work stays paused.**

## Previous continuation — local stern correction, 1:1 and M4 prototypes (now paused)

New user instructions after M3: continue next milestone; inspect excessive stern
extension past helm, use drawings to control that relationship; add LOC photos
`https://www.loc.gov/resource/hhh.md1454.photos/?sp=24&st=text` as references/QA;
switch model to **1:1**, and use feet/inches display only if SOMA supports it.

- **Stern correction is implemented and verified**, before M4 boards. Latest
  explicitly verified full build: **446 parts**, no warnings, **314.4 s**, 1:1.
  `checks/check_stern_helm.py`, `stern_helm_acceptance.json`,
  `renders/stern-helm-review.png`, `STERN_CORRECTION_PLAN.md`.
- Drawings govern: longer helm box (F0.746–4.162, about 3 ft 5 in), wheel F4.493,
  independently located stock head F2.131 (not box centre). Counter now rakes
  1.8 ft forward per vertical foot. Aftmost deck limit retained separately;
  curved rail is inset, about 1 ft 5 in behind box instead of old roughly 4 ft.
  Aft rails are taller per S04 profile, with proper deck-supported posts.
- Geometry input `drawing_package/stern_helm_registration.json`, exposed as
  `STERN_SOURCE` by datum.py; reproduce `checks/measure_stern_review.py`.
  `parts/stern_layout.py` shares the exact counter keep/normal-offset cavity
  planes. Upper body bounds stay M0 references; deck gets its small aft eave.
  Aft frames now follow actual cavity sections; raked transom stiles/braces and
  central fork clear stock/boxing. Helm has a shaft bore and three lid timbers.
- Full size: `MODEL_SCALE=1`, range **1–64**, step 1, CAD/STEP mm. Verified actual
  transform 304.8 mm/ft and body length **16,012.16 mm**; 50-ft reference =15,240 mm.
  `checks/check_model_scale.py` / `model_scale_acceptance.json`. Native SOMA
  measurement display is hard-coded mm; only decimal precision is exposed.
  User's conditional imperial-display request therefore leaves app units alone.
  Reports use source feet/inches. Do not change geometry into unlabeled inch units.
- `render_m1.render` now derives camera scale from exported Samson-post bounds;
  supports full-size views and sets a valid up vector for plan cameras.
- LOC access: normal HTML 403; official `?fo=json` endpoints work. All **32**
  review JPEGs, metadata/captions, hashes, local HTML index and contact sheets in
  `Reference Material/LOC_Kathryn_photos/`. Gallery page 24 = printed photo 23.
  Stern masters P28/29/30 downloaded; hold/deck masters being extended for M4.
  One cabin-master transfer was interrupted; review JPEG remains available;
  `prepare_loc_photos.py` now retries incomplete transfers and saves per-row metadata.
- Existing enclosure/frame tests updated for actual raked-counter geometry, not
  obsolete samples below the removed stern. They pass: 105 air points, 144
  normal skin rays, 9 counter normals, all frame seats/mortises/78 drains,
  **10,237** distinct exterior samples, 54 bays, board/steering clearances.

### M4 work underway — NOT yet registered as boards

- `parts/board_tools.py`: exact OCCT material splitting with explicit high-
  accuracy `Volume(1e-9)` on source and pieces. Default GProp integration on
  long splines produced false conservation errors (~0.014%); accurate integration
  passes. Never remove the conservation check to hide a real partition failure.
- Performance preparation is now active in hull.py: **segmented cubic lofts**
  through the SAME dense source sections for outer hull, cavity and deck, via
  `segmented_loft`. Verified max source-boundary drift **0.0685 in**, exterior
  volume difference **0.0112%**. Planking face count falls from 5,290 to about606.
  Current M1/M3 tests pass AFTER this optimization. Single giant spline patches
  timed out in booleans; bounded 12-interval patches work (~48 s prototype).
  `checks/m4_loft_prototype.json`, `prototype_smooth_enclosure.py`.
- `hull.planking_envelope()` is the one unpaint-partitioned hollow material
  reference; make_hull() still returns upper/lower paint references for checks.
  Model.py STILL registers the aggregate hull/deck/panels: M4 is unfinished.
- Deck partition prototype: **110 real strip solids**, 1,906 faces from a105-face
  reference, ~50 s, exact high-accuracy volume conservation. Needs waterway/
  butt integration and live registration. Typical deck width3.5–4 in (use3.75),
  inboard5–7 in, thickness1.75 in; ceiling9±1 in is NOT hull/deck width.
- `parts/planking.py` is an UNREGISTERED hull-board prototype. Target9 bottom,
  3 chine, 3 lower-side and1 sheer course per side; spiling and staggered butts
  explicitly inferred. Logical board groups may have separate finish regions
  above/below waterline; finish partitions are NOT timber seams.
- First open-surface compound cutters lost material and were rejected by the
  conservation guard. Closed sublevel tools with cubic lofts failed validity.
  Latest attempt uses **closed ruled loft tools**, sequential lower-region
  partitioning (`split_strakes` / `sublevel_tool`). This latest attempt still
  needs `python checks/prototype_hull_boards.py` validation. Do not register it
  until all16 courses/side, conservation and solid checks pass.
- Still pending: full independent23-set deck-beam schedule (S05-V01 / note7),
  individual deck/hull/lining/floor/bulkhead boards, exact support/material/access
  QA and M4 acceptance. M3 remains historical below; M4 is the active milestone.
  Scale range endpoint64 verification in a temporary copy is also pending after
  the final model stabilizes; never overwrite user parameters for that test.

## Historical checkpoint — M3 complete; M4 next (439 parts)

User authorized **“go on to m3”**. M3 construction, source review, material/
support/clearance verification and handoff are complete. Current SOMA/GLB/STEP:
**439 valid parts, no warnings**, default 1:32. Last complete build **304.0 s**.
Full source/member evidence and caveats: `milestones/M3.md`. M4 is next.

### Geometry and required source inputs

- `parts/hull_frames.py`: 154 individual frame pieces and 15 additional supports.
  `parts/frame_layout.py`: schedule and shared mortise/underpass tools.
  `drawing_package/m3_frame_schedule.json` is a required geometry input, now read
  through `parts/datum.py` as `FRAME_SOURCE` (alongside registration, sheer-band
  and M2-centreline JSON). Reproduce with `checks/measure_m3_frames.py`.
- 78 half-frame records: 20 numbered exposed sets, separately named five hidden
  cabin continuations/two aft sets, and 24 interpreted companion additions. Not
  every plane/pairing is directly measured. F1 stem-knee association is inferred;
  some forward starboard pairs are obscured. Per-row basis/uncertainty retained.
- Bow-to-aft numbering is supported by plan/captions/scarf; literal S05-10
  **“stern knee”** conflict is preserved. F4=42.572, F5=41.050, F13=27.616,
  F15=24.036, F20=15.938 ft. M2 scarf lies between 15/20. Do not conflate these
  with lines-station or deck-beam IDs or silently force source text agreement.
- Older graphic applies to **22 exposed bottom-member records only**, qualified
  possibly original. Associated side-futtock ages are unresolved in their names.
  Newer-frame family is associated with 1954, not a proved date for all 24
  modeled repair-pattern companions; some secondary pairings remain interpretive.
- Actual primary side mortises cut the keelson; repair-pattern feet butt outside
  it. F19/F20 continuous floors pass below it. `hull.keelson_seating_tool()` also
  excludes those underpasses, restoring real planking below floors. Do not cut
  only the log while leaving the old planking-seat gap.
- The final fine bow uses `hull_frames.frame_profile()` from the actual cavity
  section beyond lines station 9.5; separate section offsets caused a seating
  gap there. Other frames use sampled offset profiles. Every frame bottom/head
  has actual bearing; limbers are cut; replacement knees are rounded, NOT grown.
- Pine clamps are full runs inboard of frame heads, with two separate oak
  reinforcement runs. Existing six pine part names remain under Opening framing.
  Added stanchion 1 uses existing after-hatch fore header; duplicating it created
  overlapping beams. Only two new cap beams. Strongback and transom stock sizes
  follow notes; fine shapes/counts/endpoints remain reconstructed.

### Forepeak/source correction

- Source-located 1995 replacement Samson post has a real stem-knee mortise and
  square deck passage. Kneetop follows rising garboard with a compact inferred
  section; post foot extends down to it. Exact mortise/knee dimensions unprinted.
- S04 deck/profile review exposed an inherited bowsprit heel extending aft
  through the post. Heel now **F52.76993**, independent profile F52.804; height
  uses native ruler / post-deck witness. Required fields are in M3 JSON.
  `bow._heel_z` uses that source witness, not deck interpolation beyond the hull.
- Heel chock has a real shallow spar housing and one new bearing cross-timber
  to headrails. First upper cross-bearer/walking-board start and bands follow
  heel. `spars.make_bowsprit()` centralizes the actual spar. Post and spar clear;
  heel/chock/bearing/headrail and cover supports pass. Forward tip remains an
  inherited exterior reference for M5, not newly source-dimensioned here.
- Total: 269 + 154 + 15 + 1 new heel bearing = **439**. No new UI parameters;
  existing scale range unchanged. Full assembly is `output/model.step`.

### Verification and inspection

- `check_m3_frames.py`: valid pieces, numbering/stock/age rules, 9,955 distinct
  exterior samples, all bottom/head bearing, primary vs repair joints, 78 limbers,
  continuous underpasses, stanchion/strongback/post supports, five board poses,
  three steering poses and 54 genuine-air bay samples pass.
- M1/M2, companionway including all new parts, hatches including all new parts,
  and exterior/machinery regressions pass. Updated exterior regression checks
  source-corrected heel housing/bearing/headrail contacts and post/spar clearance.
  Source package original hashes/crops/notes/scales/links pass.
- `render_m3.py` fixes F and scale for actual sections; only local Z reference
  is fitted. Shell-guide RMS F4 **1.538 in**, F13 **1.733 in**, gate <1.8 in.
  `checks/m3_section_comparison.json` preserves fitted local origins and keel
  differences; do not re-label them certified global section datums.
- Inspected `renders/m3-review.png`, `m3-frame-pairings.png`,
  `m3-forepeak-headwork.png`, `m3-section-S06-V01.png`, `m3-section-S07-V01.png`.
  Main groups: Hull frames and repairs / Clamps strongback and stanchions under
  Interior. Hide shell/deck/roofs to expose skeleton; STEP retains whole boat.
- Run heavy CAD checks sequentially: concurrent whole-hull jobs reached command
  time limits. Deduplicated exact classifiers avoid redundant exterior sampling;
  do not raise the application's 600-s build limit or remove its lock.

### Next — M4

Complete individual hull/deck/lining/floor/bulkhead boards, full deck-member
schedule and detailed joints. Preserve the continuous void and current support,
drainage, board/steering/access tests. Source constraints: no chine log; irregular
primary/companion stock; survey-access ceiling removal is not permanent missing
planking; rounded replacement knees; incomplete individual dates/hidden planes.
Retain qualified pairings and fine joinery for refinement, plus M2 full-stowage
and M5 rig/fitting-reference gaps. M3 is inspectable historic reconstruction,
not certified manufacturing joinery.

## Historical checkpoint — M2 complete; M3 next (269 parts)

User authorized **“let's do m2...”** and requested continuation. M2 implementation,
source/solid review and acceptance checks are complete. Current SOMA/STEP:
**269 valid single-solid parts, no warnings**, default 1:32. Final full build
**379.7 s**, below the 600-second application limit reported during development.
Acceptance/member evidence/gaps: `milestones/M2.md`. Next milestone is M3.

- New `parts/centreline_layout.py` provides shared cutting/member interfaces;
  `parts/centreline.py` builds 29 separate centreline members. One interim M1
  mast pad is removed: 241 + 29 - 1 = 269.
- `drawing_package/m2_centreline_measurements.json` is now a required geometry
  input, alongside registration/sheer-band JSON. Reproduce with
  `checks/measure_m2_layout.py`; its measurements retain source hashes and the
  corrected-keel/profile vertical anchor. Preparation: `checks/prepare_m2_sources.py`.
- Two oak keelson sections have a complementary non-overlapping scarf, 14/16-in
  widths and the printed 10.5-in forward height at garboard. Aft continuation
  under the cabin is inferred; forward timber is **possibly original**.
- Eight 2 × 11.5-in pine trunk courses, two rails, two end timbers and an iron
  pivot surround genuine empty board space. Real slot cuts shoe/keel/deadwood/
  planking/keelson; worm-shoe widening follows this actual slot. Partitions/sole
  bearers have real centreline reliefs.
- `hull.make_centreboard()` now returns the traced S04 board with pivot bore,
  not the old thin placeholder. Five poses 0 to -15 degrees pass. A -17-degree
  trial hit the main-hatch aft beam/deck; -15 is a clearance-limited display
  state, not certified full historic stowage. Preserve this distinction.
- Lower mast is faceted, with a mortise/seat in the forward keelson, separate
  iron heel hoop, eight pine chocks, two oak partners, lapped side carlings and
  a clamp-supported forward beam. Fine mortise/hoop/laps/facet count are inferred.
- Dense ruled timber lofts caused the build timeout. Smooth trunk lofts and
  adaptive keelson sampling (55 sections, 0.0562-in max base error at 4,001 picks)
  reduce cost without removing members. Do not restore unnecessary 40/84-section
  ruled timbers indiscriminately. Build normally with `python -m soma build`;
  respect automatic-build locks, never delete them or raise the app limit.
- Tests: `check_m2_centreline.py`, `check_m1_enclosure.py`, `check_companionway.py`,
  `check_hatches.py`, `check_outer_integration.py`, `check_drawing_package.py` pass.
  Reusable exact `Contains` classifiers replace very costly repeated whole-hull
  booleans for passage/foot samples; real board/member booleans remain where useful.
  M1/hatch/access centreline tests now distinguish actual oak from the open slot.
- Inspection: `renders/m2-review.png`, `m2-mast-supports.png`,
  `m2-source-profile-comparison.png`; regenerate with `python checks/render_m2.py`.
  Group **Interior/Keelson trunk and mast supports**. Hide deck/roofs/covers and
  equipment as useful; an X section exposes the trunk/board. Full STEP is assembled.
- M3 must map actual hull-frame numbers/planes and original mortised versus later
  uninletted sister/replacement members. Keep no chine log, rounded replacement
  knees and the source datum/numbering cautions below. Do not force frame numbers
  onto M1's freely shape-registered section planes. M4 boards and M5 fit-out remain.
- Explicit source refinements: inaccessible aft keelson, exact scarf/mortise,
  trunk-end rakes/notches and pin/hoisting/full-stowage details. See M2 gap list;
  source measurements and construction inferences are not certified joinery.

## Historical checkpoint — M1 complete; M2 next (241 parts)

User: **"let's keep going"**, explicitly proceeding with M1. **M1 is accepted**:
continuous hollow enclosure, real interior spaces and supports, source-coordinate
migration and a corrected upper sheer/deck reference. Full acceptance and gap
review: `milestones/M1.md`. Current SOMA/STEP assembly has **241 valid parts**,
no warnings, default 1:32; final build took 382.4 s.

### Important geometry/source changes

- `hull.make_hull()` now cuts one continuous cavity, not local access pockets.
  Planking material is **7.63%** of the equivalent filled envelope. Thin transom
  and localized stem closure remain; no broad cargo/accommodation filler bands.
- Native source review exposed an old datum error: table Sheer is the underside
  of sheer strake, not Top of Deck. The measured upper band rises 12.5–16.1 in
  with outward flare. **Do not remove this band or reinterpret SECTIONS as raw
  offset tuples.** `SOURCE_SECTIONS` retains lower/table-reference data (including
  the existing deliberate sheer fairing); `SECTIONS` carries model deck-edge W/Z.
  True printed offsets remain in M0's separate checked table.
- `drawing_package/sheer_band_measurements.json` records source pixels/hash and
  endpoint closure assumptions. `parts/datum.py` reads it and M0 registration.
  These two JSON files are required geometry inputs when copying the project.
- Body F limits are **-1.800 / 50.733 ft**, span **52.533 ft** (500.38 mm at 1:32).
  The 50-ft recorded reference still uses world Y=25-F. Do not restore a blanket
  0–50 body normalization or silently squeeze projected appendages into it.
- Source station F values, three hatch centres and mast-at-deck now follow M0.
  The mast axis is solved from the actual deck intersection. `MAST_POSITION_FT`
  is only a legacy approximate heel alias; use `spars.mast_forward_at()` and
  `mast_heel_height()` for real joints/bearings.
- Cabin width/roof/upper-house envelope was compared with S07. The deck opening
  is now the full cabin footprint; its framing prefix is `Cabin deck opening`.
  Upper roof slot is about 2.85 ft wide. Cabin sole is Z about **4.809 ft**, with
  a source-derived 2.75-ft drop protected by actual bottom clearance.
- Six added parts: two thin (1.75-in) compartment partitions; two actual sole
  bearer/foot assemblies; a localized mast bearing; hollow timber rudder boxing.
  The engine cover is hollow as well. Full frame/board schedules remain M2–M5.
- Rudder stock still enters the wheel box at **25°**. Extra sheer-band allowance
  in `RUDDER_BLADE_TOP_DROP_FT` preserves the lower blade's underbody elevation
  while the stock reaches the corrected higher deck. Do not casually remove it.
  The keel/shoe/body projection and continuous stern run remain checked.
- Inherited fine bow/rail/davit placements transfer by hull-station correspondence;
  they are not newly measured dimensions. The migrated vine ribbon initially
  self-intersected; smooth border connections fixed it. Both faces/build pass.
- Final machinery review found an old overlong engine housing intersecting the
  migrated clutch controls. Source plan bounds around grid X610–660 give about
  3.33-ft length. `ENGINE_COVER_LENGTH_FT` now drives housing/lid/inside together;
  persistent outer-integration machinery contacts and control clearances pass.

### Acceptance and inspection

- `python checks/check_m1_enclosure.py`: one cavity, 105 air samples, four actual
  transverse material checks, **144 normal-ray skin checks**, thin transom,
  full cabin aperture, hull-seated partitions, floor/mast bearings, stock box,
  source datum and upper-band geometry all pass. `checks/m1_acceptance.json`.
- `check_companionway.py`: doorway/stairs/landing and 0–90° doors pass. Clear
  opening about 19.8 × 49.20 in, sill 2.16 in; three treads/four 8.79-in risers.
- `check_hatches.py`: covers, passages, beam/carlings/clamp/roof contacts,
  normal-ray bottom material and mast clearance pass.
- `check_outer_integration.py`: trailboard/letters/relief, boom/crutch, rubbing
  strakes, walking boards, body keel depth and -35/0/+35 steering, including the
  new stock box, pass. Source chine fit and 35 actual aft-keel sections pass;
  aft chord deviation **0.232 in**, no reverse hollow.
- The initial long normal-ray command timed out. `checks/geometry_checks.py`
  reuses exact OCC solid classifiers; the entire check subsequently passed.
- Actual calibrated source-section overlays improved from 4.31/2.45-in RMS to
  **1.13/0.88 in** after correcting the sheer band. Planes F≈42.18/7.27 are
  shape-registered representatives, **not confirmed hull-frame number locations**.
  `checks/m1_section_comparison.json` records fitted Z origins and keel/shoe
  differences; resolve these references alongside actual M2/M3 station work.
- Main evidence: `renders/m1-review.png`, `m1-open-interior.png`,
  `m1-longitudinal-cutaway.png`, `m1-section-S06-V01.png`,
  `m1-section-S07-V02.png`, `m1-sheer-band-source.png`. Inspected; normal assembly,
  source/hatch/companionway and overall/stern/side views refreshed.
- In SOMA hide `Deck/Planking` and `Deck/Cabin/Roofs`, plus hatch cover parts and
  equipment as useful. Keep `Hull/Planking envelope` and `Interior/` visible.
  The overview uses inspection visibility; `output/model.step` is complete.

### Next action — M2 centreline structure

Complete the keelson, real centreboard slot/trunk, mast/centreline joints and
source-supported bearing relationships, using checked notes S05-12, S06-07/08,
S06-12/13/14 and S07-03/11/12. Trunk walls are recorded as 2 × 11.5-in pine;
keelson average forward section is 16 × 10.5 in, aft width 14 in, with recorded
scarfs/repair distinctions. The small M1 mast pad is not a full keelson schedule.

Use actual inner shell for seating. `inner_bottom_height()` is a near-centreline
bottom-panel helper; `shell_inner_profile()` represents the real cavity boundary.
`solid_envelope()` is a filled REFERENCE used for material checks, not registered
boat material. `continuous_interior()` uses fixed-topology chord guides from true
section offsets; a full variable-edge wire loft was too slow/unstable.

Preserve old/new-frame and no-chine-log construction for M3. Do not equate frame
numbers with lines stations/deck-beam sets or force keel heights to a freely
registered section image. Keep source uncertainty and corrected/as-surveyed
conditions explicit while completing the remaining milestones.

## Historical checkpoint — M0 complete, before M1

The user said **"keep going"** after approving the specification and adding
initial drawing preparation. **M0 is implemented and accepted.** The CAD remains
the previously verified **235-part** model; this milestone prepared references.
The hull still contains filled reference regions, so M1 remains pending.

### Main artifacts

- **Open `drawing_package/index.html`** for the local searchable contact sheet;
  `INDEX.md` and `manifest.json` are AI/file-navigation entry points.
- Eight source overviews, **51 native view crops**, **498 lossless tiles**, and
  **4,623 OCR words** with original coordinates/confidence. All eight source
  SHA-256 hashes and pixel samples match the untouched TIFFs.
- **58 checked construction records**, full numbered sheet-6/7 keys, material/
  repair context and the complete 15-station/eight-row offset table. Raw OCR is
  separate; use `notes_verified.json`, `checked_notes.md`, `offsets_verified.json`.
- Six ruler calibrations in `calibration.json`, within 0.13% of printed imperial
  scale/DPI and <0.018-ft fit residual. Sheet 6's metric caption 1:32 conflicts
  with 3/4-inch imperial scale; calibrated bars support 1:16. Do not rescale by two.
- `registration.json`: source coordinate convention, line-station positions,
  sheet-4/5 plan alignment and legacy CAD placement deltas. Four independent
  deck landmarks fit within 0.102 ft against ±0.20-ft pick uncertainty.
- Full representative section demonstrations: `demos/S06-V01.html` (frame set 4)
  and `demos/S07-V02.html` (cabin hatch). `traces/` contains nine open boundary
  guides in calibrated point data and source-overlay SVG/PNG, with member/repair
  regions. These are interpretation guides, not finished member cutting profiles.
- `ACCEPTANCE.md` and machine-readable `validation.json` record the M0 checks.

### Important interpretation decisions

1. Lines stations 0–10, deck-beam numbers and hull-frame sets are different.
   Deck beams are keyed from bow; source sheet 5 note 10 says first hull-frame set
   against *stern knee*. Preserve the printed wording and establish the actual
   frame schedule separately, not by assuming equal numbering systems.
2. Sheet 6 says new frames are not mortised into the keelson and their knees are
   rounded, **not grown**. Older frames are only *possibly* original. Apply the
   vessel-specific evidence rather than generic natural-crook/sharpie assumptions.
3. Objects shown beyond a cut plane must not be modeled as material filling that
   section. The Sampson post seen forward of frame set 4 is annotated as projected.
4. Source offsets retain blanks and the 2-7-4 reading. The model's station-4 sheer
   fairing to 6-0-0 is listed separately from printed 5-9-7.
5. S02 uses a corrected keel. Surveyed sag/hollow deadrise are recorded separately;
   do not accidentally mix corrected and distorted states into one geometry.

### Next action — M1, continuous hollow enclosure

Use `registration.json` as source authority and migration input. The master F
origin is the aft witness of S02's 50-ft recorded-length dimension, not a presumed
boundary for every appendage. The old model uses a different approximate datum/
arrangement. M0 has established coordinates; **M1 must apply the geometry changes
deliberately**, preserving documented physical relationships and regression checks.
The ledger lists source versus legacy positions, including the three hatches
and mast-at-deck; do not blindly apply one global shift to all fittings.

Replace broad filled reference volumes with the continuous planked enclosure and
real cabin/hold/forepeak space. Local shafts alone do not meet M1. Compare full
transverse/longitudinal sections to the prepared 6a/7a views. Revisit tests that
assumed timber ends must be buried in a filled hull: verify actual shell enclosure
and supports instead, without weakening outside-hull/clearance requirements.

### Reproduce/validate M0

Scripts: `checks/drawing_catalog.py`, `build_drawing_package.py`,
`ocr_tesseract.py`, `drawing_evidence.py`, `register_drawings.py`,
`build_drawing_demos.py`, `check_drawing_package.py`. Commands are in
`drawing_package/README.md`. The Tesseract executable was absent, but its 5.5 C
library works. The wrapper uses that library without changing the app environment.
English `tessdata_fast` model cache: `/tmp/opencode/tessdata/`; download URL and
exact model SHA-256 are in the manifest if the cache disappears. The auxiliary
`Reference Material/Kathryn HAER drawing sheets.pdf` is also image-only; text was
generated from the TIFF views, not extracted from that PDF.

`python checks/check_drawing_package.py` passes all source-integrity, pixel,
OCR/checked-note search, offset-table, calibration, registration and section-guide
checks. CAD geometry was not edited in M0; its existing build/export is 235 parts.

## Latest agreed direction — specification and milestones M0–M5

The user said the boat still looks mostly solid and asked for the whole interior
to reflect the construction shown especially in sheets **6a/7a**, with usable
oyster-dredging/transport spaces. They approved developing the comprehensive plan,
asked that outcomes be called **milestones**, and confirmed:

1. **Include the repairs.** Represent documented original/replacement/sister
   members, patches and altered fittings, preserving evidence and distinctions.
2. **Accurate, inspectable historic CAD model.** This resolves the earlier end-use
   question; the historic survey condition, including repairs, is the baseline.
3. Add an **initial milestone for useful conversion of the TIFF references**.
   They are scanned drawings; prepare indexed readable images, searchable notes,
   checked data and calibrated geometry rather than treating an automatic raster
   trace as authoritative CAD.

**`INTERIOR_SPEC.md` is now the governing specification.** Roadmap:

| Milestone | Accepted outcome to achieve | Current state |
|---|---|---|
| M0 | AI-ready source package and common calibration/registration | Complete; `drawing_package/ACCEPTANCE.md` and `validation.json` |
| M1 | Continuous hollow planked enclosure and real interior volume | Complete; `milestones/M1.md` and M1 actual-solid/source evidence |
| M2 | Keelson, centreboard trunk and centreline support structure | Pending |
| M3 | Hull frames/clamps/knees and documented repair members | Pending |
| M4 | Deck integration and individual planking/lining/floor/bulkhead boards | Pending |
| M5 | Historic cabin fit-out, whole-vessel inspection and final gap review | Pending |

M0 is preparation ahead of the five construction outcomes M1–M5. A milestone can
require multiple modifications, builds and gap reviews. Do not call these five
iterations or close one merely because a fixed number of edits/checks occurred.
The 235-part hatch/local-framing geometry is prior work, not completion of M1.
M0 is accepted through its reference-package artifacts and validation.

### Next action

M0 and M1 are now accepted. Begin **M2** from the current M1 shell and checked
reference package, following the latest-checkpoint instructions at the top.

Keep source research and prior member/build evidence in
`INTERIOR_RECONSTRUCTION.md`, milestone gaps in `GAP_REPORT.md`, and requirements
in `NOTES.md`. Follow the detailed deliverables/acceptance in `INTERIOR_SPEC.md`.

## Current resumed checkpoint — 235 parts

The user returned: **"we're back ion business, let's resume where we left off"**.
The first hatch/local-framing stage is now implemented, built and inspected.
**235 valid single-solid parts, no warnings**, current SOMA geometry and
`output/model.step`, default scale 1:32.

### Completed in this increment

- Found the supplied book: `Reference Material/Migrations of an American Boat Type.pdf`,
  Howard I. Chapelle. Relevant printed pp. 137–139 and 146–149 discuss sharpie
  structure/building sequence and Chesapeake development; treat it as comparative
  context. No need to ask the user to identify the book now.
- Downloaded `Reference Material/Kathryn HAER MD-117 descriptive data.pdf` from
  the CAMM source in `INTERIOR_RECONSTRUCTION.md`. Reviewed printed pp. 2–4:
  fully framed fore-and-aft bottom, three narrow chine planks, **no chine log**,
  original frames inletted to keelson/later sister frames not inletted; white-oak
  coamings; forepeak lowered nearly flush in 1981.
- Calibrated sheet-4 hatch footprints: **150.75 native px/ft** versus 150 from
  400 dpi × printed 3/8-in scale. Measurements/picks are in
  `checks/hatch_measurements.json`, reproducible with `checks/measure_hatches.py`.
- Three coamings now have separate removable boards (4/8/3 = 15) and six cleats,
  plus aligned deck/hull passages. Adopted footprints across × fore/aft:
  after 3.2 × 3.4 ft, main 6.5 × 5.5 ft, forepeak 2 × 2 ft. Clear sizes are
  31.4 × 33.8, 71 × 59 and 17 × 17 inches. Fine wall/cover/cleat dimensions are
  documented reconstruction choices.
- Added **35 separately registered support timbers** in `Interior/Opening framing`:
  eight full deck headers, eight carlings, eight half beams, six local clamps and
  five companionway roof members. Beam sections are 5.5-in square; clamps are
  5.5 × 2.75 in from sheet 5. Main/forepeak share each forebody clamp. Roof aft
  header is split around the full-height doorway.
- The hull has local under-deck relief and hatch shafts intersected with a
  true inward section offset targeting 2.24-in material. The remaining filled
  reference hull is not yet a complete interior shell/frame assembly.

### Verification and views

- `python -m soma build`: **235 parts**, no warnings (191.6 s).
- `python checks/check_hatches.py`: clear shafts, coaming/cover seating, vertical
  cover removal, board/cleat attachments, beam/carlings/clamp contacts, actual
  sections, roof joints, 75 normal-ray skin samples and mast clearance pass.
- `checks/check_companionway.py` now includes new framing as obstacles; passage,
  supported steps/landing, bottom material and door sweeps pass.
- Existing pass-6 detail, bow/spar/strake, source chine/transom, body-keel,
  35-section aft-keel and -35/0/+35 rudder regressions all pass.
- The initial hatch-check run timed out; AABB rejection and compound cover checks
  removed redundant booleans, and a complete run passed. No failed geometry check
  remains unresolved.
- `renders/hatch-review.png` is the overview. Source/measurement evidence:
  `hatch-source-comparison.png`, `hatch-scale-measurements.png`. Details:
  `hatch-deck-closed.png`, `hatch-deck-open.png`, `hatch-hold-section.png`,
  `hatch-framing-plan.png`. Render with `python checks/render_hatches.py`.
- Overall/stern/side and companionway views are refreshed. Covers are seated in
  the normal assembly; removed-cover/isolated/cutaway views are inspection-only.

### Registration finding carried into M0

**I-M02 remains open:** the earlier model's normalized 50-ft hull and approximate
mast/deck arrangement are not fully reconciled to raw scaled longitudinal drawing
coordinates. This increment transfers measured hatch footprints but retains the
existing 17.5/31.1/35.2-ft forward centres and port offset 2.75 ft. Do not describe
those centres as newly verified full-size stations. Establish a common calibrated
plan/profile/section registration and member station ledger before extending the
 entire frame/keelson/trunk/clamp schedule. Then add individual lining/floor/
bulkhead boards and cabin fit-out, following `INTERIOR_RECONSTRUCTION.md`.

Technical entry points: `parts/openings.py` owns shared clear geometry;
`parts/framing.py` builds the members; `hull.interior_wire()`, `local_interior()`
and `opening_interior_tools()` create local offset/relief cutters. These depend
on the accepted outer sections without changing the exterior chine/keel run.

## Previous overnight stop — history

User: **"let's find a good spot to stop for tonight.. when you find a good
stopping point, create a passdown and we'll resume tomorrow"**.

**Stopped at a clean reference-review boundary.** The companionway correction
is built and verified at **179 parts**, no warnings. Hatch/framing geometry
has not been changed; that work has only produced source crops and research.
There is no pending geometry build. Resume only when the user returns.

### Expanded goal and method

- The user made **board-level interior reconstruction** a project goal and
  explicitly noted that dimensions may be inferred from the scaled drawings.
- The user also requested online research into skipjack construction and said
  they provided a book. Use the book and historical evidence alongside Kathryn's
  own measured drawings. General cross-planked skipjack practice must not replace
  Kathryn's fore-and-aft planking/rounded-chine construction.
- Use printed dimensions, then per-view calibrated scale measurements, then
  documented construction inferences. Calibrate original views against their
  scale bars/known distances, check X/Y scaling and dimension definitions, and
  distinguish full-size source feet from final display scale.
- `INTERIOR_RECONSTRUCTION.md` contains the full goal, method, sources and stages.
  The earlier assumption excluding internal timber framing is superseded.

### What was done after the companionway build

1. Reviewed the hatch/structural evidence on sheets 4–7. Source timber notes are
   readable: sheet 5 note 7 gives beams 1–3 as 6 × 4¾ in pine and beams 4–23 as
   averaging 5½ in square (±½ in), pine except oak 12–15 under the winders.
   The source counts members beside hatches/cabin as paired sets. Note 6 gives
   the 5½ × 2¾ in pine clamp and forward oak reinforcement.
2. Added `checks/hatch_sources.py` and generated six enlarged reference crops
   in `renders/hatch-source-*.png`. They preserve readable layouts/notes, but
   hatch/framing dimensions have not yet been calibrated or adopted.
3. Confirmed current `make_hatch()` combines cover/coaming and `make_deck()` /
   `make_hull()` still have no matching cuts for the three hatches.
4. Explored a single inward section-wire offset at forward 31.1 ft. This was a
   scratch geometry experiment only; no inner-shell/framing geometry was saved.
5. Read the local 18-page E. C. Collier HAER descriptive report. Printed pp. 2–4
   (PDF pp. 3–5) explain comparative materials, crowned beams, strongbacks,
   tie rods, natural-crook knees, frame notches and interior repairs. Do not
   transfer Collier's dimensions or species wholesale to Kathryn.
6. Began online research. The CBMM Shipyard page is readable; specific Kathryn
   HAER data and NHL nomination PDFs were found as leads but not yet read.
   URLs and review status are saved in `INTERIOR_RECONSTRUCTION.md`.

### First steps on resume

1. **Identify the user's book.** The local PDFs found in this project are the
   E. C. Collier descriptive report and photo captions under `sistership/`.
   No separate construction book was positively identified. Ask whether that
   report is intended, or request the book's title/file path. Do not claim it
   has already been read.
2. Read the vessel-specific Kathryn descriptive-data PDF and relevant book
   sections/construction sources. The local TIFFs remain the primary evidence;
   a LOC web-page HTTP 403 did not make those drawings unreadable.
3. Establish view-specific scale calibration and a member/dimension evidence
   ledger. Check reference length definitions and compare the drawing rulers
   with the current normalized 50-ft model datum before changing placements.
4. Implement the authorized hatch/local-framing stage in a usable increment:
   separate the three covers/coamings; create aligned deck/below-deck passages;
   add source-supported beams/longitudinal opening members and companionway
   support framing. Check covers, contact/support and preserved hull planking.
5. Build, compare actual sections/cutaways with the sources, run access and
   relevant core regressions, and update evidence before the next interior stage.
6. Continue through interior structural members, individual lining/deck/floor/
   bulkhead boards and cabin fit-out as described in `INTERIOR_RECONSTRUCTION.md`.

## Completed companionway checkpoint

The user authorized continued work after the six-pass close-out and flagged
the upper-only door: **"keep going... also, wy don't the door go to the bottom..
what are we supposed to do, jump in head first?"** The access correction is now
complete and verified. Current assembly: **179 valid parts**, no warnings,
current `output/model.step` and live SOMA geometry. There is no pending build or
verification. The earlier six-pass stop below is historical and was superseded
by this authorization.

The companionway now has paired full-height glazed doors down to a low sill,
continuous jambs/lintel, hollow cabin bodies, aligned wall/roof/deck openings,
and a local hull access well with supported treads/stringers/landing. Original
sheets 4/7 were readable. Small unprinted dimensions are reconstruction choices.

## Previous six-pass instruction — history

The user accepted the wheel-box/rudder correction as **"perfect!!"**, then asked
for a model review, gap report and fixes, prioritizing the bow and its decoration.
Latest user request (`markup-20261106-0556.png`): correct the bow/chine/freeboard
for real fore/aft lumber construction, reduce the oversized rudder, recheck the
transom, and make iterative review/correct/compare the goal, **maximum six more
passes**. If a required drawing detail cannot be read, stop and tell the user.
The TIFFs are readable. The user subsequently authorized the independent final
audit and corrections (**"do it"**). **All 6 of 6 passes are now used**: pass 5
audited matched drawing views; pass 6 corrected the five supported exterior
findings. The **163-part** assembly builds/checks pass. Current evidence and
remaining construction-plan work are in `GAP_REPORT.md`. Stop this cycle and
await user direction; do not start an automatic seventh iteration.

## Active objective and user decisions

- Build a 3D model of the sailboat in `2d model/`, viewable live in SOMA.
- The main subject is **Kathryn**, the 1901 two-sail bateau / Chesapeake skipjack in the eight HAER MD-117 sheets.
- User: **"keep the mast and bowsprit.. draw it as if the sails were just removed"**.
- Retain mast, main boom, bowsprit, jib club and walking boards. Omit sailcloth and rope/wire rigging, as originally requested.
- There is no gaff in the supplied triangular mainsail arrangement. Do not add one.
- The ninth TIFF depicts the accompanying yawl/pushboat; it has not been modeled.
- The earlier golf-ball task was superseded. Do not resume it.
- Reconstruct the interior at individual timber/board level, using scale-measured dimensions and construction research as explicitly authorized. See the overnight resume instructions above.

## Current checkpoint

- `model.py` is the entry point; it registers **241 parts** including separate hull planking, deck/roof, opening framing and enclosure/bearing groups.
- The latest `soma build` succeeded with **no warnings**.
- The live project remains at **1:32** scale.
- The 50-ft recorded reference is **476.25 mm** at 1:32; the source-registered projected body span is **52.533 ft / 500.38 mm**.
- One user parameter exists: `MODEL_SCALE`, label `Model scale denominator`, default 32, range 16–64, step 16.
- No `parameters.json` exists at this checkpoint.
- Model includes a continuous hollow shell, thin compartment partitions and actual floor/mast supports, 15 hatch boards and 35 opening-support timbers; full centreline/framing/lining/fit-out remain M2–M5.
- Original TIFF reference files have not been modified.
- No Git repository was available, and no commits were made.

## File map

| File | Purpose |
|---|---|
| `model.py` | Registration, colors, groups; converts every shape into model millimetres |
| `parts/params.py` | Scale, source dimensions, colors, offsets and arrangement constants |
| `parts/hull.py` | Source-fitted chine/stem envelope, transom, keel/shoe/deadwood, rudder/stock, aligned local access well through hull/deck |
| `parts/access.py` | Shared access levels and cutting tools; accepts the hull height function to avoid an import cycle |
| `parts/datum.py` | Checked source coordinates, inherited-attachment transfer and measured upper sheer-band references |
| `parts/interior.py` | M1 thin compartment partitions, actual sole/mast bearings and hollow stock box |
| `parts/openings.py` | Shared hatch/companionway clear openings, coaming levels and frame boundaries |
| `parts/framing.py` | 35 opening-support timber builders: beams, carlings, clamps and roof members |
| `parts/deck.py` | Hollow cabin/raised house, paired doors/frame/hinges, roof slot, supported descent, hatches, helm, post and traveller |
| `parts/rails.py` | Side rails, rubbing strakes, 50 stanchions and transom rails |
| `parts/equipment.py` | Cross-braced winder, perforated drums, bearings, drive wheels, brake/clutch controls, skids, engine cover, rollers and davits |
| `parts/spars.py` | Mast, main boom, gooseneck, bowsprit, jib club, walking boards and boom support |
| `parts/bow.py` | Shaped stem/cutwater, one centreline decorated trailboard, headrails, supports, linked chains, straps, eyes and collars |
| `parts/primitives.py` | Shared block, cylindrical/tapered spar and rectangular beam helpers |
| `NOTES.md` | Requirements, assumptions, parts list and verification notes |
| `GAP_REPORT.md` | Current interior/hatch/framing goals and pending findings, completed access/six-pass history and verification |
| `INTERIOR_RECONSTRUCTION.md` | Board-level goal, per-view scale measurement rules, research sources/status, timber evidence and phased acceptance |
| `milestones/M1.md` | Accepted enclosure outcome, source-reference corrections, tests, inspection instructions and remaining gaps |
| `checks/check_companionway.py` | Persistent actual-solid access, support, bottom-material and door-sweep tests |
| `checks/render_companionway.py` | Reproducible access closed/open/cutaway/source views from the current SOMA GLB |
| `checks/hatch_sources.py` | Reproduces the six readable hatch/framing evidence crops; no model geometry changes |
| `checks/measure_hatches.py`, `checks/hatch_measurements.json` | Original-pixel scale calibration and reproducible footprint measurement ledger |
| `checks/check_hatches.py`, `checks/render_hatches.py` | Actual-solid hatch/support/material/removal tests and current closed/open/section/framing/source views |
| `output/model.step` | **Authoritative current assembly**, generated by SOMA |
| `renders/kathryn-iso.png` | Latest complete model rendered from SOMA's actual GLB mesh |
| `renders/kathryn-rudder-side.png` | Latest side view of the rudder beneath the counter |
| `renders/kathryn-rudder-cutaway.png` | Cutaway showing the straight stock entering the wheel-box underside |
| `renders/kathryn-bow-port.png`, `kathryn-bow-starboard.png` | Current bow decoration, visible chain links and readable name on both faces |
| `renders/kathryn-bow-entry.png`, `kathryn-bow-plan.png` | Current flat entry/transition and single centreline board/headrail arrangement |
| `renders/kathryn-hull-profile.png`, `renders/kathryn-keel-section.png` | Current shallow keel silhouette and actual CAD-section verification |
| `renders/kathryn-planking-review.png` | Illustrative gold topside/blue bottom fore/aft battens ending at the stem |
| `renders/kathryn-chine-comparison.png`, `renders/kathryn-transom-comparison.png` | Source-offset and source/CAD sizing comparisons |
| `renders/kathryn-aft-keel-check.png` | Old hollow/hump versus corrected direct heel-to-body run |
| `renders/pass5-*-comparison.png`, `renders/pass6-*-comparison.png` | Baseline/final matched orthographic plan and profile source/model reviews |
| `renders/kathryn-cabin-detail.png`, `kathryn-winder-isolated.png`, `kathryn-bow-carving.png` | Final detail review views; engine cover hidden only in the isolated winder picture |
| `renders/kathryn-companionway-review.png` | Before/after, open and cutaway access overview |
| `renders/kathryn-companionway-source-comparison.png`, `kathryn-access-source-*.png` | Original sheet 4 profile/plan evidence and corrected access comparison |
| `renders/kathryn-companionway-open.png`, `kathryn-companionway-cutaway.png` | Inspection-only open-door and near-side-shell-removed views; normal assembly has closed doors |

Many single-part `.step` files appeared in the root directory around 20:06,
apparently exported through the app outside the agent's commands. **Leave these
alone.** They predate the latest rudder change: root `Rudder.step` is stale.
Use `output/model.step` for the latest assembly. Regenerate single-part exports
only when requested.

## Coordinates and modeling conventions

- Geometry inside the part builders is expressed in **feet** from the drawings.
- `boat_point(across, forward, height)` maps feet from the aft transom to the shared datum:
  `(across, 25 - forward, height)`.
- Bow faces **-Y**, X is across the boat, Z is up. **Port is +X**, starboard -X (`PORT_SIDE=1`); pass 6 corrected the old reversed labels and hatch side.
- `model.py:register()` scales shapes by `304.8 / MODEL_SCALE`; registered geometry and STEP output are in **mm**.
- Origin is amidships on the source lines-plan baseline.
- Source offsets use feet-inches-eighths: `offset("6-4-4")` means 6 feet, 4.5 inches.
- Hull transverse and vertical dimensions come from the sheet 2 offset table.
- Longitudinal stations and end sections were reconstructed from the plotted spacing and normalized to 50 feet; this remains an approximation.
- Sheet 3 explicitly gives the mast height as **62 feet 6 inches**. Mast taper, rake and smaller fittings are visual approximations.
- Colors and small unrecorded arrangement dimensions are assumptions documented in `NOTES.md`.

## User feedback and fixes already made

1. `.soma/feedback/markup-20261104-1952.png`: user circled a bow spike, "this feature looks weird".
2. `.soma/feedback/markup-20261104-1953.png`: user circled side lobes, "what are these wings? don't look right".
   - Cause: a global smooth loft overshot and twisted at the narrowing stem.
   - Current fix: monotone `PchipInterpolator` between source stations, subdivided into close-spaced ruled sections.
   - Deck camber fades with beam. Hull stops at deck underside so visible surfaces do not overlap.
   - Envelope assertions prevent the hull from extending beyond the bow/transom or growing side lobes.
   - Do **not** restore the original global smooth loft. An attempted cubic smooth loft also gave an invalid/disconnected underwater result.
3. User: **"the rudder don't look right"**.
   - Initial polygonal blade was too far aft and lacked a stock/support.
   - Earlier attempts used a rounded blade hanging behind the transom. These were still too far aft and are superseded by the wheel-box-aligned correction in item 7 below.
   - Reference: E.C. Collier (sister ship) drawings in `sistership/` used to understand the skeg/rudder arrangement (shape only, not dimensions).
   - The centreboard was also retracted so the hull bottom is clean, matching the profile drawings and the under-power photos.
4. User: **"there is a weird bend halfway"** (`.soma/feedback/markup-20261105-0713.png`).
   - Cause: an isolated hollow in the sheer line at station 4 (table value 5-9-7).
   - Fix: set that sheer height to 6-0-0 so the sheer stays flat at 6 ft through the middle stations.
5. User: **"the bow don't look quite right"** and **"don't forget the decorative bow details / bow chains"**.
   - Early small stem strips and rod stays were superseded by the bow review in item 8 below. Do not restore those early placeholders.
6. User: **"mast is raked back quite a bit"**.
   - Increased `MAST_RAKE_FT` from 7.0 to 14.0 (12.6 deg).
   - At that stage the build registered 115 parts.
7. User supplied `photos/rudder detail 3.png` and markup `markup-20261105-1955.png`, then insisted the stock be **under the wheel box and at the drawing's angle**.
   - Trace the **dashed stock centreline**, not the hull outline: it rises AFT at approximately **25 degrees from vertical**. The head sits inside the existing wheel box at forward 3.1 ft; the heel lies forward at about 6.67 ft, below the counter. The blade is under the stern, not behind the transom.
   - `HELM_FORWARD_FT` anchors both box and stock; `rudder_axis_point(z)` drives the blade, upper shaft, counter/deck bore and all bearings. No vertical-post-plus-diagonal-rod elbow remains.
   - The blade spans Z 3.478 to -0.622 ft, traced relative to the stock head/deck datum. These profile dimensions and rake are approximate readings, not recorded dimensions.
   - Keel/deadwood is trimmed forward of the same axis. `Skeg` is now the aligned sternpost timber joining the keel. Two bored gudgeons and the new upper bearing clear the stock; small blade reliefs clear the gudgeons.
   - The wheel box is hollow and tall enough for the wheel axle to enter it. Sheet 4 specifies hydraulic steering; no hidden hydraulic internals have been invented.
   - At that checkpoint: **117 parts**, no warnings. Rudder + upper shaft fuse to one valid solid and clear the stationary hull, deck, keel, sternpost, wheel box and bearings at -35, 0 and +35 degrees. These checks passed again after the bow review.
8. User requested a gap review and bow/decorative work, then supplied markups `20261105-2048`, `2049`, `2051`, `2102`.
   - **One centreline board** below the bowsprit, with port/starboard decoration on its two faces. It is 0.16 ft thick; it is NOT a pair of separated V-shaped nameboards. `parts/bow.py` drives this, the headrails and all bow fittings.
   - Added readable KATHRYN letters, contrasting borders, simplified foliage/volutes; headrails, knees, three cross-bearers, walking-board supports, heel saddle and bands.
   - Two bobstays plus two side stays are now visibly linked chains. Small contact fusions keep each static chain one valid solid. Source points/bands/eyes share attachment coordinates.
   - Lower hull lines rise into the stem head; shaped cutwater and rising keel shoe replace the blunt stump. The entry has flat V sections by station 9, blending smoothly from the rounded chine with local monotone interpolation.
   - The original station 8.5 table was read directly: bottom-chine half-width is **2-7-4**. The transcription and `SOURCE_SECTIONS` are retained; a separate `_fair_source` copy fairs this half-width between stations 8/9 to implement the user's flat-entry correction. Do not silently edit the source table or reintroduce the isolated hollow.
   - The buried mast heel is trimmed inside the hull without moving the accepted axis/head. Boom attachment follows the mast rake via a gooseneck; the crutch meets deck and boom. Rubbing strakes now follow the actual topside surface.
   - That iteration built **151 parts**, no warnings. The bow blend and keel were subsequently reopened and corrected in item 9 below.
9. Latest user feedback: bow transition **"needs to be more gradual"** (`20261105-2131`); **"the keel does not extend that far below the hull... do a full review and create a gap analysis, and iterate again"**.
   - The old keel filled to an independent low profile and produced an excessive continuous fin. It is replaced with a shallow oak timber and a **separately registered worm shoe**. Sheet 6 note 7 / sheet 7 note 11 give 8-inch keel width; notes 19 give a **3 x 8-inch shoe**, up to 10 inches wide at the centreboard. The oak's approximately 6-inch exposed depth is traced, not explicitly dimensioned.
   - Actual CAD sections from 12.5–43.125 ft forward verify **9-inch total body projection**. Deeper filling exists only at the stern (ends at 12.5 ft forward) and joins the accepted stock heel. The forward shoe tapers into the stem. Do not restore `KEEL_BOTTOM_FT` or the former full-length deep slab.
   - That stage used a longer transverse blend. It was still wrong for the plank runs and is superseded by item 10 below; do not restore it.
   - Sheet 4 item 10: forepeak hatch now at forward 35.2 ft, port 2.75 ft. Item 14: added athwartship jib-sheet traveller and deck feet. Samson post now tapers from 5-inch-square foot to recorded 14 x 5-inch head.
   - Full review evidence and five resolved iteration-2 findings are in `GAP_REPORT.md`. Current build **153 parts**, no warnings. The existing bow/attachment and rudder regression checks pass, including the new shoe.
10. Current 2026-11-06 review, maximum six passes, explicitly required source readability and lumber-based construction checks.
   - Pass 1 rebuilt the longitudinal chines and reduced the rudder; pass 2 corrected transom depth; pass 3 independently compared the views/notes. Later markup reopened the aft-keel profile; pass 4 below supersedes that close-out for this finding.
   - Removed the transverse V-collapse. `chine_run()` fits monotone fifth-degree bounded curves directly to the original offset runs from maximum breadth; the known station 8.5 lower-width hollow is low-weight, not silently overwritten.
   - Upper/lower chine runs end at their lower-stem/rabbet intersections, about **46.99 / 46.60 ft forward**, at heights approximately 5.0/4.4 ft. Missing end offsets must not be replaced by arbitrary deck-section fractions that drag the chine toward the stem head. After the chine ends, tiny collinear CAD edges only preserve loft topology.
   - Source residuals: upper width/height maxima about 0.56/0.57 inch; lower about 1.34/0.34 inches except the identified measured outlier. Plan radii exceed 28 ft, with no forward width reversals. These are fair reconstruction runs, not a claim of exact agreement with every distorted as-built offset.
   - Rudder blade **3.5 ft high**, down from 4.1; its outline/head-drop offsets scale together about the fixed wheel-box head. Head remains forward 3.1 ft, Z about 7.028 ft, at 25 degrees. Current blade top/bottom Z approximately **3.997 / 0.497 ft**; heel forward about **6.145 ft**. These approximate outline dimensions supersede item 7's old blade values.
   - Transom width retained **11.3 ft** (trace about 11.4); nominal centre depth increased **1.35 → 1.8 ft**, with the initial section's rabbet now 4.8 ft. Width/depth are traced sizes, not explicitly printed transom dimensions.
   - Lumber notes: estimated 2-inch hull strakes, oak below/pine above chine, fore/aft bottom planking, rounded oak chine; oak framing; 1.75-inch deck planks; oak transom members. See the report for exact notes and dimensions. The construction rendering uses illustrative battens, not a full spiling/fastener schedule.
   - Current build **153 parts**, no warnings. Source-run, actual transom dimension, legacy attachment/keel checks and -35/0/+35 steering tests all pass after pass 2. No required source was unreadable.
11. Pass 4: user marked the aft-keel indentation in `markup-20261106-1840.png`, noting it is absent from the drawings.
   - Root cause: subtracting an eased depth from the falling rabbet and ending the fill at 12.5 ft produced a dip, then an upward hump. Do not restore that formula/cutoff.
   - `keel_bottom()` now uses a direct monotone `CubicHermiteSpline` from heel (forward about 6.644 ft, Z about 0.397 ft) to station 5 (forward 25.625 ft, Z about 1.292 ft), matching the main-keel tangent. Maximum chord deviation is 0.39 inch. Forward of that join it follows the shallow body profile.
   - `STERN_DEADWOOD_END_FT` is now **25.625**, not 12.5. The filling follows the fair keel run; oak/shoe member thicknesses are unchanged. Nine-inch main-body projection applies forward of the join, not through the aft filling.
   - A model derivative assertion guards against a reverse slope. `/tmp/opencode/check_aft_keel.py` checks 35 actual CAD sections, endpoints/tangent and joining contacts. It passes, as do eight forward-body projection checks and -35/0/+35 steering tests.
   - Current build **153 parts**, no warnings. Standard renders and construction overlay are refreshed; `renders/kathryn-aft-keel-check.png` shows the old/new profiles. This cycle has used **4 of 6** passes.
12. Passes 5/6: user authorized the final independent audit and coordinated correction.
   - Pass 5 saved matched plan/profile source/model views and enlarged sheets 1/4/7 details. It found the mirrored forepeak hatch/reversed side convention, vertical companionway front, rectangular glazing, flat roofs, sparse winder and overly spread name/foliage.
   - **Port +X** now follows the actual bow -Y/up +Z handedness. `HATCH_ACROSS_FT['Forepeak hatch']=+2.75`; consistent side names are used in cabin, rails, equipment and bow builders. Symmetric geometry is the same pair, with corrected labels.
   - The companionway has a visually traced 0.75-ft roof-level front setback, larger shaped side apertures with inset/embedded panes, and a shorter roof matching the rake. Main/upper roofs have 0.12/0.10-ft transverse camber. Base/roof/body/pane contacts pass. These fine dimensions are traced approximations, not printed labels.
   - Winder exterior now has shouldered frames, top X/cross bracing, carriers, four bored bearing pedestals, two slotted aft drive wheels, perforated drum end plates, two brake/lever assemblies and two clutch controls. Shared axle centres/extended axles and existing skids support the parts. Wheel/bearing, brake/wheel and control/engine clearances pass. Hidden drivetrain/tooth manufacturing geometry remains unspecified.
   - Bow lettering is compacted to a band under 3.3 ft; continuous scrolling vine/leaf relief fills the remaining bands on both faces. Single centreline board is retained; all lettering/relief contacts pass.
   - Final build **163 parts**, no warnings. `/tmp/opencode/check_pass6.py` and existing source/body/attachment checks pass. A combined test command reached its time limit after detail/body checks; the remaining aft-keel and steering checks were rerun separately and both passed. No verification is pending.
    - All **6 of 6** passes used. The supported exterior audit findings are corrected. Actual construction plans still require frame/keelson schedules, plank spiling/cutting, rabbets/scarfs/joints, fastening and dimensioned hardware/steering design. Do not present this exterior assembly as complete boat-building plans.
13. Access continuation after new user authorization:
    - Source sheet 4 shows paired aft doors and a steep descent; sheet 7 shows the roof opening. The old upper-only sliding panel and filled house bodies were functionally incorrect even though their exterior checks passed.
    - Shared `parts/access.py` defines entry/sole/head levels and the aligned doorway, roof slot and local hull/deck well. Keep this module independent of `hull.py`/`deck.py` imports.
    - Clear doorway is 19.8 in wide × 45.27 in high; sill is 2.16 in above the aft deck. Three treads give four 7.29-in risers, with 4.8-in going; landing is 27 in below deck. These dimensions and fine hinge/wall/tread details are approximate, not printed historical labels.
    - Doors now extend to the sill; default `ACCESS_DOOR_OPEN_DEG=0` is closed. `make_companionway_doors(angle)` supplies inspection/sweep poses. Hinges intentionally contact the door edges; these are static details, not working-hinge tolerance design.
    - The local well preserves the outer hull and at least 2.04 in of normal bottom material at sampled sections including the worst aft corners. Cabin bodies are hollow above deck; the complete lower accommodation is not reconstructed.
    - `python checks/check_companionway.py` passes: actual doorway/roof/deck route, stair/landing clearances, both-stringer support, sill/landing connections, embedded glazing, preserved bottom material and door sweeps 0–90° at 15° samples including helm clearance.
    - Full build: **179 parts**, no warnings. Prior pass-6, source chine/transom, bow/spar/strake, body-keel, 35-section aft-keel and -35/0/+35 rudder tests all pass. All access views and the overall/stern/side views were refreshed and inspected.
    - Use `renders/kathryn-companionway-review.png` for the before/after overview and `kathryn-companionway-source-comparison.png` for source comparison. `python checks/render_companionway.py` recreates the views without changing the default closed model.

## Reference drawings and useful crops

Original files: `2d model/master-pnp-habshaer-md-md1400-md1454-sheet-00001a.tif`
through `...00008a.tif`; companion pushboat is `...md1494-sheet-00001a.tif`.

- Sheet 1: identity, general illustration, registered dimensions.
- Sheet 2: hull lines, body plan, offset table.
- Sheet 3: side elevation / spars, mast height and rake.
- Sheet 4: main deck plan, inboard profile, cabin and **rudder outline**.
- Sheets 5–7: structure, sections and dredge winder.
- Sheet 8: sail plan; sails are excluded.

Temporary reference previews exist in `/tmp` but may disappear:

- `/tmp/sailboat-drawings-contact.png`
- `/tmp/kathryn-sheet-01.png`, `02`, `03`, `04`, `06`, `07`
- `/tmp/kathryn-offsets.png`
- `/tmp/kathryn-rudder-lines.png`, `/tmp/kathryn-rudder-profile.png`

TIFFs are about 14,500 x 9,632 pixels (roughly 140 megapixels). Use Pillow to crop
or reduce into `/tmp` before viewing; do not modify originals. These known local
scans trigger Pillow's large-image warning; `Image.MAX_IMAGE_PIXELS = None` was
used when preparing their previews.

## Environment and required workflow

- Workspace: `/home/jlguthri/Downloads/experimetalCadWork`.
- In the latest session, `python` and `soma` on PATH point to the currently running SOMA AppImage. Use:

  ```bash
  python -m soma build
  ```

- `.soma/env/bin/python` is a broken symlink to an older AppImage mount. Do not recreate the environment or hardcode an old mount path; verify the current app interpreter with `command -v python`.

- Do not create a virtual environment, replace app packages, or write STEP yourself.
- Keep `model.py` at the root; register every part with `add_part`.
- Re-read files immediately before editing; the user edits/exports while the agent works.
- Read/follow `.soma/skills/design-workflow.md`, `cadquery.md`, `parametric.md`, and `standard-parts.md` before model changes.
- Relevant additional skills already read: `shell-environment.md`, `soma-app.md`, `assemblies.md`.
- Do not manually edit `.soma` app data; normal SOMA commands manage it.
- Run `soma build` after changes, fix failures immediately, and inspect visual results.
- SOMA also builds automatically. An explicit build may wait for its lock; this is normal. Do not delete the lock.
- The user wants to **see intermediate work live**, so build usable increments promptly and give concise progress updates.

## Validation and render details

- Current 241-part assembly builds at 1:32; `register()` asserts one valid solid per part. M1's enclosure/source-coordinate checks pass; M2 centreline structure is next.
- `python checks/check_companionway.py` passed on the 179-part checkpoint; rerun it after opening/framing changes to protect the continuous door/stair path, bottom material and door sweep.
- Final detail check: `/tmp/opencode/check_pass6.py` covers side handedness, source-plan hatch side, raked body sections, pane/roof contacts and camber, winder supports/bearings/wheels/controls/clearances and compact seated bow relief.
- Aft-keel regression: `/tmp/opencode/check_aft_keel.py`; monotone actual sections, endpoint/tangent agreement, <0.5-inch chord deviation and material joining contacts.
- Current source/construction check: `/tmp/opencode/check_review3.py` checks fit residuals, monotonic chine runs, plan radii, lower-stem intersections, preserved source values and transom/rudder sizing.
- `/tmp/opencode/check_review2.py` passed actual CAD-plane intersection checks at eight stations, keel/shoe/deadwood joining overlap, localized aft filling, hatch position, traveller seating and Samson-post dimensions.
- Bow review checks: `/tmp/opencode/check_bow.py` passed centreline-board symmetry and attachment of both reliefs/all letters, flat-entry collinearity, enclosed mast heel, boom/crutch contacts, strake fit and cross-bearer/walking-board contacts.
- Latest targeted geometry check: `/tmp/opencode/check_rudder.py`; includes steering clearance at -35, 0, +35 degrees and positive keel/sternpost joining overlap. It passed.
- Earlier 105-part version also passed STEP re-import validity checks on every part.
- Scale endpoints 1:16 and 1:64 were validated on the 107-part assembly (952.5 mm and 238.126 mm hull lengths); they were not rerun after the later stern/bow/mast changes.
- Do not write the live project's `parameters.json` for tests.
- `/tmp/check_kathryn_scale.py` is the earlier range-test helper. If reused, update its hardcoded expected part count to the current manifest rather than an older checkpoint.
- `soma render` cannot connect from this sandbox: app bridge lookup needs special handling for a folder project, then localhost sockets are blocked. No approval was requested.
- **Reliable fallback works:** VTK 9.6.2, explicit `vtkEGLRenderWindow`, `vtkGLTFImporter` reading `.soma/model.glb`. The mesh is millimetres with Z up. See `/tmp/render_color.py` and `/tmp/render_qa.py`.
- Latest renderer: `/tmp/opencode/render_rudder.py`, using the current GLB. Current close-ups: `renders/kathryn-rudder-side.png`, `renders/kathryn-rudder-cutaway.png`, `renders/kathryn-stern.png`; full views: `renders/kathryn-side.png`, `renders/kathryn-iso.png`. Older `qa-*` images predate this change.
- Bow renderer: `/tmp/opencode/render_bow.py`; port/starboard cameras now match the physical +X/-X convention, plus plan/low-entry/three-quarter views. Full builds can take roughly 2–6 minutes depending on parallel CAD work; allow the app/build lock to finish normally.
- Keel section: `/tmp/opencode/render_keel_section.py` draws actual CAD-plane intersections (not a 3D Matplotlib triangle render). It highlights the oak and shoe in the section for clarity; live surface colours remain the model palette.
- Current source/construction renderers: `/tmp/opencode/render_construction_review3.py` (chine/offset plot and gold/blue fore/aft battens) and `/tmp/opencode/render_transom_review3.py` (original body plan versus actual CAD transom wire).
- Aft-keel comparison renderer: `/tmp/opencode/render_aft_keel.py`; actual old/new profile functions, in source feet.
- Final audit/detail renderers: `/tmp/opencode/pass5_audit.py pass6` saves final matched comparisons (default `pass5` is the retained baseline); `/tmp/opencode/render_pass6_details.py` saves cabin/winder/carving close-ups and the isolated winder view.
- Earlier `renders/hull-check.png` and `renders/kathryn-check.png` use Matplotlib and have triangle sorting artifacts. Do not mistake those rendering defects for model defects or use them as the authoritative visual check.

## Resume priorities

Use **Latest checkpoint — M1 complete; M2 next (241 parts)** at the top of this file and
`INTERIOR_SPEC.md`; older overnight/resume steps are history.
Begin M2's keelson/trunk/centreline construction using M1's actual shell. The book
is found and local hatch/support work is an input to the roadmap. Preserve and
verify the established hull/chine/keel and steering relationships as further
structure is integrated. Use SOMA for exports and distinguish current
`output/model.step` from stale root-level exports.
