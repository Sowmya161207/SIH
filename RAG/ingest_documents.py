"""
ingest_documents.py
-------------------
CLI entry point for ingesting PDF documents into the RAG vector store.

Usage
-----
    # Ingest an entire directory of PDFs:
    python ingest_documents.py --pdf_dir data/demo/

    # Ingest a single PDF with custom metadata:
    python ingest_documents.py \\
        --pdf   data/raw/my_report.pdf \\
        --id    my_report \\
        --title "My Equipment Report" \\
        --equipment "Pump P-101" \\
        --doc_type maintenance \\
        --roles maintenance_engineer manager

    # Reset store before ingesting:
    python ingest_documents.py --pdf_dir data/demo/ --reset

    # Check store stats only:
    python ingest_documents.py --stats
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# ── Make the RAG package importable when run from any CWD ─────────────────────
_HERE = Path(__file__).parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

logging.basicConfig(
    level   = logging.INFO,
    format  = "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt = "%H:%M:%S",
)
logger = logging.getLogger("ingest")

# ── Predefined metadata for the four MRPL demo documents ──────────────────────
DEMO_METADATA: dict[str, dict] = {
    "maintenance_report_p101.pdf": {
        "document_id":   "maint_report_p101",
        "title":         "Pump P-101 Maintenance Report — Q2 2025",
        "equipment":     "Pump P-101",
        "document_type": "maintenance",
        "classification":"internal",
        "allowed_roles": ["maintenance_engineer", "manager"],
    },
    "equipment_manual_p101.pdf": {
        "document_id":   "equip_manual_p101",
        "title":         "Pump P-101 Equipment Manual",
        "equipment":     "Pump P-101",
        "document_type": "manual",
        "classification":"internal",
        "allowed_roles": ["maintenance_engineer", "operator", "manager"],
    },
    "sop_pump_maintenance.pdf": {
        "document_id":   "sop_pump_maint",
        "title":         "Standard Operating Procedure — Pump Maintenance",
        "equipment":     "Pump P-101",
        "document_type": "sop",
        "classification":"internal",
        "allowed_roles": ["maintenance_engineer", "operator", "safety_officer", "manager"],
    },
    "incident_report_p101.pdf": {
        "document_id":   "incident_p101_2024",
        "title":         "Incident Report — Pump P-101 Bearing Failure (2024)",
        "equipment":     "Pump P-101",
        "document_type": "incident",
        "classification":"confidential",
        "allowed_roles": ["safety_officer", "manager"],
    },
}


def ingest_one(
    pdf_path: Path,
    metadata: dict,
    reset: bool = False,
) -> dict:
    """Ingest a single PDF. Returns the result dict from rag_services."""
    from rag_services import ingest_pdf
    return ingest_pdf(pdf_path=pdf_path, metadata=metadata, reset_store=reset)


def ingest_directory(pdf_dir: Path, reset: bool = False) -> None:
    """Ingest all PDFs in a directory, using demo metadata where available."""
    pdfs = sorted(pdf_dir.glob("*.pdf"))
    if not pdfs:
        logger.error("No PDF files found in %s", pdf_dir)
        sys.exit(1)

    logger.info("Found %d PDF(s) in %s", len(pdfs), pdf_dir)

    first = True
    for pdf_path in pdfs:
        # Look up predefined metadata or build a sensible default
        meta = DEMO_METADATA.get(pdf_path.name)
        if meta is None:
            logger.warning(
                "No predefined metadata for '%s' — using defaults.", pdf_path.name
            )
            stem = pdf_path.stem.replace("-", "_").replace(" ", "_").lower()
            meta = {
                "document_id":   stem,
                "title":         pdf_path.stem.replace("_", " ").title(),
                "equipment":     "Unknown",
                "document_type": "general",
                "classification":"internal",
                "allowed_roles": [],
            }

        result = ingest_one(pdf_path, meta, reset=(reset and first))
        first  = False
        logger.info(
            "  ✓ %s → %d chunks (id=%s)",
            pdf_path.name, result["chunks_added"], result["document_id"],
        )


def main():
    parser = argparse.ArgumentParser(
        description="Ingest PDF documents into the MRPL RAG vector store.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # ── Modes ──
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--pdf_dir", type=Path,
        help="Ingest all PDFs in this directory.",
    )
    group.add_argument(
        "--pdf", type=Path,
        help="Ingest a single PDF file.",
    )
    group.add_argument(
        "--stats", action="store_true",
        help="Print vector store statistics and exit.",
    )

    # ── Single-file metadata ──
    parser.add_argument("--id",        default=None, help="document_id")
    parser.add_argument("--title",     default=None, help="Document title")
    parser.add_argument("--equipment", default="Unknown", help="Equipment tag")
    parser.add_argument("--doc_type",  default="general",
                        choices=["maintenance", "manual", "sop", "incident", "general"])
    parser.add_argument("--classification", default="internal",
                        choices=["public", "internal", "confidential", "restricted"])
    parser.add_argument("--roles", nargs="*", default=[],
                        help="Allowed roles (space-separated)")

    parser.add_argument("--reset", action="store_true",
                        help="Wipe the vector store before ingesting.")

    args = parser.parse_args()

    # ── Stats mode ──
    if args.stats:
        from rag_services import get_store_stats
        stats = get_store_stats()
        print(json.dumps(stats, indent=2))
        sys.exit(0)

    # ── Directory mode ──
    if args.pdf_dir:
        pdf_dir = args.pdf_dir
        if not pdf_dir.is_dir():
            logger.error("Not a directory: %s", pdf_dir)
            sys.exit(1)
        ingest_directory(pdf_dir, reset=args.reset)

    # ── Single PDF mode ──
    elif args.pdf:
        pdf_path = args.pdf
        if not pdf_path.exists():
            logger.error("File not found: %s", pdf_path)
            sys.exit(1)

        doc_id = args.id or pdf_path.stem.replace("-", "_").replace(" ", "_").lower()
        title  = args.title or pdf_path.stem.replace("_", " ").title()

        meta = {
            "document_id":   doc_id,
            "title":         title,
            "equipment":     args.equipment,
            "document_type": args.doc_type,
            "classification":args.classification,
            "allowed_roles": args.roles,
        }

        result = ingest_one(pdf_path, meta, reset=args.reset)
        print(json.dumps(result, indent=2))

    logger.info("Ingestion complete.")
    from rag_services import get_store_stats
    stats = get_store_stats()
    logger.info("Store now contains %d vectors.", stats["total_vectors"])


if __name__ == "__main__":
    main()
