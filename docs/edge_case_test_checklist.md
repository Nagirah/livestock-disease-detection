# PentAI — Edge Case Test Checklist

**Purpose:** Complement normal deployment tests with unusual inputs and identify situations where an image classifier may provide misleading results.  
**Status:** Suggested tests; **not marked as passed** until run and observed on the deployed application.

| ID | Test | Expected safe behavior | Result |
|---|---|---|---|
| EC01 | Upload a corrupted `.jpg` or `.png` | Show an error for that image without crashing the batch | Not tested |
| EC02 | Upload a valid image larger than 12 MB | Refuse that file with a clear size message | Not tested |
| EC03 | Select 21 images | Warn that only the first 20 will be processed | Not tested |
| EC04 | Upload a rotated phone image | Correct orientation before inference | Not tested |
| EC05 | Upload a grayscale or transparent PNG | Convert to RGB and process if otherwise valid | Not tested |
| EC06 | Upload a cat, person, building, or chicken image | Do not treat a model prediction as evidence that the content is a goat or cow; add UI warning | Not tested |
| EC07 | Select Goat and upload a cattle image (and vice versa) | Explain that species selection is manual and wrong selection can lead to misleading results | Not tested |
| EC08 | Upload a blurry, dark, distant, or obstructed photo | Display image-quality guidance; do not imply guaranteed correctness | Not tested |
| EC09 | Upload a very small image (e.g. 16×16 pixels) | Avoid a false sense of reliability; preferably request a clearer image | Not tested |
| EC10 | Upload the same image multiple times | App should not crash; results should be consistent under the same model and preprocessing | Not tested |
| EC11 | Upload 1 valid and 1 corrupted image together | Process the valid image, record the invalid one as an error | Not tested |
| EC12 | Upload photos of other livestock diseases | Explain limited class coverage; do not claim that healthy means free of illness | Not tested |
| EC13 | Switch species or change image selection after prediction | Previous results should no longer be presented as results for the new selection | Not tested |
| EC14 | Disconnect guidance API / exhaust quota | Fall back gracefully without blocking image classification | Not tested |
| EC15 | Rename or temporarily remove a model file in local test environment | Record a useful failure rather than silently inventing a classification | Not tested |
| EC16 | Upload a file disguised as JPEG but containing non-image data | Reject it through image decode/verify error | Not tested |

## Existing safeguards observed in the application code

- JPEG/PNG file-uploader restriction
- 12 MB per-file limit
- 20-image batch limit (extra images skipped with a warning)
- PIL image verification and conversion to RGB
- EXIF rotation handling
- Per-image error handling during prediction
- Stale-results notice when uploaded files or selected species change
- Clear explanation that scores are uncalibrated outputs and not diagnoses

**Important distinction:** code-level handling is not the same as observed pass/fail test evidence. The current binary classifiers do **not** reliably reject non-goat or non-cattle photos, unseen disease types, or poor-quality images.

## Suggested immediate protections (without retraining)

1. Put a short reminder near the upload control: “Choose the correct animal and upload a clear photo. Other animals and unrelated images may receive unreliable predictions.”
2. Keep the current disclaimer: a Healthy-class prediction does not exclude disease.
3. Provide a short “Photo tips and limitations” expandable panel rather than overcrowding the main prediction page.
4. Record results of EC01–EC16; retain screenshots only for failures or especially useful examples.
5. Future work: validated out-of-distribution detection, automated species identification, validated image-quality screening, independent field tests, calibration and a safe abstention policy.
