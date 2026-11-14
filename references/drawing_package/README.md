# Kathryn drawing package — milestone M0

Derived references for an accurate, inspectable historic CAD reconstruction.
The original TIFFs in `2d model/` remain the primary source.

Open **`index.html`** in a browser for a local searchable contact sheet. No web
server is required. AI/file-based navigation can start at `INDEX.md` or the JSON
records. See `ACCEPTANCE.md` and `validation.json` for the milestone evidence.

## Contents

- Eight source-sheet overviews; 51 indexed plans/sections/details/note blocks.
- Original-resolution native PNG views and 498 overlapping lossless tiles.
- Raw OCR text/TSV and 4,623 recognized words with native coordinates/confidence.
- `notes_verified.json` / `checked_notes.md`: 58 visually checked construction
  records, including the full sheet-6/7 numbered keys, materials and repairs.
- `offsets_verified.json`: all 15 source stations/eight offset rows, with blanks
  preserved and the existing model's deliberate sheer fairing kept separate.
- `calibration.json`: independently checked ruler calibrations for sheets 2–7.
- `registration.json`: the declared source coordinate system, cross-sheet
  relationships, line-station coordinates and explicit legacy-CAD migration data.
- `traces/`: source-overlay SVG/PNG and calibrated point/region data for complete
  representative sections on sheets 6a and 7a.
- `demos/S06-V01.html` and `demos/S07-V02.html`: full section demonstrations with
  linked construction notes, dimensions, repair context and scale source.

## Reading rules

Raw OCR is **unreviewed extraction**, not the dimensional authority. Use the
checked record when available, and follow its original view link when uncertain.
Words, native views, tiles and previews retain exact source-coordinate transforms
and SHA-256 provenance in `manifest.json`.

The sheet-6 metric caption reads 1:32 but conflicts with its 3/4-inch imperial
scale. The measured bar and print-resolution check support the latter (1:16).
The two representative section traces use named LOCAL vertical datums, not an
invented global frame height. The vectors are boundary guides, not finished
cutting profiles or a complete automatic CAD conversion.

`registration.json` declares the source coordinates and retains the historical
235-part legacy-placement audit. M1 has applied the principal hull/hatch/mast
coordinates; see `../milestones/M1.md` for current geometry and remaining gaps.
Lines stations, deck-beam numbers and hull-frame sets remain separate systems.

Added during M1: `sheer_band_measurements.json` retains native curve picks for
the separately labelled Top of Deck above Underside of Sheer Strake. This adds
the missing upper band/flare to the model without changing source offset cells.
Reproduce with `python checks/measure_sheer_band.py`; annotated evidence is
`../renders/m1-sheer-band-source.png`.

## Reproduction

The scripts use the existing Python/Pillow/NumPy/SciPy environment and installed
Tesseract C library; a Tesseract command-line executable is not required.
The English model used is `tessdata_fast/eng.traineddata` (Apache-2.0); exact model
SHA-256 and download URL are recorded in the manifest. Model cache used in this
session: `/tmp/opencode/tessdata/`. If that temporary cache disappears, obtain the
model from the recorded URL into a chosen cache and supply `--tessdata`.

```bash
python checks/build_drawing_package.py --stage images
python checks/build_drawing_package.py --stage ocr --tessdata /tmp/opencode/tessdata --jobs 2
python checks/register_drawings.py
python checks/build_drawing_demos.py
python checks/build_drawing_package.py --stage index
python checks/check_drawing_package.py
```

`checks/drawing_catalog.py` locates views; `checks/drawing_evidence.py` contains
the checked transcription; `checks/register_drawings.py` records calibration and
registration picks. The original source TIFFs are never rewritten.
