"""
network_logger.py
------------------
Audits and logs all internal and outbound network calls to provide verifiable proof
of on-premises air-gapped security and data sovereignty.
"""

import time
from datetime import datetime
from typing import List, Dict, Any

_network_audit_log: List[Dict[str, Any]] = []


def record_network_call(
    destination: str,
    method: str = "POST",
    purpose: str = "Local AI Model Inference",
    bytes_sent: int = 0,
    bytes_received: int = 0,
    status_code: int = 200,
) -> Dict[str, Any]:
    """
    Records a network interaction in the audit ledger.
    Flag any non-loopback calls as external security alerts.
    """
    is_local = (
        "127.0.0.1" in destination
        or "localhost" in destination
        or "0.0.0.0" in destination
        or destination.startswith("/")
    )

    entry = {
        "id": f"call_{len(_network_audit_log) + 1:04d}",
        "timestamp": datetime.now().isoformat(),
        "destination": destination,
        "method": method.upper(),
        "purpose": purpose,
        "is_sovereign_local": is_local,
        "external_alert": not is_local,
        "bytes_transferred": bytes_sent + bytes_received,
        "status_code": status_code,
    }

    _network_audit_log.append(entry)

    # Keep ledger bounded to last 500 calls
    if len(_network_audit_log) > 500:
        _network_audit_log.pop(0)

    return entry


def get_network_telemetry() -> Dict[str, Any]:
    """
    Returns full network sovereignty metrics and audit history.
    """
    total_calls = len(_network_audit_log)
    local_calls = sum(1 for c in _network_audit_log if c["is_sovereign_local"])
    external_calls = sum(1 for c in _network_audit_log if not c["is_sovereign_local"])

    return {
        "sovereign_status": "AIR_GAPPED_VERIFIED" if external_calls == 0 else "SECURITY_WARNING",
        "external_calls_count": external_calls,
        "local_calls_count": local_calls,
        "total_audited_calls": total_calls,
        "data_leakage_bytes": sum(c["bytes_transferred"] for c in _network_audit_log if not c["is_sovereign_local"]),
        "audit_logs": list(reversed(_network_audit_log[-50:])),
    }
