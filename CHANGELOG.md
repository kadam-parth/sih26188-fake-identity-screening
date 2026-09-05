# CHANGELOG

## 2026-09-01

### Phase 5 — Cross-Document Consistency + Risk Scoring

Replaced the last two stubs with full implementations. All core modules
are now implemented.

Completed:

- Cross-document consistency (src/verification/consistency.py)
  - Replaced 55-line stub with ~225-line implementation
  - Normalized name comparison (case, whitespace, punctuation)
  - Date comparison with multi-format support (DD/MM/YYYY, DD-MM-YYYY,
    YYYY-MM-DD)
  - Handles dict-style and string field values
  - Single-document → "insufficient_documents" (not inconsistent)
  - Backward-compatible return schema with new fields: compared_count,
    mismatch_count
- Rule-based risk scoring (src/risk/scoring.py)
  - Replaced 59-line stub with ~280-line implementation
  - Weighted aggregation: validation + tampering + consistency
  - Uses existing config: RISK_WEIGHTS, RISK_THRESHOLDS, RISK_LEVELS
  - Redistributes consistency weight when unavailable (single doc)
  - Explainable: every contribution has category, name, description
  - Human-readable indicators list
  - Risk levels: LOW (<=0.3), MEDIUM (0.3-0.6), HIGH (>0.6)
  - Language: "suspicious indicators", "human review" — never "fraud"
- Pipeline restructure (app.py)
  - Risk scoring deferred until after consistency check
  - Consistency runs on all documents after per-document analysis
  - Risk scorer receives consistency results
  - Enhanced "Screening Assessment" display with score/100, indicators,
    disclaimer
  - Cross-document consistency table display
  - DB record includes consistency status

Test suite:

- 22 new consistency tests (tests/test_consistency.py)
- 21 new risk scoring tests (tests/test_risk_scoring.py)
- 3 new Phase 5 integration tests (tests/test_integration.py)
- Updated interface contract tests (all stubs → real)
- Total: 219/219 passed (173 preserved + 46 new)

All test data is synthetic. No real identity documents used.

Technical decisions:

- Cross-document consistency uses deterministic normalized string comparison,
  not fuzzy matching or ML.
- Risk score is a deterministic weighted heuristic, not a trained model or
  calibrated probability.
- Missing data (single document, no consistency) does NOT incur penalty.
  Weight is redistributed to available components.
- Human review is the final decision point for all risk levels.

---

### Phase 4 — Image Tampering / Anomaly Analysis

Replaced the TamperingAnalyzer stub with a full OpenCV-based implementation.

Completed:

- Image anomaly analyzer (src/vision/tampering.py)
  - Error Level Analysis (ELA): JPEG recompression comparison in memory
  - Edge density analysis: Canny-based edge ratio measurement
  - High-frequency noise analysis: Gaussian blur subtraction
  - All techniques are heuristic — NOT trained ML models
  - Handles None, empty, too-small, grayscale, BGRA images
  - Returns backward-compatible schema: checks, ela_image,
    overall_suspicious, suspicion_score, status
  - New fields: method ("heuristic_cv"), message
  - Each check includes metrics dict for transparency
- Tampering configuration (src/config.py TAMPERING dict)
  - Centralized thresholds: ELA quality/scale/threshold,
    edge density range, noise threshold, min dimension, overall threshold
- Streamlit anomaly display (app.py)
  - Indicator table with Status/Details columns
  - ELA visualization with descriptive caption
  - Overall suspicious status as success/warning message
  - Heuristic anomaly score and method display

Test suite:

- 33 new tampering tests (tests/test_tampering.py)
  - Init, config
  - Input handling: None, empty, too small, invalid type
  - Valid images: color, grayscale, large, BGRA
  - Return schema validation
  - ELA: shape, dtype, determinism, metrics
  - Edge density: presence, blank image detection, metrics
  - Noise: presence, clean image, noisy image detection
  - Synthetic modification comparison
  - Score calculation: range, edge cases, partial
  - Honesty language: no definitive fraud claims, guarantee disclaimer
- Updated interface contract test (TestTamperingAnalyzer)
- Total: 173/173 passed (140 preserved + 33 new)

All test data is synthetic. No real identity documents used.

Technical decisions:

- ELA, edge density, and noise analysis are heuristic CV techniques,
  NOT trained ML models.
- Anomaly score = suspicious_count / total_checks — deterministic,
  not a fraud probability.
- Results are screening indicators, not proof of tampering.
- "Does not guarantee document authenticity" disclaimer on clean results.

### Remaining stubs:

- cross-document consistency (consistency.py)
- risk scoring (scoring.py)

### Next task:

Implement cross-document consistency and/or risk scoring.

---

## 2026-08-31

### Phase 3 — Document & Field Validation

Replaced the DocumentValidator stub with a full implementation.

Completed:

- Document validator (src/documents/validators.py)
  - Required-field presence checks driven by config.py
  - Format validation using config.py regex patterns
  - Aadhaar Verhoeff checksum validation (structural only)
  - Date validation: DD/MM/YYYY and DD-MM-YYYY, plausibility checks
  - Input normalization: space-stripping for Aadhaar, uppercasing for PAN/EPIC
  - Edge-case handling: None, empty, unknown type, raw string values
  - Backward-compatible return schema: checks, valid_count, total_count,
    all_passed, status; new fields: findings, document_type
  - Status values: success, partial, failed, error
- Verhoeff algorithm (verhoeff_validate, verhoeff_generate)
  - Standard lookup-table implementation
  - Detects single-digit substitution and transposition errors
- Streamlit validation display (app.py)
  - Validation results shown in a table (Check/Result/Details)
  - Findings displayed as a bullet list
  - Handles error/empty/no-check states

Test suite:

- 48 new document validator tests (tests/test_document_validator.py)
  - Verhoeff algorithm: generate, validate, invalid, spaces, non-digit, empty
  - General: init, unknown type, empty fields, None, return schema, backward compat
  - Aadhaar: required fields, format (valid/invalid/spaces/letters), checksum
    (valid/invalid), no authenticity claim in messages
  - PAN: valid, invalid (all digits, too short), lowercase normalization, no checksum
  - Voter ID: valid, invalid format, too short, no checksum
  - Dates: valid, dash format, impossible month/day, malformed, implausible year
  - Edge cases: empty value, raw string, findings type, status values
- Integration test updated with validation step
- Manual OCR test updated with validation step
- Total: 140/140 passed (92 original preserved + 48 new)

All test data is synthetic. No real identity numbers used.

Technical decisions:

- Validation results are deterministic structural indicators, NOT probabilities.
- The validator never claims fraud, legal determination, or document authenticity.
- Verhoeff checksum validity only proves structural consistency — it does NOT
  prove the Aadhaar number exists or belongs to any person.
- Return schema preserves backward compatibility with Phase 1 stub contract.

### Remaining stubs:

- tampering analysis (tampering.py)
- cross-document consistency (consistency.py)
- risk scoring (scoring.py)

### Next task:

Implement tampering/anomaly analysis using explainable OpenCV techniques.

---

## 2026-08-30

### Phase 2.5 — Streamlit OCR UI Integration Fix

Fixed OCR pipeline integration in Streamlit and improved result display.

Completed:

- Changed OCR input from threshold image to grayscale (EasyOCR needs gradients)
- Expanded OCR results section by default
- Added status handling (success, no_text, error) in OCR display
- Added region count and engine info to OCR caption
- Updated stale "pending implementation" messages
- Added integration tests (3 tests with mocked EasyOCR)
- Created manual real-EasyOCR test script (tests/manual_ocr_test.py)
- Real EasyOCR tested successfully on synthetic Aadhaar image

---

## 2026-08-29

### Phase 2 — OCR, Document Detection, Field Extraction

Implemented three core analysis modules, replacing stubs with real logic.

Completed:

- EasyOCR integration (src/ocr/engine.py)
  - Lazy initialization — no model download at import time
  - Structured result with text, confidence, per-region details, bboxes
  - Confidence threshold filtering (OCR_CONFIDENCE_THRESHOLD = 0.3)
  - Character-weighted average confidence
  - Graceful error handling for None images and EasyOCR failures
- Document type detection (src/documents/detector.py)
  - Keyword-frequency heuristic — NOT a trained ML classifier
  - Word-boundary matching for single keywords (avoids substring false positives)
  - Phrase matching for multi-word keywords
  - Minimum 2 keyword hits required to report a match
  - Confidence = matched_count / total_keywords
- Field extraction (src/documents/extractor.py)
  - Regex-based extraction using patterns from config.py
  - Extraction confidence = 0.7 (documented heuristic, not 1.0)
  - Handles unknown document types, empty text, partial extraction
  - Status codes: success, partial, no_fields, unknown_document_type

Test suite:

- 14 new OCR tests (all mocked — no model downloads required)
- 17 new document detection tests
- 21 new field extraction tests
- 7 updated interface contract tests (3 implemented, 4 stubs unchanged)
- Total: 89/89 passed (37 original preserved + 52 new)

### Technical decisions:

- All OCR tests mock easyocr.Reader so pytest runs without internet
- Extraction confidence is 0.7, not 1.0 — regex match ≠ certainty
- Document detection uses word boundaries to prevent naive substring matching
- These are documented as heuristics, not ML models

### Remaining stubs:

- document validation (validators.py)
- tampering analysis (tampering.py)
- cross-document consistency (consistency.py)
- risk scoring (scoring.py)

### Next task:

Implement document validation (Verhoeff checksum for Aadhaar, format
checks for PAN and Voter ID).

---

### Initial Project Skeleton

Created the initial SIH26188 Streamlit MVP skeleton.

Completed:

- Streamlit application
- Initial dashboard UI
- Screening page
- History page
- About/privacy section
- SQLite database module
- Image preprocessing module
- Utility/configuration modules
- Initial module interfaces/stubs
- Initial test suite
- Git repository initialization
- AI continuity documentation

### Verification

Initial test suite:

37 tests passed.

### Important Status

The project is still in the skeleton stage.

The following major capabilities are not yet considered fully implemented:

- OCR
- document type detection
- field extraction
- document validation
- tampering analysis
- cross-document consistency
- risk scoring

Do not interpret the presence of module stubs as completed functionality.

### Development Direction

Next major task:

Integrate reliable OCR and document-type detection while preserving the
working skeleton.

