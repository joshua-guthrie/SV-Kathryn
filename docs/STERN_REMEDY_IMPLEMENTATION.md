# Kathryn — implemented stern remedy and review checkpoint

**Implementation and source/geometry checks complete; ready for the user's stern review.**
**M4/M5 remain on hold.** The original specification and its baseline figures are
preserved in `STERN_REVIEW_AND_REMEDY_SPEC.md` and `renders/stern_review/`.

This checkpoint implements the complete stern work order, including the user's
additional [aft-quarter concavity markup](.soma/feedback/markup-20261110-2259.png).
It does not convert inferred hidden construction into observed historical fact.

## 1. Current verified model

| Item | Result |
|---|---|
| Registered assembly | **542 valid single-solid parts**, build `ok`, no warnings |
| Scale and units | **1:1; 304.800089 mm per source foot; STEP explicitly millimetres** |
| Recorded 50-ft reference | **15,240 mm**, separate from physical wood/fitting bounds |
| Captured successful build | **415.49 s** total, within the existing600-s limit |
| Build stages | Model333.812 s; STEP10.443 s; GLB65.945 s |
| Accepted-input/source ledger | `references/drawing_package/stern_remedy_targets.json` |
| Actual-CAD check record | `checks/stern_remedy_acceptance.json` |
| Mesh/source provenance | `renders/stern_remedy/provenance.json` |
| GLB SHA256 | `70f413f7f4acedf0faec5b0f9cae88c8586acc48a2a5f9e4e8f176cf9fffe6df` |

The image generator rejects an export older than the current geometry sources.
The reviewed assembly is the actual export, rather than a substituted proposed
surface or a render of only the construction references.

## 2. Before and after

| Preserved baseline | Implemented stern |
|---|---|
| ![Baseline defects](../renders/stern_review/cad-quarter-annotated.png) | ![Implemented stern](../renders/stern_remedy/quarter.png) |

The new stern has separate rectangular oak rails, a source-controlled curved
outside timber edge, a correctly anchored counter, registered oak moulding,
the traveller, braced iron davits, rigid tackle, external bumper and controls.

### The two concave regions identified in the markup

![Actual rebuilt plan, including fair quarter-to-side transitions](../renders/stern_remedy/plan.png)

The initial inferred shoulder controls were replaced with reviewed native S04
side observations. The moulding now has a qualified fair runout to a shared F18
rubbing-stock station, rather than ending before the next sampled section.
The large inward pinches, wing-like terminations and material gaps are resolved
in the current opaque plan. The following are **actual CAD** half-breadths:

| F forward, ft | Port half-breadth, ft | Starboard half-breadth, ft |
|---:|---:|---:|
| 13.749 | 8.12895 | 8.12895 |
| 14.500 | 8.16387 | 8.16387 |
| 16.000 | 8.21036 | 8.21036 |
| 17.990 | 8.28684 | 8.28684 |
| 18.010 | 8.28852 | 8.28852 |
| 20.000 | 8.44682 | 8.44682 |

These include the outside wood/rubbing stock. They are not a silent rewrite of
the corrected S02 offset table. The hidden runout joint and stock taper are
construction inferences; the measured aft/shoulder controls remain separate.

## 3. Source registration and comparisons

- Geometry condition: **surveyed HAER arrangement/repair condition** locally
  registered to the retained S02 source frame. Corrected offsets remain intact.
- The outside wood/moulding line, rail-fastener centres, traveller and straight
  projected davit lines have separate identities.
- Local plan image centreY841.5 is supported by the case and fastener midpoint.
  It refines image registration without translating the boat's world centreline.
- The profile's upper deck stroke isY377.5. The formerY408 anchor was the lower
  stroke; the provisional report's12–13-in discrepancy is not applied blindly.
- The independent counter anchor isF−1.139795/Z7.650031, rake1.827690 forward/
  vertical foot. Stock headF2.036907 is separate from box faces and wheel plane.

![Fixed-scale actual wood/rail plan overlay, with source observations and handoff arrows](../renders/stern_remedy/plan-source-overlay.png)

![Actual counter/deck/moulding profile over S04 with corrected upper-deck anchor](../renders/stern_remedy/profile-source-overlay.png)

| Actual-solid comparison | Result |
|---|---|
| 19 raw wood-edge controls | **0.361-in RMS; 1.283-in maximum** |
| 18 raw rail-fastener controls | **0.253-in RMS** transverse to the observed path |
| Two confirmed profile guides | Actual centreline reference intersects the picked guides |
| Pick allowance | ±0.20 ft =±2.4 in; reported source residuals remain within it |
| Counter material | Nine source-referenced normals across centre/quarters retain skin and interior air |

The checks intersect actual CAD and compare it to the archived raw observations,
not merely to the fitted parameter values. Original asymmetric picks are retained;
the visible envelope is symmetrized within their allowance. Photographs provide
appearance/arrangement checks, not uncalibrated absolute lengths.

## 4. Construction and fitting implementation

| Finding / work order | Implemented result and evidence |
|---|---|
| **R0 — source identities/state** | Classified controls, native transforms/source hash and corrected/as-surveyed qualification in the target ledger; separate source/control figures |
| **R1 — aft deck/quarters** | Curved timber boundary, normal-inset inner boundary, fair side runout; source overlay and both-side width checks include the user's markup |
| **R2 — counter** | Explicit source anchor/rake independent of inherited bbox; actual profile and normal-thickness checks |
| **R3 — rails/posts** | 3½×1¾-in rectangular oak, horizontal broad face per S07/LOC; measured irregular fastener positions; bounded cubic paths and actual supported posts |
| **R4 — helm/mechanism** | Lower front opening and retained header/legs; separate lid boards; pump/manifold, ram, polished piston, guides, crossheads, stock collar/tiller, valve enclosure and hoses |
| **R5 — traveller** | Separate S04 item18 rod, sliding eye and supported feet; distinct from case-side item4d cleat |
| **R6 — stern equipment** | Plate-web iron davits, stainless struts, pivot pedestals/pins, electric winches, rigid tackle, external timber/rubber bumper, control stations and speaker |
| **R7 — operating space** | Existing access chain retained; new controls checked against doors; full 0–90° door sweep passes at15° samples |
| **R8 — local construction** | Three inspectable oak moulding pieces, refitted transom frames/braces/clamps. M4 reconciliation found the two old stern-timber picks at preview X182/220 are the measured deck beams **23/22**; the modelled 4×3½-in oak stern timber remains at the rudder-box aft face. Member-d identity and the F≈−1.05 counter line remain unresolved (see `milestones/M4.md`) |
| **R9 — independent acceptance** | Raw-source/actual-CAD residuals, material partition, support, motion/access, actual-export images, fixed-scale overlays and hashes |

The substantial moulding is separate material, not missing from registration or
duplicated inside hull/deck. Its division into three pieces and hidden joints
are inferred. Fitted stock is8×6 in before the qualified side runout.

### Helm inspection

| Closed case | Open inspection |
|---|---|
| ![Isolated closed helm and real lower front opening](../renders/stern_remedy/helm-closed.png) | ![Case/lid hidden to inspect hydraulic steering](../renders/stern_remedy/helm-open.png) |

Closed view isolates the helm assembly to expose its opening. Open view hides
case/lid while retaining deck/rails. These visibility changes are documented in
provenance; the lower opening also has an actual-material check. The reference
comparisons are LOC-P28 closed, LOC-P29 open and LOC-P30 overall stern.

Unprinted fitting sections, hidden mountings, hose routing, fine mechanism
details and control identities not explicitly established by the source remain
**qualified reconstruction**. The hydraulic assembly depicts recognizable visible
components, not internal manufacturing geometry. No individual repair date is
invented. Existing general rigging/pushboat exclusions are retained.

## 5. Verification and acceptance status

Completed checks:

- `python -u checks/check_stern_remedy.py`: source residuals, valid parts,
  conserved/nonduplicated moulding, counter thickness/air, support, both quarter
  handoffs, fitting bases, door/control clearance, lid clearance and steering.
- `python -u checks/check_m3_frames.py`:154 frame pieces/19 supports,10,390 exterior
  samples, all bottom seats and frame-head/clamp contacts,78 drains, mortises,
  continuous floors, five board poses, steering and54 clear frame-bay samples.
- `python -u checks/check_companionway.py`: continuous doorway, supported descent,
  genuine bottom material, no filler, and paired glazed leaves over0–90° in15° steps.
- `python -u checks/check_model_scale.py`: actual export scale, mm STEP units,
  recorded-length distinction and542-part successful assembly.
- `python -u checks/render_stern_remedy.py`: actual-export plan/quarter/aft and
  helm views, fixed-scale plan/profile overlays and complete source/mesh hashes.

SA-01–SA-14 have implementation/numeric/inspection evidence above. **SA-15 and
overall stern appearance are presented for the user's review** against the
preserved baseline, the new images and the LOC photographs. This checkpoint
does not authorize advancing M4/M5 before that stern review is resolved.

### Reproduction notes

Source preparation: `checks/prepare_stern_detail_sources.py`,
`checks/measure_stern_remedy_targets.py` (which includes the side-control step).
The new source input is required alongside the previous geometry ledgers.

Two build defects were corrected: the tangent whole-hull/deck fuse that returned
an empty OCC shape, and the crosswise beam helper's parallel section axis.
Rail lofts use bounded cubic patches because a single many-section loft could
escape the source bounds despite reporting a valid solid. Explicit bounds,
actual source sections and mesh/export checks now catch that failure mode.
