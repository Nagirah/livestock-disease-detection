# PentAI — Project Scope

**Project:** Livestock Disease Detection using Image Classification  
**Institution:** Moringa School  
**Team:** PentAI  
**Scope decision:** 2 November 2026  
**Status:** Current approved direction (goats and cattle only)

## Problem and purpose
Develop and assess image-classification models that distinguish the disease classes represented in the available goat and cattle image datasets. The aim is an educational proof of concept, not a clinical diagnostic tool.

## In scope
1. **Cattle:** Binary image classification: `lumpy_skin` (Lumpy Skin Disease-labelled images) vs `healthy` (Normal Skin-labelled images).
2. **Goats:** Binary image classification: `goatpox` vs `healthy`, using image-level labels derived from the original goat annotation CSV files.
3. Inspect the two datasets separately, document provenance and source labels, identify image-level duplicates and suspicious labels, preserve a record of exclusions, and export auditable eligibility manifests.
4. Validate original goat `train` / `valid` / `test` assignments. After deduplication and leakage checks, create stratified/group-aware cattle partitions where applicable.
5. Use appropriate, reproducible preprocessing; train baseline classifiers; evaluate per-class performance with a held-out test set; document limitations and reproducibility.

## Out of scope
- Chickens, poultry, sheep and other animal categories.
- Object detection or lesion localization as an independently evaluated deliverable. Goat annotations may be used to derive image-level labels, but the planned model output is an image class.
- Claims that visual classification confirms a veterinary diagnosis or is appropriate for direct clinical deployment.
- Training on files whose label is missing or whose contradictory source labels remain unresolved.

## Dataset and label rules
- Keep source images and ZIP files unchanged in shared storage; use `relative_path` and `include` columns to select images.
- Cattle class-folder names map to `lumpy_skin` and `healthy` only after the folder taxonomy is validated.
- Goat image labels are `goatpox` or `healthy`; the presence of a goatpox annotation takes precedence for provisional image-level labeling. The two filename/annotation disagreements remain excluded unless verified with reliable evidence.
- Any ambiguous or missing annotation is documented and excluded provisionally; neither a filename nor visual appearance alone proves a veterinary diagnosis.
- Keep goat's source partition assignment; protect the test set from training/selection decisions.

## Deliverables
- `notebooks/01_data_cleaning_and_eda.ipynb`: inspection, EDA, issue detection and eligibility manifests.
- `notebooks/02_dataset_preparation_and_splitting.ipynb`: split/leakage validation, cattle splits, preprocessing readiness.
- `docs/dataset_inventory.md`, `docs/cleaning_decisions.md`, and portable review/manifests under `reports/data_quality/`.
- Subsequent reproducible training/evaluation notebooks, metrics and project README.

## Change control
Any reintroduction of chickens or another animal is a project scope change requiring an explicit documented decision, updated datasets, labels, tasks and evaluation plan. Do not silently alter this scope based on older proposal text.
