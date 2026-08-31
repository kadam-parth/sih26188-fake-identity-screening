# TODO

## Current Phase

PHASE 3 COMPLETE — OCR, DETECTION, EXTRACTION, VALIDATION

## Completed

- [x] Initialize project structure
- [x] Create Streamlit application
- [x] Create SQLite persistence layer
- [x] Create image preprocessing module
- [x] Create initial module interfaces
- [x] Create initial tests
- [x] Verify Streamlit launches
- [x] Verify test suite passes
- [x] Initialize Git repository
- [x] Create AI continuity documentation
- [x] Integrate EasyOCR
- [x] Implement document type detection (keyword heuristic)
- [x] Implement field extraction (regex-based)
- [x] Add OCR tests (mocked — no model downloads in test suite)
- [x] Add document detection tests
- [x] Add field extraction tests
- [x] Update interface contract tests
- [x] Fix OCR image input (grayscale instead of threshold)
- [x] Fix OCR display in Streamlit (expanded, status handling)
- [x] Update stale "pending implementation" messages
- [x] Add integration tests (mocked full pipeline)
- [x] Create manual real-EasyOCR test script
- [x] Test real OCR on synthetic document image
- [x] Implement Aadhaar field validation (Verhoeff checksum)
- [x] Implement PAN field validation (format checks)
- [x] Implement Voter ID field validation (format checks)
- [x] Implement required-field presence checks
- [x] Implement date validation (format + plausibility)
- [x] Implement field normalization before validation
- [x] Add comprehensive validator tests (48 tests, all synthetic data)
- [x] Add validation step to integration test
- [x] Add validation display to Streamlit UI (table + findings)
- [x] Update manual OCR test with validation step

## Day 2 (remaining)

- [ ] Review and polish preprocessing
- [x] Review Streamlit UI
- [ ] Improve error handling
- [ ] Verify configuration management
- [ ] Prepare safe synthetic/test document data

## Day 3 (remaining)

- [x] Test OCR on representative sample images (manual integration test)
- [ ] Tune OCR confidence threshold if needed
- [ ] Improve document type detection accuracy if needed

## Day 4 (complete)

- [x] Implement Aadhaar field validation (Verhoeff checksum)
- [x] Implement PAN field validation (format checks)
- [x] Implement Voter ID field validation (format checks)
- [x] Add relevant tests

## Day 5 (partial)

- [x] Implement document validation pipeline
- [ ] Improve preprocessing for OCR
- [ ] Improve document type detection
- [x] Add validation findings to screening result

## Day 6

- [ ] Implement image anomaly/tampering analysis
- [ ] Start with explainable OpenCV-based techniques
- [ ] Avoid claiming tampering detection is definitive
- [ ] Add tests

## Day 7

- [ ] Implement cross-document consistency
- [ ] Compare extracted identity fields
- [ ] Add explainable consistency findings
- [ ] Add tests

## Day 8

- [ ] Implement rule-based risk scoring
- [ ] Configure scoring weights centrally
- [ ] Implement LOW/MEDIUM/HIGH levels
- [ ] Generate explainable findings
- [ ] Add human review recommendation
- [ ] Add tests

## Day 9

- [ ] Integrate complete end-to-end screening workflow
- [ ] Improve screening history
- [ ] Improve privacy masking
- [ ] Add final error handling
- [ ] Run full test suite

## Day 10

- [ ] End-to-end testing
- [ ] Prepare safe demo/test cases
- [ ] Verify installation instructions
- [ ] Verify clean startup
- [ ] Verify GitHub repository
- [ ] Prepare hackathon demonstration
- [ ] Document limitations
- [ ] Final cleanup

## Optional / If Time Allows

- [ ] Face verification
- [ ] Additional document types
- [ ] More advanced computer-vision models
- [ ] Additional anomaly indicators

## Explicitly Avoid Unless Justified

- [ ] Training large models from scratch
- [ ] Complex distributed architecture
- [ ] Cloud infrastructure that is unnecessary for MVP
- [ ] Third-party document processing APIs
- [ ] Features that cannot be demonstrated locally
