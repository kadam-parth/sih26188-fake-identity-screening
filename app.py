"""SIH26188 — AI-Based Fake Identity & Document Screening System.

Streamlit entry point. Run with: streamlit run app.py
"""
from __future__ import annotations

import hashlib
import io
import logging
from datetime import datetime
from typing import Any

import numpy as np
import streamlit as st
from PIL import Image

from src.config import (
    APP_NAME,
    APP_VERSION,
    APP_DESCRIPTION,
    DOCUMENT_TYPES,
    RISK_LEVELS,
    PRIVACY_NOTICE,
    OCR_LANGUAGES,
    DB_PATH,
)
from src.utils.helpers import (
    setup_logging,
    mask_sensitive_field,
    format_risk_level,
    get_risk_color,
    format_timestamp,
)
from src.database.db import ScreeningDatabase
from src.vision.preprocessing import ImagePreprocessor
from src.ocr.engine import OCREngine
from src.documents.detector import DocumentDetector
from src.documents.extractor import FieldExtractor
from src.documents.validators import DocumentValidator
from src.vision.tampering import TamperingAnalyzer
from src.verification.consistency import ConsistencyChecker
from src.risk.scoring import RiskScorer

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = setup_logging("app")

# ---------------------------------------------------------------------------
# Page config (must be first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS — professional dark‑themed security dashboard
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    /* Header area */
    .main-header {
        background: linear-gradient(135deg, #1a1f2e 0%, #0e1117 100%);
        padding: 1.5rem 2rem;
        border-radius: 10px;
        border-left: 4px solid #4A9EFF;
        margin-bottom: 1.5rem;
    }
    .main-header h1 {
        color: #FAFAFA;
        margin: 0;
        font-size: 1.8rem;
    }
    .main-header .version-badge {
        background: #4A9EFF;
        color: white;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        vertical-align: middle;
        margin-left: 8px;
    }
    .main-header p {
        color: #8b949e;
        margin: 0.3rem 0 0 0;
        font-size: 0.9rem;
    }

    /* Risk level badges */
    .risk-badge {
        display: inline-block;
        padding: 4px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
    }
    .risk-low    { background: #28a74522; color: #28a745; border: 1px solid #28a745; }
    .risk-medium { background: #ffc10722; color: #ffc107; border: 1px solid #ffc107; }
    .risk-high   { background: #dc354522; color: #dc3545; border: 1px solid #dc3545; }

    /* Status module cards */
    .module-status {
        background: #1a1f2e;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 6px 0;
    }
    .module-status .status-dot {
        display: inline-block;
        width: 8px; height: 8px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-active  { background: #28a745; }
    .status-pending { background: #ffc107; }
    .status-stub    { background: #6c757d; }

    /* Screening result section */
    .result-section {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
    }
    .result-section h4 {
        color: #4A9EFF;
        margin-top: 0;
        border-bottom: 1px solid #30363d;
        padding-bottom: 0.4rem;
    }

    /* Check table rows */
    .check-pass { color: #28a745; }
    .check-fail { color: #dc3545; }
    .check-warn { color: #ffc107; }

    /* Privacy banner */
    .privacy-banner {
        background: #1a1f2e;
        border: 1px solid #30363d;
        border-left: 3px solid #4A9EFF;
        padding: 0.75rem 1rem;
        border-radius: 6px;
        font-size: 0.82rem;
        color: #8b949e;
        margin-bottom: 1rem;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: #0d1117;
        border-right: 1px solid #30363d;
    }

    /* Footer */
    .footer-text {
        color: #6c757d;
        font-size: 0.75rem;
        text-align: center;
        padding-top: 2rem;
        border-top: 1px solid #30363d;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Cached resources
# ---------------------------------------------------------------------------
@st.cache_resource
def get_database() -> ScreeningDatabase:
    """Singleton database connection."""
    return ScreeningDatabase(db_path=DB_PATH)


@st.cache_resource
def get_ocr_engine() -> OCREngine:
    """Singleton OCR engine (lazy‑initialised)."""
    return OCREngine(languages=OCR_LANGUAGES)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def file_hash(file_bytes: bytes) -> str:
    """SHA‑256 hex digest of file contents."""
    return hashlib.sha256(file_bytes).hexdigest()[:16]


def np_image_to_pil(image: np.ndarray) -> Image.Image:
    """Convert a numpy array (BGR or grayscale) to a PIL Image for display."""
    if image is None:
        return Image.new("RGB", (100, 100), (30, 30, 30))
    if len(image.shape) == 2:
        return Image.fromarray(image, mode="L")
    if image.shape[2] == 3:
        # OpenCV BGR → RGB
        return Image.fromarray(image[:, :, ::-1])
    return Image.fromarray(image)


def render_risk_badge(level: str) -> str:
    """Return HTML for a coloured risk badge."""
    css_class = f"risk-{level.lower()}" if level.upper() in RISK_LEVELS else "risk-medium"
    info = RISK_LEVELS.get(level.upper(), RISK_LEVELS["MEDIUM"])
    return f'<span class="risk-badge {css_class}">{info["icon"]} {info["label"]}</span>'


def render_module_status(name: str, status: str) -> str:
    """Return HTML for a module status indicator."""
    if status == "not_implemented":
        dot_class = "status-stub"
        label = "Pending"
    elif status == "success":
        dot_class = "status-active"
        label = "Active"
    else:
        dot_class = "status-pending"
        label = status.replace("_", " ").title()
    return (
        f'<div class="module-status">'
        f'<span class="status-dot {dot_class}"></span>'
        f'<strong>{name}</strong> — <em>{label}</em>'
        f'</div>'
    )


# ═══════════════════════════════════════════════════════════════════════════
# PAGES
# ═══════════════════════════════════════════════════════════════════════════

def page_screening() -> None:
    """Main document screening page."""
    # Header
    st.markdown(
        f'<div class="main-header">'
        f'<h1>🛡️ {APP_NAME} <span class="version-badge">v{APP_VERSION}</span></h1>'
        f"<p>{APP_DESCRIPTION}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Privacy banner (collapsed)
    with st.expander("🔒 Privacy Notice", expanded=False):
        st.markdown(PRIVACY_NOTICE)

    # ── Upload ─────────────────────────────────────────────────────────────
    st.subheader("📤 Upload Document(s)")
    uploaded_files = st.file_uploader(
        "Select identity document image(s)",
        type=["jpg", "jpeg", "png", "bmp", "tiff"],
        accept_multiple_files=True,
        help="Supported formats: JPG, PNG, BMP, TIFF. Max 10 MB per file.",
    )

    if not uploaded_files:
        st.info("👆 Upload one or more identity document images to begin screening.")
        _render_supported_docs_summary()
        return

    # Show thumbnails
    thumb_cols = st.columns(min(len(uploaded_files), 4))
    for idx, uf in enumerate(uploaded_files):
        with thumb_cols[idx % len(thumb_cols)]:
            img = Image.open(uf)
            st.image(img, caption=uf.name, use_container_width=True)
            uf.seek(0)  # reset after read

    st.divider()

    # ── Analyze button ─────────────────────────────────────────────────────
    if st.button("🔍 Analyze Document(s)", type="primary", use_container_width=True):
        db = get_database()
        ocr_engine = get_ocr_engine()

        all_doc_results: list[dict[str, Any]] = []

        for uf in uploaded_files:
            st.markdown(f"---\n### 📄 Analysis: `{uf.name}`")

            try:
                raw_bytes = uf.read()
                uf.seek(0)
                fhash = file_hash(raw_bytes)

                pil_img = Image.open(io.BytesIO(raw_bytes))
                if pil_img.mode == "RGBA":
                    pil_img = pil_img.convert("RGB")
                img_array = np.array(pil_img)

                # ── Pipeline ───────────────────────────────────────────────
                with st.status("Running analysis pipeline…", expanded=True) as status_bar:
                    # 1. Preprocessing
                    st.write("🖼️ Preprocessing image…")
                    preprocessor = ImagePreprocessor()
                    prep = preprocessor.preprocess(img_array)

                    # 2. OCR
                    # Use grayscale (not threshold) image — EasyOCR works
                    # poorly on hard-binarised images because thresholding
                    # destroys the gradient information its models need.
                    st.write("📝 Extracting text (OCR)…")
                    ocr_image = (
                        prep.get("grayscale")       # best: denoised grayscale
                        if prep.get("grayscale") is not None
                        else prep.get("processed", img_array)
                    )
                    ocr_result = ocr_engine.extract_text(ocr_image)

                    # 3. Document detection
                    st.write("🔍 Detecting document type…")
                    detector = DocumentDetector()
                    detect_result = detector.detect(ocr_result.get("text", ""))
                    doc_type = detect_result.get("document_type")

                    # 4. Field extraction
                    st.write("📋 Extracting identity fields…")
                    extractor = FieldExtractor()
                    extract_result = extractor.extract(ocr_result.get("text", ""), doc_type or "")

                    # 5. Validation
                    st.write("✅ Validating fields…")
                    validator = DocumentValidator()
                    valid_result = validator.validate(extract_result.get("fields", {}), doc_type or "")

                    # 6. Tampering analysis
                    st.write("🔬 Analyzing for tampering indicators…")
                    tampering = TamperingAnalyzer()
                    tamp_result = tampering.analyze(img_array)

                    # 7. Risk scoring
                    st.write("⚖️ Calculating risk score…")
                    scorer = RiskScorer()
                    risk_result = scorer.calculate(valid_result, tamp_result)

                    status_bar.update(label="✅ Analysis complete", state="complete")

                # Collect module statuses
                module_statuses = {
                    "OCR Engine": ocr_result.get("status", "unknown"),
                    "Document Detector": detect_result.get("status", "unknown"),
                    "Field Extractor": extract_result.get("status", "unknown"),
                    "Field Validator": valid_result.get("status", "unknown"),
                    "Tampering Analyzer": tamp_result.get("status", "unknown"),
                    "Risk Scorer": risk_result.get("status", "unknown"),
                }

                # Check if any modules are stubs
                stub_modules = [k for k, v in module_statuses.items() if v == "not_implemented"]
                if stub_modules:
                    st.warning(
                        f"⏳ **{len(stub_modules)} module(s) pending implementation:** "
                        + ", ".join(stub_modules)
                        + ". Results below reflect only active modules."
                    )

                # ── Display results ────────────────────────────────────────
                _render_results(
                    prep=prep,
                    ocr_result=ocr_result,
                    detect_result=detect_result,
                    extract_result=extract_result,
                    valid_result=valid_result,
                    tamp_result=tamp_result,
                    risk_result=risk_result,
                    module_statuses=module_statuses,
                    doc_type=doc_type,
                )

                # ── Save to DB ─────────────────────────────────────────────
                level = risk_result.get("level", "LOW")
                screening_record = {
                    "timestamp": format_timestamp(),
                    "document_type": doc_type,
                    "document_name": detect_result.get("document_name", "Unknown"),
                    "risk_score": risk_result.get("score", 0.0),
                    "risk_level": level,
                    "recommendation": risk_result.get("recommendation", ""),
                    "findings": {
                        "ocr": {"status": ocr_result.get("status"), "confidence": ocr_result.get("confidence")},
                        "detection": {"type": doc_type, "confidence": detect_result.get("confidence")},
                        "extraction": {"count": extract_result.get("extraction_count"), "total": extract_result.get("total_fields")},
                        "validation": {"valid": valid_result.get("valid_count"), "total": valid_result.get("total_count"), "checks": valid_result.get("checks", [])},
                        "tampering": {"suspicious": tamp_result.get("overall_suspicious"), "score": tamp_result.get("suspicion_score"), "checks": tamp_result.get("checks", [])},
                        "risk": {"score": risk_result.get("score"), "level": level, "factors": risk_result.get("factors", [])},
                    },
                    "file_hash": fhash,
                }
                sid = db.save_screening(screening_record)
                if sid and sid > 0:
                    st.caption(f"💾 Screening saved (ID: {sid})")

                all_doc_results.append({
                    "document_type": doc_type,
                    "fields": extract_result.get("fields", {}),
                    "validation": valid_result,
                })

            except Exception as exc:
                logger.exception("Error processing %s", uf.name)
                st.error(f"❌ Error processing **{uf.name}**: {exc}")

        # ── Cross‑document consistency (if multiple) ───────────────────────
        if len(all_doc_results) >= 2:
            st.markdown("---\n### 🔗 Cross‑Document Consistency Check")
            checker = ConsistencyChecker()
            consistency = checker.check(all_doc_results)
            if consistency.get("status") == "not_implemented":
                st.info("⏳ Cross‑document consistency checker not yet implemented.")
            else:
                st.json(consistency)


def _render_supported_docs_summary() -> None:
    """Show a compact card of supported document types."""
    cols = st.columns(len(DOCUMENT_TYPES))
    for col, (key, doc) in zip(cols, DOCUMENT_TYPES.items()):
        with col:
            st.markdown(
                f"**{doc['name']}**\n\n"
                f"_{doc['description']}_\n\n"
                f"Fields: {len(doc['fields'])}"
            )


def _render_results(
    *,
    prep: dict,
    ocr_result: dict,
    detect_result: dict,
    extract_result: dict,
    valid_result: dict,
    tamp_result: dict,
    risk_result: dict,
    module_statuses: dict,
    doc_type: str | None,
) -> None:
    """Render the full analysis results panel."""

    # ── Row 1: Risk score + Document info ──────────────────────────────────
    col_risk, col_doc = st.columns([1, 2])

    with col_risk:
        st.markdown('<div class="result-section">', unsafe_allow_html=True)
        st.markdown("#### ⚖️ Risk Assessment")
        score = risk_result.get("score", 0.0)
        level = risk_result.get("level", "LOW")
        st.metric("Risk Score", f"{score:.2f}")
        st.markdown(render_risk_badge(level), unsafe_allow_html=True)
        st.markdown(f"**Recommendation:** {risk_result.get('recommendation', 'N/A')}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_doc:
        st.markdown('<div class="result-section">', unsafe_allow_html=True)
        st.markdown("#### 📄 Document Information")
        doc_name = detect_result.get("document_name", "Unknown")
        doc_conf = detect_result.get("confidence", 0.0)
        c1, c2 = st.columns(2)
        c1.metric("Document Type", doc_name)
        c2.metric("Detection Confidence", f"{doc_conf:.0%}")
        if detect_result.get("matched_keywords"):
            st.caption(f"Matched keywords: {', '.join(detect_result['matched_keywords'])}")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Row 2: Preprocessing + OCR ─────────────────────────────────────────
    with st.expander("🖼️ Preprocessing Steps", expanded=False):
        step_cols = st.columns(min(len(prep.get("steps", [])), 4) or 1)
        for idx, step in enumerate(prep.get("steps", [])):
            with step_cols[idx % len(step_cols)]:
                st.caption(f"**{step['name'].title()}**")
                st.image(np_image_to_pil(step.get("image")), caption=step["description"], use_container_width=True)

    with st.expander("📝 OCR Results", expanded=True):
        ocr_status = ocr_result.get("status", "unknown")
        ocr_text = ocr_result.get("text", "")

        if ocr_status == "success" and ocr_text:
            st.text_area("Extracted Text", ocr_text, height=150, disabled=True)
            ocr_conf = ocr_result.get("confidence", 0.0)
            n_regions = len(ocr_result.get("details", []))
            st.caption(
                f"Confidence: {ocr_conf:.0%} · "
                f"Regions: {n_regions} · "
                f"Engine: {ocr_result.get('engine', 'N/A')}"
            )
        elif ocr_status == "no_text":
            msg = ocr_result.get("message", "No readable text was detected in this image.")
            st.warning(f"📭 {msg}")
        elif ocr_status == "error":
            msg = ocr_result.get("message", "An error occurred during text extraction.")
            st.error(f"❌ OCR Error: {msg}")
        else:
            st.info(f"OCR returned status: {ocr_status}.")

    # ── Row 3: Extracted fields ────────────────────────────────────────────
    st.markdown('<div class="result-section">', unsafe_allow_html=True)
    st.markdown("#### 📋 Extracted Fields")
    fields = extract_result.get("fields", {})
    if fields:
        field_data = []
        for fname, fval in fields.items():
            display_val = fval
            if isinstance(fval, dict):
                display_val = fval.get("value", str(fval))
            masked = mask_sensitive_field(str(display_val), fname, doc_type or "")
            # Look up label from config
            label = fname
            if doc_type and doc_type in DOCUMENT_TYPES:
                fconf = DOCUMENT_TYPES[doc_type]["fields"].get(fname, {})
                label = fconf.get("label", fname)
            field_data.append({"Field": label, "Value": masked})
        st.table(field_data)
    else:
        st.info("No identity fields were extracted. The document may be unrecognised or OCR text was insufficient.")
    st.markdown(f"Extracted **{extract_result.get('extraction_count', 0)}** / **{extract_result.get('total_fields', 0)}** defined fields.")
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Row 4: Validation checks ───────────────────────────────────────────
    st.markdown('<div class="result-section">', unsafe_allow_html=True)
    st.markdown("#### ✅ Validation Checks")
    valid_status = valid_result.get("status", "")
    checks = valid_result.get("checks", [])

    if valid_status == "error" and not checks:
        findings = valid_result.get("findings", [])
        if findings:
            for f in findings:
                st.warning(f)
        else:
            st.info("No validation checks could be performed.")
    elif checks:
        # Display as a table
        check_data = []
        for chk in checks:
            icon = "✅" if chk.get("passed") else "❌"
            check_data.append({
                "Check": chk.get("check_name", chk.get("field", "")),
                "Result": f"{icon} {'Passed' if chk.get('passed') else 'Failed'}",
                "Details": chk.get("message", ""),
            })
        st.table(check_data)

        # Show findings
        findings = valid_result.get("findings", [])
        if findings:
            st.markdown("**Validation Findings:**")
            for f in findings:
                st.markdown(f"- {f}")
    else:
        st.info("No validation checks were performed.")

    vc = valid_result.get("valid_count", 0)
    tc = valid_result.get("total_count", 0)
    st.caption(f"Passed: {vc}/{tc}")
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Row 5: Tampering analysis ──────────────────────────────────────────
    st.markdown('<div class="result-section">', unsafe_allow_html=True)
    st.markdown("#### 🔬 Tampering / Anomaly Analysis")
    tamp_checks = tamp_result.get("checks", [])
    if tamp_checks:
        for tc_item in tamp_checks:
            icon = "🚨" if tc_item.get("suspicious") else "✅"
            st.markdown(
                f"{icon} **{tc_item.get('name', '')}** — {tc_item.get('result', tc_item.get('description', ''))}"
            )
        if tamp_result.get("ela_image") is not None:
            st.image(
                np_image_to_pil(tamp_result["ela_image"]),
                caption="Error Level Analysis (ELA)",
                use_container_width=True,
            )
    else:
        st.info("No tampering analysis available yet. Tampering module is pending implementation.")
    st.caption(
        f"Suspicion score: {tamp_result.get('suspicion_score', 0.0):.2f} · "
        f"Overall suspicious: {'Yes' if tamp_result.get('overall_suspicious') else 'No'}"
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Module status overview ─────────────────────────────────────────────
    with st.expander("🔧 Module Status", expanded=False):
        status_html = "".join(render_module_status(k, v) for k, v in module_statuses.items())
        st.markdown(status_html, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
def page_history() -> None:
    """Screening history page."""
    st.markdown(
        f'<div class="main-header">'
        f"<h1>📊 Screening History</h1>"
        f"<p>Review past document screenings and their results.</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    db = get_database()
    count = db.get_screening_count()

    # Metrics row
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Screenings", count)

    screenings = db.get_all_screenings()

    # Count by risk level
    levels = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    for s in screenings:
        lv = (s.get("risk_level") or "LOW").upper()
        levels[lv] = levels.get(lv, 0) + 1
    col2.metric("🟢 Low Risk", levels["LOW"])
    col3.metric("🔴 High Risk", levels["HIGH"])

    st.divider()

    if not screenings:
        st.info("No screenings recorded yet. Go to **Document Screening** to analyze documents.")
        return

    # Table view
    for s in screenings:
        sid = s.get("id", "?")
        ts = s.get("timestamp", s.get("created_at", ""))
        doc_name = s.get("document_name", "Unknown")
        risk_lvl = (s.get("risk_level") or "LOW").upper()
        risk_score = s.get("risk_score", 0.0)

        badge = render_risk_badge(risk_lvl)
        header = f"**#{sid}** · {doc_name} · Score: {risk_score:.2f} · {ts}"

        with st.expander(header, expanded=False):
            st.markdown(badge, unsafe_allow_html=True)
            st.markdown(f"**Recommendation:** {s.get('recommendation', 'N/A')}")

            findings = s.get("findings")
            if findings and isinstance(findings, dict):
                st.json(findings)

            if st.button(f"🗑️ Delete screening #{sid}", key=f"del_{sid}"):
                db.delete_screening(sid)
                st.success(f"Screening #{sid} deleted.")
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
def page_about() -> None:
    """About / information page."""
    st.markdown(
        f'<div class="main-header">'
        f"<h1>ℹ️ About</h1>"
        f"<p>System information, supported documents, and privacy details.</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown(f"### {APP_NAME}")
    st.markdown(f"**Version:** {APP_VERSION}")
    st.markdown(APP_DESCRIPTION)

    st.divider()

    # Supported document types
    st.markdown("### 📄 Supported Document Types")
    for key, doc in DOCUMENT_TYPES.items():
        with st.expander(f"{doc['name']} — {doc['description']}", expanded=False):
            st.markdown("**Extractable fields:**")
            for fname, fconf in doc["fields"].items():
                req = "Required" if fconf.get("required") else "Optional"
                sens = " · 🔒 Sensitive" if fconf.get("sensitive") else ""
                st.markdown(f"- **{fconf['label']}** ({fconf.get('format_description', 'N/A')}) — _{req}{sens}_")
            if doc.get("checksum_algorithm"):
                st.caption(f"Checksum: {doc['checksum_algorithm']} on {doc['checksum_field']}")

    st.divider()

    # Technology stack
    st.markdown("### 🛠️ Technology Stack")
    tech_data = [
        {"Component": "UI Framework", "Technology": "Streamlit"},
        {"Component": "Image Processing", "Technology": "OpenCV"},
        {"Component": "OCR Engine", "Technology": "EasyOCR"},
        {"Component": "Database", "Technology": "SQLite"},
        {"Component": "ML/Validation", "Technology": "scikit‑learn, regex, Verhoeff checksum"},
        {"Component": "Language", "Technology": "Python 3.11+"},
    ]
    st.table(tech_data)

    st.divider()

    # Privacy
    st.markdown("### 🔒 Privacy")
    st.markdown(PRIVACY_NOTICE)

    st.divider()

    # Disclaimer
    st.markdown("### ⚠️ Disclaimer")
    st.warning(
        "This is a **screening tool** that identifies potential indicators of concern. "
        "It does **not** make legal determinations about whether a document is authentic "
        "or whether a person's identity is genuine. All findings require human review "
        "and verification through authorized channels. Suspicion scores are heuristic "
        "indicators, not statistically calibrated probabilities."
    )

    # Footer
    st.markdown(
        '<div class="footer-text">'
        f"SIH26188 · {APP_NAME} v{APP_VERSION} · Smart India Hackathon Project"
        "</div>",
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════
def main() -> None:
    """Application entry point with sidebar navigation."""

    # Sidebar
    with st.sidebar:
        st.markdown(f"### 🛡️ {APP_NAME}")
        st.caption(f"v{APP_VERSION}")
        st.divider()

        page = st.radio(
            "Navigation",
            ["📋 Document Screening", "📊 Screening History", "ℹ️ About"],
            label_visibility="collapsed",
        )

        st.divider()

        # Quick stats
        db = get_database()
        st.metric("Screenings", db.get_screening_count())

        st.divider()
        st.markdown(
            '<div class="privacy-banner">'
            "🔒 All processing is performed locally. "
            "No data is sent to external services."
            "</div>",
            unsafe_allow_html=True,
        )

    # Route
    if page == "📋 Document Screening":
        page_screening()
    elif page == "📊 Screening History":
        page_history()
    elif page == "ℹ️ About":
        page_about()


if __name__ == "__main__":
    main()
