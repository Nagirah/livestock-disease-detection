"""Apply tested, conservative PentAI app changes to the existing app/app.py.

Place this file in the repository root along with app/edge_cases.py and docs/*.
Run: python apply_pentai_updates.py
Creates app/app.py.bak. Aborts if expected anchors do not match.
"""
from pathlib import Path
import shutil

APP = Path('app/app.py')
MARKER = '# PENTAI_EDGE_CASES_V1'


def replace_one(src, old, new, label):
    count = src.count(old)
    if count != 1:
        raise ValueError(f'{label}: expected one matching anchor, found {count}; existing app not changed')
    return src.replace(old, new, 1)


def main():
    if not APP.is_file():
        raise SystemExit('Run this script from the repository root (app/app.py is missing).')
    if not Path('app/edge_cases.py').is_file():
        raise SystemExit('Copy app/edge_cases.py into the app folder first.')
    src = APP.read_text(encoding='utf-8')
    if MARKER in src:
        print('These updates are already installed; no changes made.')
        return

    src = replace_one(src,
        'from inference import load_config, prepare_image, read_probabilities, model_path_for',
        'from inference import load_config, prepare_image, read_probabilities, model_path_for\n'
        'from edge_cases import assess_image, prediction_warnings  ' + MARKER,
        'helper import')

    src = replace_one(src,
        'species = st.segmented_control("Animal type", ["Goat", "Cattle"], default="Goat") or "Goat"\n'
        '    animal = species.lower()',
        'species = st.segmented_control("Animal type", ["Goat", "Cattle"], default=None)\n'
        '    if species is None:\n'
        '        st.info("Choose the animal shown in your photos. PentAI cannot verify species automatically.")\n'
        '    else:\n'
        '        st.caption("Confirm all uploaded photos show the selected species, ideally one animal per image. Other species and unknown diseases are not supported.")\n'
        '    animal = (species or "").lower()',
        'species confirmation')

    src = replace_one(src,
        '    uploads = st.file_uploader("Upload one or more images", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="batch_upload")',
        '    with st.expander("Photo tips and supported images"):\n'
        '        st.write("Use a clear, well-lit photo of the selected goat or cow, preferably showing one animal and any relevant skin area. Avoid heavy filters, extreme close-ups, distant or obstructed views.")\n'
        '        st.caption("This app cannot automatically verify the animal, detect other diseases, or validate multiple animals in an image. Quality warnings are approximate, not guarantees.")\n'
        '    uploads = st.file_uploader("Upload one or more images", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="batch_upload")',
        'photo tips')

    src = replace_one(src,
        '                im = open_image(data)\n'
        '            except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as exc:',
        '                im = open_image(data)\n'
        '                blocking_error, _ = assess_image(im)\n'
        '                if blocking_error:\n'
        '                    raise ValueError(blocking_error)\n'
        '            except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as exc:',
        'image check')

    src = replace_one(src,
        'if st.button("✦ Analyze batch", type="primary", disabled=not bool(selected), use_container_width=True):\n'
        '        records = []',
        'if st.button("✦ Analyze batch", type="primary", disabled=not (bool(selected) and bool(species)), use_container_width=True):\n'
        '        records = []\n'
        '        seen_hashes = {}',
        'button and duplicates')

    src = replace_one(src,
        '            if error:\n'
        '                row.update(status=f"error: {error}")\n'
        '            else:\n'
        '                try:\n'
        '                    scores = infer_one(im, animal, config, label_map[animal])\n'
        '                    best_label, score = scores[0]\n'
        '                    row.update(prediction=DISPLAY_LABELS.get(best_label, best_label), score=round(float(score), 4))\n'
        '                    for label, value in scores:\n'
        '                        row[f"prob_{label}"] = round(float(value), 4)\n'
        '                except Exception as exc:\n'
        '                    row["status"] = f"error: {exc}"',
        '            digest = hashlib.sha256(data).hexdigest()\n'
        '            if error:\n'
        '                row.update(status=f"error: {error}")\n'
        '            elif digest in seen_hashes:\n'
        '                row.update(status="duplicate", warnings=f"Duplicate of image {seen_hashes[digest]}: prediction skipped")\n'
        '            else:\n'
        '                seen_hashes[digest] = index + 1\n'
        '                try:\n'
        '                    _, quality_warnings = assess_image(im)\n'
        '                    scores = infer_one(im, animal, config, label_map[animal])\n'
        '                    best_label, score = scores[0]\n'
        '                    row.update(prediction=DISPLAY_LABELS.get(best_label, best_label), score=round(float(score), 4))\n'
        '                    for label, value in scores:\n'
        '                        row[f"prob_{label}"] = round(float(value), 4)\n'
        '                    notices = quality_warnings + prediction_warnings(best_label, float(score))\n'
        '                    if notices:\n'
        '                        row["warnings"] = " | ".join(notices)\n'
        '                except Exception:\n'
        '                    row["status"] = "error: Could not analyze this image; try another photo."',
        'prediction block')

    src = replace_one(src,
        '        m3.metric("Errors", len(rows) - len(successful))\n'
        '        st.dataframe(pd.DataFrame(rows)',
        '        m3.metric("Errors / skipped", len(rows) - len(successful))\n'
        '        warnings_count = sum(bool(r.get("warnings")) for r in rows)\n'
        '        if warnings_count:\n'
        '            st.warning(f"{warnings_count} image(s) have quality, duplicate, or interpretation notices. Read the warnings column before relying on results.")\n'
        '        st.dataframe(pd.DataFrame(rows)',
        'results notice')

    src = replace_one(src,
        '        st.caption("The scores are uncalibrated model outputs, not verified disease probabilities. Files remain in memory for the active app session; only predictions are included in the CSV.")',
        '        st.caption("Scores are uncalibrated model outputs, not disease probabilities. Image-quality checks are heuristic and cannot prove the right species or detect unknown diseases. Photos remain in session memory; predictions and warnings appear in the CSV.")',
        'scores caption')

    start = 'if page == "Model insights":'
    end = 'if page == "About PentAI":'
    a, b = src.find(start), src.find(end)
    if a == -1 or b <= a:
        raise ValueError('Could not locate Model insights section; existing app not changed')
    src = src[:a] + '''if page == "Model insights":
    st.markdown('<div class="section-label">Model performance</div>', unsafe_allow_html=True)
    st.caption("Results are from held-out test images not used in training. They describe model evaluation, not predictions on new uploads or real-world diagnostic accuracy.")
    insight_view = st.radio("View results", ["Overview", "Goat", "Cattle"], horizontal=True, key="insight_view")

    if insight_view == "Overview":
        st.subheader("Evaluation overview")
        a, b = st.columns(2)
        with a:
            st.metric("Goat test accuracy", pct(metrics["goat"]["accuracy"]))
            st.caption("151 test images · 148 correct")
        with b:
            st.metric("Cattle test accuracy", pct(metrics["cattle"]["accuracy"]))
            st.caption("152 test images · 130 correct")
        st.markdown("#### Key findings")
        st.write("The goat model missed 3 of 60 goatpox images. The cattle model missed 18 of 48 lumpy skin disease images.")
        st.warning("Cattle lumpy skin disease recall is 62.5%. A Healthy result must not be used to rule out illness.")
        st.caption("Choose Goat or Cattle above for confusion matrices and detailed class-level scores.")
    else:
        animal = insight_view.lower()
        data = metrics[animal]
        st.subheader(("🐐 " if animal == "goat" else "🐄 ") + insight_view + " model")
        a, b, c = st.columns(3)
        a.metric("Accuracy", pct(data["accuracy"]))
        b.metric("Balanced accuracy", pct(data["balanced_accuracy"]))
        c.metric("Macro F1", pct(data["macro_f1"]))
        st.caption(f'{data["test_samples"]} held-out test images')
        st.markdown("#### Confusion matrix")
        matrix_path = EVALUATION_DIR / animal / "confusion_matrix.png"
        if matrix_path.exists():
            st.image(str(matrix_path), caption="Rows: actual class; columns: predicted class", use_container_width=True)
        else:
            st.info("Confusion matrix not available in the evaluation folder.")
        if animal == "goat":
            st.info("Goatpox: 57 of 60 detected; 3 incorrectly predicted healthy.")
        else:
            st.warning("Lumpy skin disease: 30 of 48 detected (62.5% recall); 18 incorrectly predicted healthy.")
        with st.expander("Detailed classification report"):
            report_path = EVALUATION_DIR / animal / "classification_report.csv"
            if report_path.exists():
                report = pd.read_csv(report_path)
                report = report.rename(columns={"Unnamed: 0": "Disease class"})
                if "Disease class" not in report.columns and len(report.columns):
                    report = report.rename(columns={report.columns[0]: "Disease class"})
                names = ["goatpox", "healthy"] if animal == "goat" else ["healthy", "lumpy_skin"]
                if "Disease class" in report.columns:
                    report = report[report["Disease class"].astype(str).isin(names)].copy()
                    report["Disease class"] = report["Disease class"].replace({"goatpox": "Goatpox", "healthy": "Healthy", "lumpy_skin": "Lumpy skin disease"})
                for col in ("precision", "recall", "f1-score"):
                    if col in report.columns:
                        report[col] = pd.to_numeric(report[col], errors="coerce").map(lambda v: f"{v:.1%}" if pd.notna(v) else "—")
                if "support" in report.columns:
                    report["support"] = pd.to_numeric(report["support"], errors="coerce").astype("Int64")
                report = report.rename(columns={"precision": "Precision", "recall": "Recall", "f1-score": "F1-score", "support": "Test images"})
                st.dataframe(report, hide_index=True, use_container_width=True)
            else:
                st.info("Classification report not available in the evaluation folder.")
        st.caption("These figures are evaluation statistics, not clinical validation or calibrated disease probabilities.")
''' + src[b:]

    src = replace_one(src,
        'st.markdown("**Limitations:** Only two classes per species; no automatic animal verification; outputs are not calibrated disease probabilities; dataset test performance may not generalize to field conditions; unrelated or poor-quality images can be misclassified.")',
        'st.markdown("**Limitations:** Only two classes per species; no automatic species verification, multiple-animal localization, or unknown-disease detection. Quality checks and low-confidence alerts are heuristics only; scores are uncalibrated and dataset performance may not generalize to field conditions.")',
        'about limitations')

    compile(src, str(APP), 'exec')
    backup = APP.with_suffix('.py.bak')
    shutil.copy2(APP, backup)
    APP.write_text(src, encoding='utf-8')
    print(f'Updated {APP}. Previous version saved as {backup}.')

if __name__ == '__main__':
    main()
