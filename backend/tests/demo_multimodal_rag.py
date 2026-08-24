"""
demo_multimodal_rag.py
----------------------
End-to-end Demonstration of the Multimodal RAG & Evidence Pipeline.

Demonstrates:
  Scanned Inspection Report
             ↓
            OCR
             ↓
      Extract findings
             ↓
    Retrieve related SOP
             ↓
Return evidence-backed information
"""

import sys
import logging
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.rag_service import (
    ingest_document,
    process_document,
    retrieve,
    build_evidence,
    get_store_stats,
)
from app.services.ingestion.file_detector import detect_file_type

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("demo_multimodal_rag")


def main():
    print("=" * 70)
    print("DEMONSTRATION: Multimodal RAG & Hallucination-Free Evidence Layer")
    print("=" * 70)

    demo_dir = backend_dir.parent / "RAG" / "data" / "demo"
    report_pdf = demo_dir / "incident_report_p101.pdf"
    sop_pdf = demo_dir / "sop_pump_maintenance.pdf"

    # Step 1: Detect File Type & Ingest Scanned Inspection Report
    print("\n[Step 1] File Type Detection & OCR Ingestion")
    file_type = detect_file_type(report_pdf)
    print(f"  File: {report_pdf.name} -> Detected Type: '{file_type}'")

    report_res = ingest_document(
        document_id="doc_inspection_scan_101",
        file_path=report_pdf,
        metadata={
            "filename": "scanned_inspection_report_p101.pdf",
            "title": "Scanned Pump P-101 Inspection Report",
            "document_type": "incident",
        }
    )
    print(f"  Ingestion Result: {report_res}")

    # Process Document Hook
    proc_res = process_document("doc_inspection_scan_101")
    print(f"  Process Status: {proc_res}")

    # Step 2: Ingest Standard Operating Procedure (SOP)
    print("\n[Step 2] Ingesting Related Standard Operating Procedure (SOP)")
    sop_res = ingest_document(
        document_id="doc_sop_pump_maint",
        file_path=sop_pdf,
        metadata={
            "filename": "sop_pump_maintenance.pdf",
            "title": "SOP - Centrifugal Pump Maintenance",
            "document_type": "sop",
        }
    )
    print(f"  SOP Ingestion Result: {sop_res}")

    # Step 3: Extract Findings via Retrieval
    print("\n[Step 3] Extracting Findings from Ingested Inspection Report")
    finding_query = "bearing failure temperature oil release fire"
    report_findings = retrieve(finding_query, document_ids=["doc_inspection_scan_101"], top_k=2)

    for idx, f in enumerate(report_findings, 1):
        print(f"  Finding {idx} (Score: {f['score']}): Page {f['page']} - {f['content'][:120]}...")

    # Step 4: Retrieve Related SOP Procedure for Extracted Findings
    print("\n[Step 4] Retrieving Related SOP for Inspection Findings")
    sop_query = "Response to Bearing Temperature Alarm and Emergency Shutdown"
    sop_results = retrieve(sop_query, document_ids=["doc_sop_pump_maint"], top_k=2)

    for idx, r in enumerate(sop_results, 1):
        print(f"  SOP Citation {idx} (Score: {r['score']}): Page {r['page']} - {r['content'][:120]}...")

    # Step 5: Construct Evidence Objects for Santhosh's Orchestrator
    print("\n[Step 5] Building Evidence-Backed Output for Orchestrator")
    if report_findings and sop_results:
        finding_chunk = report_findings[0]
        sop_chunk = sop_results[0]

        claim_1 = "Pump P-101 suffered drive-end bearing failure due to lubrication starvation."
        ev_1 = build_evidence(claim_1, finding_chunk)

        claim_2 = "SOP requires immediate controlled shutdown if bearing temperature exceeds 85 degrees C."
        ev_2 = build_evidence(claim_2, sop_chunk)

        print("\n  Verified Evidence 1:")
        print(f"    Claim: {ev_1['claim']}")
        print(f"    Source: {ev_1['source_document']} (Page {ev_1['page']})")
        print(f"    Confidence: {ev_1['confidence']}")
        print(f"    Text: {ev_1['retrieved_text'][:100]}...")

        print("\n  Verified Evidence 2:")
        print(f"    Claim: {ev_2['claim']}")
        print(f"    Source: {ev_2['source_document']} (Page {ev_2['page']})")
        print(f"    Confidence: {ev_2['confidence']}")
        print(f"    Text: {ev_2['retrieved_text'][:100]}...")

    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETED SUCCESSFULLY [OK]")
    print("=" * 70)


if __name__ == "__main__":
    main()
