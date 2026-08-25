import json
import re
from pathlib import Path
from collections import Counter


# ==============================================================================
# MRPL DOCUMENT CHUNK QUALITY CHECK
# ==============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "training" / "document_chunks.jsonl"


# ==============================================================================
# Encoding corruption patterns
# ==============================================================================

MOJIBAKE_PATTERNS = [
    "ï¬",
    "â€“",
    "â€”",
    "â€˜",
    "â€™",
    "â€œ",
    "â€¦",
    "Â",
    "�",
]


# ==============================================================================
# Load chunks
# ==============================================================================

def load_chunks():
    chunks = []

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as f:

        for line_number, line in enumerate(f, start=1):

            line = line.strip()

            if not line:
                continue

            try:
                data = json.loads(line)
                chunks.append(data)

            except json.JSONDecodeError as e:

                print(
                    f"[WARNING] Invalid JSON at line {line_number}: {e}"
                )

    return chunks


# ==============================================================================
# Encoding check
# ==============================================================================

def has_encoding_problem(text: str) -> bool:

    # Replacement character
    if "\ufffd" in text:
        return True

    # Private-use Unicode characters
    for char in text:

        code = ord(char)

        if 0xE000 <= code <= 0xF8FF:
            return True

    # Known mojibake patterns
    for pattern in MOJIBAKE_PATTERNS:

        if pattern in text:
            return True

    return False


# ==============================================================================
# Main quality check
# ==============================================================================

def main():

    print("=" * 60)
    print("MRPL DOCUMENT CHUNK QUALITY CHECK")
    print("=" * 60)

    if not INPUT_FILE.exists():

        print(f"[ERROR] Dataset not found:")
        print(INPUT_FILE)

        return

    chunks = load_chunks()

    print(f"Total chunks: {len(chunks)}")

    # --------------------------------------------------------------------------
    # Missing fields
    # --------------------------------------------------------------------------

    missing_source = sum(
        1 for c in chunks
        if not c.get("source")
    )

    missing_chunk_id = sum(
        1 for c in chunks
        if not c.get("chunk_id")
    )

    missing_text = sum(
        1 for c in chunks
        if "text" not in c
    )

    empty_text = sum(
        1 for c in chunks
        if not str(c.get("text", "")).strip()
    )

    print(f"Missing source: {missing_source}")
    print(f"Missing chunk_id: {missing_chunk_id}")
    print(f"Missing text: {missing_text}")
    print(f"Empty text: {empty_text}")

    # --------------------------------------------------------------------------
    # Duplicate chunk IDs
    # --------------------------------------------------------------------------

    chunk_ids = [
        c.get("chunk_id")
        for c in chunks
        if c.get("chunk_id")
    ]

    chunk_id_counts = Counter(chunk_ids)

    duplicate_chunk_ids = {
        cid: count
        for cid, count in chunk_id_counts.items()
        if count > 1
    }

    print(
        f"Duplicate chunk IDs: "
        f"{len(duplicate_chunk_ids)}"
    )

    # --------------------------------------------------------------------------
    # Duplicate text
    # --------------------------------------------------------------------------

    texts = [
        str(c.get("text", "")).strip()
        for c in chunks
        if str(c.get("text", "")).strip()
    ]

    text_counts = Counter(texts)

    duplicate_text_groups = {
        text: count
        for text, count in text_counts.items()
        if count > 1
    }

    duplicate_text_occurrences = sum(
        count - 1
        for count in duplicate_text_groups.values()
    )

    print(
        f"Duplicate text groups: "
        f"{len(duplicate_text_groups)}"
    )

    print(
        f"Duplicate text occurrences: "
        f"{duplicate_text_occurrences}"
    )

    # --------------------------------------------------------------------------
    # Very short chunks
    # --------------------------------------------------------------------------

    short_chunks = [
        c
        for c in chunks
        if len(str(c.get("text", "")).strip()) < 100
    ]

    print(
        f"Very short chunks (<100 characters): "
        f"{len(short_chunks)}"
    )

    # --------------------------------------------------------------------------
    # Encoding problems
    # --------------------------------------------------------------------------

    encoding_problem_chunks = []

    for chunk in chunks:

        text = str(chunk.get("text", ""))

        if has_encoding_problem(text):

            encoding_problem_chunks.append(chunk)

    print(
        f"Possible encoding problems: "
        f"{len(encoding_problem_chunks)}"
    )

    # --------------------------------------------------------------------------
    # Show encoding examples
    # --------------------------------------------------------------------------

    if encoding_problem_chunks:

        print()
        print("Encoding problem examples:")

        for chunk in encoding_problem_chunks[:10]:

            text = str(chunk.get("text", ""))

            print(
                f"  {chunk.get('source')} | "
                f"{chunk.get('chunk_id')} | "
                f"{repr(text[:150])}"
            )

    # --------------------------------------------------------------------------
    # Chunks per document
    # --------------------------------------------------------------------------

    document_counts = Counter(
        c.get("source")
        for c in chunks
    )

    print()
    print("Chunks per document:")

    for document, count in sorted(
        document_counts.items()
    ):

        print(
            f"  {document}: {count}"
        )

    # --------------------------------------------------------------------------
    # Final status
    # --------------------------------------------------------------------------

    print()
    print("=" * 60)
    print("QUALITY CHECK COMPLETE")
    print("=" * 60)

    critical_errors = (
        missing_source
        + missing_chunk_id
        + missing_text
        + empty_text
        + len(duplicate_chunk_ids)
        + len(encoding_problem_chunks)
    )

    if critical_errors == 0:

        print("STATUS: PASS")

    else:

        print("STATUS: REVIEW REQUIRED")


if __name__ == "__main__":
    main()