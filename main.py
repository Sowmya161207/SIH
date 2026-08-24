"""Sovereign On-Premise Agentic AI Workbench - MRPL (SIH26117)
Claim Verification & Evidence Layer Entry Point
"""

import json
import sys
from verification import verify_claims, ClaimVerifier, VerificationStatus


def run_benchmark_scenarios():
    print("=" * 70)
    print("  MRPL SOVEREIGN AI WORKBENCH - CLAIM VERIFICATION LAYER (SIH26117)")
    print("=" * 70)

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
        print("-" * 70)

    # Multi-claim Batch Report
    print("\n[5] Scenario 5: Multi-Claim AI Batch Report")
    batch_findings = [
        "Vibration increased 35% on P-101",
        "Possible bearing degradation.",
        "Mechanical seal leakage detected on Booster Pump P-204.",
        "Cooling water bypass valve V-402 is stuck 40% open."
    ]
    batch_evidence = [
        "Vibration increased 35% on P-101",
        "Bearing inspection overdue",
        "Equipment manual lists bearing wear as a possible cause of vibration",
        "Maintenance log: P-204 seal inspected and passed pressure test with zero leakage"
    ]

    verifier = ClaimVerifier()
    report = verifier.verify_to_report(batch_findings, batch_evidence)
    print("\n  Summary Statistics:")
    print(f"    Total Claims Analyzed: {len(report.results)}")
    print(f"    Summary by Status: {json.dumps(report.summary)}")
    print(f"    Overall Confidence: {report.overall_confidence:.2f}")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        import unittest
        suite = unittest.defaultTestLoader.discover("verification/tests")
        runner = unittest.TextTestRunner(verbosity=2)
        runner.run(suite)
    else:
        run_benchmark_scenarios()


if __name__ == "__main__":
    main()
