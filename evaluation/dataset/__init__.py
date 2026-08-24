"""Industrial RAG evaluation dataset subpackage."""
from pathlib import Path
import json

DATASET_PATH = Path(__file__).resolve().parent / "industrial_test_set.json"


def load_industrial_test_set():
    """Loads the canonical 25-question industrial evaluation dataset."""
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


__all__ = ["load_industrial_test_set", "DATASET_PATH"]
