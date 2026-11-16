# PentAI D01-D04 acceptance checklist — Goats and cattle only

## D01: Canonical taxonomy
- [ ] Review goat archive and all detection/CSV annotations; determine valid image-level labels.
- [ ] Review cattle folders and associated ground-truth labels.
- [ ] Enter species-specific approved raw-to-canonical mappings in `config/label_mapping.csv`.
- [ ] Obtain label-review sign-off, provenance and permitted-use confirmation.
- [ ] Do not convert object detection annotations into classification labels without documented validation.

## D02: Cleaning
- [ ] Run audits separately for both species and review raw class counts and exact duplicates.
- [ ] Manually review label correctness, irrelevant photos, near duplicates and modality.
- [ ] Run prepare only with approved mappings.
- [ ] Check exclusions, output sizes, conversion rules and all image paths.
- [ ] Record human decisions; the script cannot clinically validate image labels.

## D03: Leakage and splitting
- [ ] Supply reliable animal identifiers/source groups when known in image_metadata.csv.
- [ ] Verify no same animal, source derivative, augmented version or near duplicate crosses splits.
- [ ] Generate seed-fixed group-aware splits independently per species.
- [ ] Inspect per-class coverage and split proportions; revise scarce classes when impossible.
- [ ] Sign off split manifests and leakage audit.

## D04: Version v1
- [ ] Record manifest, mapping, configuration, code commit and seed.
- [ ] Record source/rights and file access approvals.
- [ ] Archive approved processed images in access-controlled storage, outside Git.
- [ ] Rerun from untouched raw data and compare file checksums/manifests.
- [ ] Obtain reviewer acceptance before changing metadata status from PENDING.
