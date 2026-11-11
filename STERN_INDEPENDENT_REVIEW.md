# Independent stern review — 2026-11-11

**Accepted for the historic reconstruction; resume M4, then M5.** The user
authorized this review to release the remaining milestones without another
approval round. This supersedes the earlier instruction to await user review.

The review compared actual CAD with archived raw drawing observations and
examined opaque exported views against Kathryn's own LOC photographs. It was
performed by the working agent, not a separate reviewer or engineering authority.
Unprinted joints, hidden mechanism details and repair dates retain their stated
uncertainty.

## Evidence and disposition

| Acceptance | Evidence / review result |
|---|---|
| SA-01 / SA-02, identities and registration | S04 wood edge, fastener centres, traveller and projected davit lines remain distinct. Fixed drawing scale/F registration; surveyed arrangement qualified against corrected S02 lines. |
| SA-03 / SA-06, plan controls | Fresh `check_stern_remedy.py`: 19 raw wood observations, **0.361-in RMS**, **1.283-in maximum**; 18 rail observations, **0.253-in RMS**. Within the declared pick allowance. |
| SA-04, counter | Actual CAD intersects independently picked profile guides. The upper-deck anchor is retained; the former lower-stroke datum error is not reintroduced. |
| SA-05, appearance | Inspected `renders/stern_remedy/plan.png`, `quarter.png`, both fixed-scale overlays and fresh `renders/current-stern-independent.png`. Both aft quarters fair into the sides; no open shoulder gap, wing termination or unsupported shelf is visible. |
| SA-07, rails | Rectangular timber stock and its orientation are credible against LOC-P07/P28/P30. Actual post bearing and side-to-transom rail joins pass. |
| SA-08 / SA-09, helm | Kept distinct case/wheel/stock/cabin datums. Reviewed closed/open helm against LOC-P28/P29: lower opening and header, timber lid, pump/ram/guides/crossheads/hoses are represented. Fine pump details and hose routes remain reconstructed. |
| SA-10, fittings | Traveller, plate-web davits, stainless struts, tackle, bumper and local controls are present in the opaque export and comparable with LOC-P30. No rope/wire rigging is added. |
| SA-11, construction | Moulding partition conserves material without duplicating hull/deck; aft posts, beams and fore-aft frames bear on actual wood. |
| SA-12, closure | Nine source-referenced normal sections retain counter skin with genuine interior air. Both shoulder widths and rubbing-stock contacts pass. |
| SA-13, motion/access | Fresh −35/0/+35-degree rudder/stock checks, closed-lid clearance and 0/45/90-degree door checks pass. Previously captured full 0–90-degree doorway sweep remains applicable; repeat when M4 adds adjacent members. |
| SA-14, export | Reviewed baseline is 542 valid single solids, 1:1/mm, successful SOMA export without warnings. A separate mast mesh repair is rebuilding; its completion is not claimed here. |
| SA-15, repeatability | Original baseline and remedy images retained; numeric results in `checks/stern_remedy_acceptance.json`; reviewed hashes in `checks/stern_independent_review.json`. |

## Mast finding discovered during this review

The mast was still a full-height valid CAD solid, but its periodic conical side
face had **zero triangles** in the actual viewer GLB. Independent tessellation
also reproduced the defect: only **14.6%** of the CAD surface area was meshed.
This explains why bounds/solid-validity checks missed the missing mast. Some
interior inspection renders additionally clip the mast deliberately.

The repair converts the completed mast to exact rational surfaces before
registration. High-accuracy before/after volume agrees within one part per
million, and exact Boolean differences contain no solids. The subsequent SOMA
build succeeds with 542 parts and no warnings; actual export contains the full
side surface. Three-scale mesh checks pass at 1/32/64 and the restored mast is
visible in `renders/current-full-vessel-side.png`.

## Remaining qualifications

Photo perspective is an appearance check, not a calibrated dimensional ruler.
The absent auxiliary pushboat remains outside the main-vessel scope. The fair
hidden moulding runout, joint details, individual control functions and fine
hydraulic internals are reconstruction, not certified fabrication data. M4 must
preserve this accepted stern envelope and its material/support/motion checks.
