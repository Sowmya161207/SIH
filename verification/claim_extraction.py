"""Claim extraction and modality analysis for refinery AI findings."""

import re
from typing import List, Union, Dict, Any
from .schemas import Claim, ClaimModality

# Common hedging terms indicating probabilistic or inferred claims
PROBABILISTIC_INDICATORS = [
    r"\bpossible\b",
    r"\bpossibly\b",
    r"\bpotential\b",
    r"\blikely\b",
    r"\bsuspected\b",
    r"\bprobable\b",
    r"\bprobably\b",
    r"\bmay\b",
    r"\bmight\b",
    r"\bcould\b",
    r"\bseems\b",
    r"\bappears\b",
    r"\bsuggests?\b",
    r"\bindicates? (a |the )?possib(ility|le)\b",
    r"\bhypothesis\b",
    r"\bpresumed\b",
    r"\btentative\b",
]

# Recommendation keywords
RECOMMENDATION_INDICATORS = [
    r"\brecommend(s|ed|ation)?\b",
    r"\bshould (be|have)\b",
    r"\bmust (be|have)\b",
    r"\brequires?\b",
    r"\badvise(d)?\b",
    r"\bschedule\b",
    r"\bpropose(d)?\b",
    r"\baction needed\b",
]

# Stopwords to filter out from keyword extraction
STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "because", "as", "what",
    "which", "this", "that", "these", "those", "then", "just", "so", "than",
    "such", "both", "through", "about", "for", "is", "of", "while", "during",
    "to", "from", "in", "out", "on", "off", "again", "further", "then", "once",
    "here", "there", "when", "where", "why", "how", "all", "any", "both", "each",
    "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only",
    "own", "same", "so", "than", "too", "very", "can", "will", "just", "should",
    "now", "by", "with", "at", "be", "was", "were", "been", "being", "have", "has",
    "had", "do", "does", "did", "doing", "i", "we", "you", "they", "it", "its"
}


def clean_claim_text(text: str) -> str:
    """Strip bullet markers, prefixes like 'Finding:', quotes, and extra whitespace."""
    cleaned = text.strip()
    # Remove leading markdown headers or prefixes
    cleaned = re.sub(r"^(finding|claim|ai finding|observation|finding\s*\d*)\s*:\s*", "", cleaned, flags=re.IGNORECASE)
    # Remove leading list bullets / numbers repeatedly (e.g. '- 1. ', '* ', '1. ')
    cleaned = re.sub(r"^(\s*[-*•]|\s*\d+[\.\)])+\s*", "", cleaned)
    # Remove surrounding quotes
    cleaned = cleaned.strip("\"' \t\r\n")
    return cleaned


def detect_modality(text: str) -> ClaimModality:
    """Analyze the grammatical modality/hedging of the claim."""
    lower_text = text.lower()
    for pattern in RECOMMENDATION_INDICATORS:
        if re.search(pattern, lower_text):
            return ClaimModality.RECOMMENDATION
    for pattern in PROBABILISTIC_INDICATORS:
        if re.search(pattern, lower_text):
            return ClaimModality.PROBABILISTIC
    return ClaimModality.DEFINITE


def extract_keywords(text: str) -> List[str]:
    """Extract significant domain keywords from claim text."""
    words = re.findall(r"\b[a-zA-Z0-9_\-\.%]+\b", text.lower())
    keywords = [w for w in words if w not in STOPWORDS and len(w) > 1 and not w.isdigit()]
    return list(dict.fromkeys(keywords))


def extract_entities(text: str) -> List[str]:
    """Extract equipment codes, unit names, and critical components."""
    entities = []
    # Equipment tags like P-101, K-201A, V-302, TK-1002, E-104
    tag_matches = re.findall(r"\b[A-Z]{1,4}-[0-9]{2,4}[A-Z]?\b", text)
    entities.extend(tag_matches)

    # Common refinery equipment components
    equipment_terms = [
        "bearing", "impeller", "casing", "seal", "mechanical seal",
        "coupling", "motor", "rotor", "stator", "valve", "compressor",
        "pump", "turbine", "heat exchanger", "column", "furnace", "pipe",
        "pipeline", "flange", "gasket", "lubrication", "oil", "filter"
    ]
    lower = text.lower()
    for term in equipment_terms:
        if re.search(r"\b" + re.escape(term) + r"\b", lower):
            entities.append(term)

    return list(dict.fromkeys(entities))


def extract_claims(findings: Union[str, List[Union[str, Dict[str, Any]]], Dict[str, Any]]) -> List[Claim]:
    """
    Extract atomic claims from various finding input structures.

    Supports:
    - Single finding string: "Possible bearing degradation."
    - Multi-line / bulleted findings string
    - List of finding strings: ["Vibration spike in P-101", "Possible bearing wear"]
    - List of dicts: [{"finding": "...", "confidence": 0.8}]
    - Single dict with keys like 'findings', 'claim', 'text'
    """
    raw_texts = []

    if isinstance(findings, str):
        # Split multiline findings or bullet points
        lines = [line.strip() for line in findings.split("\n") if line.strip()]
        if len(lines) > 1:
            raw_texts.extend(lines)
        else:
            raw_texts.append(findings)

    elif isinstance(findings, list):
        for item in findings:
            if isinstance(item, str):
                if "\n" in item:
                    raw_texts.extend([l.strip() for l in item.split("\n") if l.strip()])
                else:
                    raw_texts.append(item)
            elif isinstance(item, dict):
                text = item.get("claim") or item.get("finding") or item.get("text") or item.get("description")
                if text:
                    raw_texts.append(str(text))
            elif hasattr(item, "text"):
                raw_texts.append(getattr(item, "text"))
            else:
                raw_texts.append(str(item))

    elif isinstance(findings, dict):
        nested = findings.get("findings") or findings.get("claims") or findings.get("finding") or findings.get("claim")
        if nested:
            return extract_claims(nested)
        else:
            for k in ["text", "description", "summary"]:
                if k in findings:
                    raw_texts.append(str(findings[k]))
                    break

    # Build claim objects
    claims: List[Claim] = []
    for raw in raw_texts:
        cleaned = clean_claim_text(raw)
        if not cleaned:
            continue

        modality = detect_modality(cleaned)
        keywords = extract_keywords(cleaned)
        entities = extract_entities(cleaned)

        claims.append(
            Claim(
                text=cleaned,
                modality=modality,
                keywords=keywords,
                entities=entities,
                source_finding=raw
            )
        )

    return claims
