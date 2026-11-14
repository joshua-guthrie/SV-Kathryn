# Stop for tonight — stern remedy implementation PARTIAL / UNVERIFIED

**Historical handoff, now superseded.** The work was resumed and implemented.
Read `STERN_REMEDY_IMPLEMENTATION.md` and the latest section of `PASSDOWN.md`.
Current verified assembly542 parts; moulding registration and build errors fixed.
The user's stern appearance review is next; M4/M5 remain held.

User requested a passdown and immediate stop because usage is nearly exhausted.
**Do not continue tonight.** Latest authorized task: implement the complete
`STERN_REVIEW_AND_REMEDY_SPEC.md`. General M4/M5 remain **on hold**.

## Critical state

- Last reviewed/exported baseline: **446 parts, 1:1, CAD/STEP mm**, geometrically
  valid but stern not visually accepted. Existing exports may still be that
  baseline or an automatic rebuild; inspect `.soma/build.json` when resuming.
- **No build/check/render verification has been run after the latest source
  patches. Current source is NOT an accepted stern checkpoint.**
- **Incomplete material registration:** hull.py now subtracts new
  `stern_moulding()` from planking/deck, but `model.py` has NOT been updated to
  register that timber. An automatic build could omit upper stern material.
  Complete/validate/register it before accepting/exporting the new model, or
  temporarily retain the material references while developing the moulding.
- Rails, hydraulic/helm detail, traveller, davits, bumper and controls are NOT
  implemented yet; their current geometry is still the criticized version.
- Preserve before-remedy images under `renders/stern_review/`. Originals remain
  untouched. No general board prototypes should run while stern work is active.

## New independent measurements completed

Files: `checks/extract_stern_controls.py`,
`checks/measure_stern_remedy_targets.py`, and required geometry input
**`references/drawing_package/stern_remedy_targets.json`**.

- Nine clear native cap-rail fastener centres found at ring score>0.90.
  Review images: `renders/stern-fastener-picks.png`,
  `renders/stern-remedy-source-controls.png` (blue centres/red wood contour).
- Local S04 image centre is native crop **Y841.5**, supported independently by
  case mid-breadth and midpoint of outer fasteners Y103/1580. This refines image
  registration about1.4 in within M0 uncertainty; model world X0 is unchanged.
- **First-pass datum error resolved:** profile rows374–381 are upper deck;
  rows401–409 are lower stroke. New anchor **Y377.5**, not previous Y408.
  Do not blindly translate by the report's provisional12–13 in without this fix.
- New counter rake **1.8276895904 forward/vertical ft**.
  Anchor **F−1.139794551, Z7.650030770**.
  Source guides: **F−1.037648662/Z7.594142785** and
  **F4.214603847/Z4.720431332**.
- New stock upper-deck crossing **F2.270060918**, stock head **F2.036907089**.
  Keep stock separate from box centre and wheel plane.
- Fitted wood controls (absX,F), feet:
  `(0,-1.2200),(.6435,-1.2101),(2.2205,-1.1438),(3.677,-.8453),
   (4.331,-.5370),(5.0375,.2307),(5.4975,1.0596),(6.15,6.2),
   (6.8,10),(7.4,12),(25,12)`.
- Rail controls (absX,F):
  `(0,-.6941),(.6435,-.6928),(2.2205,-.5834),(3.677,-.3314),
   (4.331,.0300),(4.924,.5274)`.
  Original irregular side picks, source hash, uncertainties and inferred shoulder
  handoff are preserved separately in JSON. Do not claim all fitted joins are
  directly measured. New rail heights use upper deck, not lower stroke.

## Latest code patches — not runtime validated

1. `parts/datum.py`: new required `STERN_REMEDY_SOURCE` JSON.
2. `parts/params.py`: head/rake use new targets; `STERN_BLEND_END_FT=14`,
   moulding depth8/12, normal thickness6/12.
3. Replaced `parts/stern_layout.py`:
   - classified curved plan keep, exact cubic Bezier PCHIP pieces;
   - genuine inward2D plan offset plus independently anchored counter plane;
   - `keep()` intersects these volumes, replacing universal old rake plane;
   - helpers `wood_halfwidth`, `plan_limit`, `counter_forward`, `face_forward`,
     rail path/heights and `knuckle_height`;
   - first validate positive/valid solids and **inset moves forward/inward**.
4. `parts/hull.py`: aft widths constrained by plan belowF14; old compulsory
   52.533-ft body span guard replaced with classified-source aft/fore guards.
   Former deck builder is `deck_material_reference()`. New `stern_moulding()`
   uses filled exterior+deck minus inward6-in keep, limited to8-in upper band.
   `make_deck()` and `planking_envelope()` subtract it. **Registration missing.**
   Avoid recursion: moulding uses `solid_envelope()`/`deck_material_reference()`,
   never `make_deck()` or `planking_envelope()`.
5. `parts/framing.py`: clamp aft start at leastF−.45, provisional interface.
6. `parts/hull_frames.py`: actual cavity sections throughF14; aft limber/bore
   logic extended. Stile lofts include outer/inset knuckle heights and across-X
   surface limits. Brace endpoints use provisional fore-face contact offsets.
   All require new source/support/collision checks.

## Resume sequence

1. Read this file/report and inspect current source/build status.
2. Validate keep volumes/offset direction, hull/cavity/deck references and
   moulding. Complete housing/registration of separately inspectable8×6 oak
   moulding timbers before a new accepted checkpoint.
3. Rebuild fair rectangular3.5×1.75-in rails/post schedule and side joins,
   replacing14 round segments. Refit all aft structure and prove actual bearing.
4. Implement real case front opening/hydraulic replacement/mounts, S04 item18
   traveller, iron davits/stainless struts, external bumper, local controls and
   visible secondary details. Follow source references/report work-order order.
5. Build usable increments with `python -m soma build`; respect automatic-build
   locks and600-s app limit. Run heavy CAD checks sequentially.
6. Verify independent plan/profile controls, opaque/photo-comparable views,
   closure/thickness, structure, steering/board/access and1:1 export scale.
   Preserve304.8 mm/ft without forcing the old aft bbox span.
7. Close R0–R9 and SA-01–15 with after-remedy images in a NEW directory.
   Do not resume other milestones until the stern is resolved.

SOMA display remains mm-only; the user's conditional imperial-display request
does not authorize relabeling geometry or modifying the app. Reports use feet/
inches. Main `PASSDOWN.md` retains earlier research/environment/reference history.
