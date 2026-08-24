"""Sovereignty Monitor & Security Dashboard Controller.

Provides:
- security_monitor.get_status()
- security_monitor.log_event()
- security_monitor.verify_destination_or_block()
- security_monitor.get_ui_summary()
"""

from typing import Dict, Any, List, Optional, Union

from .schemas import (
    SovereigntyStatus,
    DeploymentMode,
    SecurityStatus,
    AuditEventType,
    AuditEvent,
)
from .firewall import DataLeakageFirewall
from .audit import AuditLogger


class SovereigntyMonitor:
    """Central Controller for Air-Gapped Sovereign Enforcement & Monitoring."""

    def __init__(self, firewall: Optional[DataLeakageFirewall] = None, audit_logger: Optional[AuditLogger] = None):
        self.firewall = firewall or DataLeakageFirewall()
        self.audit_logger = audit_logger or AuditLogger()
        self.external_calls_count: int = 0
        self.blocked_external_calls_count: int = 0
        self.deployment_mode = DeploymentMode.LOCAL_AIR_GAPPED
        self._local_models: List[str] = [
            "llama3-8b-instruct (Local Ollama @ localhost:11434)",
            "mistral-7b-instruct (Local vLLM @ localhost:8000)",
            "nomic-embed-text (Local On-Prem Embedder)"
        ]

    def get_status(self) -> Dict[str, Any]:
        """
        Primary interface required by Backend (Sharun) and Frontend (Tharun).
        Returns the exact sovereign status payload.
        """
        # Determine security status
        if self.external_calls_count > 0:
            current_sec_status = SecurityStatus.WARNING
            data_leaving = "Warning: External traffic detected"
        elif self.blocked_external_calls_count > 0:
            current_sec_status = SecurityStatus.ALERT_BLOCKED_EXTERNAL_CALL
            data_leaving = "None (Blocked by Firewall)"
        else:
            current_sec_status = SecurityStatus.SECURE
            data_leaving = "None"

        status = SovereigntyStatus(
            deployment_mode=self.deployment_mode,
            external_calls=self.external_calls_count,
            local_models=self._local_models,
            local_vector_db=True,
            internet_required=False,
            security_status=current_sec_status,
            data_leaving_system=data_leaving,
            firewall_active=True,
            blocked_attempts=self.blocked_external_calls_count
        )
        return status.to_dict()

    def log_event(
        self,
        event_type: Union[AuditEventType, str],
        action: str = "",
        details: Optional[Dict[str, Any]] = None,
        severity: str = "INFO",
        resource_id: Optional[str] = None
    ) -> AuditEvent:
        """
        Record a security or operational event to the audit log.
        """
        if isinstance(event_type, str):
            try:
                event_type_enum = AuditEventType(event_type)
            except ValueError:
                event_type_enum = AuditEventType.SYSTEM_EVENT
        else:
            event_type_enum = event_type

        return self.audit_logger.log_event(
            event_type=event_type_enum,
            action=action or f"Event: {event_type}",
            resource_id=resource_id,
            details=details or {},
            severity=severity
        )

    def verify_destination_or_block(self, target_url: str, caller: str = "system") -> bool:
        """
        Intercept and validate destination URL.
        If allowed: returns True.
        If blocked: increments blocked counter, records security alert in audit log, and returns False.
        """
        is_allowed, reason = self.firewall.validate_destination(target_url)

        if not is_allowed:
            self.blocked_external_calls_count += 1
            self.audit_logger.log_external_connection_attempt(
                target_url=target_url,
                blocked=True,
                caller=caller,
                reason=reason
            )
            return False

        return True

    def get_ui_summary(self) -> Dict[str, str]:
        """
        Formatted summary for Tharun's Frontend Top Navigation Status Bar:
        🟢 Local Mode
        External Calls: 0
        Data Leaving System: None
        """
        return {
            "mode_badge": "🟢 Local Mode",
            "mode_text": "[LOCAL AIR-GAPPED MODE]",
            "external_calls": f"External Calls: {self.external_calls_count}",
            "data_leaving_system": f"Data Leaving System: {'None' if self.external_calls_count == 0 else 'ALERT'}",
            "security_status": "SECURE" if self.external_calls_count == 0 else "WARNING"
        }

    def get_audit_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve recent sanitized audit logs."""
        events = self.audit_logger.get_recent_events(limit=limit)
        return [e.to_dict() for e in events]


# Global singleton instance
security_monitor = SovereigntyMonitor()
