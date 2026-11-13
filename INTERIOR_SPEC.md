# Kathryn — inspectable interior specification and milestones

## 1. Goal and agreed decisions

Reconstruct Kathryn so the entire interior can be inspected as a credible wooden
oyster-dredging and transport vessel: planked enclosure, individual structural
members, usable cabin/hold/forepeak spaces and the documented interior fit-out.

- The user approved the comprehensive-specification approach and requested that
  the five planned outcomes be called **milestones** from now on.
- The user explicitly confirmed: **include the repairs**. Represent documented
  original and replacement construction, including sistered frames, replacement
  timber/planking and altered fittings. Preserve the distinctions where supported
  by the survey.
- Kathryn's supplied HAER measured drawings and descriptive record are the
  historical baseline, including the repairs and alterations they document.
- Dimensions may be obtained from calibrated scaled drawings. The supplied
  Chapelle book and historical construction research support details omitted
  from the vessel-specific record.
- The user confirmed the end use: **an accurate, inspectable historic CAD model**.
  Geometry, member organization and inspection views serve that purpose.
- The user requested an **initial drawing-preparation milestone** if converting
  the TIFF references would improve interpretation. This is M0, preceding the
  five construction milestones M1–M5.

M0–M3 delivered reference, enclosure, centreline and framing increments. The
current 446-part model has genuine interior space and separate frame/repair
members, but its stern fidelity is reopened and not accepted. M4/M5 cover
individual boards, deck integration and fit-out and are currently on hold.

## 2. Geometry requirements

| ID | Requirement |
|---|---|
| INT-01 | Replace the filled reference hull and isolated pockets with a continuous interior enclosure following the hull/planking thickness. Cabin, hold and forepeak must contain genuine space, divided only by represented structure and documented partitions. |
| INT-02 | Represent wood as the actual planks, timbers and furnishings occupying that space. Individual pieces can be solid material; broad solid volumes must not substitute for open accommodation or cargo space. Local stem, stern and deadwood masses must follow the evidence. |
| INT-03 | Reconstruct the keelson, mast support, centreboard trunk, frames, clamps, beams, carlings, knees and other depicted structural members, with source-supported sizes and credible joining/support relationships. |
| INT-04 | Follow Kathryn's fully framed, fore-and-aft bottom planking and rounded chine: three narrow chine planks, side frames meeting bottom frames, and no generic skipjack chine log. |
| INT-05 | Include original and repaired member arrangements. In particular, distinguish original bottom frames inletted into the keelson from later sister frames that were not inletted, as described in Kathryn's survey. |
| INT-06 | Model individual lining, floor, deck and bulkhead boards where the evidence supports their arrangement, plus berths, settees, cabinets and other depicted fit-out. Plain seam lines on a filled body do not constitute board-level construction. |
| INT-07 | Hatches, companionway, doors and other openings must connect to the correct spaces. Covers, thresholds, stairs and roof/deck openings must have continuous clear paths and represented supports. |
| INT-08 | Preserve and verify the established exterior, chine/keel and steering relationships while adding the interior. Any source-driven change to the common datum or accepted exterior dimensions must have documented evidence and downstream checks. |
| INT-09 | Prepare an AI-readable, searchable and calibrated reference package from the scanned drawings, preserving a traceable relationship to the original pixels. Its converted text and geometry must be checked against the source before driving CAD. |
| INT-10 | Keep the offset-table underside-of-sheer-strake reference separate from the actual Top-of-Deck curve. Model the source-derived upper band and flare; do not remove usable depth/freeboard by treating the lower reference as deck level. |

## 3. Sources, measurement and repair evidence

### Primary construction views

- Sheet 5a: structural/hold plans, beam/member arrangement and timber notes.
- Sheet 6a (`2d model/master-pnp-habshaer-md-md1400-md1454-sheet-00006a.tif`):
  frame-set sections and structural conception, including connections among
  planking, bottom/side frames, keel/keelson and deck structure.
- Sheet 7a (`...sheet-00007a.tif`): frame-set 13 and cabin-hatch sections,
  interior arrangement, lining, deck/roof supports and material notes.
- Sheets 1–4 and Kathryn HAER descriptive data: hull identity, offsets,
  arrangement, unusual construction and repair/alteration history.

Use Kathryn-specific evidence first. The Chapelle book, E. C. Collier record and
shipyard/historical references provide comparative construction evidence; apply
them with the vessel's differences explicitly considered.

Each member family—and individual member where its history or geometry differs—
needs an evidence record containing:

1. Part/member ID, location, section size and material.
2. Source sheet/note/figure/page or URL.
3. Dimension basis: **dimensioned**, **scale-measured**, or **construction-inferred**.
4. Repair state: documented original, replacement/sister/patch, or unresolved.
   Include the documented date/period when known.
5. Measurement uncertainty or the assumption used for an obscured detail.

Measure original TIFF geometry using a view-specific scale bar or known dimension;
cross-check another known distance and the other projections. Do not assume all
views share a scale or treat register/deck/waterline/overall lengths as equivalent.
Full-size source feet remain separate from the model's millimetre scale.

The principal **I-M02 longitudinal-registration gap** was resolved in M0/M1:
source stations, hatch centres and mast references follow the checked ledger.
M3 adds an independent hull-frame schedule supported by plan, captions and scarf
evidence. Inaccessible bays, some individual pairings and local vertical datum
differences remain explicitly qualified reconstruction inputs.

Documented repair evidence already available includes the 1954 rebuilding and
sister frames, replacement deck/clamp/lining materials, white-oak coamings, and
the later forepeak, doghouse, steering/rudder and fitting alterations described
in the survey. Record the source for the particular condition being modeled;
do not combine incompatible repair states or invent exact patch locations.

## 4. Inspection and assembly organization

- Group hull/planking, structural framing, keelson/trunk, deck/roof, interior
  lining, furnishings and removable covers so each can be inspected separately.
- Give individual timbers and boards stable, meaningful names. Record repair
  identity in names or member metadata where useful.
- Support useful assembled, deck/roof-hidden, transverse-section and longitudinal
  cutaway views. Opening only a hatch must not be the sole way to see the interior.
- Keep inspection visibility/cutaway states reproducible and distinguish them
  from the normal complete assembly.
- Retain the source-coordinate convention. The user's current scale is full-size
  **1:1**, with millimetre CAD/export units; the denominator control spans1–64.
  Feet/inches are used in source reports. Installed SOMA measurements display mm.

## 5. Milestone roadmap — M0 preparation, M1–M5 construction

A milestone is an **accepted outcome**, not a fixed number of edits, builds or
review cycles. Several modification → build → comparison → gap-analysis cycles
may be needed within one milestone.

### M0 — AI-ready drawing package and common calibration

**Purpose:** make the scanned references easier to inspect, search, measure and
cross-reference before further modeling. The TIFFs contain raster drawings;
conversion improves access and interpretation, not their underlying detail.

**Deliver:**
- An indexed overview for each of Kathryn's eight main-vessel sheets, with
  stable IDs for individual plans, sections, details, scales, tables and notes.
  Prioritize the structural plans and sections on sheets 5a, 6a and 7a.
- Lossless, readable detail crops/tiles at useful viewing sizes, with original
  native-pixel crop bounds and any resize/rotation transforms recorded.
- Searchable OCR text for titles, annotations and construction notes; structured
  tables for critical offsets, timber sizes, material notes and repair evidence.
  Review critical values and mark uncertain readings explicitly.
- A searchable PDF or indexed contact-sheet document for navigation, linked to
  the lossless detail images and extracted records.
- A per-view calibration and coordinate ledger: units, ruler/dimension anchors,
  scale, orientation, common boat datum and cross-sheet registration checks.
  Resolve I-M02 sufficiently to place the full interior member schedule.
- Where useful for CAD, checked vector traces of selected boundaries/centreline
  features in SVG/DXF or structured point/curve data. Retain source overlays and
  labels so image edges, construction lines and actual member boundaries remain
  distinguishable. Automatic tracing is a draft requiring source comparison.
- Reproducible conversion/extraction scripts and an inventory connecting each
  derived asset to its source filename, view ID and original dimensions.

**Acceptance:**
- The original TIFFs are preserved; all derived assets are traceable to them.
- Each important view on sheets 6a/7a can be located and read without repeatedly
  opening the full oversized scan; its notes and member references are searchable.
- Critical timber dimensions, source offsets and material/repair notes are
  spot-checked against the original; OCR uncertainty is never silently converted
  into an authoritative dimension.
- Per-view scale checks use known distances and agree across relevant plans and
  sections to recorded measurement uncertainty. Boat/view origins and member
  stations are consistent or remaining discrepancies are explicitly resolved.
- Selected vector/point geometry agrees with a source overlay and preserves
  the original measured readings separately from any faired reconstruction.
- The package is demonstrated on at least one complete section from each of
  sheets 6a and 7a, including notes, member IDs, dimensions and calibration.

### M1 — Continuous hollow hull and inspectable spaces

**Deliver:** a continuous planked enclosure with genuine interior volume from
stern to bow, including realistic transom/stem transitions and the relevant
cabin/hold/forepeak separations.

**Acceptance:**
- Deck-hidden and longitudinal cutaway views reveal the vessel's interior volume
  instead of isolated shafts bounded by filled reference material.
- Transverse sections follow the source's shell/planking envelope and material
  thickness; no missing shell, unintended bottom breach or residual filler block.
- Existing access, steering and exterior-envelope checks are appropriately
  updated and pass. A former test requiring a mast heel to be buried in filled
  reference material must instead verify its enclosure/support in the real boat.

### M2 — Keelson, centreboard trunk and centreline supports

**Deliver:** the source-based keel/keelson relationship, open centreboard slot
and trunk, mast support and associated centreline structural connections.

**Acceptance:**
- Trunk walls, slot and surrounding structural members are separately identifiable
  and agree with plan/profile/section evidence.
- These members have credible material/support relationships and preserve the
  required interior and access space.
- Source-supported repairs, joints and material changes are recorded and modeled
  to the chosen historical baseline.

### M3 — Hull frames, clamps, knees and repair members

**Deliver:** a registered member schedule and individually modeled bottom/side
frames, clamps, knees, strongbacks and documented sister/replacement members.

**Acceptance:**
- Representative sections match sheets 6a/7a in arrangement, shape and section
  sizes; deck-beam averages are not substituted indiscriminately for hull frames.
- Original inletted frames and later uninletted sisters are distinguishable where
  the evidence supports them; Kathryn's no-chine-log construction is respected.
- Framing seats against the correct shell/centreline/deck interfaces, with
  supported ends and documented intentional joints.

### M4 — Deck structure and individual planking/lining

**Deliver:** complete deck/opening support integration and board-level hull,
deck, lining, floor and bulkhead representation consistent with the evidence.

**Acceptance:**
- Separate boards/timbers account for the represented material, with appropriate
  thickness, runs, joints and supports. Board seams are construction features,
  not a visual treatment concealing large filled volumes.
- Openings and useful interior spaces remain clear; ceilings/lining can be hidden
  to inspect framing and repair members behind them.
- Known irregular timber sizes and replacement areas are preserved or explicitly
  identified as inferred; board widths are not borrowed from unrelated components.

### M5 — Cabin fit-out and whole-vessel fidelity review

**Deliver:** source-based cabin/hold/forepeak fit-out and a complete inspection
set, member evidence list and final gap analysis.

**Acceptance:**
- Berths, settees, cabinets, partitions, steps and depicted fittings occupy their
  proper spaces with represented construction and access.
- Whole-vessel longitudinal cutaways and matched transverse sections demonstrate
  the combined shell, structure, repairs, boards and fit-out.
- All applicable support, clearance, thickness, access and exterior regressions
  pass; unresolved historical details remain clearly identified in the gap report.
- The user can inspect the entire interior by hiding logical assemblies, with
  stable part names and a current SOMA/STEP checkpoint.

## 6. Review and milestone closure

For each milestone:

1. Record the source/member measurements and current gaps.
2. Implement a usable increment and build it in SOMA.
3. Compare actual sections and cutaways with the corresponding drawings,
   especially sheets 6a/7a; a valid solid alone is not a fidelity acceptance test.
4. Verify genuine interior voids, material thickness, member support and relevant
   clearances. Distinguish intentional timber joints from unintended intersections.
5. Update the gap report with finding, evidence, correction and verification.
6. Close the milestone only after its acceptance criteria pass; carry forward
   unresolved evidence questions explicitly.

The final review after M5 reports the outcome against this specification. M0
prepares the evidence for the five construction milestones; it is not counted
as one of those five outcomes. Historical review-pass counts remain historical.

## 7. Current checkpoint and next milestone

- **2026-11-13 checkpoint:** 841-part 1:1 model. M4 deck planking is complete;
  the M5 cabin fit-out and whole-vessel inspection set (sole, settees, lining,
  stove, table, lockers, cutaway/evidence) are built and checked. M4 side
  planking/individual side lining and the measured waterway remain open.
- **2026-11-11:** the user authorized independent stern review followed by
  M4/M5 without another approval round. That review passed:
  `STERN_INDEPENDENT_REVIEW.md`.
- The historical M1–M3 entries below describe delivered increments and historical
  geometry checkpoints.

- Historical M3 geometry checkpoint: **439 parts**, successful build with no warnings,
  **304.0 s** (below the 600-second application limit).
- **M3 is complete:** individual primary/repair-pattern frames, real mortises,
  under-keelson floors, limbers, frame-head clamps/reinforcement and centreline/
  aft supports. Fixed registered source comparisons and clearance/material checks
  pass. Source limits and acceptance: `milestones/M3.md`,
  `checks/m3_acceptance.json`, `renders/m3-review.png`.
- **M2 is complete:** separate oak keelson/scarf, eight pine trunk courses, real
  board passage/pivot and integrated mortised mast/partners/chocks. Acceptance,
  fine-joint/stowage inferences and review: `milestones/M2.md`,
  `checks/m2_acceptance.json`, `renders/m2-review.png`.
- **M1 is complete:** continuous hollow enclosure, thin partitions, real local
  supports, corrected source/deck references and inspected full cutaways. See
  `milestones/M1.md`, `checks/m1_acceptance.json` and `renders/m1-review.png`.
- **M0 is complete:** indexed reference package, checked records, calibrated
  coordinate ledger and section demonstrations are in `drawing_package/`.
  Acceptance: `drawing_package/ACCEPTANCE.md`; validation: `validation.json`.
- Next action: **M4**, individual hull/deck/lining/floor/bulkhead boards and the
  complete deck-member/joint integration. Use the existing shell/frame/centreline
  interfaces; retain source/repair qualifications and corrected/as-surveyed
  distinctions while refining inaccessible or ambiguous details.
