from __future__ import annotations
import logging

logger = logging.getLogger(__name__)


class ConsistencyChecker:
    """Checks consistency across multiple identity documents.
    
    Currently a stub. Will be implemented on Day 9 to compare:
    - Name matching across documents
    - Date of birth consistency
    - Address consistency (if available)
    """
    
    def __init__(self):
        """Initialize consistency checker."""
        logger.info("ConsistencyChecker initialized (stub)")
    
    def check(self, documents: list[dict]) -> dict:
        """Check consistency across multiple document analysis results.
        
        Args:
            documents: List of document analysis results, each containing
                      'document_type', 'fields', and 'validation' keys.
            
        Returns:
            dict with keys:
                - checks (list[dict]): Consistency checks, each with:
                    'field', 'documents_compared', 'consistent' (bool),
                    'message', 'values' (list)
                - consistent (bool): True if all cross-checks pass
                - consistency_score (float): 0.0 (inconsistent) to 1.0 (consistent)
                - status (str): 'success', 'insufficient_documents', or 'not_implemented'
        """
        if len(documents) < 2:
            return {
                "checks": [],
                "consistent": True,
                "consistency_score": 1.0,
                "status": "insufficient_documents",
                "message": "Need at least 2 documents for consistency checking.",
            }
        
        # TODO (Day 9): Implement cross-document field comparison
        
        logger.warning("Consistency checker stub active — returning no checks")
        return {
            "checks": [],
            "consistent": True,
            "consistency_score": 1.0,
            "status": "not_implemented",
            "message": "Consistency checker not yet implemented.",
        }
