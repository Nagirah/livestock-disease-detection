# PentAI — Data Cleaning Decision Record

**Project scope:** goats and cattle only  
**Reference:** `01_data_cleaning_and_eda.ipynb` and its saved original inspection outputs  
**Decision type:** conservative exclusion; no source image modification  
**Status:** provisional in notebook; final acceptance pending a successful latest Colab run and team sign-off

## Cattle decisions (1,024 source images)

The notebook detected **five exact-byte duplicate occurrences**. Two are within the `Lumpy Skin` folder and three span conflicting `Lumpy Skin` and `Normal Skin` labels.

| Pair | Original | Other copy | Issue | Provisional action |
|---|---|---|---|---|
| C1 | `Lumpy_Skin_317.png` | `Lumpy_Skin_318.png` | same-class exact duplicate | Retain 317; exclude 318 |
| C2 | `Lumpy_Skin_269.png` | `Lumpy_Skin_285.png` | same-class exact duplicate | Retain 269; exclude 285 |
| C3 | `Lumpy_Skin_86.png` | `Normal_Skin_242.png` | same image, contradictory labels | Exclude both pending verified source label |
| C4 | `Lumpy_Skin_154.png` | `Normal_Skin_429.png` | same image, contradictory labels | Exclude both pending verified source label |
| C5 | `Lumpy_Skin_229.png` | `Normal_Skin_588.png` | same image, contradictory labels | Exclude both pending verified source label |

**Cattle expected after applying the above:** 1,024 initial − 2 redundant same-class copies − 6 conflicting-label files = **1,016 provisionally eligible**, **8 excluded**. These are derived expectations, **not a fresh Colab execution result**.

## Goat decisions (1,009 source image files)

The original notebook reconciled actual files with annotation CSVs. It found **1,006 unique annotated files** and three image files absent from annotations:

| Image | Split | Reason | Provisional action |
|---|---|---|---|
| `healthy862_png.rf.c5980516823c71401655d3feea53ef2b.jpg` | train | no annotation record | Exclude |
| `healthy838_png.rf.2e6977b35614cce2ead67aac777b1bbc.jpg` | train | no annotation record | Exclude |
| `healthy815_png.rf.52908ccf872ad52f191148bdfd5d0816.jpg` | test | no annotation record | Exclude |

Two **train** images have filenames beginning `healthy` but annotation class `goatpox` (full filenames are retained in the notebook-generated `goat_annotation_review.csv`; notebook extracts may truncate their display):

| Image identifier | Issue | Provisional action |
|---|---|---|
| `healthy832_png.rf.8d4a401bd5ca7ce04418a6c989a5...` | filename and annotation disagreement | Exclude until source verification |
| `healthy23_png.rf.ff44a1e2cf0423cb9c9be8f0d3361...` | filename and annotation disagreement | Exclude until source verification |

**Goat expected after applying the above:** 1,009 initial − 3 without annotations − 2 unresolved disagreements = **1,004 provisionally eligible**, **5 excluded**. No assumption is made that the filename is a correct diagnosis.

## Consolidated expected outcome

| Animal | Source files | Provisional exclusions | Provisionally eligible |
|---|---:|---:|---:|
| Cattle | 1,024 | 8 | 1,016 |
| Goat | 1,009 | 5 | 1,004 |
| **Total** | **2,033** | **13** | **2,020** |

## Implementation and evidence
1. The notebook creates `cow_review_df`, `cow_manifest`, and `goat_manifest` and sets `include=False` plus an `exclusion_reason`. It does **not** delete or alter image bytes.
2. After a successful Colab run, inspect `cow_cleaning_manifest.csv`, `cow_eligible_manifest.csv`, `goat_cleaning_manifest.csv`, `goat_eligible_manifest.csv`, `cow_duplicate_review.csv`, and `goat_annotation_review.csv`.
3. Validate that excluded records are present with reasons and that included records have valid `relative_path` and `class` values. Compare the printed class counts with the actual CSVs.
4. Do not relabel contradictory pairs without reliable source evidence. Keep both files excluded if unresolved.
5. Approve the manifest *version* before starting split preparation; after sign-off, do not silently regenerate a different version without recording it.

## Approval record (to complete after Colab run)

| Field | Entry |
|---|---|
| Reviewer | [Name] |
| Approval date | [YYYY-MM-DD] |
| Colab notebook commit/hash | [Commit] |
| Cattle included/excluded confirmed | [Counts] |
| Goat included/excluded confirmed | [Counts] |
| Remaining unresolved issues | [Details] |
| Decision | [Approved / Changes required] |

**Limitation:** Exact-byte hashing does not rule out visual near-duplicates or shared-source leakage. These checks belong to Notebook 02 before creating/approving model splits.
