# Kathryn — skipjack reconstruction

## Requirements

- **2026-11-11 user continuation:** independently review the stern; when it
  passes, proceed through M4 and M5 without awaiting separate user approval.
  The review passes; see `STERN_INDEPENDENT_REVIEW.md`. Preserve the accepted
  stern envelope and rerun relevant checks after new structure/planking.
- The user authorizes frequent local Git commits with detailed change, evidence,
  validation and remaining-work messages. Use `./project-git`; metadata is in
  `.local-git/` because this session's `.git` mount is read-only. No remote.
- Mast visibility repaired: its upper conical side was absent from the viewer
  mesh despite a valid full-height CAD solid. Exact rational surfaces restore
  it; successful 542-part build and inspected full-vessel image. Complete mesh
  surfaces pass at scales 1/32/64; material conserved within one part per million.
- Earlier stern-only holds and user-review gates below are historical and
  superseded by the 2026-11-11 authorization and independent review.

- Current stern checkpoint: **542 valid parts, 1:1/mm, captured successful415.49-s build**, with source/material/support/steering/door checks and actual-export images. Implementation/qualified inferences: `STERN_REMEDY_IMPLEMENTATION.md`; evidence: `renders/stern_remedy/`, `checks/stern_remedy_acceptance.json`. Await the user's stern appearance review; M4/M5 remain held. The earlier partial/unregistered-moulding handoff is superseded.

- User markup `.soma/feedback/markup-20261110-2259.png` flags inward pinching at BOTH aft quarters. Treat the actual plan silhouette and fair side handoff as explicit stern acceptance, not just the centreline/back edge. Extend the measured shoulder to a qualified fair F18 runout and a shared rubbing-stock station; verify source controls, both actual widths and no gap. Hidden runout joints/stock taper are inferred (assumed).
- Stern visible mechanism/fittings now include the LOC-P28 front opening, P29 hydraulic ram/guide/crosshead/pump/valve/hoses and timber lid, S04 item18 traveller, item4d cleat, plate-web iron davits with stainless struts/winches/rigid tackle, external timber/rubber bumper and local control stations. Unprinted sections, hose routing, hidden mountings and individual control functions remain visual reconstruction/inference; no manufacturing internals or new repair dates are claimed (assumed).

- Resumed stern remedy: independently anchored curved plan/counter keep volumes and inward offsets validate. The Null TopoDS_Shape failure came from the tangent whole-hull/deck fuse returning an empty compound; moulding now uses a single section-built outer blank. Three separately registered 8×6-in oak moulding pieces restore the material removed from hull/deck; their hidden joints and aft/side runout are construction inferences (assumed). Full stern acceptance remains pending.

- **Latest user priority — STERN ONLY:** pause M4 and the remaining milestones until the stern is right. User requested a complete review, a detailed remedy specification saved as Markdown, and images with arrows comparing model problems to references. Governing report: **`STERN_REVIEW_AND_REMEDY_SPEC.md`**. Status: remedy required; overall stern not accepted.
- Stern report baseline: actual 446-part 1:1 GLB, annotated CAD/drawing/LOC figures in `renders/stern_review/`, measured evidence in `checks/stern_review_measurements.json`. Previous geometry passes do not establish historic shape acceptance. Preserve baseline figures for before/after comparison.

- User requested full-size **1:1** (2026-11-09): default `MODEL_SCALE=1`, CAD/export millimetres. Scale control now spans 1–64, step 1; source geometry remains full-size feet. Verify full-size export bounds and scale-aware inspection views.
- User requested feet/inches display only if SOMA supports it. Installed viewer source fixes Measure labels to mm and exposes decimal precision, without an imperial display mode; keep native mm and report source dimensions in feet/inches.
- Before M4 board work, review/fix the stern-to-helm relationship against S02/S04 drawings as explicitly requested. Drawings control dimensions/positions; LOC photos provide vessel-specific visual QA. Plan: `STERN_CORRECTION_PLAN.md`.
- User-supplied LOC gallery `https://www.loc.gov/resource/hhh.md1454.photos/?sp=24&st=text` is archived under `Reference Material/LOC_Kathryn_photos/`: all 32 review images, captions, source links/hashes, local index/contact sheets and selected full-resolution masters. Caption numbers differ from gallery pages. Use these references for QA throughout the remaining milestones.

- Current agreed plan: follow `INTERIOR_SPEC.md` for an **accurate, inspectable historic CAD model**, including documented repairs. Use **milestones** from now on: M0 drawing preparation/calibration, then five construction milestones M1–M5. A milestone may require multiple modification/review cycles.
- Historical M3 authorization: **“go on to m3”**. The frame increment reached439 valid parts/no warnings (304.0 s); source/member evidence: `milestones/M3.md`. Current stern review supersedes its overall appearance acceptance; M4 is on hold.
- M3 models 154 separate frame pieces plus 15 supports; 78 half-frame records distinguish primaries and 24 repair-pattern companions. Older graphic identification applies only to exposed bottoms; side-futtock ages remain unresolved. Inaccessible bays and some secondary pairings are explicitly inferred (assumed).
- M3 source input `drawing_package/m3_frame_schedule.json` joins registration, sheer-band and M2-centreline JSON as required geometry inputs. Hull-frame numbering is independent; the contradictory source “stern knee” wording is preserved with the bow-to-aft interpretation documented.
- M3 forepeak review source-locates the 1995 replacement Samson post and its stem-knee mortise. The bowsprit heel is located at the stem head (F52.770), with scaled profile height; this removes the old aft extension through the post. Separate heel housing/bearing contacts pass. Fine knee/bearing joints remain reconstructed (assumed).
- M2 complete: historical 269-part checkpoint, full keelson/scarf, open slot, pine trunk and mast supports. Evidence: `milestones/M2.md`. Printed stock governs; fine hidden joints and the clearance-limited -15-degree board pose remain inferred, not certified historic stowage (assumed).
- Model the entire interior as open vessel spaces surrounded by planks and individual construction members, using sheets 6a/7a as primary section references. Local pockets through otherwise filled hull material do not satisfy this goal.
- Include documented sistered/replacement members, patches and altered fittings, preserving original/repaired distinctions and their sources. The supplied HAER survey condition is the historical baseline.
- M0 complete: `drawing_package/index.html` / `INDEX.md` index eight sheets, 51 native views, 498 lossless tiles, 4,623 coordinate-linked OCR words, 58 checked construction records, the complete offset table, six ruler calibrations and two section demonstrations. All original hashes/pixel provenance pass validation; see `drawing_package/ACCEPTANCE.md` and `validation.json`.
- M1 complete: continuous hollow enclosure, thin cabin/forepeak partitions, real sole and mast bearings, hollow stock boxing and full cabin deck aperture. Its 241-part checkpoint is historical; M2 replaces the interim mast pad with a mortised keelson. Acceptance: `milestones/M1.md`.
- Source station positions, hatch centres and mast-at-deck now follow M0's ledger. Body F bounds -1.800 to 50.733 ft are distinct from the 50-ft recorded reference. Inherited minor fittings were transferred by hull-station correspondence and remain proportional reconstructions.
- M1 section review corrected a legacy datum error: table Sheer is the underside of sheer strake, not Top of Deck. Original-pixel band picks (12.5–16.1-in rise, measured flare) are in `drawing_package/sheer_band_measurements.json`. Source table values remain unchanged; actual deck/freeboard and dependent fittings now use the upper curve.
- Source-reading rules from M0: sheet-6 3/4-inch imperial bar supports 1:16 despite its metric caption 1:32; hull-frame numbering differs from deck-beam/lines station numbering. Sheet 5 note 10 says first hull-frame set at the stern knee; preserve the wording. New-frame chine knees are explicitly rounded, not grown; possible originality remains uncertain.
- Active 2026-11-07 goal: reconstruct Kathryn's interior at the individual timber/board level. The user explicitly permits inferring dimensions by measuring the scaled drawings and requests construction research using online references and a supplied book. See `INTERIOR_RECONSTRUCTION.md` for the measurement policy, sources and phased work.
- Use printed dimensions first, then per-view calibrated scale measurements; record construction inferences with their source. Check each view's scale and dimension definitions, and separate full-size geometry from final model scale. Kathryn's own evidence governs over general skipjack examples.
- The supplied book is `Reference Material/Migrations of an American Boat Type.pdf`; relevant construction sections and Kathryn's HAER descriptive data have been reviewed. The former 235-part hatch-only checkpoint is historical.
- Earlier hatch-footprint calibration is retained in `checks/hatch_measurements.json`; M0 refines sheet-4 ruler calibration to 149.9803 original px/ft. The current three hatch centres use the canonical source coordinates, rather than the earlier arrangement estimates.
- Active 2026-11-07 continuation: user authorized more work and flagged the door stranded on the upper cabin. Correct the continuous companionway access, including the lower doorway, roof/deck openings and depicted descent. This is new authorization after the completed six-pass cycle.
- Sheet 4's paired aft doors/steep steps and sheet 7's roof opening are readable. Retain the traced exterior envelope; small unprinted access dimensions are approximate, consistent with the existing arrangement-reconstruction scope (assumed).
- Access reconstruction uses a 1.65-ft clear doorway, 0.18-ft sill, three treads/four equal risers and 0.4-ft going. M1 uses a scale-derived 2.75-ft sole drop with actual bottom-clearance protection, and separate bearer/feet supports; small details remain approximate. Doors are normally closed.
- Active 2026-11-06 goal: review → correct → compare again against the original drawings and recorded lumber construction, at most six further passes. Include bow/chine/freeboard, rudder size and transom sizing. Stop and tell the user if a required drawing detail cannot be read.
- Current six-pass cycle is complete. Pass 5 audited matched drawing views; pass 6 corrected five supported exterior findings. The original TIFFs and required notes were readable; results and construction-plan limitations are recorded in `GAP_REPORT.md`.
- Replace the golf ball with the sailboat depicted in `2d model/`.
- The main subject is Kathryn, the two-sail bateau/skipjack in HAER MD-117 sheets 1–8.
- Keep the mast and bowsprit; show the vessel as though its sails were removed.
- Include the wooden spars shown in the plans; omit sailcloth and rope/wire rigging.
- Retain the mast, main boom, bowsprit, jib club and bowsprit walking boards. The triangular mainsail has no gaff in the supplied plans.
- Preserve the supplied TIFF images without modifications.
- Use the sheet-2 recorded-length witnesses and checked station/offset data. Keep the 50-ft reference separate from physical body/appendage extents; do not compress all projections into a 50-ft box.
- Represent the rounded chine, rising bow, cambered deck, keel, centreboard, transom and under-counter rudder with stock piercing forward of the transom.
- Historical display scale was1:32; superseded by the user's full-size1:1 request. Current CAD/export uses millimetres and the denominator control spans1–64.
- Cabin, deck fittings, colours and spar tapers are visual reconstructions from the supplied drawings, with small unrecorded dimensions estimated (assumed).
- Model the exterior, visible deck equipment and a staged board-level interior. The earlier exterior-only/internal-framing exclusion is superseded by the user's expanded goal.
- The separate pushboat on the ninth drawing is not included in the main-vessel model (assumed).
- Follow `.soma/skills/shell-environment.md`. In the current session the app's `python -m soma` works; `.soma/env/bin/python` points at an obsolete AppImage mount. Do not recreate the environment.
- Follow `.soma/skills/soma-app.md` for viewer/build guidance and `.soma/skills/assemblies.md` for shared coordinates and part registration; this is a static representation.
- The rudder stock must enter the underside of the wheel box on one straight axis. Its approximately 25-degree rake and blade proportions are traced from sheet 4 and `photos/rudder detail 3.png`; those traced dimensions are approximate.
- User bow corrections: one centreline nameboard directly under the bowsprit with decoration on both faces; flat entry with a smooth transition into the hull; mast heel enclosed within the hull.
- Second review: make the bow transition more gradual and correct the excessive keel projection below the hull. Sheets 6/7 specify an 8-inch-wide oak keel plus a 3-inch by 8-inch worm shoe; the approximately 6-inch exposed oak depth is traced from the sections (approximate).
- Bow ornament follows the identifiable name, border, foliage and scrolls in sheet 1 / `photos/bow details.png`; fine relief, link contact details and paint shades are approximate (assumed).
- World-side convention: bow -Y, up +Z, port +X (`PORT_SIDE=1`). The previous port/starboard labels were reversed; the forepeak hatch and side names are reconciled with the source plan.
- Final detail dimensions traced visually: 0.75-ft companionway front setback, 0.12/0.10-ft roof cambers, and winder exterior features. Exact machinery manufacturing dimensions and fine relief cuts are not printed and remain approximate (assumed).

## Interior work plan

`INTERIOR_SPEC.md` is the governing specification and acceptance roadmap.
`INTERIOR_RECONSTRUCTION.md` retains source research, measurements and prior
implementation evidence. M0–M3 are complete;
next complete M4 deck/planking/lining, then M5 fit-out and whole-vessel review.
Scale-measured features are usable evidence without printed numeric labels.
Compare each usable increment with the drawings and recorded timber construction;
close milestones by their acceptance criteria, not by edit/build counts.

## Parts and assembly

The model is a static visual assembly, not a fabrication kit. Add the hull, keel,
centreboard and rudder first, then the deck and its fittings, then the spars.
For the companionway, fit the landing/stringers/treads before closing the house
roofs; fit the door leaves and glazing after the sill, jambs, lintel and hinges.

| Part | Count | Representation |
|---|---:|---|
| Topsides / underwater hull | 1 each | Continuous hollow planking envelope, divided for paint at waterline; actual upper sheer band included |
| Deck | 1 | Cambered timber with full cabin aperture and three source-positioned hatch openings |
| Keel / worm shoe | 1 / 1 | Oak timber and recorded 3-inch shoe on a fair heel-to-body run; shallow below the main-body rabbet, shoe locally 10 inches wide at centreboard |
| Centreboard | 1 | Source-traced outline/pivot, clearance-checked raised pose; open slot through actual timber |
| Keelson sections / trunk courses / rails / ends / pivot | 2 / 8 / 2 / 2 / 1 | Separately inspectable oak scarf sections and hollow pine trunk with actual board passage |
| Hull-frame pieces | 154 | Measured/interpreted irregular primaries and repair-pattern members; 78 half-frame records, mortises, open limbers and two continuous under-keelson floors |
| Additional clamps/supports | 15 | Two oak reinforcements, three oak stanchions/two extra cap beams, two pine strongback pieces, stem knee, three transom frames/two braces |
| Bowsprit heel bearing cross-timber | 1 | Supported across projecting headrails, seated heel chock fits spar; source-located heel clears Samson post |
| Mast partners / chocks / hoop / carlings / support beam | 2 / 8 / 1 / 2 / 1 | Printed oak/pine stock sizes, faceted mast foot and supported lapped frame |
| Rudder | 1 | Reduced 3.5-ft-high blade (approximate outline reconstruction) under the counter; straight stock into the wheel box |
| Skeg / rudder gudgeons | 1 / 2 | Localized stern deadwood and inclined post joining the rudder heel; bored straps |
| Mast / main boom / bowsprit / jib club | 1 each | Tapered wooden spars; 62-foot-6-inch mast height from sheet 3 |
| Bowsprit walking boards / boom support / gooseneck | 2 / 1 / 1 | Supported walking boards and connected boom fittings |
| Bowsprit bobstays / side stays | 2 / 2 | Alternating oval-link chains, with stem straps, side chainplates, eyes and collars |
| Centreline trailboard / decorated faces / name letters | 1 / 2 / 14 | Single board under the bowsprit; dark ground, warm ivory borders, foliage, scrolls and readable KATHRYN on both sides |
| Headrails / knees / cross-bearers | 2 / 2 / 3 | Projecting triangular headwork supporting the walking-board assembly |
| Stem / underwater stem shoe | 1 / 1 | Shaped raked cutwater; keel shoe rises into the stem |
| Main cabin and raised companionway | 1 each | Hollow painted enclosures; raked upper front and shaped inset panes |
| Cabin / companionway roofs | 1 each | Cambered roofs; lower roof has connected companionway slot |
| Companionway doors / door panes / hinges | 2 / 2 / 4 | Paired full-height timber leaves with upper glazing, normally closed; static hinge details |
| Companionway jambs / lintel / sill | 2 / 1 / 1 | Continuous frame down to a low deck-level threshold |
| Companionway treads / stringers / landing | 3 / 2 / 1 | Timber descent into the open cabin; thin central sole with real bearer/foot contacts |
| Compartment partitions / sole bearer assemblies / stock box | 2 / 2 / 1 | Thin shell-seated panels relieved around centreline wood, notched sole bearers and hollow rudder boxing; interim mast pad replaced in M2 |
| Deck hatch coamings | 3 | White oak, with clear deck/below-deck passages; main footprint 6.5 × 5.5 ft; forepeak nearly flush and offset to port |
| Hatch cover boards / retaining cleats | 15 / 6 | Separate removable boards (4/8/3), two connected underside cleats per hatch; normally seated |
| Opening deck beams / carlings / half beams | 8 / 8 / 8 | Nominal 5.5-in-square pine timbers, cambered under deck; support/contact checks pass |
| Main pine clamp segments / companionway roof supports | 6 / 5 | Full-length frame-head-supported pine runs and traced roof framing; oak forward reinforcement separate; aft roof header split around doorway |
| Jib-sheet traveller | 1 | Athwartship bar and joined deck feet ahead of the mast |
| Helm | 1 set | Hollow wheel box, eight-spoke wheel, wheel axle, coaxial rudder shaft and upper bearing |
| Side rails / rubbing strakes | 6 | Painted oak rails |
| Stanchions / transom rails | 50 / 2 | Iron posts and bowed aft rails |
| Dredge winder | 1 set | Shouldered cross-braced frame, perforated drums, four bored bearings, two slotted drive wheels, brake/clutch controls and skids |
| Dredge rollers | 2 sets | Rollers and supports at the deck edges |
| Engine cover | 1 | Simplified enclosure ahead of the cabin |
| Pushboat davits / Samson post | 2 / 1 | Deck fittings; Samson post tapers from a 5-inch-square foot to a 14 x 5-inch head |

## Geometry checks

- Replaced a global spline loft after viewer feedback identified bow and side lobes. Local monotone interpolation and closely spaced ruled sections preserve the measured envelope.
- The hull stops at the underside of the separate deck to prevent overlapping visible surfaces.
- Every registered component is checked for one valid solid.
- Re-traced the rudder stock's dashed centreline on sheet 4: the head is at the existing wheel-box centre (3.1 ft forward of the transom), and the heel is farther forward beneath the counter. The stock rises aft at approximately **25 degrees from vertical**. The blade and upper shaft are coaxial overlapping solids, without an elbow or an external connecting rod.
- The counter and deck have a coaxial stock passage. The wheel box is hollow, the wheel axle enters its front face, and the stock enters its underside through an aligned upper bearing. Sheet 4 identifies hydraulic steering; hidden hydraulic internals are not reconstructed.
- The keel/deadwood ends forward of the inclined stock, joined to a matching sternpost. Bored gudgeons and local blade reliefs provide running clearance. The fused rudder and shaft were checked at **-35, 0 and +35 degrees**: no interference with the hull, deck, wheel box, keel, sternpost or bearings; the keel and sternpost have positive joining overlap.
- The main oak timber and separate worm shoe project about 9 inches below the main-body rabbet from station 5 (25.625 ft forward) onward. The aft timber/shoe follows a nearly straight, monotone heel-to-body run, with filling above it; the bow shoe tapers into the cutwater. The former 12.5-ft cutoff is superseded because it created a dip/hump.
- Pass 4: a direct cubic profile joins the rudder heel to the main keel with matching height/tangent, retaining oak/shoe thicknesses. Its straight-chord deviation is at most 0.39 inch. 35 actual CAD sections verify no reverse slope; a model assertion guards monotonicity. Positive solid contacts, eight main-body projection checks and -35/0/+35 steering clearances pass.
- Retracted the centreboard so the hull bottom is clean, matching the profile drawings and the under-power photos.
- Smoothed an isolated hollow in the sheer amidships (station 4) that read as a "weird bend"; the sheer is now flat at 6 ft through the middle stations.
- Rebuilt the bow after the gap review: lower lines now merge into the stem head instead of leaving a deep vertical face. The keel shoe follows the rising rabbet into the cutwater.
- The current forebody has independently faired longitudinal chine runs fitted to the offsets. The station 8.5 source reading 2-7-4 is retained and identified as a low-weight measured outlier. The old transverse collapse/V-blend is removed; it must not be restored.
- Upper/lower chine runs meet the lower stem at about 46.99/46.60 ft forward. Their fitted plan radii exceed 28 ft; topside and bottom battens end progressively at the stem. This follows the drawings' fore/aft planking and rounded chine rather than forcing the chines toward the deck-height bow endpoint.
- Source material constraints: estimated 2-inch hull strakes, mostly oak below/pine above the chine; oak frames; 1.75-inch deck planking; oak transom framing/moulding. Exact strake widths are irregular and not prescribed by the 9-inch ceiling-board width.
- The rudder blade height is reduced from 4.1 to 3.5 ft and its outline offsets are scaled consistently about the fixed head. This is an approximate proportional reconstruction, not a labelled historical dimension. The 25-degree axis and shaft entry under the wheel box are retained; steering regressions pass.
- Transom width checks at 11.3 ft versus about 11.4 ft traced from sheet 2. Its nominal centre depth was corrected from 1.35 to about 1.8 ft, excluding railwork, by changing the centre bottom to 4.8 ft. CAD dimensions, source comparison and stern regressions pass.
- The decorated bow piece is one centreline board, not two separated boards. Both relief faces and all lettering have positive overlap with the board, which seats into the bowsprit underside. Bow chains use alternating oval links fused at small contact patches for the static model.
- Pass 6 compacts KATHRYN to a band under 3.3 ft long and adds continuous scrolling vines with attached leaves, following the enlarged source detail. Both faces retain normal readable lettering and positive board attachment.
- Bowsprit/walking-board/cross-bearer attachment checks pass. The mast's buried heel stays inside the hull; its accepted rake and head location are retained. Boom/gooseneck and crutch/deck contacts pass; rubbing-strake fit was checked at seven positions on each side.
- Sheet 4's forepeak hatch is now 2.75 ft to port (+X) and 35.2 ft forward; the jib-sheet traveller is included. Samson-post foot/head dimensions follow sheets 5/6. Placement, side handedness and deck-contact checks pass.
- Pass 6 companionway sections verify the raked front; shaped panes embed into their frames. Both cambered roofs have positive wall/body seating, including the raised-house base on the main roof.
- Access continuation: both aft walls and the main-roof overhang have one aligned doorway extending to a 2.16-in sill above deck. Both cabin bodies are hollow; the main roof and deck open into a local access well. The paired glazed doors clear the enclosure, deck and helm at 0–90° in 15° increments, excluding their intentional hinge contacts.
- Access descent: three treads have positive contacts with both stringers; stringers join the sill and landing. Four equal risers are 7.29 in; going is 4.8 in; the landing is 27 in below deck. Actual-solid probes verify the doorway, steps, roof/deck passage and landing clearance. The worst sampled normal bottom-material thickness, including the aft corners, is 2.04 in, preserving the source's estimated 2-in strakes.
- Pass 6 winder checks verify frame/skid contact, four bearing/frame contacts with clear bores, drive-wheel/axle joining, brake/skid seating and control clearances from wheels and engine cover. Visible details are static exterior reconstructions, not dimensioned drivetrain manufacturing models.
- Increased the mast rake from 7 ft to 14 ft (12.6 deg), matching the strongly raked skipjack mast.
- Current reviewed assembly: **446 parts**, 1:1, build OK/no warnings; `output/model.step`. Overall stern fidelity is not accepted. Governing evidence, remedy and closure criteria: `STERN_REVIEW_AND_REMEDY_SPEC.md`; general milestones held.
- M3 checks prove 9,955 distinct exterior samples, all frame bottom/head bearings, primary mortises versus uninletted repairs, 78 open drains, 54 clear bays, five board poses and steering clearance. Fixed registered frame-4/13 shell-guide RMS is 1.538/1.733 in; source vertical references remain separate.
- M3 primary/repair dimensions are independent of deck-beam averages. Frame 1 uses the actual cavity section to avoid a fine-bow seating gap. Main clamps now sit on frame heads; exact board/panel/deck laps remain M4/M5 work.
- M2 performance correction: smooth trunk lofts and adaptive keelson sections preserve the base to 0.0562 in while reducing unnecessary faces. Reusable exact classifiers replace repeated broad passage booleans. No app time limit was increased.
- M1 actual-solid evidence: 105 distributed air points, four transverse sections, 144 normal-ray material checks and local bearing contacts. Representative source shell-guide RMS is 1.13/0.88 in; section planes are shape-registered, not confirmed frame-number locations.
- Inspect in SOMA by hiding `Deck/Planking` and `Deck/Cabin/Roofs` plus covers/equipment as useful; retain the hull planking and `Interior/` groups. Reproduce overview/cutaway/section overlays with `python checks/render_m1.py`.
- Hatch/local-framing evidence: `renders/hatch-review.png`, `hatch-source-comparison.png`, `hatch-scale-measurements.png`, `hatch-deck-closed.png`, `hatch-deck-open.png`, `hatch-hold-section.png`, `hatch-framing-plan.png`. The hull has local under-deck relief and hatch shafts to a bottom offset targeting 2.24-in material; the complete interior/frame station schedule is the next stage.
- Latest access views: `renders/kathryn-companionway-review.png` (before/after, open and cutaway), `kathryn-companionway-source-comparison.png`, `kathryn-companionway-open.png`, `kathryn-companionway-cutaway.png`; current closed view is `kathryn-cabin-detail.png`. Source crops are retained in `renders/kathryn-access-source-profile.png` and `kathryn-access-source-plan.png`. Reproduce with `python checks/render_companionway.py`.
- Final matched views: `renders/pass6-plan-comparison.png`, `renders/pass6-side-comparison.png`. Detail views: `kathryn-cabin-detail.png`, `kathryn-winder-detail.png`, `kathryn-winder-isolated.png`, `kathryn-bow-carving.png`. The isolated winder view hides the engine cover for inspection only.
- Construction/size comparisons: `renders/kathryn-planking-review.png` (illustrative gold topside/blue bottom battens), `kathryn-chine-comparison.png`, `kathryn-transom-comparison.png`. Battens are review overlays, not a production spiling/cutting schedule.
- Keel profile and actual CAD section: `renders/kathryn-hull-profile.png`, `renders/kathryn-keel-section.png`.
- Aft-keel correction comparison: `renders/kathryn-aft-keel-check.png`; refreshed assembly views show the corrected continuous run.
- Bow views: `renders/kathryn-bow-port.png`, `kathryn-bow-starboard.png`, `kathryn-bow-plan.png`, `kathryn-bow-entry.png`, and `kathryn-bow.png`.
- Rudder alignment views: `renders/kathryn-rudder-side.png` and `renders/kathryn-rudder-cutaway.png`; the cutaway highlights the stock/blade and bearings to show entry into the wheel box.
- Reliable local renders: `renders/kathryn-iso.png`, `kathryn-side.png`, `kathryn-bow.png`, `kathryn-stern.png` (VTK EGL on `.soma/model.glb`). Earlier Matplotlib check pictures have drawing-order artifacts.
