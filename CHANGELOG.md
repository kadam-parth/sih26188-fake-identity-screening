# CHANGELOG

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

