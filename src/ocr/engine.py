from __future__ import annotations
import logging
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)


class OCREngine:
    """Abstraction layer for OCR processing.
    
    Currently a stub. Will be implemented with EasyOCR on Day 3.
    The interface is designed to be engine-agnostic so EasyOCR can be
    swapped for PaddleOCR or Tesseract without changing calling code.
    """
    
    def __init__(self, languages: Optional[list[str]] = None):
        """Initialize OCR engine.
        
        Args:
            languages: List of language codes (e.g., ['en', 'hi']).
                      Defaults to config.OCR_LANGUAGES.
        """
        from src.config import OCR_LANGUAGES
        self.languages = languages or OCR_LANGUAGES
        self._reader = None
        self._initialized = False
        logger.info("OCREngine initialized (stub) — languages: %s", self.languages)
    
    def _ensure_initialized(self) -> None:
        """Lazy-initialize the OCR reader."""
        if not self._initialized:
            # TODO (Day 3): Initialize EasyOCR reader here
            # import easyocr
            # self._reader = easyocr.Reader(self.languages, gpu=False)
            self._initialized = True
            logger.info("OCR reader initialized (stub)")
    
    def extract_text(self, image: np.ndarray) -> dict:
        """Extract text from a preprocessed image.
        
        Args:
            image: Preprocessed image as numpy array (BGR or grayscale).
            
        Returns:
            dict with keys:
                - text (str): Full extracted text, concatenated from all regions
                - confidence (float): Average confidence score (0.0–1.0)
                - details (list[dict]): Per-region results, each with
                    'text', 'confidence', 'bbox'
                - engine (str): Name of the OCR engine used
                - status (str): 'success', 'error', or 'not_implemented'
        """
        self._ensure_initialized()
        
        # TODO (Day 3): Replace with real EasyOCR implementation
        # results = self._reader.readtext(image)
        # ...
        
        logger.warning("OCR stub active — returning empty text")
        return {
            "text": "",
            "confidence": 0.0,
            "details": [],
            "engine": "stub",
            "status": "not_implemented",
            "message": "OCR engine not yet implemented. Will use EasyOCR.",
        }
