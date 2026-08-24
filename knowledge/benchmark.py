"""Retrieval & Evaluation Benchmark for MRPL Sovereign AI Workbench (SIH26117).

Evaluates:
- Precision@K
- Recall@K
- Mean Reciprocal Rank (MRR)
- Metadata Filtering Accuracy
- Latency (ms)
"""

import time
from typing import List, Dict, Any
from .retriever import search_documents, EvidenceRetriever


BENCHMARK_TEST_SUITE = [
    {
        "query": "What causes vibration increase in crude feed pump P-101?",
        "filter": {"equipment_tag": "P-101"},
        "expected_chunk_ids": ["P101-OEM-C42", "P101-MAINT-C12"],
        "target_category": "Vibration Troubleshooting"
    },
    {
        "query": "P-101 motor high-high temperature trip limit",
        "filter": {"doc_type": "OEM_MANUAL"},
        "expected_chunk_ids": ["P101-OEM-C58"],
        "target_category": "Temperature Limits"
    },
    {
        "query": "Mechanical seal nitrogen pressure test on booster pump P-204",
        "filter": {"equipment_tag": "P-204"},
        "expected_chunk_ids": ["P204-MAINT-C04", "P204-SOP-C15"],
        "target_category": "Seal Maintenance"
    },
    {
        "query": "Wet gas compressor K-101 surge protection minimum safe suction flow",
        "filter": {"equipment_tag": "K-101"},
        "expected_chunk_ids": ["K101-OEM-C88"],
        "target_category": "Compressor Protection"
    },
    {
        "query": "Bypass valve V-402 positioner stroke test and air supply pressure",
        "filter": {"unit": "Utilities"},
        "expected_chunk_ids": ["V402-ALARM-C23"],
        "target_category": "Valve Actuator Troubleshooting"
    }
]


def run_retrieval_benchmark(top_k: int = 3) -> Dict[str, Any]:
    """Execute evaluation benchmark suite on knowledge retrieval engine."""
    results: List[Dict[str, Any]] = []
    total_queries = len(BENCHMARK_TEST_SUITE)
    reciprocal_ranks: List[float] = []
    precisions: List[float] = []
    recalls: List[float] = []
    latencies: List[float] = []

    for test in BENCHMARK_TEST_SUITE:
        start_time = time.perf_counter()
        search_res = search_documents(test["query"], filters=test["filter"], top_k=top_k)
        latency = (time.perf_counter() - start_time) * 1000.0
        latencies.append(latency)

        retrieved_ids = [c.chunk_id for c in search_res.citations]
        expected_ids = set(test["expected_chunk_ids"])

        # 1. Precision@K
        hits = [cid for cid in retrieved_ids if cid in expected_ids]
        precision = len(hits) / float(len(retrieved_ids)) if retrieved_ids else 0.0
        precisions.append(precision)

        # 2. Recall@K
        recall = len(hits) / float(len(expected_ids)) if expected_ids else 0.0
        recalls.append(recall)

        # 3. Reciprocal Rank (RR)
        rr = 0.0
        for rank, cid in enumerate(retrieved_ids, 1):
            if cid in expected_ids:
                rr = 1.0 / rank
                break
        reciprocal_ranks.append(rr)

        results.append({
            "query": test["query"],
            "category": test["target_category"],
            "filter": test["filter"],
            "retrieved_chunks": retrieved_ids,
            "expected_chunks": list(expected_ids),
            "precision_at_k": round(precision, 3),
            "recall_at_k": round(recall, 3),
            "reciprocal_rank": round(rr, 3),
            "latency_ms": round(latency, 2)
        })

    mrr = sum(reciprocal_ranks) / float(total_queries) if total_queries else 0.0
    avg_precision = sum(precisions) / float(total_queries) if total_queries else 0.0
    avg_recall = sum(recalls) / float(total_queries) if total_queries else 0.0
    avg_latency = sum(latencies) / float(total_queries) if total_queries else 0.0

    benchmark_summary = {
        "total_test_queries": total_queries,
        "top_k_evaluated": top_k,
        "mrr": round(mrr, 4),
        "mean_precision_at_k": round(avg_precision, 4),
        "mean_recall_at_k": round(avg_recall, 4),
        "average_latency_ms": round(avg_latency, 2),
        "status": "PASS" if mrr >= 0.85 and avg_recall >= 0.80 else "FAIL",
        "detailed_results": results
    }

    return benchmark_summary


if __name__ == "__main__":
    report = run_retrieval_benchmark()
    import json
    print(json.dumps(report, indent=2))
