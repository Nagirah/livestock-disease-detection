# Goat and Cattle Disease Detection — D01-D04

**PentAI | Moringa School**. Two separate species-specific classification pipelines. No other species are within scope.

## Setup (PowerShell, from cloned repository root)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy the `src/`, `config/`, `docs/`, `requirements.txt` and `.gitignore` contents into your cloned repository (merge `.gitignore`, don't overwrite it). Extract your two original archives **separately** into `data/raw/goats/` and `data/raw/cattle/` without altering originals. Keep any class and annotation folder hierarchy. Do not commit images.

## Workflow
```powershell
python src/pipeline.py audit
```
Check `data/reports/goat_dataset_audit/` and `data/reports/cattle_dataset_audit/`. Audit discovers candidate labels from folder names and reads any explicit overrides in `config/image_metadata.csv`. If images live in `train/images` with detection CSV labels, do **not** infer an image class automatically. Inspect the original annotations, verify whether image-level labels are justified, and enter each approved individual image's `raw_label` in metadata. Audit does NOT certify label correctness.

Fill `config/label_mapping.csv` from the **observed** raw classes. Example headers only are supplied; mark `approved=yes` only after human verification. Use species values `goats` or `cattle`. If an image has a known animal ID, source ID, source group or modality, enter those in `config/image_metadata.csv` using exact path relative to that species' raw folder. Re-run audit after metadata updates.

```powershell
python src/pipeline.py audit
python src/pipeline.py prepare --size 256
python src/pipeline.py split --seed 42
python src/pipeline.py freeze --seed 42
```

**Outputs:** separate audit manifest, class counts, duplicate candidates, clean/exclusion manifest, split manifest, per-species split counts; consolidated split manifest, leakage audit and dataset v1 metadata. Processed image files are named by SHA256 and saved by species; conversion preserves aspect ratio and pads to square (review this policy before use). Raw data is never modified. Exclusion is a logical quarantine in CSV, not a physical move.

## Limitations and mandatory review
- The script detects corrupt images and byte-identical duplicates; it **does not** identify mislabeled images, unrelated livestock, near-duplicates, clinical diagnosis or source provenance automatically.
- Goat object-detection annotations require inspection and an explicit, documented conversion decision; do not use raw CSV bbox names as automatic image-level labels.
- Split grouping defaults to `animal_id`, then `source_group`, then file SHA256. **Without trusted animal and source IDs, absence of same-animal/source leakage cannot be proven.** Provide group metadata and manually inspect near duplicates before approving splits.
- The split heuristic prioritizes keeping groups intact and class coverage; actual proportions may differ from 70/15/15. It fails when class coverage is impossible.
- The `freeze` command drafts a **pending** manifest; it cannot verify permissions, evidence of rights or an independent fresh rerun.
- `config/image_metadata.csv` is optional for folder-labelled datasets but essential when labels cannot be inferred or grouping needs improvement.
- Never overwrite a previously approved v1 release without an explicit version change.

See `docs/D01_D04_ACCEPTANCE.md` for acceptance evidence.
