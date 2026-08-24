# -*- coding: utf-8 -*-
"""
generate_demo_docs.py
---------------------
Generates four realistic industrial PDF documents for the MRPL RAG demo.

Documents
---------
1. maintenance_report_p101.pdf  — Pump P-101 maintenance report (Q2 2025)
2. equipment_manual_p101.pdf    — Pump P-101 equipment manual
3. sop_pump_maintenance.pdf     — Standard operating procedure for pump maintenance
4. incident_report_p101.pdf     — Historical incident report (bearing failure, 2024)

Run
---
    python data/demo/generate_demo_docs.py

Output
------
    data/demo/*.pdf   (4 files)

Dependencies
------------
    pip install reportlab
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make sure we can import this script standalone
_DEMO_DIR = Path(__file__).parent
_RAG_ROOT = _DEMO_DIR.parent.parent
sys.path.insert(0, str(_RAG_ROOT))

import io
# Force UTF-8 output on Windows terminals
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    )
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
except ImportError:
    print("ERROR: reportlab not installed. Run:  pip install reportlab")
    sys.exit(1)


# ─── Shared styles ─────────────────────────────────────────────────────────────

def _styles():
    base = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DocTitle",
        parent=base["Title"],
        fontSize=16,
        spaceAfter=12,
        alignment=TA_CENTER,
    )
    heading1 = ParagraphStyle(
        "H1",
        parent=base["Heading1"],
        fontSize=13,
        spaceBefore=14,
        spaceAfter=6,
    )
    heading2 = ParagraphStyle(
        "H2",
        parent=base["Heading2"],
        fontSize=11,
        spaceBefore=10,
        spaceAfter=4,
    )
    body = ParagraphStyle(
        "Body",
        parent=base["Normal"],
        fontSize=10,
        leading=14,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
    )
    return title_style, heading1, heading2, body


def _build_pdf(filepath: Path, story: list) -> None:
    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    doc.build(story)
    print("  [OK] Generated: {}".format(filepath.name))


# ══════════════════════════════════════════════════════════════════════════════
# Document 1 — Maintenance Report
# ══════════════════════════════════════════════════════════════════════════════

def gen_maintenance_report(out_dir: Path) -> None:
    ts, h1, h2, body = _styles()
    story = []

    story.append(Paragraph("MRPL — Mangalore Refinery and Petrochemicals Ltd.", ts))
    story.append(Paragraph("PUMP P-101 MAINTENANCE REPORT — Q2 2025", ts))
    story.append(Spacer(1, 0.4 * cm))

    meta_data = [
        ["Equipment ID:", "Pump P-101"],
        ["Equipment Name:", "Crude Oil Feed Pump — Unit 3"],
        ["Location:", "Process Area 3, Block B"],
        ["Report Date:", "15-June-2025"],
        ["Prepared By:", "Rajan K., Senior Maintenance Engineer"],
        ["Approved By:", "Suresh N., Maintenance Manager"],
        ["Classification:", "Internal — Restricted"],
    ]
    t = Table(meta_data, colWidths=[5 * cm, 11 * cm])
    t.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F5F5F5")),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#F0F4FF")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.6 * cm))

    # Section 1 — Executive Summary
    story.append(Paragraph("1. Executive Summary", h1))
    story.append(Paragraph(
        "This report covers the quarterly preventive maintenance and inspection of Centrifugal Pump P-101 "
        "located in Process Area 3, Unit 3 of the MRPL refinery. The pump was taken offline on 10-June-2025 "
        "for scheduled maintenance. Inspection revealed significant wear on the mechanical seal and early-stage "
        "bearing degradation. Both components were replaced. The pump was returned to service on 13-June-2025 "
        "following successful commissioning tests.", body))

    # Section 2 — Equipment Specifications
    story.append(Paragraph("2. Equipment Specifications", h1))
    specs = [
        ["Parameter", "Value", "Unit"],
        ["Pump Type", "Centrifugal, Single-Stage", "—"],
        ["Manufacturer", "Grundfos / KSB", "—"],
        ["Model", "NK 100-250/260 A2-F-A-E-BQQE", "—"],
        ["Flow Rate (Design)", "320", "m³/h"],
        ["Head (Design)", "85", "m"],
        ["Speed", "1480", "RPM"],
        ["Motor Power", "110", "kW"],
        ["Operating Temp.", "65–85", "°C"],
        ["Fluid Handled", "Crude Oil (SG 0.87)", "—"],
        ["Suction Pressure", "1.2", "bar(g)"],
        ["Discharge Pressure", "9.8", "bar(g)"],
    ]
    t2 = Table(specs, colWidths=[7 * cm, 5 * cm, 4 * cm])
    t2.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A3A6B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EEF2FF")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t2)
    story.append(Spacer(1, 0.3 * cm))

    # Section 3 — Inspection Findings
    story.append(Paragraph("3. Inspection Findings", h1))
    story.append(Paragraph("3.1 Mechanical Seal", h2))
    story.append(Paragraph(
        "The mechanical seal (John Crane Type 1 equivalent, 50mm shaft) exhibited heavy scoring on the "
        "stationary face. Leakage was observed at approximately 12 drops per minute at the seal flush "
        "connection, significantly above the acceptable threshold of 3 drops per minute. The seal faces "
        "showed signs of dry-running, likely caused by intermittent loss of flush fluid pressure during "
        "the upstream vessel low-level event recorded on 02-April-2025.", body))

    story.append(Paragraph("3.2 Bearings — Drive End (DE)", h2))
    story.append(Paragraph(
        "De-Energy and Lock Out / Tag Out (LOTO) was applied per SOP-PM-007. Bearing SKF 6316 (DE) was "
        "inspected. Vibration readings taken prior to shutdown: radial 4.2 mm/s RMS at DE, 2.1 mm/s at NDE. "
        "ISO 10816-3 alarm threshold for this pump class is 4.5 mm/s; the DE reading was approaching alarm. "
        "Bearing disassembly revealed slight pitting on the outer race. Grease analysis indicated contamination "
        "with particulate matter consistent with seal material debris. Bearing replaced with OEM equivalent.", body))

    story.append(Paragraph("3.3 Bearings — Non-Drive End (NDE)", h2))
    story.append(Paragraph(
        "NDE bearing (SKF 6313) was within acceptable condition. Grease was refreshed. No replacement required.", body))

    story.append(Paragraph("3.4 Impeller", h2))
    story.append(Paragraph(
        "Impeller (316 SS, semi-open, 5-vane) was removed and inspected. Minor erosion pitting observed on "
        "leading edges — within acceptable wear limits. Impeller clearance reset to 0.3 mm per OEM specification. "
        "No replacement necessary at this interval.", body))

    story.append(Paragraph("3.5 Shaft Alignment", h2))
    story.append(Paragraph(
        "Post-reassembly laser alignment check performed using Pruftechnik Rotalign Ultra. Final alignment values: "
        "Angular offset 0.02 mm/100mm (limit 0.05), Parallel offset 0.03 mm (limit 0.10). Within tolerance.", body))

    story.append(PageBreak())

    # Section 4 — Temperature Readings
    story.append(Paragraph("4. Bearing Temperature History (Pre-Maintenance)", h1))
    story.append(Paragraph(
        "The following bearing temperatures were recorded via the plant DCS over the 90 days prior to "
        "this maintenance event. Elevated temperatures at the DE bearing were the primary trigger for "
        "scheduling maintenance ahead of the normal 6-month interval.", body))

    temp_data = [
        ["Date", "DE Bearing Temp (°C)", "NDE Bearing Temp (°C)", "Alarm Limit (°C)"],
        ["01-Mar-2025", "72", "68", "85"],
        ["15-Mar-2025", "74", "69", "85"],
        ["01-Apr-2025", "77", "70", "85"],
        ["15-Apr-2025", "79", "71", "85"],
        ["01-May-2025", "81", "70", "85"],
        ["15-May-2025", "84", "71", "85"],
        ["28-May-2025", "87 ⚠", "71", "85"],  # ALARM
        ["05-Jun-2025", "89 ⚠", "72", "85"],
        ["10-Jun-2025", "Shutdown", "Shutdown", "—"],
    ]
    t3 = Table(temp_data, colWidths=[4 * cm, 4.5 * cm, 4.5 * cm, 3 * cm])
    t3.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A3A6B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FFF8F0")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("TEXTCOLOR", (1, 7), (1, 8), colors.red),
        ("FONTNAME", (1, 7), (1, 8), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t3)
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(
        "⚠ Bearing temperature exceeded alarm setpoint (85°C) on 28-May-2025. Maintenance team was "
        "notified. Visual inspection on 29-May confirmed seal leakage. Decision taken to advance scheduled "
        "maintenance to 10-June-2025.", body))

    # Section 5 — Work Performed
    story.append(Paragraph("5. Work Performed", h1))
    work_items = [
        "• Complete pump disassembly per Equipment Manual EM-P101-2019, Section 7.",
        "• Mechanical seal replacement: John Crane Type 1, 50mm, Part No. JC-50-316-TC.",
        "• DE bearing replacement: SKF 6316/C3, lubricated with Shell Gadus S3 V220C grease.",
        "• NDE bearing grease refresh: Shell Gadus S3 V220C, 25g applied.",
        "• Impeller clearance reset to 0.3 mm (OEM specification).",
        "• Shaft run-out check: Max 0.025 mm TIR — within limit.",
        "• Casing wear ring clearance check: 0.45 mm — within acceptable limit.",
        "• Coupling element (Rexnord Thomas disc coupling) inspected — no replacement needed.",
        "• Complete reassembly with new gaskets and fastener re-torquing per EM-P101-2019, Table 9.",
        "• Laser alignment: Angular 0.02 mm/100mm, Parallel 0.03 mm — in tolerance.",
        "• Seal flush line flushed and pressure tested at 4 bar.",
        "• Pre-commissioning run (1 hour at 50% flow): Bearing temps DE 68°C, NDE 65°C — acceptable.",
        "• Full flow commissioning (2 hours): DE 71°C, NDE 67°C — stable.",
    ]
    for item in work_items:
        story.append(Paragraph(item, body))

    # Section 6 — Recommendations
    story.append(Paragraph("6. Recommendations", h1))
    story.append(Paragraph(
        "1. Investigate the root cause of the upstream vessel low-level event (02-April-2025) that caused "
        "seal dry-running. Implement a low-level interlock on the seal flush supply vessel.", body))
    story.append(Paragraph(
        "2. Reduce bearing temperature alarm setpoint from 85°C to 80°C for Pump P-101 given the observed "
        "trend of accelerated bearing degradation.", body))
    story.append(Paragraph(
        "3. Increase maintenance frequency from 6-monthly to quarterly for P-101 until root cause of "
        "seal and bearing degradation is fully resolved.", body))
    story.append(Paragraph(
        "4. Consider installing online vibration monitoring (accelerometer) on P-101 DE bearing to enable "
        "continuous trending without manual readings.", body))

    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(
        "Report prepared in compliance with MRPL Maintenance Procedure MP-001 Rev.4 and "
        "ISO 17359 (Condition Monitoring). All work performed under PTW No. PTW-2025-0614-003.", body))

    _build_pdf(out_dir / "maintenance_report_p101.pdf", story)


# ══════════════════════════════════════════════════════════════════════════════
# Document 2 — Equipment Manual
# ══════════════════════════════════════════════════════════════════════════════

def gen_equipment_manual(out_dir: Path) -> None:
    ts, h1, h2, body = _styles()
    story = []

    story.append(Paragraph("MRPL — Equipment Manual", ts))
    story.append(Paragraph("PUMP P-101: CRUDE OIL FEED PUMP", ts))
    story.append(Paragraph("Document No: EM-P101-2019 | Rev. 3 | June 2019", ts))
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("CHAPTER 1 — INTRODUCTION AND SAFETY", h1))
    story.append(Paragraph("1.1 Scope", h2))
    story.append(Paragraph(
        "This manual covers installation, operation, maintenance, and troubleshooting of Centrifugal Pump P-101 "
        "installed at MRPL Process Area 3, Unit 3. The pump is a single-stage, end-suction centrifugal type "
        "handling crude oil service at operating temperatures up to 90°C and pressures up to 10 bar(g).", body))

    story.append(Paragraph("1.2 Safety Warnings", h2))
    story.append(Paragraph(
        "WARNING: Never operate the pump against a closed discharge valve. Cavitation and bearing failure "
        "will result within 2 minutes. Minimum flow protection must be maintained at all times. "
        "Minimum continuous flow: 80 m³/h.", body))
    story.append(Paragraph(
        "WARNING: Do not exceed bearing temperature alarm setpoint of 85°C. If bearing temperature exceeds "
        "85°C, initiate controlled shutdown per SOP-PM-007 Section 4.3 and notify the maintenance team "
        "immediately.", body))
    story.append(Paragraph(
        "CAUTION: Seal flush supply must be maintained at all times when pump is rotating. Loss of seal flush "
        "for more than 30 seconds will result in mechanical seal dry-running and premature failure.", body))

    story.append(Paragraph("CHAPTER 2 — TECHNICAL SPECIFICATIONS", h1))
    story.append(Paragraph("2.1 Performance Data", h2))
    story.append(Paragraph(
        "Design point: 320 m³/h at 85 m head. Best efficiency point (BEP): 340 m³/h at 83 m. "
        "Specific speed Ns = 1850 rpm(m³/s). NPSH required at design flow: 4.2 m. "
        "Pump efficiency at BEP: 79.5%.", body))

    story.append(Paragraph("2.2 Mechanical Seal Specification", h2))
    story.append(Paragraph(
        "Seal type: Single mechanical seal, balanced. Shaft diameter: 50 mm. Seal face materials: "
        "Silicon carbide (rotating) / Silicon carbide (stationary). Secondary seal: Viton O-rings. "
        "Flush arrangement: API Plan 11 (discharge recirculation). Flush flow rate: 3–5 L/min. "
        "Flush pressure: Suction + 1.5 bar minimum.", body))

    story.append(Paragraph("2.3 Bearing Specification", h2))
    story.append(Paragraph(
        "Drive End (DE): SKF 6316/C3, single row deep groove ball bearing. "
        "Non-Drive End (NDE): SKF 6313/C3, single row deep groove ball bearing. "
        "Lubrication: Grease — Shell Gadus S3 V220C. Regreasing interval: 2000 operating hours or "
        "6 months, whichever is earlier. Grease quantity per regreasing: DE 25g, NDE 15g. "
        "Maximum bearing temperature: 85°C (alarm), 95°C (trip).", body))

    story.append(Paragraph("CHAPTER 3 — OPERATION", h1))
    story.append(Paragraph("3.1 Starting Procedure", h2))
    story.append(Paragraph(
        "Step 1: Confirm all isolation valves open. Step 2: Prime pump casing — open vent valve V-101A "
        "until clear liquid flows without air bubbles. Step 3: Confirm seal flush flow (rotameter FR-101 "
        "reading 3–5 L/min). Step 4: Close vent valve. Step 5: Start motor via DCS or local panel. "
        "Step 6: Slowly open discharge control valve FCV-101 to bring flow to operating point. "
        "Step 7: Verify discharge pressure PI-101 reads 9.5–10.0 bar(g). Step 8: Check bearing "
        "temperatures after 30 minutes — must be below 75°C at steady state.", body))

    story.append(Paragraph("3.2 Normal Shutdown", h2))
    story.append(Paragraph(
        "Step 1: Ramp down flow gradually using FCV-101. Step 2: When flow reaches minimum (80 m³/h), "
        "stop motor. Step 3: Close suction isolation valve after motor stops. Step 4: Close discharge "
        "valve. Step 5: Seal flush may remain running for 10 minutes after shutdown to cool seal faces.", body))

    story.append(Paragraph("3.3 Emergency Shutdown", h2))
    story.append(Paragraph(
        "Activate ESD button PB-101-ESD or DCS ESD command. The pump motor will trip and the discharge "
        "valve will close automatically. Do NOT restart without maintenance inspection if shutdown was "
        "caused by bearing temperature trip or mechanical seal failure alarm.", body))

    story.append(PageBreak())

    story.append(Paragraph("CHAPTER 4 — TROUBLESHOOTING", h1))
    trouble_data = [
        ["Symptom", "Probable Cause", "Corrective Action"],
        ["Bearing temperature > 85°C",
         "Insufficient lubrication; bearing failure; misalignment; overload",
         "Check grease; measure vibration; check alignment; reduce flow"],
        ["High vibration (>4.5 mm/s RMS)",
         "Bearing wear; cavitation; imbalance; misalignment",
         "Check NPSH; inspect bearings; re-balance impeller; realign"],
        ["Mechanical seal leaking",
         "Seal face wear; dry-running; spring failure; contamination",
         "Inspect seal faces; verify flush supply; replace seal"],
        ["Low flow / low head",
         "Worn impeller; wrong rotation; air entrainment; blocked suction",
         "Inspect impeller; check rotation direction; prime pump"],
        ["Noisy operation / cavitation",
         "Low suction head; high fluid temperature; cavitation",
         "Check NPSH available; reduce flow; inspect suction line"],
        ["Motor overloading",
         "Fluid density too high; overspeeding; mechanical seizure",
         "Check fluid SG; measure power; inspect rotating parts"],
    ]
    t4 = Table(trouble_data, colWidths=[4.5 * cm, 5 * cm, 6.5 * cm])
    t4.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A3A6B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EEF2FF")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t4)

    story.append(Paragraph("CHAPTER 5 — MAINTENANCE SCHEDULE", h1))
    maint_data = [
        ["Task", "Frequency", "Reference"],
        ["Visual inspection — leaks, vibration, noise", "Daily", "SOP-PM-007 §2"],
        ["Bearing temperature check", "Daily (DCS)", "SOP-PM-007 §2"],
        ["Seal flush flow check", "Weekly", "SOP-PM-007 §2"],
        ["Vibration measurement (handheld)", "Monthly", "SOP-PM-007 §3"],
        ["Bearing regreasing", "6-monthly or 2000h", "SOP-PM-007 §5"],
        ["Mechanical seal inspection", "Annually or on alarm", "EM-P101-2019 §7"],
        ["Full overhaul (bearings, seal, impeller clearance)", "3-yearly or on alarm", "EM-P101-2019 §7"],
        ["Pressure test and hydrostatic check", "3-yearly", "EM-P101-2019 §8"],
    ]
    t5 = Table(maint_data, colWidths=[8 * cm, 4 * cm, 4 * cm])
    t5.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A3A6B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EEF2FF")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t5)

    _build_pdf(out_dir / "equipment_manual_p101.pdf", story)


# ══════════════════════════════════════════════════════════════════════════════
# Document 3 — SOP
# ══════════════════════════════════════════════════════════════════════════════

def gen_sop(out_dir: Path) -> None:
    ts, h1, h2, body = _styles()
    story = []

    story.append(Paragraph("MRPL — Standard Operating Procedure", ts))
    story.append(Paragraph("SOP-PM-007: CENTRIFUGAL PUMP MAINTENANCE", ts))
    story.append(Paragraph("Rev. 5 | Effective: 01-Jan-2025 | Area: Process Maintenance", ts))
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("1. PURPOSE", h1))
    story.append(Paragraph(
        "This SOP defines the standard steps for safe and effective preventive and corrective "
        "maintenance of centrifugal pumps across all process areas at MRPL. It applies to all "
        "maintenance engineers and technicians involved in pump maintenance activities.", body))

    story.append(Paragraph("2. SCOPE", h1))
    story.append(Paragraph(
        "Applicable to all centrifugal pumps in Process Areas 1–5, including Pump P-101, P-102, "
        "P-201, and P-301 series. For high-pressure pumps (>50 bar), refer to SOP-PM-012.", body))

    story.append(Paragraph("3. SAFETY REQUIREMENTS", h1))
    story.append(Paragraph("3.1 Personal Protective Equipment (PPE)", h2))
    story.append(Paragraph(
        "Mandatory PPE for all pump maintenance activities: Safety helmet, safety glasses (chemical-rated), "
        "chemical-resistant gloves (nitrile, min. 0.4mm), fire-retardant coverall, safety boots (steel toe, "
        "chemical resistant), face shield when working within 0.5m of flange connections.", body))

    story.append(Paragraph("3.2 Permit to Work", h2))
    story.append(Paragraph(
        "A valid Permit to Work (PTW) must be obtained before any work commences. PTW must specify: "
        "Equipment tag number, work scope, LOTO requirements, gas test requirements, and nearest "
        "fire point location. For hot work: additional Hot Work Permit (HWP) required.", body))

    story.append(Paragraph("3.3 Lock-Out / Tag-Out (LOTO)", h2))
    story.append(Paragraph(
        "LOTO procedure per MRPL-LOTO-001: (1) Notify control room. (2) Stop pump at DCS. "
        "(3) Open local isolator switch — lock with personal lock. (4) Isolate suction and discharge "
        "valves — apply blinds if required. (5) Isolate seal flush supply. (6) Depressurise casing — "
        "open drain valve D-101. (7) Verify zero energy state with multi-meter and pressure gauge. "
        "(8) Attach DANGER tag to isolator.", body))

    story.append(Paragraph("4. PREVENTIVE MAINTENANCE PROCEDURE", h1))
    story.append(Paragraph("4.1 Bearing Inspection and Regreasing", h2))
    story.append(Paragraph(
        "Step 1: Apply LOTO per Section 3.3. "
        "Step 2: Remove bearing housing covers. "
        "Step 3: Inspect bearing visually for pitting, spalling, discolouration. "
        "Step 4: Measure bearing radial play with feeler gauge — acceptable limit 0.02–0.05 mm. "
        "Step 5: Remove old grease completely using clean cloth and approved solvent. "
        "Step 6: Inspect bearing races for surface damage — replace if any pitting observed. "
        "Step 7: Apply fresh grease — Shell Gadus S3 V220C. Fill bearing housing 1/3 to 1/2 capacity. "
        "DO NOT over-grease — over-greasing causes bearing temperature rise. "
        "Step 8: Replace bearing housing covers — torque to 25 Nm. "
        "Step 9: Record in maintenance log: date, grease quantity, condition observations.", body))

    story.append(Paragraph("4.2 Mechanical Seal Inspection", h2))
    story.append(Paragraph(
        "Step 1: With LOTO applied, drain casing via drain valve D-101. "
        "Step 2: Remove coupling guard and flexible coupling element. "
        "Step 3: Remove gland plate bolts — note torque values for re-assembly. "
        "Step 4: Withdraw mechanical seal assembly carefully — do not scratch shaft. "
        "Step 5: Inspect seal faces under good lighting. Acceptable: fine lapping marks only. "
        "Reject if: Cracks, chips, heavy scoring, blistering, or erosion visible. "
        "Step 6: Inspect O-rings — replace if any deformation, cracking, or chemical attack. "
        "Step 7: Measure face wear — reject if face width reduced by >20% from new dimension. "
        "Step 8: Clean shaft sleeve and inspect for scoring — replace if deep scratches present. "
        "Step 9: Reassemble with new O-rings and spring — do not touch seal faces with bare hands. "
        "Step 10: Flush and pressure test seal system at 4 bar for 15 minutes before restart.", body))

    story.append(PageBreak())

    story.append(Paragraph("4.3 Response to Bearing Temperature Alarm (>85°C)", h2))
    story.append(Paragraph(
        "IMMEDIATE ACTIONS (within 5 minutes of alarm): "
        "(1) Notify Shift Supervisor and Control Room Operator. "
        "(2) Reduce pump flow by 20% to reduce load. "
        "(3) Check bearing temperature trend on DCS historian — is it rising or stable? "
        "(4) Dispatch technician for immediate on-site inspection.", body))
    story.append(Paragraph(
        "ON-SITE INSPECTION: "
        "(1) Touch-test bearing housing (with back of hand — do not burn yourself). "
        "(2) Listen for bearing noise (grinding, rumbling = bearing failure). "
        "(3) Check for visible grease leakage from bearing housing (over-temperature causes grease "
        "to liquefy and leak out). "
        "(4) Check seal flush rotameter FR-101 — must read 3–5 L/min.", body))
    story.append(Paragraph(
        "DECISION: If bearing temperature is above 85°C and rising, or any bearing noise is present: "
        "Initiate CONTROLLED SHUTDOWN per Section 3.2 and Section 3.3. "
        "Switch to standby pump P-101B immediately. "
        "Do NOT operate above 95°C — motor trip will activate automatically at 95°C.", body))

    story.append(Paragraph("5. POST-MAINTENANCE COMMISSIONING", h1))
    story.append(Paragraph(
        "After any maintenance activity, complete the following before returning to service: "
        "(1) Remove all LOTO devices — confirm with shift supervisor. "
        "(2) Check pump rotation direction (bump test): must be clockwise viewed from drive end. "
        "(3) Open suction valve fully, prime pump casing. "
        "(4) Start on minimum flow — confirm no unusual noise or vibration. "
        "(5) Monitor bearing temperatures for first 30 minutes — must stabilise below 75°C. "
        "(6) Confirm seal flush flow at FR-101: 3–5 L/min. "
        "(7) Complete maintenance close-out report and sign off PTW.", body))

    story.append(Paragraph("6. DOCUMENTATION", h1))
    story.append(Paragraph(
        "All maintenance activities must be recorded in the SAP PM system within 24 hours of completion. "
        "Required fields: Equipment tag, work order number, work performed (description), "
        "parts replaced (part numbers and quantities), next planned maintenance date, "
        "engineer signature and employee ID.", body))

    _build_pdf(out_dir / "sop_pump_maintenance.pdf", story)


# ══════════════════════════════════════════════════════════════════════════════
# Document 4 — Incident Report
# ══════════════════════════════════════════════════════════════════════════════

def gen_incident_report(out_dir: Path) -> None:
    ts, h1, h2, body = _styles()
    story = []

    story.append(Paragraph("MRPL — INCIDENT INVESTIGATION REPORT", ts))
    story.append(Paragraph("Confidential — Restricted Distribution", ts))
    story.append(Spacer(1, 0.3 * cm))

    meta_data = [
        ["Incident Ref:", "INC-2024-0312-P101"],
        ["Incident Date:", "12-March-2024, 14:35 hrs"],
        ["Location:", "Process Area 3, Pump Bay — P-101"],
        ["Incident Type:", "Equipment Failure — Bearing Failure with Secondary Fire Risk"],
        ["Severity:", "High — Production Impact + Potential Safety Risk"],
        ["Investigated By:", "Safety Officer — Priya M., Lead Investigator"],
        ["Report Date:", "25-March-2024"],
        ["Distribution:", "Maintenance Manager, Plant Manager, Safety Committee"],
    ]
    t = Table(meta_data, colWidths=[4 * cm, 12 * cm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF3F3")),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.HexColor("#FFF3F3"), colors.HexColor("#FFE8E8")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CC0000")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("1. INCIDENT DESCRIPTION", h1))
    story.append(Paragraph(
        "At approximately 14:35 hrs on 12-March-2024, Pump P-101 (Crude Oil Feed Pump, Process Area 3) "
        "suffered a catastrophic drive-end (DE) bearing failure. The bearing seizure caused the shaft to "
        "deflect, resulting in mechanical seal failure and subsequent crude oil release. The released crude "
        "oil contacted the hot bearing housing (surface temperature approximately 220°C at failure) and "
        "ignited, causing a small fire in the pump bay.", body))
    story.append(Paragraph(
        "The fire was contained within 3 minutes by the plant fire team using CO2 extinguishers. "
        "No personnel injuries were sustained. Estimated production loss: 8 hours (2,560 m³ crude throughput). "
        "Equipment damage: Pump P-101 required complete rebuild.", body))

    story.append(Paragraph("2. TIMELINE OF EVENTS", h1))
    timeline = [
        ["Time", "Event"],
        ["06:00, 12-Mar", "Shift handover — P-101 reported normal. DE bearing temp 82°C (DCS)."],
        ["09:15", "DE bearing temp alarm activated at 85°C. Control room acknowledged."],
        ["09:20", "Shift supervisor notified. Decision to monitor (no action taken per operator judgment)."],
        ["11:30", "Second bearing temp alarm — 88°C. Technician dispatched."],
        ["11:45", "Technician inspection: pump noisy but continuing to run. Decision to keep running until next shift."],
        ["13:00", "DE bearing temp reaches 95°C — DCS trip signal generated. Trip was bypassed by control room (INCORRECT ACTION)."],
        ["14:35", "Bearing seizure. Shaft deflection. Seal failure. Crude oil release. Fire ignition."],
        ["14:38", "Fire alarm activated. Fire team response. ESD initiated."],
        ["14:41", "Fire extinguished. Area evacuated and secured."],
    ]
    t2 = Table(timeline, colWidths=[4 * cm, 12 * cm])
    t2.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#8B0000")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FFF0F0")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TEXTCOLOR", (1, 7), (1, 7), colors.red),
        ("FONTNAME", (1, 7), (1, 7), "Helvetica-Bold"),
    ]))
    story.append(t2)

    story.append(Paragraph("3. ROOT CAUSE ANALYSIS", h1))
    story.append(Paragraph("3.1 Immediate Cause", h2))
    story.append(Paragraph(
        "Catastrophic failure of DE bearing SKF 6316 due to lubrication starvation and metal fatigue. "
        "Post-failure analysis of bearing debris confirmed: (a) Complete grease oxidation — grease had "
        "turned to dry carbon coke, providing no lubrication. (b) Severe spalling on outer race over "
        "approximately 60% of the bearing raceway. (c) Roller cage fracture due to metal fatigue.", body))

    story.append(Paragraph("3.2 Contributing Causes", h2))
    story.append(Paragraph(
        "(a) MISSED REGREASING: SAP PM records confirm that the last regreasing of P-101 DE bearing "
        "was performed 18 months before the incident — 12 months beyond the required 6-month interval. "
        "Work Order WO-2022-P101-REG was closed without execution due to plant outage scheduling conflict "
        "and was not rescheduled.", body))
    story.append(Paragraph(
        "(b) ALARM MANAGEMENT FAILURE: The 85°C bearing temperature alarm was acknowledged but not acted "
        "upon from 09:15 to 13:00 (3 hours 45 minutes). This is a violation of SOP-PM-007 Section 4.3 "
        "which requires controlled shutdown if bearing temperature is above 85°C and rising.", body))
    story.append(Paragraph(
        "(c) DCS TRIP BYPASS: At 13:00, the DCS high-high temperature trip (95°C) was bypassed by the "
        "control room operator without authorisation. This is a critical safety violation. The bypass "
        "removed the last automatic protective layer that would have prevented the bearing seizure.", body))

    story.append(Paragraph("3.3 Root Cause", h2))
    story.append(Paragraph(
        "Root cause: Inadequate Maintenance Management System. Specifically, the absence of a robust "
        "system to ensure overdue preventive maintenance is rescheduled and escalated when not completed "
        "on time. The missed regreasing was the primary initiating event.", body))

    story.append(PageBreak())

    story.append(Paragraph("4. CORRECTIVE AND PREVENTIVE ACTIONS (CAPA)", h1))
    capa = [
        ["#", "Action", "Responsible", "Due Date", "Status"],
        ["1", "Bearing regreasing overdue >30 days: mandatory escalation to Maintenance Manager.", "Maint. Mgr.", "01-Apr-2024", "CLOSED"],
        ["2", "DCS protection bypass: require dual authorisation (Shift Supervisor + Safety).", "Instrument Engr.", "15-Apr-2024", "CLOSED"],
        ["3", "Retrain all operators on SOP-PM-007 Section 4.3 alarm response.", "HSE Dept.", "30-Apr-2024", "CLOSED"],
        ["4", "Install continuous online vibration monitor on P-101 DE bearing.", "Project Engr.", "30-Jun-2024", "IN PROGRESS"],
        ["5", "Reduce bearing temperature alarm from 85°C to 80°C for P-101.", "Instrument Engr.", "01-Apr-2024", "CLOSED"],
        ["6", "Monthly audit of overdue PM work orders for critical rotating equipment.", "Maint. Mgr.", "Ongoing", "ACTIVE"],
    ]
    t3 = Table(capa, colWidths=[0.8 * cm, 7 * cm, 3 * cm, 2.5 * cm, 2.7 * cm])
    t3.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A3A6B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EEF2FF")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t3)

    story.append(Paragraph("5. LESSONS LEARNED", h1))
    story.append(Paragraph(
        "1. Never ignore a bearing temperature alarm on crude oil service pumps. The alarm-to-failure "
        "window can be as short as 5 hours when lubrication is severely degraded.", body))
    story.append(Paragraph(
        "2. DCS protective trips must never be bypassed without full safety review and dual authorisation. "
        "Protective systems are the last line of defence against catastrophic failure.", body))
    story.append(Paragraph(
        "3. Overdue preventive maintenance on critical equipment must trigger automatic escalation. "
        "Manual tracking is insufficient for high-consequence items.", body))
    story.append(Paragraph(
        "4. Lubrication starvation is the leading cause of bearing failure on centrifugal pumps "
        "in hydrocarbon service. Strict adherence to regreasing intervals is essential.", body))

    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(
        "This report is classified CONFIDENTIAL. Distribution restricted to Maintenance Manager, "
        "Plant Manager, Safety Committee, and Process Safety Engineer. Do not copy or distribute "
        "without written approval from the Plant Manager.", body))

    _build_pdf(out_dir / "incident_report_p101.pdf", story)


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

def main():
    out_dir = _DEMO_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Generating 4 MRPL demo PDFs -> {}".format(out_dir))
    print()
    gen_maintenance_report(out_dir)
    gen_equipment_manual(out_dir)
    gen_sop(out_dir)
    gen_incident_report(out_dir)
    print()
    print("All demo documents generated successfully.")
    print("Location: {}".format(out_dir))


if __name__ == "__main__":
    main()
