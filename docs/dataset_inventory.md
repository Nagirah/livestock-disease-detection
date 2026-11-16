# PentAI — Dataset Inventory

**Scope:** Goatpox versus healthy; cattle Lumpy Skin Disease versus healthy. Chicken dataset excluded by current scope.  
**Evidence date:** original notebook saved inspection outputs, reviewed 2 November 2026.  
**Counting convention:** image *files* and unique annotated *images* are distinct from annotation *rows*.

## 1. Source-image inventory

| Item | Cattle | Goats |
|---|---:|---:|
| Actual image files | **1,024** | **1,009** |
| Unique images with annotation entries | Source uses class folders; no annotation CSV count recorded | **1,006** |
| Files without an annotation record | Not applicable to folder-derived labels | **3** |
| Exact-byte duplicate occurrences found | **5** | **0** |
| Corrupted files reported by initial verification | **0** | **0** |
| Original image format | **1,024 PNG** | **1,009 JPEG** |
| RGB images | **1,011** | **1,009** |
| RGBA images | **13** | **0** |
| Width × height | **256 × 256** for all | Varies (see below) |

`Image.verify()` reported zero corrupt files in the original notebook. A full decode pass and independent rereun are still recommended; do not interpret this as proof of perfect semantic image quality.

## 2. Goat partitions and classes — observed counts

| Split | Actual files | Annotated unique images | Unannotated files | Healthy annotated | Goatpox annotated |
|---|---:|---:|---:|---:|---:|
| Train | **707** | **705** | **2** | **423** | **282** |
| Validation | **202** | **202** | **0** | **122** | **80** |
| Test | **100** | **99** | **1** | **63** | **36** |
| **Total** | **1,009** | **1,006** | **3** | **608** | **398** |

Goat annotated-image distribution: `healthy` **608 / 1,006 = 60.44%**; `goatpox` **398 / 1,006 = 39.56%**. Training annotations originally contained **834 rows** for **705 unique training images**; **442 `healthy_skin` rows** and **392 `goatpox` rows**. Those are annotation rows, not 834 distinct images.

After excluding two *annotated* goat images with filename/annotation disagreements and three unannotated files, the expected eligible inventory is **1,004**. If both ambiguous images carry the notebook's provisional `goatpox` annotation, the calculated eligible class totals are `healthy` **608** and `goatpox` **396**. Confirm these against the regenerated CSV before reporting them as final.

## 3. Cattle classes and expected cleaned counts

The cattle directory contains the source classes `Lumpy Skin` and `Normal Skin`. The dataset description previously supplied reports **324 Lumpy Skin** and **700 Normal Skin** files (sum **1,024**). The original notebook's saved outputs independently confirm **1,024 total** but do **not** include a dedicated printed cattle per-class count; treat the 324/700 breakdown as **source-reported pending verification** with `cow_metadata` or the current manifest.

| Class | Source-reported count | Provisional exclusions based on identified pairs | Expected included, if source counts match |
|---|---:|---:|---:|
| Lumpy Skin | 324 | 5 (2 same-class extras + 3 conflicting) | **319** |
| Normal Skin | 700 | 3 (conflicting) | **697** |
| **Total** | **1,024** | **8** | **1,016** |

Exact cattle duplicate pairs: `317↔318` and `269↔285` in Lumpy Skin; `86↔Normal_Skin_242`, `154↔Normal_Skin_429`, and `229↔Normal_Skin_588` cross class. See `docs/cleaning_decisions.md` for actions.

## 4. Image properties observed in notebook

**Cattle:** Every image was 256 × 256 px, PNG. Of 1,024 images, 1,011 were RGB and 13 were RGBA. Convert to RGB consistently before model ingestion.

**Goat:** Every image was JPEG and RGB. Observed width range: **194–2,048 px**, median **698 px**, mean **734.71 px**. Observed height range: **159–2,048 px**, median **674 px**, mean **642.50 px**. These varying sizes require a consistent resize/shape policy later.

## 5. Provisional cleaning summary

| Animal | Original | Expected excluded | Expected eligible | Status |
|---|---:|---:|---:|---|
| Cattle | 1,024 | 8 | **1,016** | Provisional, requires latest Colab confirmation |
| Goats | 1,009 | 5 | **1,004** | Provisional, requires latest Colab confirmation |
| **Total** | **2,033** | **13** | **2,020** | Not yet a signed-off prepared dataset |

The original source archives must remain unchanged. Eligible images are selected via portable `relative_path` and `include` fields in the manifest CSVs. Goat split assignments must remain unchanged. The cattle dataset has **no verified source train/valid/test split**; splitting comes after leakage checks in Notebook 02.

## 6. Provenance and verification needed

- **Goat source:** Roboflow-exported Goat Pox Detection (TensorFlow-format archive), with `_annotations.csv` per split. Exact version URL, license and acquisition date should be copied from the original export metadata; not verified by the saved notebook outputs.
- **Cattle source:** Provided `Cow data.zip`, with `Lumpy Skin` and `Normal Skin` class folders; image content already 256×256 PNG. Original hosting URL, license and acquisition date were not evidenced in the notebook outputs.
- **Storage:** Keep original ZIPs in approved shared Google Drive storage; do not commit images or ZIP archives into standard Git.
- **Fresh validation:** Run Notebook 01 in Colab, compare actual printed counts and exported class totals, and update this inventory if results differ. Run Notebook 02 to check related-image leakage and create split manifests.
