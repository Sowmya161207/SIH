"""Verification and Evidence layer for Sovereign On-Premise AI Workbench (MRPL).

Distinguishes:
- SUPPORTED
- INFERRED
- UNSUPPORTED
- INSUFFICIENT_EVIDENCE
"""

from typing import List, Dict, Any, Union, Optional
from .schemas import (
    VerificationStatus,
    ClaimModality,
    EvidenceItem,
    Claim,
    ClaimVerificationResult,
    VerificationReport,
)
from .claim_extraction import extract_claims
from .evidence_matching import match_claim_to_evidence, MatchResult


def _generate_limitations(claim: Claim, match: MatchResult, status: VerificationStatus) -> List[str]:
    """Identify operational and physical data limitations for explainability."""
    limitations: List[str] = []
    claim_text_lower = claim.text.lower()

    if status == VerificationStatus.INSUFFICIENT_EVIDENCE:
        limitations.append("No corresponding sensor telemetry or RAG documentation available for this assertion.")
        return limitations

    if status == VerificationStatus.UNSUPPORTED:
        limitations.append("Claim directly contradicts recorded sensor or maintenance inspection logs.")
        return limitations

    # For inferred or supported claims, check for missing physical confirmations
    has_physical_inspection = any(
        "inspect" in e.text.lower() and ("pass" in e.text.lower() or "conducted" in e.text.lower() or "performed" in e.text.lower())
        for e in match.supporting_items
    )

    if ("bearing" in claim_text_lower or "wear" in claim_text_lower or "degradation" in claim_text_lower) and not has_physical_inspection:
        limitations.append("No physical bearing inspection available.")

    if ("leak" in claim_text_lower or "seal" in claim_text_lower) and not any("pressure test" in e.text.lower() or "visual" in e.text.lower() for e in match.supporting_items):
        if not ("bearing" in claim_text_lower):
            limitations.append("No visual or pressure seal test recorded.")

    # Inferred from indirect symptoms
    if status == VerificationStatus.INFERRED and not limitations:
        limitations.append("Synthesized from indirect symptoms without direct physical teardown confirmation.")

    return limitations


def _classify_claim(claim: Claim, match: MatchResult) -> Tuple[VerificationStatus, float, str]:
    """
    Classify claim into SUPPORTED, INFERRED, UNSUPPORTED, or INSUFFICIENT_EVIDENCE.
    Returns (status, confidence, reason).
    """
    from typing import Tuple

    # 1. Check for contradictions
    if match.has_contradiction:
        contra_reasons = "; ".join([e.text for e, _ in match.contradictions[:2]])
        return (
            VerificationStatus.UNSUPPORTED,
            0.90,
            f"Contradicted by evidence: {contra_reasons}"
        )

    # 2. Check for insufficient evidence
    if not match.supporting_items:
        return (
            VerificationStatus.INSUFFICIENT_EVIDENCE,
            0.15,
            "No direct or indirect evidence found in RAG or sensor data to substantiate the claim."
        )

    # 3. Check for Inferred vs Supported
    has_direct = len(match.direct_matches) > 0
    has_indirect = len(match.indirect_matches) > 0
    num_supporting = len(match.supporting_items)

    # If the claim is hedged (e.g. "Possible bearing degradation")
    if claim.modality == ClaimModality.PROBABILISTIC:
        if has_indirect or has_direct:
            # E.g. 3 supporting pieces of evidence -> confidence ~0.78
            base_conf = 0.65 + min(0.15, num_supporting * 0.05)
            # If multiple evidence sources support it (e.g. vibration + overdue + manual)
            if num_supporting >= 3:
                confidence = 0.78
            else:
                confidence = min(0.85, base_conf)

            reason = "Indirect evidence supports the possibility." if has_indirect and not has_direct else "Evidence correlates with the hypothesized condition."
            return (VerificationStatus.INFERRED, confidence, reason)

    # If claim is a recommendation
    if claim.modality == ClaimModality.RECOMMENDATION:
        confidence = min(0.88, 0.70 + num_supporting * 0.06)
        return (
            VerificationStatus.INFERRED,
            confidence,
            "Operational recommendation supported by correlative telemetry and maintenance guidelines."
        )

    # If claim is definite (e.g. "Bearing has failed" or "Vibration increased 35%")
    if has_direct and match.best_score >= 0.35:
        confidence = min(0.96, 0.85 + min(0.10, match.best_score * 0.15))
        return (
            VerificationStatus.SUPPORTED,
            confidence,
            "Direct evidence explicitly confirms the factual assertion."
        )

    # If claim is definite but we only have indirect or weak evidence
    if has_indirect:
        confidence = min(0.72, 0.55 + num_supporting * 0.05)
        return (
            VerificationStatus.INFERRED,
            confidence,
            "Indirect symptoms or guidelines suggest this condition, though direct physical proof is pending."
        )

    # Fallback to insufficient if match was too weak
    return (
        VerificationStatus.INSUFFICIENT_EVIDENCE,
        0.25,
        "Evidence provided has insufficient relevance to verify the claim."
    )


class ClaimVerifier:
    """Core Verifier engine for MRPL Workbench."""

    def __init__(self, default_threshold: float = 0.3):
        self.default_threshold = default_threshold

    def verify(
        self,
        findings: Union[str, List[Union[str, Dict[str, Any]]], Dict[str, Any]],
        evidence: Union[str, List[Union[str, Dict[str, Any]]], Dict[str, Any]]
    ) -> List[ClaimVerificationResult]:
        """
        Verify findings against evidence and return list of ClaimVerificationResult.
        """
        # 1. Extract claims
        claims = extract_claims(findings)
        if not claims:
            return []

        # 2. Normalize evidence items
        evidence_items: List[EvidenceItem] = []
        if isinstance(evidence, str):
            lines = [l.strip() for l in evidence.split("\n") if l.strip()]
            for line in lines:
                evidence_items.append(EvidenceItem.from_input(line))
        elif isinstance(evidence, list):
            for item in evidence:
                if isinstance(item, str) and "\n" in item:
                    for sub in item.split("\n"):
                        if sub.strip():
                            evidence_items.append(EvidenceItem.from_input(sub))
                else:
                    evidence_items.append(EvidenceItem.from_input(item))
        elif isinstance(evidence, dict):
            items = evidence.get("evidence") or evidence.get("items") or evidence.get("snippets")
            if isinstance(items, list):
                for item in items:
                    evidence_items.append(EvidenceItem.from_input(item))
            else:
                for k in ["text", "content", "summary"]:
                    if k in evidence:
                        evidence_items.append(EvidenceItem.from_input(evidence[k]))
                        break

        # 3. Match and verify each claim
        results: List[ClaimVerificationResult] = []
        for claim in claims:
            match = match_claim_to_evidence(claim, evidence_items)
            status, confidence, reason = _classify_claim(claim, match)
            limitations = _generate_limitations(claim, match, status)

            result = ClaimVerificationResult(
                claim=claim.text,
                status=status,
                confidence=confidence,
                supporting_evidence=match.supporting_texts,
                reason=reason,
                limitations=limitations,
                contradicting_evidence=[e.text for e, _ in match.contradictions]
            )
            results.append(result)

        return results

    def verify_to_report(
        self,
        findings: Union[str, List[Any], Dict[str, Any]],
        evidence: Union[str, List[Any], Dict[str, Any]]
    ) -> VerificationReport:
        """Verify and return a complete VerificationReport with summary stats."""
        results = self.verify(findings, evidence)
        summary: Dict[str, int] = {
            VerificationStatus.SUPPORTED.value: 0,
            VerificationStatus.INFERRED.value: 0,
            VerificationStatus.UNSUPPORTED.value: 0,
            VerificationStatus.INSUFFICIENT_EVIDENCE.value: 0,
        }
        total_conf = 0.0
        for r in results:
            st = str(r.status)
            summary[st] = summary.get(st, 0) + 1
            total_conf += r.confidence

        avg_conf = total_conf / len(results) if results else 0.0
        return VerificationReport(
            results=results,
            summary=summary,
            overall_confidence=avg_conf
        )


def verify_claims(
    findings: Union[str, List[Union[str, Dict[str, Any]]], Dict[str, Any]],
    evidence: Union[str, List[Union[str, Dict[str, Any]]], Dict[str, Any]],
    as_dict: bool = True
) -> Union[List[Dict[str, Any]], Dict[str, Any], List[ClaimVerificationResult]]:
    """
    Main verification entrypoint for SIH26117 MRPL Sovereign AI Workbench.

    Accepts findings and evidence from RAG + Sensor Analytics, extracts claims,
    matches against evidence, classifies status (SUPPORTED, INFERRED, UNSUPPORTED,
    INSUFFICIENT_EVIDENCE), generates confidence score, reasons, and limitations.

    If findings is a single string/claim and as_dict=True, returns the single result dict:
    {
      "claim": "Possible bearing degradation",
      "status": "INFERRED",
      "confidence": 0.78,
      "supporting_evidence": [...],
      "reason": "Indirect evidence supports the possibility.",
      "limitations": ["No physical bearing inspection available."]
    }

    If findings contains multiple claims, returns a List of result dicts.
    """
    verifier = ClaimVerifier()
    results = verifier.verify(findings, evidence)

    if not as_dict:
        return results

    dict_results = [r.to_dict() for r in results]

    # If input was a single finding string with one claim, return the single dict
    if isinstance(findings, str) and len(dict_results) == 1 and "\n" not in findings.strip():
        return dict_results[0]

    return dict_results
