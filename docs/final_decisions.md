# Final decisions and minimum task handoff

**Group:** PentAI · **Project:** Multi-Livestock Disease Detection System  
**Decision record date:** 29 October 2026 · **Project deadline:** 20 November 2026  
**Decision status:** FINAL for project planning; actual dataset checks remain separately verifiable.

## Final agreed technical scope

Build an **image-classification screening prototype** with three explicitly different input types:

| User selects | User uploads | Classifier output |
|---|---|---|
| Goat | Goat skin/body photo | Goat pox vs healthy |
| Cattle | Cattle skin/body photo | Lumpy skin disease vs healthy |


The application uses a manual animal selection and the corresponding species-specific classifier (or an equivalent architecture with separated outputs). Do not merge all labels into one undifferentiated classifier.

This is an educational prototype, **not a confirmed veterinary diagnosis**. Show model prediction and confidence, and include a non-diagnostic disclaimer. No bounding-box localization, animal-level identification, or new disease categories are in the MVP scope.

## ClickUp task decisions and minimum evidence

| Task | Final decision / work product | Acceptance evidence |
|---|---|---|
| **Inventory and provenance** | The selected datasets and their roles are finalized in `docs/dataset_inventory.md`. | Inventory in repository; source metadata filled once checked. |
| **Dataset integrity** | Check archives for unreadable images, orphan or missing labels, duplicates, and leakage. No separate narrative audit report required.
| **Label and task audit** | **Image classification** is the chosen task. Goat and cattle use body/skin images for source-defined classes. New bounding boxes are not required. | Exact label names and sample checks recorded in ClickUp or the data-preparation notebook. |
| **Feasible classes** | Final class structure: **2 goat + 2 cattle disease classes**; each species is evaluated separately. | Dataset class counts and class mappings visible in notebook output.
| **Scope freeze** | Two species confirmed: **goat, cattle.|

## Implementation conventions

1. Build and evaluate separate species tasks because inputs and label spaces differ. Make train/validation/test partitions without duplicate leakage; evaluate with confusion matrices, precision, recall, F1 and accuracy per species.
2. Keep raw datasets outside the repository. Document preparation/splitting code in notebooks/scripts as the technical evidence for F02–F04; only a short summary is needed in ClickUp.
3. One classifier route per selected animal; instruct users to upload the appropriate input type. 
4. Scope is frozen for planning. Unverified data characteristics and model performance must not be presented as verified findings.

## Where these files go

```text
livestock-disease-detection/
├── README.md                      # Link to these two documents
└── docs/
    ├── dataset_inventory.md       # F01; update existing file rather than duplicate
    └── F01-F05_FINAL_DECISIONS.md  # Final F02–F05 decisions + handoff
```


