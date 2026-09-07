"""SIH26188 — AI-Based Fake Identity & Document Screening System.

Streamlit entry point. Run with: streamlit run app.py
"""
from __future__ import annotations

import hashlib
import io
import json
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

    /* Suspicious / alert highlights */
    .indicator-suspicious {
        background: #dc354515;
        border-left: 3px solid #dc3545;
        padding: 0.5rem 0.75rem;
        border-radius: 4px;
        margin: 0.3rem 0;
        font-size: 0.88rem;
    }
    .indicator-normal {
        background: #28a74510;
        border-left: 3px solid #28a745;
        padding: 0.5rem 0.75rem;
        border-radius: 4px;
        margin: 0.3rem 0;
        font-size: 0.88rem;
    }

    /* Risk score hero display */
    .risk-hero {
        text-align: center;
        padding: 1.2rem 0.5rem;
    }
    .risk-hero .score-value {
        font-size: 2.8rem;
        font-weight: 800;
        line-height: 1;
    }
    .risk-hero .score-label {
        font-size: 0.8rem;
        color: #8b949e;
        margin-top: 0.3rem;
    }
    .risk-hero .score-low    { color: #28a745; }
    .risk-hero .score-medium { color: #ffc107; }
    .risk-hero .score-high   { color: #dc3545; }

    /* Intro card */
    .intro-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        margin-bottom: 1rem;
    }
    .intro-card h4 { color: #4A9EFF; margin-top: 0; }

    /* Download button area */
    .download-area {
        background: #1a1f2e;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
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

    # ── Intro card ────────────────────────────────────────────────────────
    st.markdown(
        '<div class="intro-card">'
        "<h4>How It Works</h4>"
        "<p>Upload an identity document image and the system will automatically:</p>"
        "<ol>"
        "<li><strong>Extract text</strong> using OCR (EasyOCR)</li>"
        "<li><strong>Detect document type</strong> (Aadhaar, PAN, Voter ID)</li>"
        "<li><strong>Extract &amp; validate fields</strong> (name, ID number, DOB)</li>"
        "<li><strong>Analyze image anomalies</strong> (ELA, edge density, noise)</li>"
        "<li><strong>Score risk indicators</strong> with an explainable heuristic</li>"
        "</ol>"
        "<p style='color:#8b949e;font-size:0.82rem;'>"
        "🧪 For testing, use synthetic or dummy document images. "
        "Do not upload real identity documents in demo environments.</p>"
        "</div>",
        unsafe_allow_html=True,
    )

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

                    # Risk scoring deferred until after consistency check
                    risk_result = None

                    status_bar.update(label="✅ Analysis complete", state="complete")

                # Collect per-document results for consistency
                all_doc_results.append({
                    "document_type": doc_type,
                    "fields": extract_result.get("fields", {}),
                    "validation": valid_result,
                    "tampering": tamp_result,
                    # These are needed for rendering and DB save
                    "_prep": prep,
                    "_ocr": ocr_result,
                    "_detect": detect_result,
                    "_extract": extract_result,
                    "_valid": valid_result,
                    "_tamp": tamp_result,
                    "_doc_type": doc_type,
                    "_fhash": fhash,
                })

            except (OSError, IOError) as exc:
                logger.exception("Image read error for %s", uf.name)
                st.error(
                    f"❌ Could not read **{uf.name}**. The file may be corrupted "
                    f"or in an unsupported format. Please try a different image."
                )
            except MemoryError:
                logger.exception("Memory error processing %s", uf.name)
                st.error(
                    f"❌ **{uf.name}** is too large to process. "
                    f"Please use a smaller image (recommended: under 5 MB)."
                )
            except Exception as exc:
                logger.exception("Error processing %s", uf.name)
                st.error(
                    f"❌ An unexpected error occurred while processing **{uf.name}**. "
                    f"Please try a different image or check the file format."
                )
                with st.expander("Technical details", expanded=False):
                    st.code(str(exc))

        # ── Cross-document consistency ──────────────────────────────────
        checker = ConsistencyChecker()
        consistency_result = checker.check(all_doc_results)

        # ── Risk scoring + display per document ─────────────────────────
        scorer = RiskScorer()

        for doc_data in all_doc_results:
            valid_result = doc_data["_valid"]
            tamp_result = doc_data["_tamp"]
            risk_result = scorer.calculate(
                valid_result, tamp_result, consistency_result,
            )

            module_statuses = {
                "OCR Engine": doc_data["_ocr"].get("status", "unknown"),
                "Document Detector": doc_data["_detect"].get("status", "unknown"),
                "Field Extractor": doc_data["_extract"].get("status", "unknown"),
                "Field Validator": valid_result.get("status", "unknown"),
                "Tampering Analyzer": tamp_result.get("status", "unknown"),
                "Risk Scorer": risk_result.get("status", "unknown"),
            }

            # Display results for this document
            try:
                _render_results(
                    prep=doc_data["_prep"],
                    ocr_result=doc_data["_ocr"],
                    detect_result=doc_data["_detect"],
                    extract_result=doc_data["_extract"],
                    valid_result=valid_result,
                    tamp_result=tamp_result,
                    risk_result=risk_result,
                    module_statuses=module_statuses,
                    doc_type=doc_data["_doc_type"],
                )
            except Exception as render_exc:
                logger.exception("Error in _render_results")
                st.error(f"❌ Error rendering results: {render_exc}")

            # Save to DB
            level = risk_result.get("level", "LOW")
            screening_record = {
                "timestamp": format_timestamp(),
                "document_type": doc_data["_doc_type"],
                "document_name": doc_data["_detect"].get("document_name", "Unknown"),
                "risk_score": risk_result.get("score", 0.0),
                "risk_level": level,
                "recommendation": risk_result.get("recommendation", ""),
                "findings": {
                    "ocr": {"status": doc_data["_ocr"].get("status"), "confidence": doc_data["_ocr"].get("confidence")},
                    "detection": {"type": doc_data["_doc_type"], "confidence": doc_data["_detect"].get("confidence")},
                    "extraction": {"count": doc_data["_extract"].get("extraction_count"), "total": doc_data["_extract"].get("total_fields")},
                    "validation": {"valid": valid_result.get("valid_count"), "total": valid_result.get("total_count"), "checks": valid_result.get("checks", [])},
                    "tampering": {"suspicious": tamp_result.get("overall_suspicious"), "score": tamp_result.get("suspicion_score"), "checks": tamp_result.get("checks", [])},
                    "risk": {"score": risk_result.get("score"), "level": level, "factors": risk_result.get("factors", [])},
                    "consistency": {"status": consistency_result.get("status"), "consistent": consistency_result.get("consistent")},
                },
                "file_hash": doc_data["_fhash"],
            }
            sid = db.save_screening(screening_record)
            if sid and sid > 0:
                st.caption(f"💾 Screening saved (ID: {sid})")

            # ── Report download ──────────────────────────────────────────
            report = {
                "report_type": "SIH26188 Document Screening Report",
                "generated_at": format_timestamp(),
                "document_type": doc_data["_doc_type"],
                "document_name": doc_data["_detect"].get("document_name", "Unknown"),
                "screening": {
                    "heuristic_score": risk_result.get("score_pct", 0),
                    "heuristic_score_raw": risk_result.get("score", 0.0),
                    "risk_level": level,
                    "recommendation": risk_result.get("recommendation", ""),
                    "indicators": risk_result.get("indicators", []),
                    "factors": risk_result.get("factors", []),
                    "summary": risk_result.get("summary", ""),
                },
                "extracted_fields": {
                    fname: (fval.get("value", str(fval)) if isinstance(fval, dict) else str(fval))
                    for fname, fval in doc_data["_extract"].get("fields", {}).items()
                },
                "validation": {
                    "status": valid_result.get("status"),
                    "passed": valid_result.get("valid_count", 0),
                    "total": valid_result.get("total_count", 0),
                    "checks": valid_result.get("checks", []),
                },
                "tampering_analysis": {
                    "status": tamp_result.get("status"),
                    "overall_suspicious": tamp_result.get("overall_suspicious"),
                    "suspicion_score": tamp_result.get("suspicion_score"),
                    "checks": [
                        {k: v for k, v in tc.items() if k != "image"}
                        for tc in tamp_result.get("checks", [])
                    ],
                    "message": tamp_result.get("message", ""),
                },
                "consistency": {
                    "status": consistency_result.get("status"),
                    "consistent": consistency_result.get("consistent"),
                    "score": consistency_result.get("consistency_score"),
                    "checks": consistency_result.get("checks", []),
                },
                "ocr": {
                    "status": doc_data["_ocr"].get("status"),
                    "confidence": doc_data["_ocr"].get("confidence"),
                    "engine": doc_data["_ocr"].get("engine", "EasyOCR"),
                },
                "disclaimer": (
                    "This is a heuristic screening report generated by the "
                    "SIH26188 AI Document Screening System. Scores are "
                    "deterministic heuristics, not probabilities of fraud. "
                    "All findings require human review and verification "
                    "through authorized channels."
                ),
            }
            report_json = json.dumps(report, indent=2, default=str)
            doc_slug = (doc_data["_doc_type"] or "document").replace(" ", "_")
            st.download_button(
                label="📥 Download Screening Report (JSON)",
                data=report_json,
                file_name=f"screening_report_{doc_slug}_{doc_data['_fhash'][:8]}.json",
                mime="application/json",
                key=f"dl_{doc_data['_fhash']}",
            )

        # ── Cross-document consistency display ──────────────────────────
        if consistency_result.get("status") == "success":
            st.markdown("---")
            st.markdown("### 🔗 Cross-Document Consistency")
            checks = consistency_result.get("checks", [])
            if checks:
                check_data = []
                for c in checks:
                    icon = "✅" if c.get("consistent") else "⚠️"
                    check_data.append({
                        "Field": c.get("field_label", c.get("field", "")),
                        "Status": f"{icon} {'Consistent' if c.get('consistent') else 'Mismatch'}",
                        "Details": c.get("message", ""),
                    })
                st.table(check_data)
            else:
                st.info("No comparable fields found across documents.")
            st.caption(
                f"Consistency score: {consistency_result.get('consistency_score', 0):.2f} · "
                f"{consistency_result.get('message', '')}"
            )


def _render_supported_docs_summary() -> None:
    """Show a compact card of supported document types."""
    doc_icons = {"aadhaar": "🪪", "pan": "💳", "voter_id": "🗳️"}
    cols = st.columns(len(DOCUMENT_TYPES))
    for col, (key, doc) in zip(cols, DOCUMENT_TYPES.items()):
        with col:
            icon = doc_icons.get(key, "📄")
            n_fields = len(doc["fields"])
            checksum = f"✅ {doc['checksum_algorithm'].title()} checksum" if doc.get("checksum_algorithm") else ""
            st.markdown(
                f"**{icon} {doc['name']}**\n\n"
                f"_{doc['description']}_\n\n"
                f"**{n_fields}** extractable fields"
                + (f"  \n{checksum}" if checksum else "")
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
    """Render the full analysis results panel with tabbed layout."""

    st.divider()
    doc_label = doc_type.upper() if doc_type else "UNKNOWN"
    st.markdown(f"## 📊 Screening Report — {doc_label}")

    # ── Headline: Risk score hero + Document info (always visible) ─────────
    score = risk_result.get("score", 0.0)
    score_pct = risk_result.get("score_pct", round(score * 100))
    level = risk_result.get("level", "LOW")
    score_css = f"score-{level.lower()}"

    col_score, col_badge, col_doc = st.columns([1, 1, 2])

    with col_score:
        st.markdown(
            f'<div class="risk-hero">'
            f'<div class="score-value {score_css}">{score_pct}</div>'
            f'<div class="score-label">Heuristic Score / 100</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with col_badge:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(render_risk_badge(level), unsafe_allow_html=True)
        st.caption("Heuristic screening score — not a probability of fraud")

    with col_doc:
        doc_name = detect_result.get("document_name", "Unknown")
        doc_conf = detect_result.get("confidence", 0.0)
        c1, c2 = st.columns(2)
        c1.metric("Document Type", doc_name)
        c2.metric("Detection Confidence", f"{doc_conf:.0%}")
        if detect_result.get("matched_keywords"):
            st.caption(f"Matched keywords: {', '.join(detect_result['matched_keywords'])}")

    # ── Tabs ───────────────────────────────────────────────────────────────
    tab_assessment, tab_fields, tab_image, tab_details = st.tabs([
        "⚖️ Screening Assessment",
        "📋 Fields & Validation",
        "🔬 Image Analysis",
        "📝 Details",
    ])

    # ── Tab 1: Screening Assessment ────────────────────────────────────────
    with tab_assessment:
        col_ind, col_rec = st.columns([3, 2])

        with col_ind:
            st.markdown("#### Risk Indicators")
            indicators = risk_result.get("indicators", [])
            if indicators:
                for ind in indicators:
                    st.markdown(
                        f'<div class="indicator-suspicious">🚨 {ind}</div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    '<div class="indicator-normal">✅ No suspicious indicators identified.</div>',
                    unsafe_allow_html=True,
                )

            # Show contributing factors
            factors = risk_result.get("factors", [])
            if factors:
                st.markdown("##### Contributing Factors")
                factor_data = []
                for f in factors:
                    factor_data.append({
                        "Category": f.get("category", "").title(),
                        "Factor": f.get("name", ""),
                        "Weight": f"{f.get('contribution', 0)}%",
                        "Description": f.get("description", ""),
                    })
                st.table(factor_data)

        with col_rec:
            st.markdown("#### Recommendation")
            recommendation = risk_result.get("recommendation", "N/A")
            st.info(f"📋 {recommendation}")

            st.markdown("#### Score Breakdown")
            st.markdown(f"**Heuristic Score:** {score_pct} / 100")
            st.markdown(f"**Risk Level:** {render_risk_badge(level)}", unsafe_allow_html=True)
            st.markdown(f"**Summary:** {risk_result.get('summary', 'N/A')}")

    # ── Tab 2: Fields & Validation ─────────────────────────────────────────
    with tab_fields:
        # Extracted fields
        st.markdown("#### 📋 Extracted Fields")
        fields = extract_result.get("fields", {})
        if fields:
            field_data = []
            for fname, fval in fields.items():
                display_val = fval
                if isinstance(fval, dict):
                    display_val = fval.get("value", str(fval))
                masked = mask_sensitive_field(str(display_val), fname, doc_type or "")
                label = fname
                if doc_type and doc_type in DOCUMENT_TYPES:
                    fconf = DOCUMENT_TYPES[doc_type]["fields"].get(fname, {})
                    label = fconf.get("label", fname)
                field_data.append({"Field": label, "Value": masked})
            st.table(field_data)
        else:
            st.info(
                "No identity fields were extracted. "
                "The document may be unrecognised or OCR text was insufficient."
            )
        st.caption(
            f"Extracted **{extract_result.get('extraction_count', 0)}** / "
            f"**{extract_result.get('total_fields', 0)}** defined fields."
        )

        st.divider()

        # Validation checks
        st.markdown("#### ✅ Validation Checks")
        valid_status = valid_result.get("status", "")
        checks = valid_result.get("checks", [])

        if valid_status == "error" and not checks:
            findings = valid_result.get("findings", [])
            if findings:
                for f in findings:
                    st.warning(f)
            else:
                st.info("No validation checks could be performed for this document type.")
        elif checks:
            check_data = []
            for chk in checks:
                passed = chk.get("passed")
                icon = "✅" if passed else "❌"
                check_data.append({
                    "Check": chk.get("check_name", chk.get("field", "")),
                    "Result": f"{icon} {'Passed' if passed else 'Failed'}",
                    "Details": chk.get("message", ""),
                })
            st.table(check_data)

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

    # ── Tab 3: Image Analysis ──────────────────────────────────────────────
    with tab_image:
        st.markdown("#### 🔬 Image Anomaly Analysis")
        tamp_status = tamp_result.get("status", "")
        tamp_checks = tamp_result.get("checks", [])

        if tamp_status == "error" and not tamp_checks:
            st.warning(f"⚠️ {tamp_result.get('message', 'Analysis could not be performed.')}")
        elif tamp_checks:
            check_data = []
            for tc_item in tamp_checks:
                suspicious = tc_item.get("suspicious")
                icon = "🚨" if suspicious else "✅"
                check_data.append({
                    "Indicator": tc_item.get("name", ""),
                    "Status": f"{icon} {'Suspicious' if suspicious else 'Normal'}",
                    "Details": tc_item.get("result", tc_item.get("description", "")),
                })
            st.table(check_data)

            if tamp_result.get("ela_image") is not None:
                st.image(
                    np_image_to_pil(tamp_result["ela_image"]),
                    caption="Error Level Analysis (ELA) — brighter regions indicate higher compression difference",
                    use_container_width=True,
                )

            if tamp_result.get("overall_suspicious"):
                st.warning(f"⚠️ {tamp_result.get('message', '')}")
            else:
                st.success(f"✅ {tamp_result.get('message', '')}")
        else:
            st.info("No image anomaly checks were performed.")

        t_score = tamp_result.get("suspicion_score", 0.0)
        method = tamp_result.get("method", "N/A")
        st.caption(
            f"Heuristic anomaly score: {t_score:.2f} · "
            f"Method: {method} · "
            f"Overall suspicious: {'Yes' if tamp_result.get('overall_suspicious') else 'No'}"
        )

    # ── Tab 4: Details ─────────────────────────────────────────────────────
    with tab_details:
        # OCR results
        st.markdown("#### 📝 OCR Results")
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

        st.divider()

        # Preprocessing steps
        st.markdown("#### 🖼️ Preprocessing Steps")
        steps = prep.get("steps", [])
        if steps:
            step_cols = st.columns(min(len(steps), 4))
            for idx, step in enumerate(steps):
                with step_cols[idx % len(step_cols)]:
                    st.caption(f"**{step['name'].title()}**")
                    st.image(
                        np_image_to_pil(step.get("image")),
                        caption=step["description"],
                        use_container_width=True,
                    )
        else:
            st.info("No preprocessing steps recorded.")

        st.divider()

        # Module status
        st.markdown("#### 🔧 Module Status")
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
    screenings = db.get_all_screenings()
    count = len(screenings)

    # Count by risk level
    levels = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    for s in screenings:
        lv = (s.get("risk_level") or "LOW").upper()
        levels[lv] = levels.get(lv, 0) + 1

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Screenings", count)
    col2.metric("🟢 Low Risk", levels["LOW"])
    col3.metric("🟡 Medium Risk", levels["MEDIUM"])
    col4.metric("🔴 High Risk", levels["HIGH"])

    st.divider()

    if not screenings:
        st.info("No screenings recorded yet. Go to **Document Screening** to analyze documents.")
        return

    # Clear all button
    col_spacer, col_clear = st.columns([4, 1])
    with col_clear:
        if st.button("🗑️ Clear All", type="secondary"):
            st.session_state["confirm_clear_all"] = True
    if st.session_state.get("confirm_clear_all"):
        st.warning("⚠️ This will delete **all** screening records. This cannot be undone.")
        c1, c2, _ = st.columns([1, 1, 4])
        with c1:
            if st.button("✅ Confirm Delete All", type="primary"):
                for s in screenings:
                    db.delete_screening(s.get("id"))
                st.session_state["confirm_clear_all"] = False
                st.success("All screening records deleted.")
                st.rerun()
        with c2:
            if st.button("Cancel"):
                st.session_state["confirm_clear_all"] = False
                st.rerun()

    # Screening records
    for s in screenings:
        sid = s.get("id", "?")
        ts = s.get("timestamp", s.get("created_at", ""))
        doc_name = s.get("document_name", "Unknown")
        risk_lvl = (s.get("risk_level") or "LOW").upper()
        risk_score = s.get("risk_score", 0.0)
        risk_pct = round(risk_score * 100)

        badge = render_risk_badge(risk_lvl)
        header = f"**#{sid}** · {doc_name} · Score: {risk_pct}/100 · {ts}"

        with st.expander(header, expanded=False):
            # Summary row
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"**Risk Level:** {badge}", unsafe_allow_html=True)
            c2.metric("Heuristic Score", f"{risk_pct} / 100")
            c3.markdown(f"**Recommendation:** {s.get('recommendation', 'N/A')}")

            # Structured findings
            findings = s.get("findings")
            if findings and isinstance(findings, dict):
                with st.expander("📋 Detailed Findings", expanded=False):
                    # Validation
                    val = findings.get("validation", {})
                    if val:
                        st.markdown(f"**Validation:** {val.get('valid', 0)}/{val.get('total', 0)} checks passed")
                    # Tampering
                    tamp = findings.get("tampering", {})
                    if tamp:
                        susp = "⚠️ Yes" if tamp.get("suspicious") else "✅ No"
                        st.markdown(f"**Tampering suspicious:** {susp} (score: {tamp.get('score', 0):.2f})")
                    # Consistency
                    cons = findings.get("consistency", {})
                    if cons:
                        st.markdown(f"**Consistency:** {cons.get('status', 'N/A')}")
                    # Risk factors
                    risk = findings.get("risk", {})
                    if risk and risk.get("factors"):
                        st.markdown("**Risk Factors:**")
                        for f in risk["factors"]:
                            st.markdown(f"- [{f.get('category', '')}] {f.get('name', '')}: {f.get('description', '')}")

                    # Raw JSON fallback
                    with st.expander("🔍 Raw JSON", expanded=False):
                        st.json(findings)

            if st.button(f"🗑️ Delete #{sid}", key=f"del_{sid}"):
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

        # Quick stats with risk distribution
        db = get_database()
        screenings = db.get_all_screenings()
        total = len(screenings)
        st.metric("Total Screenings", total)

        if total > 0:
            levels = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
            for s in screenings:
                lv = (s.get("risk_level") or "LOW").upper()
                levels[lv] = levels.get(lv, 0) + 1
            st.caption(
                f"🟢 {levels['LOW']} Low  ·  "
                f"🟡 {levels['MEDIUM']} Medium  ·  "
                f"🔴 {levels['HIGH']} High"
            )

        st.divider()

        # Pipeline overview
        st.markdown("**Screening Pipeline**")
        st.caption(
            "1. 📝 OCR text extraction\n"
            "2. 🔍 Document type detection\n"
            "3. 📋 Field extraction & validation\n"
            "4. 🔬 Image anomaly analysis\n"
            "5. 🔗 Cross-document consistency\n"
            "6. ⚖️ Risk scoring"
        )

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
