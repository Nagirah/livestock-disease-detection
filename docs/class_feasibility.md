# Class feasibility assessment

## Decision tests for each class

1. **Trustworthy labels:** label definition stable; sample images visibly align with labels.
2. **Sufficient and balanced data:** record verified images per class, class ratio, and risks of overfitting. Do not set an arbitrary universal minimum.
3. **Independence:** subject/session/source grouping can be considered before splitting; no known leakage.
4. **Reproducibility:** data licence/source and transformations recorded.
5. **Task fit:** labels actually represent image-level classification; the prototype does not promise lesion localization or clinical confirmation.

## Preliminary per-species recommendation

| Species | Proposed classes | Evidence so far | Provisional recommendation |
| --- | --- | --- | --- |
| Goat | goat pox, healthy skin | ~1,009 images total; detection-oriented export; 3 label/image discrepancies previously reported | **Conditional:** verify image-label conversion, class counts and samples |
| Cattle | lumpy skin disease, healthy | 324 vs 700 images, preprocessed PNG | **Conditional:** proceed with imbalance safeguards after validation |

