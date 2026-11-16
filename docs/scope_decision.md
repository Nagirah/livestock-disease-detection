
## Decision 

 Multi-Livestock Disease Detection System as an **image-classification screening prototype**, starting with goat pox versus healthy, cattle lumpy skin disease versus healthy, and a third species only when label audit and team approval support it. Provide a manual species selector; report predicted class and confidence with a clear non-diagnostic disclaimer.

## Open scope choice

goats + cattle MVP only if adding a third species would undermine quality before the 20 November 2026 deadline; requires explicit mentor/team agreement.


Image dataset inventory and audits; label normalization; leakage-aware train/validation/test partitioning; training and comparing defensible classification models; evaluation with per-class precision, recall, F1 and confusion matrix; simple user interface for upload and prediction; GitHub documentation.

## Explicitly out of scope for MVP

Veterinary diagnosis or treatment advice; automatic species identification unless separately validated; animal identification by individual; detecting lesion locations/bounding boxes; predicting diseases not represented by verified classes; claiming clinical accuracy without external validation.
