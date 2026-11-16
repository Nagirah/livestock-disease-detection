"""PentAI Livestock Disease Detection — enhanced research dashboard.

Only the presentation layer is expanded; inference.py retains the model's
original raw RGB 0..255 preprocessing and class order.
"""
from pathlib import Path
import json
import csv

import streamlit as st
from PIL import Image, UnidentifiedImageError

from inference import load_config, prepare_image, read_probabilities, model_path_for

ROOT = Path(__file__).resolve().parents[1]
EVALUATION_DIR = ROOT / "evaluation"
DISPLAY_LABELS = {
    "goatpox": "Goatpox",
    "lumpy_skin": "Lumpy skin disease",
    "healthy": "Healthy (model class)",
}

st.set_page_config(
    page_title="PentAI | Livestock Intelligence",
    page_icon="🐄",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap');
:root { --brand:#45dfb4; --ink:#e9f5f2; --muted:#9bb4ac; --line:#263d39; }
html, body, [data-testid="stAppViewContainer"] { font-family:'DM Sans', sans-serif; }
[data-testid="stAppViewContainer"] {
  background: radial-gradient(ellipse at 85% -15%, #173b36 0%, transparent 44%),
  linear-gradient(145deg,#0b1817 0%,#0e2220 55%,#0c1919 100%);
  color:var(--ink);
}
[data-testid="stSidebar"] { background:#0c1b1a; border-right:1px solid #27443e; }
[data-testid="stSidebar"] * { color:#dcece8; }
.block-container { padding-top:1.55rem; padding-bottom:3rem; max-width:1420px; }
h1,h2,h3 { font-family:'Outfit', sans-serif !important; letter-spacing:-.025em; }
h1 { font-weight:750 !important; }
[data-testid="stMetric"] { border:1px solid #29473f; background:linear-gradient(130deg,#142c28,#10231f); border-radius:15px; padding:1rem 1.2rem; }
[data-testid="stMetricLabel"] { color:#a9c1b8; }
[data-testid="stMetricValue"] { color:#f1faf6; }
[data-testid="stFileUploader"] { background:#122723; border:1px dashed #47736a; border-radius:16px; padding:.5rem; }
[data-testid="stTabs"] button { font-weight:700; }
[data-testid="stTabs"] [data-baseweb="tab-highlight"] { background:#45dfb4; }
.stButton > button[kind="primary"] { background:#43d8aa; color:#08211a; border:0; border-radius:11px; font-weight:800; }
.stButton > button[kind="primary"]:hover { background:#6cebc4; color:#08211a; }
.stButton > button { border-radius:11px; }
[data-testid="stAlert"] { border-radius:13px; }
.hero { padding:2rem 2.2rem; border-radius:22px; border:1px solid #315b51;
 background:linear-gradient(112deg,rgba(30,77,65,.96),rgba(17,48,43,.92) 60%,rgba(15,43,39,.90)); margin-bottom:1.2rem; }
.eyebrow { letter-spacing:.15em; text-transform:uppercase; font-size:.72rem; font-weight:800; color:#7af0cb; }
.hero h1 { font-size:clamp(2rem,3.3vw,3.25rem); margin:.5rem 0; line-height:1.1; color:#f1faf7; }
.hero p { color:#c4dbd4; font-size:1.01rem; max-width:720px; margin:.3rem 0 1.1rem; }
.hero-tags span { display:inline-block; margin:.2rem .45rem .1rem 0; font-size:.75rem; padding:.35rem .7rem;
 border:1px solid #47796c; border-radius:99px; color:#c8f4e7; background:#173c32; }
.section-label {font-weight:750; font-family:'Outfit',sans-serif; font-size:1.5rem; padding:.4rem 0 .7rem; color:#ecf7f1;}
.panel { background:linear-gradient(150deg,#142b27,#102420); border:1px solid #2b4840; border-radius:17px; padding:1.2rem 1.4rem; margin-bottom:1rem; }
.panel-title { font-family:'Outfit',sans-serif; font-size:1.1rem; color:#f0f7f3; font-weight:700; margin:0 0 .45rem; }
.panel-desc { font-size:.89rem; color:#a9c4bb; line-height:1.6; }
.kpi-row {display:flex; flex-wrap:wrap; gap:.75rem; margin:1rem 0 .8rem;}
.kpi-chip {display:inline-flex; gap:.35rem; align-items:center; background:#173c32; border:1px solid #35695a; border-radius:9px; padding:.45rem .7rem; font-size:.8rem; color:#d8f6e9;}
.result { background:linear-gradient(120deg,#173c32,#19332d); border:1px solid #4aa987; border-radius:17px; padding:1.25rem 1.4rem; margin:.7rem 0; }
.result .eyebrow {font-size:.71rem;}
.result .big {font-family:'Outfit',sans-serif;font-size:2rem;font-weight:800;color:#f6fff9;line-height:1.25;margin:.35rem 0;}
.result .small {color:#a8d4c5;font-size:.82rem;}
.brand-name {font-family:'Outfit',sans-serif;font-size:1.65rem;font-weight:800;color:#ebfcf4;}
.brand-sub {color:#85bcab;font-size:.75rem;letter-spacing:.1em;text-transform:uppercase;}
.info-dot {padding:.85rem 1rem;border-left:3px solid #53deb4; background:#122c26; color:#bbd6cd; border-radius:0 10px 10px 0; font-size:.88rem;}
footer {visibility:hidden;}
@media(max-width:700px) { .hero{padding:1.35rem;} .hero h1{font-size:2rem;} }
</style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner="Loading trained classification model...")
def get_model(path: str):
    import tensorflow as tf
    return tf.keras.models.load_model(path, compile=False)


@st.cache_data
def get_metadata():
    return load_config()


@st.cache_data
def get_metrics(animal: str):
    with (EVALUATION_DIR / animal / "metrics.json").open(encoding="utf-8") as f:
        return json.load(f)


def pct(value):
    return f"{value:.1%}"


def diagnostic_result(image: Image.Image, animal: str, config, labels):
    """Run existing inference pipeline with exact training-time preprocessing."""
    model_path = model_path_for(animal, config)
    if not model_path.is_file():
        raise FileNotFoundError(f"Model file not found: {model_path}")
    if config[animal]["preprocessing"] != "inside_model_raw_0_255":
        raise ValueError("Unexpected preprocessing mode; verify training metadata")
    batch = prepare_image(image, config[animal]["image_size"])
    model = get_model(str(model_path))
    raw = model.predict(batch, verbose=0)
    return read_probabilities(raw, labels)


with st.sidebar:
    st.markdown('<div class="brand-name">◈ PentAI</div><div class="brand-sub">Livestock intelligence</div>', unsafe_allow_html=True)
    st.divider()
    st.markdown("**CAPSTONE WORKSPACE**")
    st.caption("Image-based livestock disease classification")
    st.markdown("**Species covered**")
    st.markdown("🐐  Goats — Goatpox / Healthy")
    st.markdown("🐄  Cattle — Lumpy skin / Healthy")
    st.divider()
    st.markdown("**Model pipeline**")
    st.caption("MobileNetV2 transfer learning  ·  224 × 224 RGB  ·  2-class softmax")
    st.markdown('<div class="info-dot">This is a research demonstration, not a veterinary diagnostic device.</div>', unsafe_allow_html=True)
    st.divider()
    st.caption("PentAI  •  Moringa School capstone")

st.markdown("""
<div class="hero">
  <div class="eyebrow">AI-POWERED LIVESTOCK HEALTH · RESEARCH PROTOTYPE</div>
  <h1>Detect patterns.<br>Support healthier herds.</h1>
  <p>Explore image-based disease classification for goats and cattle using PentAI's trained MobileNetV2 models. View model predictions, confidence distributions and evaluation evidence in one workspace.</p>
  <div class="hero-tags"><span>🐐 Goatpox screening model</span><span>🐄 Lumpy skin classification</span><span>◈ MobileNetV2</span></div>
</div>
""", unsafe_allow_html=True)

config, label_map = get_metadata()
try:
    goat_metrics = get_metrics("goat")
    cattle_metrics = get_metrics("cattle")
except (OSError, ValueError, KeyError) as exc:
    st.error(f"Evaluation metadata could not be loaded: {exc}")
    st.stop()

metric_cols = st.columns(4)
with metric_cols[0]:
    st.metric("Animal species", "2", help="Goat and cattle models are separate")
with metric_cols[1]:
    st.metric("Disease targets", "2", help="Goatpox and lumpy skin disease")
with metric_cols[2]:
    st.metric("Goat test accuracy", pct(goat_metrics["accuracy"]))
with metric_cols[3]:
    st.metric("Cattle test accuracy", pct(cattle_metrics["accuracy"]))

work, performance, guide = st.tabs(["🔎  Disease prediction", "📊  Model insights", "📘  About the system"])

with work:
    st.markdown('<div class="section-label">Prediction workspace</div>', unsafe_allow_html=True)
    left, right = st.columns([1, 1.12], gap="large")
    with left:
        st.markdown('<div class="panel"><div class="panel-title">01 · Select your animal</div><div class="panel-desc">Choose the livestock species before uploading an image. The selection controls which disease model is used.</div></div>', unsafe_allow_html=True)
        species = st.segmented_control("Species", options=["Goat", "Cattle"], default="Goat", key="species")
        if species is None:
            species = "Goat"
        animal = species.lower()
        labels = label_map[animal]
        descriptions = {"goat": "Goatpox vs healthy (model class)", "cattle": "Lumpy skin disease vs healthy (model class)"}
        st.caption("**Supported predictions:** " + descriptions[animal])
        st.markdown('<div class="panel"><div class="panel-title">02 · Upload an image</div><div class="panel-desc">Choose a clear image in JPEG or PNG format. The uploaded image is resized to match the model input.</div></div>', unsafe_allow_html=True)
        uploaded = st.file_uploader("Choose a livestock image", type=["jpg", "jpeg", "png"], key="image_upload")
        predict = st.button("✦ Analyze image", type="primary", use_container_width=True, disabled=uploaded is None)
    with right:
        st.markdown('<div class="panel"><div class="panel-title">Image preview & prediction</div><div class="panel-desc">Your image appears here. Click Analyze image to run the selected classifier.</div></div>', unsafe_allow_html=True)
        if uploaded is None:
            st.info("Upload a goat or cattle image to begin the analysis.", icon="📷")
        else:
            try:
                with Image.open(uploaded) as source:
                    image = source.copy()
                    image.load()
                st.image(image, caption="Uploaded image • image will be resized to 224 × 224 for inference", use_container_width=True)
            except (UnidentifiedImageError, OSError, ValueError):
                st.error("Please upload a valid JPEG or PNG image.")
                st.stop()
            if predict:
                try:
                    with st.spinner(f"Running {species.lower()} disease model..."):
                        scores = diagnostic_result(image, animal, config, labels)
                    predicted, confidence = scores[0]
                    st.markdown(
                        '<div class="result"><div class="eyebrow">Top predicted class</div>'
                        f'<div class="big">{DISPLAY_LABELS.get(predicted, predicted)}</div>'
                        f'<div class="small">Model output score: {confidence:.1%} · not calibrated confidence</div></div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown("**Class probability distribution**")
                    for label, probability in scores:
                        st.progress(
                            min(max(probability, 0.0), 1.0),
                            text=f"{DISPLAY_LABELS.get(label, label)} — {probability:.1%}",
                        )
                    st.warning(
                        "This is a two-class research classifier, not a veterinary diagnosis. "
                        "A 'healthy' prediction does not rule out other diseases. "
                        "Consult a veterinarian if illness is suspected."
                    )
                except Exception as exc:
                    st.error(f"Prediction could not be completed: {exc}")
                    st.caption("Verify the saved models, TensorFlow compatibility and configuration files.")
    st.markdown('<div class="info-dot">Model probabilities measure how strongly the classifier favors its two known classes. They are not verified disease likelihoods and may be unreliable for unusual images.</div>', unsafe_allow_html=True)

with performance:
    st.markdown('<div class="section-label">Model evaluation insights</div>', unsafe_allow_html=True)
    st.caption("Metrics are read from the packaged held-out evaluation reports. They do not update when individual images are uploaded.")
    for animal, icon in [("goat", "🐐"), ("cattle", "🐄")]:
        metrics = goat_metrics if animal == "goat" else cattle_metrics
        st.subheader(f"{icon} {animal.capitalize()} classifier")
        cols = st.columns(4)
        cols[0].metric("Test accuracy", pct(metrics["accuracy"]))
        cols[1].metric("Balanced accuracy", pct(metrics["balanced_accuracy"]))
        cols[2].metric("Macro F1", pct(metrics["macro_f1"]))
        cols[3].metric("Held-out images", f"{metrics['test_samples']:,}")
        matrix_col, report_col = st.columns([1, 1], gap="large")
        with matrix_col:
            st.markdown("**Confusion matrix**")
            matrix_path = EVALUATION_DIR / animal / "confusion_matrix.png"
            if matrix_path.is_file():
                st.image(str(matrix_path), use_container_width=True)
            else:
                st.caption("Confusion matrix image unavailable")
        with report_col:
            st.markdown("**Class-level evaluation**")
            csv_path = EVALUATION_DIR / animal / "classification_report.csv"
            if csv_path.is_file():
                with csv_path.open(encoding="utf-8-sig", newline="") as f:
                    report = list(csv.DictReader(f))
                st.dataframe(report, use_container_width=True, hide_index=True)
            else:
                st.caption("Classification report unavailable")
            st.caption("Metrics reflect a single held-out test split and may not generalize to other farms, camera conditions, breeds, or disease presentations.")
        st.divider()

with guide:
    st.markdown('<div class="section-label">How the system works</div>', unsafe_allow_html=True)
    cards = st.columns(3, gap="medium")
    for col, title, body in [
        (cards[0], "01 · Choose species", "Select Goat or Cattle. The app does not infer species automatically and uses the selected species-specific model."),
        (cards[1], "02 · Prepare image", "The image is converted to RGB, resized to 224 × 224 and supplied as raw 0–255 pixels. Preprocessing is already included in the saved models."),
        (cards[2], "03 · Review output", "MobileNetV2 returns probabilities for two supported classes. The higher-scoring class is shown with the full distribution."),
    ]:
        with col:
            st.markdown(f'<div class="panel"><div class="panel-title">{title}</div><div class="panel-desc">{body}</div></div>', unsafe_allow_html=True)
    st.subheader("What can the models detect?")
    st.markdown("""
| Model | Supported classes | Not covered |
|---|---|---|
| Goat | Goatpox, Healthy (model class) | Other goat diseases and unspecified conditions |
| Cattle | Lumpy skin disease, Healthy (model class) | Other cattle diseases and unspecified conditions |
""")
    st.subheader("Interpretation and limitations")
    st.markdown("""
- **Research prototype:** Images do not replace veterinary examination, laboratory testing, or professional judgment.
- **Two classes per model:** Any image is scored against only the two learned classes, even when neither truly applies.
- **Not confidence-calibrated:** A high softmax value does not establish a correspondingly high probability of a true diagnosis.
- **Dataset-dependent accuracy:** The evaluation scores are based on held-out samples from the supplied datasets, not field deployment.
- **Manual species choice:** Choosing the wrong animal selects the wrong model and invalidates the result.
""")
    with st.expander("Technical architecture"):
        st.code("Upload → RGB + resize 224×224 → Saved MobileNetV2 model (internal preprocessing) → Softmax → Class mapping", language="text")
        st.caption("Goat classes: goatpox, healthy. Cattle classes: healthy, lumpy_skin. Saved models use the original 0–255 image scale.")

st.divider()
st.caption("PentAI · Livestock Disease Detection · Educational research demonstration · Poultry excluded")
