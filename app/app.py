"""PentAI livestock-disease app: home, batch predictions, model insights and optional AI guidance."""
from pathlib import Path
from io import BytesIO
import hashlib
import json
import os

import pandas as pd
import streamlit as st
from PIL import Image, ImageOps, UnidentifiedImageError

from inference import load_config, prepare_image, read_probabilities, model_path_for
from guidance import basic_guidance
from google import genai

ROOT = Path(__file__).resolve().parents[1]
EVALUATION_DIR = ROOT / "evaluation"
DISPLAY_LABELS = {"goatpox": "Goatpox", "healthy": "Healthy (model class)", "lumpy_skin": "Lumpy skin disease"}
MAX_BATCH_FILES = 20
MAX_BYTES_PER_FILE = 12 * 1024 * 1024

st.set_page_config(page_title="PentAI | Livestock Intelligence", page_icon="🐄", layout="wide", initial_sidebar_state="expanded")
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
[data-testid="stSidebar"] [role="radiogroup"] { gap: .3rem; }
[data-testid="stSidebar"] [role="radiogroup"] label { padding: .62rem .55rem; border-radius: .7rem; }
[data-testid="stSidebar"] [role="radiogroup"] label:hover { background:#1b3b34; }
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) { background:#214b3e; border:1px solid #428c70; }
[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] { color:#a9cabc; }

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

[data-testid="stImage"] img { max-height: 235px; object-fit: contain; border-radius: 12px; }
.thumb-caption { color:#c8dfd6; font-size:.77rem; line-height:1.3; overflow-wrap:anywhere; }
.summary-tag { color:#72e7c2; font-size:.9rem; font-weight:700; }
@media(max-width:700px){.block-container,[data-testid="stMainBlockContainer"]{padding:5rem .8rem 2rem!important;max-width:100%!important;}h1,h2,h3,.hero h1{white-space:normal!important;overflow-wrap:anywhere;line-height:1.3!important;}.hero h1{font-size:1.65rem!important;}[data-testid="stImage"] img{max-width:100%!important;height:auto!important;}[data-testid="stMetric"]{padding:.55rem .75rem;}}
</style>
""", unsafe_allow_html=True)



@st.cache_resource(show_spinner="Loading model...")
def get_model(path: str):
    import tensorflow as tf
    return tf.keras.models.load_model(path, compile=False)

@st.cache_data
def get_metadata():
    return load_config()

@st.cache_data
def get_metrics(animal):
    with (EVALUATION_DIR / animal / "metrics.json").open(encoding="utf-8") as f:
        return json.load(f)

def pct(value):
    return f"{value:.1%}"

def infer_one(image, animal, config, labels):
    path = model_path_for(animal, config)
    if not path.is_file():
        raise FileNotFoundError(f"Missing model: {path.name}. Copy it into models/.")
    if config[animal]["preprocessing"] != "inside_model_raw_0_255":
        raise ValueError("Unexpected preprocessing setting; consult the model metadata")
    batch = prepare_image(image, config[animal]["image_size"])
    scores = get_model(str(path)).predict(batch, verbose=0)
    return read_probabilities(scores, labels)

def open_image(data):
    with Image.open(BytesIO(data)) as im:
        im.verify()
    with Image.open(BytesIO(data)) as im:
        return ImageOps.exif_transpose(im).convert("RGB")

def get_api_key():
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
        if key and key.strip():
            return key.strip()
    except (FileNotFoundError, KeyError, OSError):
        pass

    return os.getenv("GEMINI_API_KEY", "").strip()
    

def create_gemini_response(api_key, question, prediction_context, history):
    """Generate educational animal-health guidance without sending photos or filenames."""
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    recent_history = "\n".join(
        f"{msg['role']}: {msg['content'][:1500]}"
        for msg in history[-6:]
        if msg.get('role') in ('user', 'assistant')
    )
    prompt = (
        "You are PentAI's educational livestock-health assistant, focused on goats "
        "and cattle. Give practical, concise, careful general guidance. "
        "The image classifier only distinguishes goatpox/healthy for goats and "
        "lumpy skin disease/healthy for cattle, and is not clinically validated. "
        "Treat predictions as unverified screening results, not diagnoses. "
        "Explain observation, safe separation, biosecurity, and when to contact "
        "a qualified veterinarian. Do not prescribe drugs, doses, or treatment "
        "plans; advise urgent veterinary care for severe or rapidly worsening signs. "
        "Do not claim to have examined any images. If the question is unrelated to "
        "animal health, politely steer back to livestock guidance.\n\n"
        f"Prediction summary: {prediction_context}\n"
        f"Recent conversation:\n{recent_history}\n"
        f"Current question: {question[:3000]}"
    )
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
    )
    if not response.text:
        raise ValueError("Gemini returned no text")
    return response.text


def result_context(rows):
    valid = [r for r in rows if r.get("status") == "ok"]
    if not valid:
        return "No successful model predictions available."
    # only aggregate results; never transmit photos or their filenames
    counts = {}
    for row in valid:
        key = row["prediction"]
        counts[key] = counts.get(key, 0) + 1
    return f"Species: {valid[0]['animal']}; {len(valid)} processed images; class counts: {counts}. Predictions are unverified research outputs."

config, label_map = get_metadata()
try:
    metrics = {animal: get_metrics(animal) for animal in ("goat", "cattle")}
except (OSError, ValueError, KeyError) as exc:
    st.error(f"Evaluation metadata missing or invalid: {exc}")
    st.stop()

if "results" not in st.session_state:
    st.session_state.results = []
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.markdown('<div class="brand-name">◈ PentAI</div><div class="brand-sub">Livestock intelligence</div>', unsafe_allow_html=True)
    st.caption("Image-based animal health screening")
    st.divider()
    st.markdown("**NAVIGATION**")
    page = st.radio(
        "Navigate",
        ["Home", "Analyze images", "Guidance assistant", "Model insights", "About PentAI"],
        format_func=lambda name: {
            "Home": "⌂  Home",
            "Analyze images": "▣  Analyze images",
            "Guidance assistant": "◉  Guidance assistant",
            "Model insights": "▥  Model insights",
            "About PentAI": "ⓘ  About PentAI",
        }[name],
        key="active_page",
        label_visibility="collapsed",
    )
    st.divider()
    st.markdown("**SUPPORTED ANIMALS**")
    st.write("🐐 Goat · Goatpox / Healthy")
    st.write("🐄 Cattle · Lumpy skin / Healthy")
    st.divider()
    st.caption("Decision-support tool. Veterinary assessment is required for diagnosis and treatment.")

if page == "Home":
    st.markdown("""<div class="hero"><div class="eyebrow">PENTAI · LIVESTOCK DISEASE DETECTION</div>
      <h1>Understand animal health,<br>one photo at a time.</h1>
      <p>An image-based screening assistant for recognizing patterns associated with goatpox and cattle lumpy skin disease. Upload one photo or a batch, review the results, and learn what to do next with veterinary guidance.</p>
      <div class="hero-tags"><span>🐐 Goat</span><span>🐄 Cattle</span><span>📷 Batch-ready</span><span>💬 Guidance assistant</span></div></div>""", unsafe_allow_html=True)
    a, b, c = st.columns(3)
    with a:
        st.markdown('<div class="panel"><div class="panel-title">1 · Choose an animal</div><div class="panel-desc">Select goat or cattle. Each animal has a different trained classifier.</div></div>', unsafe_allow_html=True)
    with b:
        st.markdown('<div class="panel"><div class="panel-title">2 · Upload photos</div><div class="panel-desc">Upload up to 20 images at once. Preview compact thumbnails rather than scrolling through large photos.</div></div>', unsafe_allow_html=True)
    with c:
        st.markdown('<div class="panel"><div class="panel-title">3 · Review next steps</div><div class="panel-desc">See model predictions and ask for general advice about appropriate veterinary follow-up.</div></div>', unsafe_allow_html=True)
    st.info("This system supports only two classes per animal. A Healthy prediction does not rule out illness. Seek a veterinarian for diagnosis or treatment.")
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Species", "2")
    m2.metric("Disease targets", "2")
    m3.metric("Goat test accuracy", pct(metrics["goat"]["accuracy"]))
    m4.metric("Cattle test accuracy", pct(metrics["cattle"]["accuracy"]))
    st.caption("Model accuracy was measured on held-out evaluation images, not independent veterinary field validation.")
    if st.button("Start analyzing images →", type="primary"):
        st.session_state.active_page = "Analyze images"
        st.rerun()

if page == "Analyze images":
    st.markdown('<div class="section-label">Analyze livestock images</div>', unsafe_allow_html=True)
    st.caption("Select an animal, upload up to 20 JPEG/PNG images, then click Analyze batch. Photos are processed locally by this app's trained classifiers.")
    species = st.segmented_control("Animal type", ["Goat", "Cattle"], default="Goat") or "Goat"
    animal = species.lower()
    uploads = st.file_uploader("Upload one or more images", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="batch_upload")
    if len(uploads) > MAX_BATCH_FILES:
        st.warning(f"Select at most {MAX_BATCH_FILES} files per batch. Only the first {MAX_BATCH_FILES} will be processed.")
    selected = uploads[:MAX_BATCH_FILES]
    prepared = []
    if selected:
        st.markdown(f"**Image thumbnails · {len(selected)} selected**")
        cols = st.columns(4)
        for idx, uploaded in enumerate(selected):
            data = uploaded.getvalue()
            error = None
            im = None
            try:
                if len(data) > MAX_BYTES_PER_FILE:
                    raise ValueError("Image exceeds 12 MB")
                im = open_image(data)
            except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as exc:
                error = str(exc)
            prepared.append((uploaded.name, data, im, error))
            with cols[idx % 4]:
                if im is not None:
                    thumb = im.copy()
                    thumb.thumbnail((200, 135))
                    st.image(thumb, width=155)
                else:
                    st.warning("Invalid image")
                st.caption(f"{idx+1}. {uploaded.name[:34]}")
    if st.button("✦ Analyze batch", type="primary", disabled=not bool(selected), use_container_width=True):
        records = []
        progress = st.progress(0, text="Processing images...")
        for index, (filename, data, im, error) in enumerate(prepared):
            row = {"image": filename, "animal": species, "prediction": "", "score": None, "status": "ok"}
            if error:
                row.update(status=f"error: {error}")
            else:
                try:
                    scores = infer_one(im, animal, config, label_map[animal])
                    best_label, score = scores[0]
                    row.update(prediction=DISPLAY_LABELS.get(best_label, best_label), score=round(float(score), 4))
                    for label, value in scores:
                        row[f"prob_{label}"] = round(float(value), 4)
                except Exception as exc:
                    row["status"] = f"error: {exc}"
            records.append(row)
            progress.progress((index + 1) / len(prepared), text=f"Processed {index + 1}/{len(prepared)}")
        st.session_state.results = records
        st.session_state.results_signature = hashlib.sha256((animal + "|" + "|".join(hashlib.sha256(d).hexdigest() for _, d, _, _ in prepared)).encode()).hexdigest()
        st.session_state.messages = []
        progress.empty()
    rows = st.session_state.results
    current_signature = hashlib.sha256((animal + "|" + "|".join(hashlib.sha256(d).hexdigest() for _, d, _, _ in prepared)).encode()).hexdigest() if prepared else ""
    if rows and st.session_state.get("results_signature") != current_signature:
        st.info("The selected animal or uploaded files have changed. Click Analyze batch to refresh the results.")
        rows = []
    if rows:
        st.markdown('<div class="section-label">Batch results</div>', unsafe_allow_html=True)
        successful = [r for r in rows if r["status"] == "ok"]
        m1, m2, m3 = st.columns(3)
        m1.metric("Images processed", len(rows))
        m2.metric("Successful predictions", len(successful))
        m3.metric("Errors", len(rows) - len(successful))
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, column_config={"score": st.column_config.NumberColumn("Model score", format="%.2f")})
        csv_bytes = pd.DataFrame(rows).to_csv(index=False).encode("utf-8-sig")
        st.download_button("⬇ Download results (CSV)", csv_bytes, file_name="pentai_batch_predictions.csv", mime="text/csv")
        st.caption("The scores are uncalibrated model outputs, not verified disease probabilities. Files remain in memory for the active app session; only predictions are included in the CSV.")
        st.warning("Any animal showing illness, unusual skin lesions, fever, or rapid worsening should be assessed by a veterinarian. Do not use model results alone to decide treatment.")
        if successful:
            with st.expander("Inspect individual class scores"):
                choices = [i for i,r in enumerate(rows) if r["status"] == "ok"]
                idx = st.selectbox("Image", choices, format_func=lambda i: f"{i+1}. {rows[i]['image']}")
                for label in label_map[rows[idx]["animal"].lower()]:
                    probability = rows[idx].get(f"prob_{label}", 0.0)
                    st.progress(float(probability), text=f"{DISPLAY_LABELS.get(label,label)} · {probability:.1%}")

if page == "Guidance assistant":
    st.markdown('<div class="section-label">Guidance assistant</div>', unsafe_allow_html=True)
    st.write("Ask about model results, observation, safe isolation practices, or how to prepare for a veterinary visit. This is general educational support, not a diagnosis or prescription.")
    key = get_api_key()
    if key:
        st.success("AI assistant enabled (Google Gemini API key configured).")
    else:
        st.info("AI chat is not connected yet. Basic offline guidance is available. Configure GEMINI_API_KEY in Streamlit secrets to enable AI responses.")
    if st.session_state.results:
        st.caption("Current prediction summary: " + result_context(st.session_state.results))
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    question = st.chat_input("Example: What should I do if a cow has suspicious skin lumps?")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)
        if key:
            try:
                answer = create_gemini_response(key, question, result_context(st.session_state.results), st.session_state.messages[-7:-1])
            except Exception as exc:
                answer = ("The AI service is unavailable right now. " + basic_guidance(question) + "\n\n" + f"Technical detail: {type(exc).__name__}")
        else:
            answer = "**Basic guidance (not AI):** " + basic_guidance(question)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)
    st.caption("Only your chat text and an aggregate of prediction labels are sent to Google Gemini when AI is enabled. Uploaded photos and filenames are not sent. Avoid entering private identifying details.")

if page == "Model insights":
    st.markdown('<div class="section-label">Model evaluation</div>', unsafe_allow_html=True)
    st.caption("Figures below are from fixed held-out evaluation reports, not generated from your new uploads.")
    for animal, icon in [("goat", "🐐"), ("cattle", "🐄")]:
        st.subheader(f"{icon} {animal.capitalize()} model")
        data = metrics[animal]
        cols = st.columns(4)
        for col, (label, value) in zip(cols, [("Accuracy", pct(data["accuracy"])), ("Balanced accuracy", pct(data["balanced_accuracy"])), ("Macro F1", pct(data["macro_f1"])), ("Test images", str(data["test_samples"]))]):
            col.metric(label, value)
        one, two = st.columns(2)
        with one:
            path = EVALUATION_DIR / animal / "confusion_matrix.png"
            if path.exists():
                st.image(str(path), caption="Confusion matrix", use_container_width=True)
        with two:
            path = EVALUATION_DIR / animal / "classification_report.csv"
            if path.exists():
                st.dataframe(pd.read_csv(path), hide_index=True, use_container_width=True)
        st.divider()

if page == "About PentAI":
    st.markdown('<div class="section-label">About PentAI</div>', unsafe_allow_html=True)
    st.write("PentAI is an image-based livestock screening application that analyzes goat and cattle photographs using separate MobileNetV2 models. It helps users review supported disease-class predictions and prepare for veterinary follow-up.")
    st.markdown("**Prediction flow:** Choose species → upload image(s) → RGB conversion and resize to 224×224 → saved species-specific model (internal preprocessing) → class scores → result and optional guidance.")
    st.markdown("**Limitations:** Only two classes per species; no automatic animal verification; outputs are not calibrated disease probabilities; dataset test performance may not generalize to field conditions; unrelated or poor-quality images can be misclassified.")
    st.markdown("**Veterinary advice:** Seek qualified veterinary assessment for clinical signs, testing and decisions. Do not medicate animals based solely on app predictions.")
    st.caption("Currently supports goats and cattle only; poultry and other conditions are not supported.")

st.divider()
st.caption("© PentAI · Livestock Disease Detection | Predictions support screening only; veterinary confirmation required.")
