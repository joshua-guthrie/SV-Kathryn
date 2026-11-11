# Kathryn — board-level interior goal and research plan

Checkpoint: M0–M3 complete; **439-part** hollow enclosure, centreline and frame
structure are built and verified. M4 individual boards/deck integration is next.

## M3 frames and repair members — complete

Full member/source table, acceptance and source qualifications:
`milestones/M3.md`. Geometry ledger: `drawing_package/m3_frame_schedule.json`;
reproduction: `checks/measure_m3_frames.py`, `checks/prepare_m3_sources.py`.

154 frame pieces and 15 supports include primary mortises, uninletted companions,
continuous floors below the keelson at 19/20, open limbers, rounded replacement
knees, full pine clamps/oak forward reinforcement, stanchions, strongback and
stem/transom members. Numbering is independently registered; the printed
stern-knee conflict is retained. Twenty numbered exposed sets, five hidden cabin
continuations and two aft sets have explicit per-member measurement/inference
bases. Some secondary pairings and individual dates remain unresolved.

Source older stipple qualifies 22 bottom-member records as possibly original;
side-futtock age is not inferred from that identification. S06 links the newer
frame family to 1954, without proving a date for every modeled companion.
The Samson post is the source's 1995 replacement, now seated in its stem knee.
S04 deck/profile review also corrects an inherited inboard bowsprit extension:
the heel is at F52.770, clearing the post, with real headrail/chock/bearing seats.

Checks: 9,955 distinct exterior samples, all frame bearings, mortises and 78
limbers, 54 clear bays and moving-board/steering regressions pass. Source frame-4
and frame-13 planes are fixed longitudinally: shell-guide RMS 1.538/1.733 in.
Named local vertical datums remain separate from corrected-keel coordinates.
Latest build: 439 parts, no warnings, 304.0 s. Inspection: `renders/m3-review.png`,
`renders/m3-forepeak-headwork.png`, `renders/m3-section-S06-V01.png`,
`renders/m3-section-S07-V01.png`. Machine records: `checks/m3_acceptance.json`,
`checks/m3_section_comparison.json`.

## M2 centreline structure — complete

See `milestones/M2.md` for the member/source table, acceptance and unresolved
fine-joint/stowage evidence. Measurements and source hashes:
`drawing_package/m2_centreline_measurements.json`; actual-solid records:
`checks/m2_acceptance.json`, `checks/m2_source_comparison.json`.

Two oak keelson sections (14/16-in widths, complementary scarf), eight separate
2 × 11.5-in pine trunk courses, rails/ends, true shoe-to-trunk slot, traced board
and pivot are modeled. The temporary mast pad is replaced by a mortised keelson,
iron heel hoop, faceted lower mast, 2-in pine chocks, 3.5 × 11-in oak partners and
supported lapped carlings. Inaccessible aft continuation and fine joinery remain
declared inferences; possible originality of the forward timber is not certainty.

The -17-degree board trial fouled a hatch beam; the -15-degree displayed pose
and three intermediate poses clear actual structure. This is a reproducible
clearance state, not certification of full historic stowage. Case end rakes/notches
and frame/deck references remain targets for source refinement in M3/M5.

Latest complete build: 269 parts, no warnings, 379.7 s. Adaptive timber lofts
resolve the 600-second timeout while retaining the keelson base within 0.0562 in.
Inspection: `renders/m2-review.png`, `m2-mast-supports.png`,
`m2-source-profile-comparison.png`, all under `renders/`.

## M1 accepted enclosure

See `milestones/M1.md` for acceptance, model/source corrections and gaps.
`renders/m1-review.png` shows the actual open-deck/cutaway model. The continuous
shell uses 7.63% of its equivalent filled exterior-envelope volume; 105 air
samples, 144 normal-ray checks, four sections and actual supports pass.

M1 migrated source coordinates and corrected a crucial older reference error:
offset-table Sheer is the underside of sheer strake, while Top of Deck is a
separate higher/wider curve. Native picks are retained in
`drawing_package/sheer_band_measurements.json`. Source-shell guide RMS is now
1.13/0.88 in on representative 6a/7a comparisons; plane identity remains inferred.
The source records, model envelope and exact keel/frame-plane references must
remain distinguished in M2/M3.

## Governing specification and milestone terminology

The user approved the comprehensive plan, requested **milestones** rather than
iterations, confirmed **include the repairs** and **accurate inspectable historic
CAD model**, and added initial drawing conversion/preparation as a milestone.
`INTERIOR_SPEC.md` governs outcomes and acceptance: **M0** AI-ready references /
registration, followed by five construction milestones **M1–M5**. The research
and earlier local-hatch evidence below are inputs, not milestone completion.

## M0 reference package — accepted

Start at `drawing_package/index.html` or `INDEX.md`. The package contains eight
indexed sheets, 51 lossless native views, 498 tiles, 4,623 coordinate-linked OCR
words, 58 checked construction records, all source offsets, six ruler calibrations
and two complete section demonstrations. Raw OCR is not the checked data layer.

Key files: `manifest.json`, `notes_verified.json`, `offsets_verified.json`,
`calibration.json`, `registration.json`, `demos/S06-V01.html`,
`demos/S07-V02.html`, `traces/`, `ACCEPTANCE.md`, `validation.json`, all under
`drawing_package/`. Reproduction commands are in its README.

M0 established source coordinates and a legacy-CAD migration ledger. M1 has
applied the principal hatch/mast/station coordinates. Sheet-4/5 deck landmarks align within
0.102 ft, but original/repaired members and corrected/as-built drawing conditions
must remain distinguished. Source interpretation found a sheet-6 metric-caption
conflict and separate line/deck-beam/hull-frame numbering systems; these are
documented instead of silently rewritten.

## Goal

Reconstruct the interior as identifiable individual timbers and boards: structural
framing, opening supports, keelson/trunk interfaces, lining, floors, bulkheads
and cabin furnishings. The user explicitly authorized measuring unlabelled
dimensions from the scaled drawings and researching skipjack construction,
including a book they supplied. This expands the earlier exterior-only scope.

Keep the evidence for each member or dimension identifiable:

- **Dimensioned:** a printed measurement or material note; cite sheet/note/page.
- **Scale-measured:** measured from a calibrated drawing view; retain the view,
  reference distance, pixel measurement, conversion and practical uncertainty.
- **Construction-inferred:** inferred from construction evidence; cite the book
  page, report or historical source and explain its application to Kathryn.

## Drawing measurement rules

1. Use original TIFFs for measurements. Thumbnails and enlarged review crops are
   viewing aids; their pixel sizes do not establish full-size dimensions.
2. Calibrate each view/detail separately using its scale bar and/or a labelled
   distance. Different views on the same sheet can have different scales.
3. For a reference of `R` full-size feet spanning `P` pixels, a measured span of
   `p` pixels gives `p * R / P` feet. Check a second known distance where possible.
   Check horizontal/vertical scaling and scan skew rather than trusting image DPI.
4. Cross-check plan, profile and sections. Record line-weight/measurement
   uncertainty and avoid claiming precision unsupported by the drawing.
5. Check what a reference dimension measures: registered length, deck length,
   waterline length and overall length need not be interchangeable. Compare
   source calibration with the current normalized 50-ft model datum before
   transferring new member positions; document and resolve discrepancies.
6. Keep full-size source feet separate from the final model scale
   (`304.8 / MODEL_SCALE` millimetres per source foot).
7. A readable, calibrated feature can supply a dimension without a printed
   numerical label. If essential evidence is unreadable, stop and notify the user.

## Construction research rules

- Kathryn's own measured drawings, notes and vessel-specific documentation
  govern its arrangement, materials and geometry.
- Use the supplied book and credible historical/shipyard references to explain
  construction sequence, joints, plank fastening, framing and load paths.
- Distinguish vessel-specific evidence from general skipjack practice and later
  restoration work. Kathryn's fore-and-aft bottom planking and rounded chine
  are essential; generic cross-planked, hard-chine examples cannot substitute.
- Record the actual page/figure/URL and the detail it supports before adopting
  a construction inference. Search snippets and bibliographies are leads.

## Source inventory and research status

| ID | Source | Reviewed / use |
|---|---|---|
| K-01 | Local HAER MD-117 sheets 1–8 in `2d model/` | Primary geometry. Sheets 4–7 read. Sheet-4 hatch footprint/ruler calibration is saved in `checks/hatch_measurements.json`; full longitudinal station registration remains pending. |
| S-01 | Local HAER MD-77 E. C. Collier descriptive report, `sistership/Two-Sail Bateau E. C. COLLIER, Chesapeake Bay Maritime Museum, Mills Street, Saint Michaels, Talbot County, MD/master-pnp-habshaer-md-md1200-md1203-data-md1203data.pdf` | Read. Printed pp. 2–4 (PDF pp. 3–5) describe materials, strongbacks/tie rods, crowned beams, natural-crook knees, notched replacement frames and interior alterations. Comparative construction evidence, not Kathryn dimensions. Printed p. 12 lists Chapelle references. |
| W-01 | [CBMM working Shipyard](https://cbmm.org/shipyard/) | Page read 2026-11-07; identifies the museum's traditional construction/preservation work and Rosie Parks restoration in 2011–2013. Useful route to technical restoration records; no specific joint detail adopted from the overview. |
| L-01 | [CBMM, The Chesapeake Log, Summer 2012](https://cbmm.org/resources/the-chesapeake-log-summer-2012/) | Landing page read; advertises Rosie Parks restoration coverage. Underlying article/issue still to obtain and review. |
| K-02 | [Kathryn HAER descriptive data, CAMM-hosted PDF](https://councilofamericanmaritimemuseums.org/wp-content/uploads/2024/12/kathryn-data.pdf), saved as `Reference Material/Kathryn HAER MD-117 descriptive data.pdf` | Construction/alteration discussion reviewed, printed pp. 2–4. Fully framed fore-and-aft bottom; original frames inletted to keelson, later sisters not inletted; three narrow chine planks and no chine log. White-oak hatch coamings; forepeak lowered nearly flush in 1981. |
| L-03 | [Kathryn National Historic Landmark nomination](https://npgallery.nps.gov/pdfhost/docs/NHLS/Text/94001192.pdf) | Located through online search; full document not yet reviewed. |
| B-01 | Howard I. Chapelle, *The Migrations of an American Boat Type*, `Reference Material/Migrations of an American Boat Type.pdf` | Found in the resumed workspace. Relevant construction discussion reviewed: printed pp. 137–139 (sharpie structure) and 146–149 (building sequence/Chesapeake development). This is a sharpie/development study; use its comparative methods with Kathryn's own construction evidence. |

The LOC catalogue page returned HTTP 403 during research; the local TIFFs remain
readable. That web retrieval failure is not a source-drawing readability failure.

## Timber evidence already read

| Item | Evidence |
|---|---|
| Deck beams | Sheet 5 note 7: beams 1–3 are 6 × 4¾ in pine; beams 4–23 average 5½ in square (±½ in), pine except 12–15 oak under the winders. Members beside hatches/cabin are counted as paired sets. |
| Deck clamp | Sheet 5 note 6: 5½ × 2¾ in pine; forward reinforcement with 5½ × 2¾ in oak. |
| Deck planks | Sheet 5 note 8: mainly fir/pine with oak replacements, 1¾ in thick, typical widths 3½–4 in, some inboard boards 5–7 in. |
| Interior ceiling/lining | Sheets 5–7: approximately 1¾ in pine, roughly 9 in wide with variation. These widths are not hull-strake widths. |
| Hull strakes | Sheet 7 note 10 / sheet 1: estimated 2 in thick, irregular widths, generally oak below/pine above the rounded chine; bottom planking runs fore-and-aft. |
| Frames | Oak; old/new members and shapes vary. Portions were inferred by the survey from exposed structure, probing and nail patterns. |
| Fastenings | Sheet 5 general note identifies drift pins between keelson sections and nails among observed hull fastenings; a complete fastening layout is not recorded. |

## Milestones and acceptance

| Milestone | Outcome | Current state |
|---|---|---|
| M0 | Indexed AI-ready drawing package, searchable/checked notes and tables, per-view calibration and common registration | Complete; acceptance and validation in `drawing_package/` |
| M1 | Continuous hollow planked enclosure and real cabin/hold/forepeak volume | Complete; `milestones/M1.md` and `checks/m1_acceptance.json` |
| M2 | Keelson, centreboard trunk and centreline supports | Pending |
| M3 | Hull frames, clamps, knees and documented repair/sister members | Pending; local opening supports are prior work |
| M4 | Complete deck integration and individual planking/lining/floor/bulkhead boards | Pending |
| M5 | Cabin fit-out, whole-vessel inspection and final fidelity/gap review | Pending |

Full deliverables and acceptance criteria are in `INTERIOR_SPEC.md`. A milestone
may require several modeling/review cycles; there is no five-build shortcut.

At each usable increment: build, inspect sections/cutaways against the sources,
verify member support/contact and opening clearances, run relevant existing
regressions, then update the member list and gap report. Name/register separate
members so they can be inspected in SOMA; cosmetic seam lines alone do not
satisfy the board-level interior goal.

## Completed first increment — hatches and local opening supports

Historical local-opening checkpoint: **235 parts**, no warnings, 1:32. It is
superseded by M1's 241-part continuous hollow enclosure; this section retains
the earlier footprint/member evidence.

### Scale-measured footprints

`python checks/measure_hatches.py` records original-TIFF pixel coordinates and
reproduces `checks/hatch_measurements.json` / `renders/hatch-scale-measurements.png`.
The 0/10/50-ft ruler gives **150.75 native pixels/ft**, agreeing within 0.5% with
the 400-dpi, 3/8-in-per-foot printed scale (150 px/ft). Footprint picks have an
estimated ±0.15-ft uncertainty. The measured outer widths × lengths are:

| Hatch | Scale-measured feet | Adopted feet | Clear opening inches |
|---|---|---|---|
| After deck | 3.195 × 3.400 | 3.2 × 3.4 | 31.4 × 33.8 |
| Main hold | 6.522 × 5.533 | 6.5 × 5.5 | 71.0 × 59.0 |
| Forepeak | 2.063 × 2.000 | 2.0 × 2.0 | 17.0 × 17.0 |

**Registration finding I-M02:** the earlier model uses a normalized 50-ft hull
datum and approximate arrangement centres. The raw scaled drawing coordinates
are not yet reconciled across the hull, mast and all deck fittings. This increment
uses measured hatch footprints, but retains existing forward centres
17.5/31.1/35.2 ft and forepeak port offset 2.75 ft. They must not be described as
newly verified full-size station measurements. Establish the common drawing/model
registration before extending the complete interior frame schedule.

### Member evidence and representation

| Member family | Count | Evidence / method |
|---|---:|---|
| White-oak hatch coamings | 3 | Material: Kathryn HAER pp. 3–4. Footprints scale-measured. 3.5-in wall and above-deck heights 0.75/0.90/0.06 ft are traced/construction-inferred. |
| Individual removable cover boards | 15 (4/8/3) | Separate named boards. 1.5-in thickness, small overhangs/gaps and board division are reconstruction details; no cosmetic-only seam substitute. |
| Underside cover cleats | 6 | Two retaining cleats per hatch, joined to every board; fine dimensions inferred. |
| Aft/fore deck support beams | 8 | Two per hatch/companionway opening; cambered sections are the sheet-5 average 5.5-in square. Local positions follow the current opening interfaces, not a complete original frame-number schedule. |
| Longitudinal opening carlings | 8 | Two per opening, same nominal section, following the paired opening-side framing arrangement on sheet 5. |
| Cambered half beams | 8 | Two per opening, joining carlings to clamps; sheet-5 member section. |
| Local pine clamp members | 6 | 5.5 × 2.75 in from sheet 5 note 6. Main/forepeak share each forebody clamp instead of overlapping duplicate members. |
| Companionway roof supports | 5 | Two carlings, split aft header and fore header. Traced 0.20 × 0.22-ft sections; aft header is split to keep the full-height doorway clear. |

The 35 opening-support timbers are separately named in `Interior/Opening framing`.
The hull is relieved locally below these members, and hatch shafts reach an
inward-offset bottom surface. The offset targets 2.24-in material, retaining a
margin over the estimated 2-in strakes. This is a local opening-support increment;
the rest of the original filled reference hull is still to be replaced as the
full interior structure is reconstructed.

### Verification and evidence

- `python checks/check_hatches.py`: clear passages, cover seating and vertical
  removal at 0/0.05/0.5/1.5 ft; board/cleat connections; header/carling/half-beam/
  clamp contacts; actual 5.5-in-square sections; roof support joints; 75 bottom
  normal-ray samples; mast/framing clearance.
- `python checks/check_companionway.py` now includes all the new framing among
  its obstacles. Doorway, stairs, landing, bottom thickness and 0–90° door sweep pass.
- Prior detail, bow/attachment, chine/transom, body-keel, 35-section aft-keel and
  -35/0/+35 rudder regressions pass.
- `renders/hatch-review.png`, `hatch-source-comparison.png`,
  `hatch-deck-closed.png`, `hatch-deck-open.png`, `hatch-hold-section.png`,
  `hatch-framing-plan.png` inspected. Source comparison is explicitly the local
  support subset; the full frame schedule and station registration are pending.
- Reproduce views with `python checks/render_hatches.py`. Normal assembly has
  covers seated; open/section/isolated-support views are inspection views.

## Next milestone

Start **M2** using M0's checked references and M1's actual shell/bearing geometry.
Complete the keelson, centreboard slot/trunk and centreline joints, then proceed
to M3's full frame/repair schedule. Keep section-plane identity and corrected/
as-surveyed references explicit; later M4/M5 provide boards and cabin fit-out.
