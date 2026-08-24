"""Sovereign On-Premise Agentic AI Workbench - MRPL (SIH26117)
Industrial Knowledge, Dataset, Retrieval & Verification Layer Entry Point
Role: Yoagesh (Industrial Knowledge, Dataset & QA Engineer)
"""

import json
import sys
from verification import verify_claims, ClaimVerifier
from knowledge import search_documents, format_citations, run_retrieval_benchmark, answer_and_verify


def run_verification_benchmarks():
    print("=" * 75)
    print("  [1] CLAIM VERIFICATION & EVIDENCE LAYER BENCHMARK (SIH26117)")
    print("=" * 75)

    scenarios = [
        {
            "title": "Scenario 1: Probabilistic Failure (INFERRED)",
            "finding": "Possible bearing degradation.",
            "evidence": [
                "Vibration increased 35% on P-101",
                "Bearing inspection overdue",
                "Equipment manual lists bearing wear as a possible cause of vibration"
            ]
        },
        {
            "title": "Scenario 2: Factual Telemetry Corroboration (SUPPORTED)",
            "finding": "Motor temperature reached 130 deg C on Crude Distillation Pump P-101.",
            "evidence": [
                "Telemetry Sensor TE-101 on Pump P-101 reading 130 deg C (High Alarm threshold 110 deg C)",
                "Cooling water inlet flow: 12 m3/h (Normal)"
            ]
        },
        {
            "title": "Scenario 3: Refuted Fault Assertion (UNSUPPORTED)",
            "finding": "Mechanical seal leakage detected on Booster Pump P-204.",
            "evidence": [
                "Maintenance log: P-204 seal inspected and passed pressure test with zero leakage",
                "Drain pot level normal"
            ]
        },
        {
            "title": "Scenario 4: Missing Telemetry / Data Gap (INSUFFICIENT_EVIDENCE)",
            "finding": "Cooling water bypass valve V-402 is stuck 40% open.",
            "evidence": [
                "Vibration increased 10% on Compressor K-101",
                "Ambient air temperature is 34 deg C"
            ]
        }
    ]

    for idx, sc in enumerate(scenarios, 1):
        print(f"\n[{idx}] {sc['title']}")
        print(f"  Finding: \"{sc['finding']}\"")
        print("  Evidence:")
        for ev in sc["evidence"]:
            print(f"    - {ev}")

        result = verify_claims(sc["finding"], sc["evidence"])
        print("\n  Verification Output:")
        print(json.dumps(result, indent=4))
        print("-" * 75)


def run_retrieval_demonstration():
    print("\n" + "=" * 75)
    print("  [2] INDUSTRIAL KNOWLEDGE BASE & RETRIEVAL BENCHMARK (`search_documents`)")
    print("=" * 75)

    sample_queries = [
        {"q": "What causes vibration increase in crude feed pump P-101?", "f": {"equipment_tag": "P-101"}},
        {"q": "Mechanical seal nitrogen pressure test on booster pump P-204", "f": {"doc_type": "MAINTENANCE_LOG"}},
        {"q": "Anti-surge protection minimum safe suction flow for K-101", "f": {"equipment_tag": "K-101"}},
    ]

    for item in sample_queries:
        print(f"\nQuery: \"{item['q']}\" | Filter: {item['f']}")
        res = search_documents(item["q"], filters=item["f"], top_k=2)
        print(f"Matched Chunks: {res.total_matched} (Latency: {res.search_latency_ms:.2f}ms)")
        print(format_citations(res.citations))
        print("-" * 75)

    print("\nExecuting Standardized Retrieval Evaluation Benchmark Suite...")
    benchmark_report = run_retrieval_benchmark(top_k=3)
    print(f"  Total Benchmark Queries : {benchmark_report['total_test_queries']}")
    print(f"  Mean Reciprocal Rank (MRR): {benchmark_report['mrr']:.4f}")
    print(f"  Mean Precision@3        : {benchmark_report['mean_precision_at_k']:.4f}")
    print(f"  Mean Recall@3           : {benchmark_report['mean_recall_at_k']:.4f}")
    print(f"  Average Latency         : {benchmark_report['average_latency_ms']:.2f} ms")
    print(f"  Benchmark Status        : {benchmark_report['status']}")


def run_end_to_end_qa():
    print("\n" + "=" * 75)
    print("  [3] END-TO-END QA: RETRIEVAL -> REASONING -> CLAIM VERIFICATION")
    print("=" * 75)

    qa_result = answer_and_verify(
        query="What is the high-high alarm temperature limit for P-101 motor and recommended action?",
        filters={"equipment_tag": "P-101"},
        telemetry_context=["Live Sensor TE-101 reading: 130 deg C (Alarm tripped)"]
    )
    print(f"Query: {qa_result['query']}")
    print("\nGround-Truth Citations Retrieved:")
    print(qa_result['citations_formatted'])
    print("Verification Result on Synthesized Finding:")
    print(json.dumps(qa_result['verification'], indent=4))


def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["--test", "-t"]:
            import unittest
            suite = unittest.defaultTestLoader.discover(".")
            runner = unittest.TextTestRunner(verbosity=2)
            runner.run(suite)
            return
        elif arg in ["--verify", "-v"]:
            run_verification_benchmarks()
            return
        elif arg in ["--retrieval", "-r"]:
            run_retrieval_demonstration()
            return
        elif arg in ["--qa", "-q"]:
            run_end_to_end_qa()
            return

    # Default: Run complete workbench pipeline
    run_verification_benchmarks()
    run_retrieval_demonstration()
    run_end_to_end_qa()


if __name__ == "__main__":
    main()
