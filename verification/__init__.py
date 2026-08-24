"""Claim Verification and Evidence Layer for MRPL Sovereign AI Workbench (SIH26117)."""

from .schemas import (
    VerificationStatus,
    ClaimModality,
    EvidenceItem,
    Claim,
    ClaimVerificationResult,
    VerificationReport,
)
from .claim_extraction import extract_claims, detect_modality
from .evidence_matching import match_claim_to_evidence
from .verifier import ClaimVerifier, verify_claims

__all__ = [
    "verify_claims",
    "ClaimVerifier",
    "VerificationStatus",
    "ClaimModality",
    "EvidenceItem",
    "Claim",
    "ClaimVerificationResult",
    "VerificationReport",
    "extract_claims",
    "detect_modality",
    "match_claim_to_evidence",
]
