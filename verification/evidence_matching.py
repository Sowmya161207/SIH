"""Evidence matching, semantic similarity, and contradiction detection."""

import re
from typing import List, Dict, Any, Tuple
from .schemas import Claim, EvidenceItem, ClaimModality

# Negation and contradiction indicators in evidence
CONTRADICTION_PATTERNS = [
    r"\bnot\b",
    r"\bno (signs?|evidence|wear|damage|abnormality|degradation)\b",
    r"\bwithin normal (limits?|range|parameters?)\b",
    r"\bnormal condition\b",
    r"\bhealthy\b",
    r"\bintact\b",
    r"\bno anomaly\b",
    r"\bpassed inspection\b",
    r"\bzero (leakage|vibration|defect)\b",
    r"\bfalse alarm\b",
    r"\bincorrect\b",
    r"\brefuted\b",
    r"\bno deviation\b"
]

# Indirect or causal link indicators in evidence
CAUSAL_INDIRECT_PATTERNS = [
    r"\b(cause|causes|caused by|result of|leads to|associated with)\b",
    r"\b(manual|sop|guide|handbook|documentation) (lists|specifies|indicates|states)\b",
    r"\b(possible|potential|probable) (cause|source|reason)\b",
    r"\b(symptom|indicator|sign) of\b",
    r"\b(correlated with|coincides with)\b",
    r"\b(overdue|delayed|pending) (inspection|maintenance|lubrication|replacement)\b",
    r"\b(increase|drop|fluctuation|spike|drift) in\b"
]


def normalize_tokens(text: str) -> List[str]:
    """Tokenize and clean text into normalized terms."""
    words = re.findall(r"\b[a-zA-Z0-9_\-\.%]+\b", text.lower())
    # Strip basic suffixes for light stem matching
    stems = []
    for w in words:
        if len(w) > 4 and w.endswith("ing"):
            stems.append(w[:-3])
        elif len(w) > 3 and w.endswith("ed"):
            stems.append(w[:-2])
        elif len(w) > 4 and w.endswith("tion"):
            stems.append(w[:-4])
        elif len(w) > 3 and w.endswith("s"):
            stems.append(w[:-1])
        else:
            stems.append(w)
    return stems


def compute_token_overlap(claim_tokens: List[str], evidence_tokens: List[str]) -> float:
    """Calculate Jaccard and containment overlap between claim and evidence tokens."""
    if not claim_tokens or not evidence_tokens:
        return 0.0
    set_c = set(claim_tokens)
    set_e = set(evidence_tokens)
    overlap = set_c.intersection(set_e)
    if not overlap:
        return 0.0
    # Weighted score emphasizing coverage of claim requirements
    containment = len(overlap) / len(set_c)
    jaccard = len(overlap) / len(set_c.union(set_e))
    return 0.7 * containment + 0.3 * jaccard


def check_contradiction(claim: Claim, evidence: EvidenceItem) -> bool:
    """
    Check if an evidence item explicitly contradicts the claim.
    Example: Claim states 'Bearing degradation', Evidence states 'Bearing inspected: healthy, no wear found'.
    """
    evidence_lower = evidence.text.lower()
    claim_lower = claim.text.lower()

    # Check if entities in claim are mentioned in evidence
    entity_found = False
    for entity in claim.entities:
        if entity.lower() in evidence_lower:
            entity_found = True
            break
    for kw in claim.keywords:
        if kw in evidence_lower:
            entity_found = True
            break

    if not entity_found:
        return False

    # Check for negation patterns
    for pattern in CONTRADICTION_PATTERNS:
        if re.search(pattern, evidence_lower):
            # Verify the negation refers to a core topic in the claim
            # e.g. "no wear" when claim is about "wear" or "degradation"
            negative_claim_words = ["degrad", "fail", "leak", "overheat", "wear", "spike", "exceed", "abnormal", "fault", "vibrat"]
            if any(term in claim_lower for term in negative_claim_words):
                return True

    return False


def is_indirect_evidence(claim: Claim, evidence: EvidenceItem) -> bool:
    """
    Check if evidence provides indirect/correlational/causal context rather than direct proof.
    e.g. Equipment manual cause lists, symptom descriptions, overdue maintenance, correlated sensor metrics.
    """
    evidence_lower = evidence.text.lower()
    claim_lower = claim.text.lower()

    # If evidence describes a symptom (e.g. vibration increase) while claim describes a root cause (bearing degradation)
    if "vibrat" in evidence_lower and any(term in claim_lower for term in ["bearing", "gear", "shaft", "rotor", "degrad", "wear", "misalign"]):
        return True

    # If overdue inspection correlates with wear/degradation/failure on the same component
    if ("overdue" in evidence_lower or "pending" in evidence_lower):
        if any(ent.lower() in evidence_lower for ent in claim.entities) or any(kw in evidence_lower for kw in claim.keywords):
            return True
        if any(t in claim_lower and t in evidence_lower for t in ["bearing", "pump", "motor", "valve", "seal", "lubricat", "oil"]):
            return True

    # If evidence explicitly mentions causal manual rules or guidelines
    for pattern in CAUSAL_INDIRECT_PATTERNS:
        if re.search(pattern, evidence_lower):
            # Check if the causal statement relates to the claim's entities, keywords, or shared topic
            if any(kw in evidence_lower for kw in claim.keywords) or any(ent.lower() in evidence_lower for ent in claim.entities):
                return True
            matching_topics = ["bearing", "wear", "degrad", "vibrat", "leak", "overheat", "pump", "motor", "valve", "seal", "lubricat"]
            if any(t in claim_lower and t in evidence_lower for t in matching_topics):
                return True

    if "temperature" in evidence_lower and any(term in claim_lower for term in ["overheat", "thermal", "hot", "cool"]):
        if any(ent.lower() in evidence_lower for ent in claim.entities):
            return True

    return False


class MatchResult:
    def __init__(self, claim: Claim):
        self.claim = claim
        self.direct_matches: List[Tuple[EvidenceItem, float]] = []
        self.indirect_matches: List[Tuple[EvidenceItem, float]] = []
        self.contradictions: List[Tuple[EvidenceItem, float]] = []
        self.best_score: float = 0.0
        self.total_evidence_count: int = 0

    @property
    def has_contradiction(self) -> bool:
        return len(self.contradictions) > 0

    @property
    def supporting_items(self) -> List[EvidenceItem]:
        items = [item for item, _ in self.direct_matches]
        for item, _ in self.indirect_matches:
            if item not in items:
                items.append(item)
        return items

    @property
    def supporting_texts(self) -> List[str]:
        return [item.text for item in self.supporting_items]


def match_claim_to_evidence(claim: Claim, evidence_items: List[EvidenceItem]) -> MatchResult:
    """
    Match an individual claim against all available evidence items.
    Classifies matched evidence into direct, indirect, and contradicting evidence.
    """
    result = MatchResult(claim)
    result.total_evidence_count = len(evidence_items)

    claim_tokens = normalize_tokens(claim.text)
    claim_keywords_stems = normalize_tokens(" ".join(claim.keywords))
    combined_claim_tokens = list(dict.fromkeys(claim_tokens + claim_keywords_stems))

    for item in evidence_items:
        if not item.text.strip():
            continue

        item_tokens = normalize_tokens(item.text)
        score = compute_token_overlap(combined_claim_tokens, item_tokens)

        # Entity boost
        for entity in claim.entities:
            if entity.lower() in item.text.lower():
                score += 0.25

        # Check contradiction first
        if check_contradiction(claim, item):
            result.contradictions.append((item, max(score, 0.7)))
            continue

        # Check for direct vs indirect relevance
        if is_indirect_evidence(claim, item):
            adjusted_score = max(score, 0.45)
            result.indirect_matches.append((item, adjusted_score))
        elif score >= 0.25 or (score >= 0.15 and len(claim.entities) > 0):
            result.direct_matches.append((item, score))
        elif score > 0.1:
            # Low overlap, treat as weak indirect or context
            result.indirect_matches.append((item, score))

    # Calculate overall best match score
    all_scores = [s for _, s in result.direct_matches] + [s * 0.85 for _, s in result.indirect_matches]
    if all_scores:
        result.best_score = min(1.0, max(all_scores))
    else:
        result.best_score = 0.0

    return result
