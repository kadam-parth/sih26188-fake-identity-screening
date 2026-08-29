# ARCHITECTURAL DECISIONS

## Decision 001 — MVP First

### Decision

Prioritize a reliable end-to-end demonstration over theoretical sophistication.

### Reason

The project has approximately 10 days and is being developed by
beginner/intermediate developers.

Complex infrastructure and large model training are out of scope.

---

## Decision 002 — Local-First Processing

### Decision

Process identity documents locally whenever practical.

### Reason

Identity documents contain sensitive personal information.

The MVP should avoid unnecessary external document-processing services.

---

## Decision 003 — Streamlit

### Decision

Use Streamlit for the MVP interface.

### Reason

It allows rapid development of a professional demonstration UI without
requiring a separate frontend/backend stack.

---

## Decision 004 — OpenCV

### Decision

Use OpenCV for image preprocessing and visual analysis.

### Reason

It is mature, widely used, and suitable for the required MVP image-processing
tasks.

---

## Decision 005 — EasyOCR

### Decision

Initial OCR direction is EasyOCR.

### Reason

The original development session prioritized installation reliability and
simplicity on Windows.

The OCR implementation should remain replaceable.

If EasyOCR becomes technically unsuitable, evaluate the simplest compatible
alternative rather than forcing it.

---

## Decision 006 — Initial Document Types

### Decision

Start with:

- Aadhaar
- PAN Card
- Voter ID

### Reason

The hackathon requires a small demonstrable scope.

The architecture should allow additional document types later.

---

## Decision 007 — Rule-Based Risk Engine

### Decision

Use an explainable rule-based risk engine for the initial MVP.

### Reason

A rule-based system is transparent, testable, and achievable within the
10-day timeline.

The score represents screening indicators, not a calibrated probability.

---

## Decision 008 — Face Verification Deferred

### Decision

Face verification is optional and should be deferred unless it can be
implemented reliably within the remaining time.

### Reason

It can introduce substantial model, dependency, and image-quality complexity.

Core document screening has higher MVP priority.

---

## Decision 009 — Git as Project Memory

### Decision

Git and GitHub should be treated as the source of truth for project code and
development history.

### Reason

The project must remain usable if:

- Antigravity quota is exhausted
- the AI account changes
- another AI coding tool is used
- another developer takes over
- development moves to another computer

AI conversation history must not be the only source of project context.

---

## Decision 010 — AI Continuity Documentation

### Decision

Maintain:

- AGENTS.md
- PROJECT_CONTEXT.md
- ARCHITECTURE.md
- TODO.md
- DECISIONS.md
- CHANGELOG.md

### Reason

These files provide persistent context that any compatible AI agent can read
from the repository.

---

## Decision 011 — No Fake AI Results

### Decision

The application must never generate random, fabricated, or hardcoded fraud
results as if they came from real analysis.

### Reason

The project must remain technically honest and demonstrable.

Synthetic data may be used for testing, but must be clearly identified.

---

## Decision 012 — Human Review

### Decision

High-risk screening results must recommend human review.

### Reason

The system is a screening aid and must not claim definitive legal or
fraudulent-person determinations.

---

## Decision 013 — No Real Identity Documents in Git

### Decision

Real Aadhaar, PAN, Voter ID, or other sensitive identity documents must never
be committed to GitHub.

### Reason

The repository may be shared with judges, teammates, or external developers.

Synthetic or explicitly safe test data should be used instead.

---

## Decision 014 - Mocked OCR Tests

### Decision

All OCR unit tests mock easyocr.Reader. The normal test suite (pytest tests/ -v)
must work without internet access and without downloading OCR model weights.

### Reason

The baseline test suite must remain fast and reliable. Model downloads add
~100 MB of network traffic and significant latency. Tests should validate
the wrapper logic, not the underlying OCR library.

Real EasyOCR integration testing is done manually or via clearly separated
optional tests.

---

## Decision 015 - Extraction Confidence is Not 1.0

### Decision

Regex-based field extraction assigns a heuristic confidence of 0.7
(EXTRACTION_CONFIDENCE), not 1.0, to every extracted field.

### Reason

A regex match confirms a pattern was found in OCR text, but it does not
prove the extracted value is correct. OCR noise, misreads, and regex
over-matching mean extracted values may be wrong. 1.0 would falsely
imply certainty. The 0.7 value is a documented heuristic, not a
calibrated probability.

---

## Decision 016 - Word-Boundary Document Detection

### Decision

The document type detector uses word-boundary regex matching for single
keywords (e.g., \bpan\b) to prevent false substring matches. Multi-word
phrases use plain substring matching after normalization.

### Reason

Naive substring matching causes false positives. For example, the keyword
"pan" would incorrectly match "company" or "pandemic". Word-boundary
matching prevents this while still being simple and fast. This is a
rule-based heuristic, not a trained ML classifier.
