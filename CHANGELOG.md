# PentAI Changelog

This file records official releases of the PentAI Livestock Disease Detection application. Earlier Git commits represent development history and were not individually versioned.

## [1.0.0] - 2026-11-18

**First formally designated capstone release** (tag only after the verified main-branch revision is committed).

### Included capabilities
- Separate goatpox/healthy and cattle lumpy-skin-disease/healthy image classifiers.
- Single-image and batch image analysis, up to 20 JPEG/PNG uploads, with CSV export.
- Held-out evaluation views with metrics, confusion matrices and classification reports.
- Image-quality checks, duplicate detection, invalid-upload handling and user warnings.
- Gemini educational guidance assistant with offline guidance fallback.
- Frequently asked questions, Kenya-focused veterinary links and application information.
- Responsive desktop/mobile interface, navigation improvements, tooltips and clear-upload action.

### Verified held-out evaluation
| Measure | Goat | Cattle |
|---|---:|---:|
| Test images | 151 | 152 |
| Accuracy | 98.0% | 85.5% |
| Balanced accuracy | 97.5% | 79.3% |
| Macro F1 | 97.9% | 81.6% |

### Known limitations
- Supports only the trained classes, with no automatic species or unknown-disease detection.
- A healthy-class prediction does not establish that an animal is disease-free.
- Cattle lumpy-skin-disease recall was 62.5% on the held-out test data.
- Model scores are not calibrated clinical probabilities; veterinary examination is required.
- Gemini depends on an external API and may be temporarily unavailable.

### Versioning policy
- Development prior to v1.0.0 was not formally versioned. Git history retains individual commits.
- Use `v1.0.1` for a subsequent bug-fix release and `v1.1.0` for a subsequent backwards-compatible feature release, if needed.
- Create a Git tag for each confirmed release and update this file when changes are released.
