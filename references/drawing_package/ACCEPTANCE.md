# M0 — drawing preparation and calibration acceptance

**Result: accepted as the reference-preparation milestone.** The CAD geometry
remains at its previously verified 235-part checkpoint. M1–M5 are not closed.

| M0 criterion | Evidence / result |
|---|---|
| Original scans preserved and derived data traceable | All eight SHA-256 hashes checked; 51 native crops and 498 tiles sampled against original pixels. Exact native boxes and preview/OCR transforms recorded. |
| Important sections easy to locate/read | Stable IDs, indexed overviews, native views, previews and tiled details; full demonstrations for S06-V01 (frame set 4) and S07-V02 (cabin hatch). |
| Searchable notes and checked critical records | 4,623 coordinate-linked OCR words, separated from 58 checked construction records. Full sheet-6/7 note keys included; checked text and raw OCR are searchable locally. |
| Critical table values retained | All 15 stations/eight table rows transcribed. Missing chine cells remain null; 2-7-4 lower breadth retained. Source station-4 sheer 5-9-7 remains distinct from the existing 6-0-0 model fairing. |
| Calibrated views and common coordinates | Six imperial ruler fits, independent print-resolution checks within 0.13%; maximum ruler-fit residual 0.018 ft. Four sheet-4/5 deck landmarks align within 0.102 ft against declared ±0.20-ft pick uncertainty. |
| Scale conflict handled explicitly | Sheet-6 imperial 3/4-inch scale/physical ruler supports 1:16 despite its printed metric 1:32 caption. Raw source caption is preserved; no factor-of-two geometry change is inferred from it. |
| Selected vector/point geometry checked on source | Two complete source section views carry nine open boundary guides plus linked member/repair regions. Source overlays inspected. Local datums, forward viewing direction and positive-port axis are explicit. |
| Reproducible package and validation | Builder, C-API OCR wrapper, evidence/calibration scripts, demonstration builder and `checks/check_drawing_package.py`; machine-readable result in `validation.json`. |

## Decisions and findings carried into later milestones

1. **Source/model coordinates:** `registration.json` establishes the source
   convention and records old-CAD deltas. M1 applies a controlled geometry
   migration; M0 does not silently move the hull/mast/hatches. The 50-ft recorded
   dimension witnesses are explicit, not assumed to bound every appendage.
2. **Numbering:** source line stations, bow-keyed deck-beam sets and hull-frame
   sets are different. Sheet 5 note 10 says the first hull-frame set is against
   the *stern* knee; preserve its literal wording and interpret the member
   schedule before assigning section planes in M3.
3. **Repair geometry:** sheet 6 expressly says newer oak frames are not mortised
   into the keelson and their chine knees are rounded, not grown. Older frames
   are described as possibly original. This specific evidence governs over
   generic sharpie/skipjack practice.
4. **Projected versus cut geometry:** the Sampson post visible ahead of the
   frame-set-4 section is a projected member, not proof of a solid frame filling
   that section. The cabin view likewise includes furnishings beyond its plane.
5. **Historic deformation:** the lines use a corrected keel. The survey records
   roughly 8-in stern sag and midship hollow deadrise separately; these conditions
   must not be inadvertently mixed with the corrected line geometry.
6. **Trace precision:** the exported polylines are checked interpretation guides,
   not finished plank edges/joints or manufacturing templates. Final member
   geometry still requires the relevant milestone's source/section acceptance.
