# PROJECT CONTEXT

## Project

SIH26188 — AI-Based Fake Identity & Document Screening System

## Current Goal

Build a hackathon MVP that screens identity documents for suspicious
indicators and provides an explainable risk assessment for human review.

The system must NOT claim to legally determine whether a person is fraudulent
or whether a document is definitively fake.

## Current Development Stage

DAY 1 — PROJECT SKELETON

The initial Streamlit skeleton has been created and tested.

Current test result:

37 tests passed.

## What Currently Exists

Working components include:

- Streamlit application
- Basic dashboard UI
- Screening page
- History page
- About/privacy section
- SQLite database module
- Image preprocessing module
- Utility/configuration modules
- Initial test suite
- Module interfaces/stubs for future functionality

## IMPORTANT CURRENT LIMITATION

The major fraud-screening pipeline is NOT fully implemented yet.

The following areas currently contain initial interfaces/stubs and must not
be described as fully implemented:

- OCR
- Document type detection
- Field extraction
- Document validation
- Tampering analysis
- Cross-document consistency
- Risk scoring

Future AI agents must inspect the actual source code before claiming any
feature is implemented.

## Initial Document Types

Planned initial document types:

1. Aadhaar
2. PAN Card
3. Voter ID

The architecture should allow additional document types later.

## Planned Workflow

User
?
Upload document(s)
?
Image preprocessing
?
Document type detection
?
OCR
?
Field extraction
?
Document validation
?
Tampering/anomaly analysis
?
Cross-document consistency
?
Risk engine
?
Explainable result
?
Human review recommendation

## Planned Core Features

1. Document upload
2. Image preprocessing
3. Document type identification
4. OCR
5. Identity field extraction
6. Document format/field validation
7. Image anomaly/tampering analysis
8. Cross-document consistency checking
9. Optional face verification
10. Risk scoring
11. Explainable screening report
12. Screening history
13. Privacy-conscious document handling

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

Risk levels:

- LOW
- MEDIUM
- HIGH

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

Current Python environment observed during Day 1:

Python 3.13.2

The original target was Python 3.11 or compatible Python.

Do not change Python versions unnecessarily while the current environment is
working.

## Current Project Location

Current local development workspace:

C:\Users\kadam\.gemini\antigravity\scratch\sih26188-fake-identity-screening

This should eventually be moved or copied to a permanent project location
outside the Antigravity scratch directory after the working version has been
safely committed to Git.

## Git Status

Git repository has been initialized locally.

The project currently has no commits at the time this document was created.

GitHub remote has not yet been configured.

## Current Priority

1. Preserve the working Day 1 skeleton.
2. Create the first clean Git commit.
3. Push the project to GitHub.
4. Establish AI-continuity documentation.
5. Begin OCR integration only after the repository is safely backed up.

## Current Test Status

37/37 tests passed during initial skeleton verification.

## Next Major Development Task

Integrate reliable OCR and document-type detection while preserving the
existing working skeleton.
