# Kathryn — M4 deck-beam continuation passdown

Saved 2026-11-11 after resuming from `PASSDOWN_2026-11-11.md`. The user
authorized independent stern review and, once it passed, continuation through
M4/M5 without a separate acceptance round.

## Verified stopping point

- **659 registered parts**, 1:1 CAD/STEP in millimetres.
- `soma build` succeeded without warnings: **564.9 s** wall, captured stages
  model 211.211 s / STEP 11.305 s / GLB 138.133 s.
- `output/model.step`, `.soma/model.glb` and the viewer map are current.
- No parameter-panel values were edited; the scale control remains at 1:1.

## Bookmark before the experiment

`pre-experiment-2026-11-11` is an annotated tag on baseline commit `3debabd`
(the prior verified 650-part stopping point). Return with:

```sh
./project-git reset --hard pre-experiment-2026-11-11
```

## What this increment did

`references/drawing_package/m4_deck_schedule.json` is now a reconciled geometry source
produced by `checks/measure_m4_layout.py`:

- **23 S05-07 deck-beam sets** are registered as **29 parts** by
  `parts/beam_layout.py` + `parts/deck_beams.py`: 17 full/header beams and
  12 half beams for six split sets.
- The split sets were proved from the drawing, not assumed: at each picked
  edge the beam line is absent across the measured clear opening width.
  Splits: **8/9** main hold hatch, **16** after deck hatch, **18/19/20** cabin.
- Headers/carlings: sets 5/6, 7/10, 15, 17, 21. The after hatch has no separate
  aft header set; its carlings bear on the cabin fore header (set 17).
- Stock: sets 1–3 6×4¾-in pine (4¾ in sided); sets 4–23 5½ square pine except
  12–15 oak under the winders. The three hold stanchions land on sets
  15/14/13 within 0.06 ft, so no extra beam was invented.
- Header build stations are snapped by at most the stated ±0.20-ft pick
  allowance only where needed to keep the measured openings clear. Both the
  source pick and build station are retained in the ledger.
- A functional centreboard notch keeps the fully raised board clear of the
  beam that crosses the trunk; the stock section off-centre remains 5½ in.

### Stern reconciliation

- The old `Stern oak deck timber` picks at preview X182/220 are the measured
  beam sets **23/22**, now registered with source pine stock.
- The full transverse timber at the rudder-box aft face remains the modelled
  **4×3½-in oak** stern timber.
- The 7(c) leader also touches a line near **F≈−1.05**, but it lies in the
  solid counter/transom edge and outside the continuous interior air, so it
  cannot be a standard deck beam. It is recorded as unresolved, not geometry.
- Member **d** (6×3-in pine) is not lettered on the plan and cannot be
  identified without inventing stock. It remains unresolved; no third timber
  was invented.

### Unrelated pre-existing latents corrected

- Starboard hydraulic ram hose rerouted around the forward side of the rudder
  stock; it had intersected the moving stock at every steering angle.
- `check_stern_helm` now accepts the stern moulding as the bearing for the
  inset aft rail posts (posts 2/3 bear on the moulding, not the deck).
- `check_outer_integration` checks the strake-to-stern-moulding handoff
  directly and samples only body stations for the hull/strake overlap.
- `check_m1_enclosure` starts distributed air probes at the first full hull
  station; the old range began inside the solid aft counter.

## Validation on the actual 659-part export

Passing checks:

- `checks/check_m4_beams.py` — schedule/stock/roles/stanchions/stern timbers,
  29 exported beam meshes, no missing faces.
- `checks/check_registered_deck.py` — 109 boards exported, unchanged bounds and
  volume, no aggregate backing.
- `checks/check_mast_mesh.py` — complete mast mesh at 1:1/1:32/1:64.
- `checks/check_model_scale.py` — 1:1 mm STEP, 659 parts.
- `checks/check_hatches.py`, `check_m3_frames.py`, `check_m2_centreline.py`,
  `check_m1_enclosure.py`, `check_companionway.py`, `check_stern_remedy.py`,
  `check_stern_helm.py`, `check_outer_integration.py`.

Images inspected:

- `renders/m4-deck-beams-plan.png` — plan with planking/cabin/spars hidden;
  all beams frame the hull and are interrupted at the openings.
- `renders/m4-stern-beams.png` — aft quarter with planking hidden.

## Remaining M4 work

- Oak waterways and supported staggered plank butts with qualified joints.
- Individual hull/chine/transom boards; keep physical board IDs distinct from
  waterline paint regions.
- Pine ceiling/lining, bulkhead and sole boards; retain absent main-hold limber
  boards and survey-removal qualifications.
- Resolve member-d identity and the F≈−1.05 counter line if new evidence
  appears.
- Then M5 cabin/hold/forepeak fit-out; M4/M5 completion is not claimed.

## Resume sequence

1. Read this file, `milestones/M4.md`, and the current build state. Preserve
   the stern envelope, mast repair and the verified 23-set beam layout.
2. Validate the retained unregistered hull-board prototype before live use
   (`parts/planking.py`, `checks/prototype_hull_boards.py`); its closed ruled
   cutters were not validated in this session.
3. Continue M4 waterways/butts, then individual interior boards.
4. Build, inspect actual exports/images and commit each coherent increment.
   Heavy whole-hull jobs run sequentially; do not delete build locks or raise
   the app timeout.

No remote publication, package installation, virtual environment, external
messaging, source-image modification or parameter-panel change was performed.
