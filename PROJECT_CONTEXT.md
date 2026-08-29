# PROJECT CONTEXT

## Project

SIH26188 - AI-Based Fake Identity & Document Screening System

## Current Goal

Build a hackathon MVP that screens identity documents for suspicious
indicators and provides an explainable risk assessment for human review.

The system must NOT claim to legally determine whether a person is fraudulent
or whether a document is definitively fake.

## Current Development Stage

PHASE 2 COMPLETE — OCR, DOCUMENT DETECTION, FIELD EXTRACTION

The initial skeleton has been extended with three real implementations:
OCR (EasyOCR wrapper), document type detection (keyword heuristic),
and field extraction (regex-based).

Current test result:

89 tests passed (37 original + 52 new).

## What Currently Exists

### Fully implemented components:

- Streamlit application (dashboard, screening, history, about pages)
- Image preprocessing module (OpenCV pipeline)
- SQLite database module (full CRUD)
- Utility/configuration modules (masking, formatting, risk levels)
- **OCR engine** (EasyOCR wrapper with lazy initialization)
- **Document type detector** (keyword-frequency heuristic for Aadhaar,
  PAN, Voter ID)
- **Field extractor** (regex-based extraction using patterns from config)

### Modules still in stub form:

- Document validation (validators.py)
- Tampering analysis (tampering.py)
- Cross-document consistency (consistency.py)
- Risk scoring (scoring.py)

Future AI agents must inspect the actual source code before claiming any
stub feature is implemented.

## Implementation Details — Phase 2

### OCR Engine (src/ocr/engine.py)

- Wraps EasyOCR with lazy initialization (no model download at import).
- Returns structured results: text, confidence, per-region details, bbox.
- Filters regions below OCR_CONFIDENCE_THRESHOLD (0.3).
- Confidence is character-weighted average across accepted regions.
- Handles None images, empty results, and EasyOCR exceptions.
- All unit tests mock easyocr.Reader — no model downloads in test suite.

### Document Detector (src/documents/detector.py)

- Rule-based keyword-frequency heuristic — NOT a trained ML classifier.
- Uses word-boundary matching for single-word keywords to avoid false
  substring positives (e.g., "pan" does not match "company").
- Uses phrase matching for multi-word keywords.
- Requires >= 2 keyword hits to report a match.
- Returns confidence as matched_count / total_keywords.

### Field Extractor (src/documents/extractor.py)

- Applies regex patterns defined in config.py for each document type.
- Extraction confidence is set to 0.7 (EXTRACTION_CONFIDENCE), NOT 1.0.
- A regex match does not prove the extracted value is correct — OCR text
  may contain errors and patterns may capture false positives.
- Confidence is a documented heuristic, NOT a calibrated probability.
- Handles unknown document types, empty text, and partial extraction.

## Initial Document Types

1. Aadhaar
2. PAN Card
3. Voter ID

The architecture allows additional document types by editing config.py.

## Planned Workflow

User → Upload document(s) → Image preprocessing → Document type detection
→ OCR → Field extraction → Document validation → Tampering/anomaly analysis
→ Cross-document consistency → Risk engine → Explainable result → Human
review recommendation

## Current Technology Direction

- Python
- Streamlit
- OpenCV
- EasyOCR
- NumPy
- Pandas
- Pillow
- scikit-learn where useful
- SQLite

EasyOCR was selected during initial planning because installation simplicity
was prioritized for the Windows development environment.

## Deferred Feature

Face verification should remain optional/deferred unless it can be implemented
reliably within the 10-day hackathon.

## Risk Model

Risk levels: LOW, MEDIUM, HIGH

The risk engine should initially be explainable and rule-based.

Risk scores are indicators, not proof of fraud and not calibrated
probabilities.

## Privacy

Documents may contain highly sensitive identity information.

The MVP should:

- process documents locally where possible
- avoid third-party document uploads
- avoid logging complete identity numbers
- avoid permanently storing raw documents unless necessary
- mask sensitive fields in the UI
- clearly label synthetic test data

## Current Environment

Development environment is Windows.
Python 3.13.2
Virtual environment in venv/

## Current Project Location

C:\Users\kadam\Documents\SIH26188\sih26188-fake-identity-screening

## Git Status

GitHub remote configured (origin/main).
Project has commits and is synced.

## Current Test Status

89/89 tests passed.

- tests/test_db.py — 10 tests (database)
- tests/test_preprocessing.py — 11 tests (image preprocessing)
- tests/test_validators.py — 16 tests (interface contracts, 3 updated + 4 stub)
- tests/test_ocr.py — 14 tests (OCR wrapper, mocked)
- tests/test_detector.py — 17 tests (document detection)
- tests/test_extractor.py — 21 tests (field extraction)

All OCR tests use mocked easyocr.Reader. No model downloads required
to run the test suite. No internet access required.

## Next Major Development Task

Implement document validation (Verhoeff checksum for Aadhaar, format
checks for PAN and Voter ID) — TODO Day 4.
