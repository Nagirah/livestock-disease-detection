# PentAI — Model Evaluation Report

**Project:** Goat and Cattle Disease Detection  
**Team:** PentAI (Group 5), Moringa School  
**Evaluation date documented:** 18 November 2026  
**Models:** Separate image-classification models for goats and cattle  
**Status:** Held-out dataset evaluation complete; field validation not performed

## 1. Purpose and scope

This report documents performance of two image-classification models on held-out test images. The goat classifier distinguishes **goatpox** from **healthy (dataset class)**. The cattle classifier distinguishes **lumpy skin disease** from **healthy (dataset class)**. Chicken and other animal species are outside the project scope.

The team has confirmed the dataset and the application has passed normal functional testing. The metrics below are transcribed from the team's evaluation dashboard screenshots. They reflect **offline evaluation on held-out images**, not the outcome of new user uploads and not clinical/veterinary field validation.

## 2. Evaluation approach

Both classifiers were assessed using held-out test data and confusion matrices, per-class precision, recall, F1-score, overall accuracy, balanced accuracy, and macro-averaged F1-score. Test sets contained 151 goat images and 152 cattle images. The team reports that dataset validation has been confirmed; the actual split code and leakage-audit evidence should remain available in the project notebooks/reports for reproducibility.

**Metric meanings:** Accuracy is the percentage of all test images classified correctly. Precision is the fraction of predictions for a class that were correct. Recall is the fraction of actual class examples detected. F1-score balances precision and recall. Balanced accuracy averages class recall and is particularly informative when classes have different support. Macro F1 averages class F1-scores equally.

## 3. Summary of results

| Metric | Goat model | Cattle model |
|---|---:|---:|
| Test images | 151 | 152 |
| Correct predictions | 148 | 130 |
| Overall accuracy | 98.0% | 85.5% |
| Balanced accuracy | 97.5% | 79.3% |
| Macro F1-score | 97.9% | 81.6% |

Figures are rounded for display. Counts in the confusion matrices provide the exact number of correct and incorrect predictions.

## 4. Goat model — detailed evaluation

### 4.1 Confusion matrix

Rows represent **actual** classes; columns represent **predicted** classes.

| Actual / Predicted | Goatpox | Healthy |
|---|---:|---:|
| Goatpox | 57 | 3 |
| Healthy | 0 | 91 |

- Correct predictions: 57 goatpox + 91 healthy = **148/151**.
- Missed goatpox cases (predicted healthy): **3/60 = 5.0%**.
- Healthy images incorrectly identified as goatpox: **0/91**.

### 4.2 Class-level results

| Disease class | Precision | Recall | F1-score | Support |
|---|---:|---:|---:|---:|
| Goatpox | 100.0% | 95.0% | 97.4% | 60 |
| Healthy | 96.8% | 100.0% | 98.4% | 91 |
| **Macro average** | **98.4%** | **97.5%** | **97.9%** | **151** |

### 4.3 Interpretation

The goat model shows strong performance on this held-out dataset. It detected 57 of 60 goatpox cases and correctly classified all 91 healthy images. However, three actual goatpox cases were predicted as healthy; users must not interpret a healthy-class prediction as proof that an animal has no disease.

## 5. Cattle model — detailed evaluation

### 5.1 Confusion matrix

Rows represent **actual** classes; columns represent **predicted** classes.

| Actual / Predicted | Healthy | Lumpy skin disease |
|---|---:|---:|
| Healthy | 100 | 4 |
| Lumpy skin disease | 18 | 30 |

- Correct predictions: 100 healthy + 30 lumpy skin = **130/152**.
- Missed lumpy skin disease cases (predicted healthy): **18/48 = 37.5%**.
- Healthy images incorrectly identified as lumpy skin disease: **4/104 = 3.8%**.

### 5.2 Class-level results

| Disease class | Precision | Recall | F1-score | Support |
|---|---:|---:|---:|---:|
| Healthy | 84.7% | 96.2% | 90.1% | 104 |
| Lumpy skin disease | 88.2% | 62.5% | 73.2% | 48 |
| **Macro average** | **86.5%** | **79.3%** | **81.6%** | **152** |

### 5.3 Interpretation

The cattle model classified 85.5% of its held-out images correctly, but lumpy skin disease recall was only 62.5%. In particular, it predicted *healthy* for 18 of 48 actual lumpy skin disease images. This is a significant false-negative limitation. Consequently, a healthy-class result should never be used to rule out disease when clinical signs are present. Further model improvement and external field validation would be needed before any higher-stakes use.

## 6. Comparison and implications

The goat model achieved higher overall accuracy and stronger class-balanced measures on its respective test set. However, these models use different datasets and conditions, so the observed difference does not establish which model would generalize better across farms, cameras, lighting, or populations.

Cattle model improvements for future iterations could include reviewing false negatives, adding more representative lumpy skin disease images, investigating class imbalance and image conditions, calibrating prediction scores, and validating with independently collected field images. None of these activities should be represented as already performed unless documented.

## 7. Operational limitations and edge cases

1. **Closed class sets:** each model predicts between only two known classes; an unrelated condition may still be forced into one of them.
2. **Species selection:** the user selects goat or cattle; the application does not reliably identify the species from the photo.
3. **Unsupported imagery:** non-animal images, other species, extreme close-ups, or wrong body regions may receive misleading outputs.
4. **Photo quality:** very dark, blurry, compressed, partially obstructed, or poorly framed photos can reduce reliability; there is no fully validated automated quality assessment.
5. **Prediction score:** a high model score is not a calibrated probability of disease and does not establish diagnostic certainty.
6. **False negatives:** especially for cattle, some diseased animals were classified as healthy in the held-out test set.
7. **Distribution shift:** performance on real farm imagery has not been established by the displayed test results.
8. **Clinical scope:** this is an educational screening prototype and cannot replace professional veterinary examination or diagnostic testing.

## 8. Application testing and outstanding robustness checks

The team confirms successful normal-function application testing. The application implementation contains checks for corrupt/unreadable JPEG/PNG input, a 12 MB per-file limit, a maximum of 20 selected images per batch, EXIF rotation correction, RGB conversion, and per-image inference-error handling. These safeguards are code-level observations; they are not evidence that every edge case has been experimentally tested.

Remaining targeted tests should include: non-animal image, wrong species selection, dark or blurred photo, tiny image, unsupported format, duplicate uploads, corrupted image, 21-image batch, over-limit image, mixed valid/invalid batch, and missing-model failure. Record the observed outcome rather than assuming that the app rejects unsupported visual content.

## 9. Conclusion

The primary dataset evaluation phase is complete: both models have measured accuracy, balanced accuracy, macro F1, class-level precision/recall/F1 and confusion matrices. The goat model performed strongly on its held-out dataset, while the cattle model showed a material disease-detection recall limitation. The next project steps are focused edge-case testing, documented limitations, final report and presentation preparation, rather than claiming clinical readiness.

**Recommended dashboard disclosure:** “Evaluation results are based on held-out test images, not new uploads or veterinary field validation.”
