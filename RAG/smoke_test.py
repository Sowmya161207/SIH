"""End-to-end smoke test for the MRPL RAG pipeline."""
import json, sys
sys.path.insert(0, '.')
from rag_services import search_documents, get_store_stats

print("=== STORE STATS ===")
print(json.dumps(get_store_stats(), indent=2))

print()
print("=== QUERY 1: bearing temperature (role=maintenance_engineer) ===")
r = search_documents("bearing temperature exceeded alarm", user_role="maintenance_engineer", top_k=3)
for e in r["evidence"]:
    print("  [%.3f] %s p.%d -- %s..." % (e["score"], e["source"], e["page"], e["text"][:80]))

print()
print("=== QUERY 2: fire incident (role=maintenance_engineer -- should NOT see incident report) ===")
r2 = search_documents("DCS trip bypass bearing seizure fire", user_role="maintenance_engineer", top_k=5)
sources2 = [e["source"] for e in r2["evidence"]]
print("  Sources returned:", sources2)
blocked = "incident_report_p101.pdf" not in sources2
print("  Incident report BLOCKED:", blocked, "  <-- ACL working" if blocked else "  <-- ACL FAILURE")

print()
print("=== QUERY 3: same query (role=safety_officer -- SHOULD see incident report) ===")
r3 = search_documents("DCS trip bypass bearing seizure fire", user_role="safety_officer", top_k=5)
sources3 = [e["source"] for e in r3["evidence"]]
print("  Sources returned:", sources3)
visible = "incident_report_p101.pdf" in sources3
print("  Incident report VISIBLE:", visible, "  <-- ACL working" if visible else "  <-- ACL FAILURE")

print()
print("=== SUMMARY ===")
ok = blocked and visible
print("  PASS" if ok else "  FAIL", "-- Permission-aware retrieval is", "CORRECT" if ok else "BROKEN")
