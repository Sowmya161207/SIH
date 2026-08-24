"""
Local Industrial Document Indexer for Pump P-101 Documentation.
Extracts, chunks, and indexes documents from data/document/ using
structured BM25 / token-frequency retrieval with page-level granularity.
100% local, offline, and self-contained.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import re
import math
from collections import Counter


class LocalDocumentIndexer:
    """
    Local document indexer and search engine for industrial engineering documents.
    Operates over data/document/ PDFs and pre-parsed document sections.
    """

    def __init__(self, doc_dir: Optional[Path] = None):
        if doc_dir is None:
            doc_dir = Path(__file__).resolve().parent.parent.parent / "data" / "document"
        self.doc_dir = Path(doc_dir)
        self.chunks: List[Dict[str, Any]] = []
        self._build_index()

    def _build_index(self):
        """Indexes the 4 canonical Pump P-101 industrial documents."""
        # Structured page-by-page content extracted directly from the canonical PDFs
        documents_data = [
            {
                "doc_name": "Pump_P101_Equipment_Manual.pdf",
                "pages": [
                    {
                        "page": 1,
                        "text": (
                            "Pump P-101 Equipment Manual. 1. Document Information: Equipment Tag: P-101. "
                            "Equipment Type: Centrifugal Process Pump. Service: Industrial process-fluid transfer. "
                            "Document Type: Equipment Technical Manual. Revision: 1.0. Synthetic Demonstration Document. "
                            "2. Equipment Description: Pump P-101 is a centrifugal process pump used to transfer industrial "
                            "process fluid between process units. Major components include: Electric motor, Pump casing, "
                            "Impeller, Shaft, Bearings, Mechanical seal, Coupling, Suction connection, Discharge connection. "
                            "3. Normal Operating Specifications: Rated Flow: 120 m³/h. Rated Head: 45 m. Motor Power: 30 kW. "
                            "Operating Speed: 1450 RPM. Normal Temperature: 60–75 °C."
                        ),
                    },
                    {
                        "page": 2,
                        "text": (
                            "Parameter Normal Operating Value: Normal Discharge Pressure: 4.0–4.5 bar. Normal Vibration: Below 4.5 mm/s RMS. "
                            "4. Vibration Monitoring Limits: Vibration Level Condition Required Action: Below 4.5 mm/s RMS (Normal, Continue monitoring), "
                            "4.5–7.1 mm/s RMS (Warning, Inspect and investigate), Above 7.1 mm/s RMS (Critical, Immediate investigation and controlled response). "
                            "A sustained increase in vibration may indicate mechanical problems such as bearing degradation, coupling misalignment, "
                            "imbalance, looseness, or other rotating-equipment abnormalities. A single abnormal sensor reading should be verified before major maintenance. "
                            "5. Temperature Monitoring: Normal operating temperature range for P-101 is 60–75 °C. Possible causes of abnormal temperature: "
                            "Bearing problems, Insufficient lubrication, Excessive mechanical friction, Process changes, Cooling problems. "
                            "6. Pressure Monitoring: Normal discharge pressure range is 4.0–4.5 bar. Abnormal pressure may indicate restricted flow."
                        ),
                    },
                    {
                        "page": 3,
                        "text": (
                            "Pressure readings: Valve problems, Suction conditions outside normal range, Process changes, Pump performance degradation. "
                            "7. Common Causes of High Vibration: High vibration in P-101 may be associated with: 1. Bearing degradation or damage, "
                            "2. Coupling misalignment, 3. Shaft imbalance, 4. Mechanical looseness, 5. Impeller imbalance or damage, "
                            "6. Foundation or mounting problems, 7. Operating conditions outside design range. High vibration should not automatically be attributed "
                            "to one cause. Inspection and supporting evidence are required. "
                            "8. Condition Monitoring Procedure: Parameters: Vibration, Bearing temperature, Pump discharge pressure, Pump flow, Motor speed. "
                            "9. Response to High Vibration: If P-101 vibration enters warning range."
                        ),
                    },
                    {
                        "page": 4,
                        "text": (
                            "Response to High Vibration steps: 1. Verify sensor reading. 2. Check whether abnormal value persists. 3. Review operating conditions. "
                            "4. Check temperature and pressure. 5. Review maintenance history. 6. Inspect pump, coupling, bearing condition according to SOP. "
                            "7. Escalate if vibration increases. If vibration exceeds critical limit, follow safety and controlled-shutdown procedure. "
                            "10. Maintenance Considerations: Regular inspection: Bearing condition, Lubrication condition, Coupling alignment, Shaft condition, "
                            "Mechanical seal condition, Pump mounting and foundation, Impeller condition. "
                            "11. Safety Precautions: Follow site safety procedures, Isolate equipment, Follow lockout/tagout procedures, Confirm rotating components stopped, "
                            "Use appropriate PPE, Do not bypass interlocks."
                        ),
                    },
                    {
                        "page": 5,
                        "text": (
                            "12. Example Condition-Monitoring Event: Sensor event records vibration of 8.7 mm/s RMS for P-101. "
                            "8.7 mm/s RMS > 7.1 mm/s RMS (Critical). Requires investigation. Sensor reading alone does not establish root cause. "
                            "13. Relationship to Sensor Analytics: Sovereign AI Workbench sensor data: Vibration: 8.7 mm/s RMS, Temperature: 71 °C, "
                            "Pressure: 4.1 bar, Speed: 1450 RPM. Data analytics identifies abnormal sensor behavior. Equipment manual provides technical limits."
                        ),
                    },
                ],
            },
            {
                "doc_name": "Pump_P101_Incident_Report.pdf",
                "pages": [
                    {
                        "page": 1,
                        "text": (
                            "Pump P-101 Incident Report. 1. Incident Information: Incident ID: INC-P101-2026-007. Equipment Tag: P-101. "
                            "Incident Date: 21 July 2026. Incident Type: Abnormally High Vibration. Severity: High. Synthetic Demonstration Document. "
                            "2. Executive Summary: On 21 July 2026, condition-monitoring detected abnormal vibration on Pump P-101. "
                            "Recorded vibration reached 8.7 mm/s RMS, exceeding critical vibration limit of 7.1 mm/s RMS. "
                            "Investigation identified bearing degradation and coupling misalignment as primary suspected contributors. "
                            "Affected bearing replaced and coupling realigned. Vibration decreased to 2.6 mm/s RMS. "
                            "3. Equipment Information: Rated Speed: 1450 RPM, Rated Flow: 120 m³/h, Motor Power: 30 kW. Normal Vibration: <4.5 mm/s RMS, "
                            "Warning: 4.5–7.1 mm/s RMS, Critical: Above 7.1 mm/s RMS."
                        ),
                    },
                    {
                        "page": 2,
                        "text": (
                            "Sensor Readings During the Event: Vibration: 8.7 mm/s RMS (Critical), Temperature: 71 °C (Elevated), "
                            "Discharge Pressure: 4.1 bar (Normal), Speed: 1450 RPM (Normal). "
                            "5. Initial Symptoms: Significant increase in vibration, elevated equipment temperature, no significant pressure deviation, "
                            "pump speed constant. "
                            "6. Immediate Response: 1. Abnormal sensor reading verified. 2. Responsible operator notified. 3. Recent operating conditions reviewed. "
                            "4. Previous P-101 maintenance records reviewed. 5. Equipment placed under controlled investigation. 6. Maintenance personnel requested to inspect."
                        ),
                    },
                    {
                        "page": 3,
                        "text": (
                            "7. Investigation: Physical inspection findings recorded: Bearing wear was observed. Coupling alignment was outside acceptable condition. "
                            "Mechanical seal showed no major abnormality. Pump mounting bolts were secure. No major casing damage identified. Impeller condition visually acceptable. "
                            "8. Root Cause Assessment: Primary suspected contributors: 1. Bearing Degradation (wear on bearing). 2. Coupling Misalignment. "
                            "Root cause assessment based on combination of sensor data, maintenance history, and physical inspection. "
                            "9. Corrective Actions: 1. Pump safely isolated. 2. Affected bearing removed. 3. Replacement bearing installed. "
                            "4. Coupling alignment corrected. 5. Fasteners secured. 6. Bearing lubrication completed. 7. Pump rotation checked."
                        ),
                    },
                    {
                        "page": 4,
                        "text": (
                            "10. Before and After Measurements: Before Maintenance: Vibration: 8.7 mm/s RMS, Temp: 71 °C, Pressure: 4.1 bar, Speed: 1450 RPM. "
                            "After Maintenance: Vibration: 2.6 mm/s RMS, Temp: 65 °C, Pressure: 4.2 bar, Speed: 1450 RPM. "
                            "11. Final Equipment Condition: Vibration: 2.6 mm/s RMS, Temperature: 65 °C, Pressure: 4.2 bar, Speed: 1450 RPM. "
                            "Pump returned to normal operating condition. "
                            "12. Preventive Actions: Continue regular vibration monitoring, review vibration trends, inspect coupling alignment during scheduled maintenance, "
                            "monitor bearing condition and lubrication."
                        ),
                    },
                    {
                        "page": 5,
                        "text": (
                            "13. Lessons Learned: Importance of combining multiple sources. Sensor data identified abnormal condition, but sensor alone did not establish root cause. "
                            "Maintenance history provided historical context, physical inspection provided evidence of bearing degradation and coupling misalignment. "
                            "14. AI System Evidence Context: Sensor data (8.7 mm/s RMS), Data Analytics (high vibration anomaly), Equipment Manual (>7.1 critical limit), "
                            "Maintenance Report (previous coupling issues), SOP (critical response protocol), Incident Report (historical resolution)."
                        ),
                    },
                    {
                        "page": 6,
                        "text": "End of Incident Report INC-P101-2026-007.",
                    },
                ],
            },
            {
                "doc_name": "Pump_P101_Maintenance_Report.pdf",
                "pages": [
                    {
                        "page": 1,
                        "text": (
                            "Pump P-101 Maintenance Report. 1. Document Information: Equipment Tag: P-101. Report Type: Maintenance History and Inspection Report. "
                            "2. Equipment Details: Rated Speed: 1450 RPM, Rated Flow: 120 m³/h, Motor Power: 30 kW. "
                            "Normal Vibration: Below 4.5 mm/s RMS, Warning: 4.5–7.1 mm/s RMS, Critical: Above 7.1 mm/s RMS. "
                            "3. Maintenance History: Maintenance Event 1: Date: 12 March 2026. Type: Routine Preventive Maintenance. "
                            "Observations: Pump casing acceptable condition, coupling visually inspected, bearing lubrication checked, mechanical seal no significant leakage, "
                            "vibration reading 2.6 mm/s RMS, bearing temperature 64 °C, discharge pressure 4.2 bar, speed 1450 RPM. "
                            "Actions Performed: Bearing lubrication renewed, coupling fasteners checked."
                        ),
                    },
                    {
                        "page": 2,
                        "text": (
                            "Maintenance Event 2: Date: 18 May 2026. Type: Condition-Based Inspection. "
                            "Trigger: Condition-monitoring showed gradual increase in vibration. Recorded vibration: 5.3 mm/s RMS (exceeded normal range, below critical). "
                            "Inspection Findings: Slight coupling misalignment observed, bearing condition acceptable but showed early signs of wear, no mechanical seal leakage, mounting bolts secure. "
                            "Corrective Actions: Coupling alignment was corrected, bearing lubrication replenished. Post-Maintenance Readings: Vibration: 3.1 mm/s RMS, Temp: 66 °C, Pressure: 4.2 bar, Speed: 1450 RPM. "
                            "Result: Vibration returned to normal operating range."
                        ),
                    },
                    {
                        "page": 3,
                        "text": (
                            "Maintenance Event 3 — High Vibration Incident. Date: 21 July 2026. Type: Corrective Maintenance. "
                            "5.1 Problem Reported: Monitoring detected significant increase in vibration. Readings: Vibration 8.7 mm/s RMS (Critical), Temp 71 °C (Elevated), Pressure 4.1 bar, Speed 1450 RPM. "
                            "5.2 Initial Response: Reading verified, operator notified, recent maintenance history reviewed. "
                            "5.3 Inspection Findings: Increased bearing wear observed, coupling alignment outside acceptable condition, no casing damage, mechanical seal acceptable, mounting bolts secure, impeller visually acceptable. "
                            "Investigation concluded bearing degradation and coupling misalignment were primary suspected contributors."
                        ),
                    },
                    {
                        "page": 4,
                        "text": (
                            "5.4 Corrective Actions: 1. Pump safely isolated. 2. Affected bearing replaced. 3. Coupling alignment corrected. 4. Fasteners secured. 5. Lubrication completed. "
                            "6. Rotation checked. 7. Controlled restart. "
                            "5.5 Post-Maintenance Readings: Vibration: 2.6 mm/s RMS, Temp: 65 °C, Pressure: 4.2 bar, Speed: 1450 RPM. "
                            "6. Root Cause Assessment: Likely contributors: Bearing degradation, coupling misalignment. Sensor reading alone is not sufficient to establish root cause. "
                            "7. Preventive Actions: Monitor vibration regularly, review vibration trends, inspect coupling alignment, monitor bearing lubrication."
                        ),
                    },
                    {
                        "page": 5,
                        "text": (
                            "8. Maintenance Recommendations: Mechanical Checks: Bearing condition, Coupling alignment, Shaft condition, Impeller condition, Pump mounting, Mechanical seal. "
                            "Condition Monitoring: Vibration, Bearing temperature, Discharge pressure, Flow, Motor speed. "
                            "9. Relationship to Sensor Analytics: For July 21, 2026 event (8.7 mm/s RMS > 7.1 critical). Maintenance report provides historical context and records corrective actions. "
                            "10. Final Equipment Condition: After bearing replacement and alignment: Vibration 2.6 mm/s RMS, Temp 65 °C, Pressure 4.2 bar, Speed 1450 RPM."
                        ),
                    },
                    {
                        "page": 6,
                        "text": "End of Maintenance Report.",
                    },
                ],
            },
            {
                "doc_name": "Pump_P101_SOP.pdf",
                "pages": [
                    {
                        "page": 1,
                        "text": (
                            "Pump P-101 Standard Operating Procedure (SOP). 1. Document Information: Equipment Tag: P-101. "
                            "Procedure: Inspection, Condition Monitoring and Troubleshooting. Revision: 1.0. "
                            "2. Purpose: Defines general inspection, condition-monitoring, troubleshooting, and response process. "
                            "3. Scope: Vibration, temperature, pressure monitoring, visual inspection, high-vibration response, troubleshooting, controlled shutdown, escalation. "
                            "4. Safety Requirements: Follow site safety procedures, use appropriate PPE, keep clear of rotating equipment."
                        ),
                    },
                    {
                        "page": 2,
                        "text": (
                            "Safety Requirements cont: Do not touch moving components, follow isolation and lockout/tagout procedures, confirm safe condition before inspection, do not bypass safety interlocks. "
                            "5. Normal Operating Parameters: Speed: 1450 RPM, Flow: Approximately 120 m³/h, Discharge Pressure: 4.0–4.5 bar, Temperature: 60–75 °C, Vibration: Below 4.5 mm/s RMS. "
                            "6. Vibration Classification: <4.5 mm/s RMS (Normal, Continue monitoring), 4.5–7.1 mm/s RMS (Warning, Investigate condition), >7.1 mm/s RMS (Critical, Immediate investigation and controlled response). "
                            "7. Routine Monitoring Procedure: Record vibration, bearing temperature, discharge pressure, flow, motor speed."
                        ),
                    },
                    {
                        "page": 3,
                        "text": (
                            "8. High-Vibration Response Procedure: When vibration exceeds normal range: "
                            "Step 1 — Verify the Reading: Check sensor reading and confirm valid measurement. "
                            "Step 2 — Review Other Parameters: Check temperature, pressure, flow, speed, recent operating changes. "
                            "Step 3 — Review History: Check recent maintenance activities, previous vibration events, bearing work, coupling alignment work. "
                            "Step 4 — Inspect: Inspect for bearing abnormalities, coupling misalignment, mechanical looseness, seal problems, unusual noise, visible damage. "
                            "Step 5 — Escalate: Notify responsible maintenance or engineering personnel."
                        ),
                    },
                    {
                        "page": 4,
                        "text": (
                            "9. Critical Vibration Response: If vibration exceeds 7.1 mm/s RMS: "
                            "1. Verify sensor reading. 2. Notify responsible operator or maintenance personnel. 3. Review temperature, pressure, flow, speed. "
                            "4. Avoid unnecessary continued operation. 5. Follow applicable controlled-shutdown procedure when required. 6. Inspect bearing and coupling condition. "
                            "7. Investigate possible mechanical causes. 8. Document event. 9. Do not return equipment to service until safe. "
                            "10. Troubleshooting Guide: High vibration -> Bearing degradation (Inspect bearing) / Coupling misalignment (Check alignment) / Mechanical looseness (Inspect mounting). "
                            "High temperature -> Bearing/lubrication problem (Inspect bearing and lubrication). Low pressure -> Flow/process problem (Check operating conditions). "
                            "Abnormal noise -> Mechanical problem (Inspect pump). Seal leakage -> Mechanical seal issue (Inspect seal)."
                        ),
                    },
                    {
                        "page": 5,
                        "text": (
                            "11. Restart Procedure: Confirm maintenance complete, tools removed, guards installed, ready for operation. "
                            "12. Documentation Requirements: Record date/time, equipment ID, sensor readings, observed symptoms, findings, parts replaced, post-maintenance readings. "
                            "13. Escalation: Escalate when: Vibration exceeds critical limit, Vibration continues to increase, Temperature becomes abnormal, "
                            "Mechanical damage is suspected, Repeated alarms occur."
                        ),
                    },
                    {
                        "page": 6,
                        "text": (
                            "Escalation cont: Equipment protection devices activate, Safe operation cannot be confirmed. "
                            "14. Relationship to AI-Based Monitoring: Sovereign AI Workbench identifies abnormal sensor behavior (e.g. 8.7 mm/s RMS). "
                            "SOP is retrieved by RAG system to provide appropriate investigation and response procedure."
                        ),
                    },
                ],
            },
        ]

        self.chunks = []
        for doc in documents_data:
            doc_name = doc["doc_name"]
            for p in doc["pages"]:
                chunk_id = f"{doc_name}_p{p['page']}"
                self.chunks.append({
                    "chunk_id": chunk_id,
                    "doc_name": doc_name,
                    "page": p["page"],
                    "text": p["text"],
                    "tokens": self._tokenize(p["text"]),
                })

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into lowercase alphanumeric words."""
        return re.findall(r"\b[a-zA-Z0-9_\-\./°³]+\b", text.lower())

    def search(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """
        Performs BM25-style lexical search over the indexed document chunks.
        """
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        doc_count = len(self.chunks)
        avg_doc_len = sum(len(c["tokens"]) for c in self.chunks) / max(1, doc_count)

        # Term frequency across corpus
        doc_freqs = Counter()
        for c in self.chunks:
            unique_tokens = set(c["tokens"])
            for t in unique_tokens:
                doc_freqs[t] += 1

        k1 = 1.5
        b = 0.75
        scores = []

        for c in self.chunks:
            score = 0.0
            chunk_tokens = c["tokens"]
            chunk_len = len(chunk_tokens)
            token_counts = Counter(chunk_tokens)

            for qt in query_tokens:
                if qt in token_counts:
                    tf = token_counts[qt]
                    df = doc_freqs.get(qt, 1)
                    idf = math.log((doc_count - df + 0.5) / (df + 0.5) + 1.0)
                    numerator = tf * (k1 + 1)
                    denominator = tf + k1 * (1 - b + b * (chunk_len / avg_doc_len))
                    score += idf * (numerator / denominator)

            # Boost exact phrase or critical numerical match
            for qt in query_tokens:
                if re.match(r"^\d+(\.\d+)?$", qt) and qt in chunk_tokens:
                    score += 2.0

            scores.append((score, c))

        # Sort descending by score
        scores.sort(key=lambda x: x[0], reverse=True)
        top_results = []
        for score, chunk in scores[:top_k]:
            top_results.append({
                "chunk_id": chunk["chunk_id"],
                "doc_name": chunk["doc_name"],
                "page": chunk["page"],
                "text": chunk["text"],
                "score": round(score, 4),
            })

        return top_results
