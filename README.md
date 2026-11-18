# PentAI — Goat and Cattle Disease Detection

**Institution:** Moringa School  
**Capstone group:** Group 5 — PentAI  
**Repository:** https://github.com/justdanimatu/livestock-disease-detection  
**Project deadline:** 20 November 2026  
**Prepared by:** Dan Wamatu

## Overview

PentAI is a capstone research prototype for image-based screening of **goats and cattle**. It uses separate saved TensorFlow/Keras image classifiers and a Streamlit web interface. Users can classify up to 20 photographs in one batch, view model scores, download a CSV of predictions, inspect held-out evaluation results, and ask an optional Google Gemini assistant for general veterinary guidance.

**Final scope:** Goats and cattle only. Chickens/poultry are **excluded**.

| Animal | Supported classes |
|---|---|
| Goat | Goatpox, Healthy (dataset class) |
| Cattle | Lumpy skin disease, Healthy (dataset class) |

Predictions are **research screening results, not veterinary diagnoses**. A Healthy output does not rule out other diseases. Seek a qualified veterinarian for assessment and treatment decisions.

## Team

| Member | Role |
|---|---|
| Dan Wamatu | Project Manager |
| Linnet Kinyua | Scrum Master |
| Meshack Kimanzi | Team Member |
| Grace Muthoni | Team Member |
| Cleophas Ndunda | Team Member |

The team uses GitHub for code reviews/version control and ClickUp for task coordination.

## Implemented application

- **Home:** project overview and held-out test accuracy summary.
- **Analyze images:** choose goat or cattle; upload up to 20 JPEG/PNG images (12 MB limit per file); run species-specific classification; inspect class scores and export a prediction CSV.
- **Guidance assistant:** optional text-only Google Gemini advice; offline safety guidance remains usable without an API key or when Gemini is busy. Temporary **503** server errors are retried automatically (1, 2, and 4 seconds between attempts).
- **Model insights:** displays evaluation metrics, classification reports and confusion matrices already saved in the repository.
- **About PentAI:** method, boundaries and limitations.

Only chat text and an aggregate of prediction labels are sent to Gemini when enabled; uploaded photographs and filenames are **not** sent to Gemini by this app. API access requires an eligible Google Gemini key; a free tier may be available with quotas and capacity restrictions. No paid API is required for core image classification or offline guidance.

## Repository layout and required runtime files

```text
livestock-disease-detection/
├── app/
│   ├── app.py                 # Streamlit application and Gemini integration
│   ├── inference.py           # Preprocessing and model inference
│   └── guidance.py            # Conservative offline guidance
├── models/
│   ├── model_config.json      # Species-specific image size and model filenames
│   ├── labels.json            # Ordered model class labels
│   ├── goat_model.keras       # Saved goat classifier (required)
│   └── cattle_model.keras     # Saved cattle classifier (required)
├── evaluation/
│   ├── goat/
│   │   ├── metrics.json
│   │   ├── classification_report.csv
│   │   └── confusion_matrix.png
│   └── cattle/
│       ├── metrics.json
│       ├── classification_report.csv
│       └── confusion_matrix.png
├── data/                      # Raw and processed research data (may be external)
├── notebooks/                 # Data audit, preparation, training, evaluation
├── src/                       # Supporting scripts, if maintained
├── docs/                      # Proposal, inventory, project documentation
├── reports/                   # Project report, figures and presentation
├── requirements.txt           # Streamlit deployment dependencies
├── requirements-dev.txt       # Optional local/test dependencies
└── README.md
```

The app reads the `models/` and `evaluation/` files **at runtime**. If your deployment excludes saved `.keras` models or evaluation JSON files, the relevant pages will fail. Large raw datasets do **not** need to be uploaded to Streamlit. Check that your `.gitignore` does not exclude model files that the deployed app needs, or arrange another legitimate way of making them available at runtime.

## Installation (Windows / VS Code / PowerShell)

Install **Python 3.13** (64-bit), Git, and the Python extension for VS Code. From the project root:

```powershell
cd "$HOME\Documents\livestock-disease-detection"
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app/app.py
```

The development dependency file may contain extra test tooling; it is **not** needed for production deployment. If PowerShell blocks virtual-environment activation, use `.venv\Scripts\python.exe` to run Python directly, or follow your organization's execution-policy guidance.

## Google Gemini setup (optional)

1. Create an API key at https://aistudio.google.com/api-keys and use an available project/model with eligible free-tier access. API usage can be rate-limited and availability can change.
2. For **Streamlit Community Cloud**, open your deployed app → **Settings** → **Secrets** and save:

   ```toml
   GEMINI_API_KEY = "your-secret-api-key"
   # Optional: override the model if Google changes its availability
   GEMINI_MODEL = "gemini-3.5-flash-lite"
   ```

3. For **local development**, create `.streamlit/secrets.toml` in the repository root with the same keys. **Never commit this file or any API key to Git.** Alternatively, set environment variable `GEMINI_API_KEY` before launching the app.
4. Use the **Guidance assistant** page to test a general question such as: “What should I observe if a goat has suspicious skin lesions?”

`app/app.py` uses the maintained `google-genai` SDK rather than the paid OpenAI API. The project does not require `openai` in `requirements.txt`. The existing `app/guidance.py` file must remain available because the app imports `basic_guidance` for its fallback response.

### Handling Gemini errors

| Status | Meaning / action |
|---|---|
| 503 UNAVAILABLE | Google is temporarily overloaded. The app retries then shows offline guidance; test again later. |
| 429 RESOURCE_EXHAUSTED | Rate limit/quota reached. Check Google AI Studio API usage and free-tier limits. |
| 404 NOT_FOUND | Model not available to the project. Set `GEMINI_MODEL` to a currently supported model. |
| 401/403 | Invalid API key, project access, or permissions. Recheck Streamlit Secrets. |

Model identifiers and free-tier policies can change; validate available models in your Google AI Studio project. Do not switch to an arbitrary model name without confirming access.

## Deploying on Streamlit Community Cloud

1. Push the source code, model configuration, saved model weights, and required evaluation metadata to the GitHub repository (subject to file size and licensing limits).
2. In Streamlit Community Cloud, choose the GitHub repository and its deployment branch.
3. Set the **main file path** to `app/app.py` and use Python 3.13 if offered in advanced settings.
4. Add `GEMINI_API_KEY` under the app's **Secrets** if you want AI advice; it is optional.
5. Deploy. Test both **Analyze images** and **Guidance assistant**. The classifier should work even if Google Gemini is unavailable.

### Update and push changes

From the repository root:

```powershell
python -m py_compile app/app.py
git status
git add app/app.py README.md requirements.txt
git commit -m "Improve Gemini reliability and update project documentation"
git push origin main
```

If you use a feature branch, push that branch and merge the pull request before expecting the deployment from `main` to update. If VS Code warns that a file is *newer on disk*, use **Compare** and merge deliberately rather than overwriting unreviewed changes.

## Data and model methodology

Goat and cattle datasets are audited separately, with label mapping, image checks, splitting, model training, and held-out evaluation recorded in the project notebooks and documentation. The current application loads **pretrained/saved** models; it does not train models on user uploads. Inference uses RGB conversion, resize according to `models/model_config.json` (currently 224 × 224 for both animals), and model-internal preprocessing. The model output is a class score, **not a calibrated clinical probability**.

Project dataset references:
- Goat: [Goat Pox Detection dataset](https://drive.google.com/file/d/1Dpw1SHO_P0QVEiOo_VnCMDRE10Sae8Ed/view?usp=sharing)
- Cattle: [Healthy and Lumpy Skin Disease dataset](https://drive.google.com/file/d/1COCT4TeyrFEKH6oooxD62CzGXFHs67Ku/view?usp=sharing)
- Dataset details: [`docs/dataset_inventory.md`](docs/dataset_inventory.md)

## Limitations and safety

- Only the two listed classes per animal are supported. Other species, diseases, or low-quality images can produce unreliable labels.
- The app does not verify that an uploaded photograph actually depicts the selected animal.
- Held-out dataset results do not establish real-world clinical accuracy.
- Gemini advice is educational, may be incomplete or incorrect, and is not a substitute for veterinary examination.
- Contact a qualified veterinarian or animal-health authority for suspected infectious or notifiable diseases; do not prescribe or administer treatment based solely on this application.
- Do not enter confidential identifying information into the Gemini chat.

## Academic deliverables

Data audit and preprocessing notebooks, trained models, evaluation reports, the Streamlit prototype, technical documentation, and the final capstone report and presentation. Refer to the project documentation for evidence of completion; do not infer that all deliverables are finalized from the existence of this README.
