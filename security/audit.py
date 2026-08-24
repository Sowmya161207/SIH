"""Security & Sovereignty Audit Logging Engine.

Tracks:
- Model selected
- Tool executed
- Document processed
- File generated
- External connection attempts

Zero sensitive document content is logged to prevent data leakage in audit records.
"""

import json
import os
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from .schemas import AuditEvent, AuditEventType


class AuditLogger:
    """Structured audit logger with in-memory buffer and on-disk append-only log."""

    def __init__(self, log_dir: Optional[str] = None):
        if not log_dir:
            log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, "sovereignty_audit.log")
        self._events: List[AuditEvent] = []
        self._max_in_memory_events = 200

    def log_event(
        self,
        event_type: AuditEventType,
        action: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: str = "INFO",
        blocked: bool = False,
        actor: str = "system"
    ) -> AuditEvent:
        """
        Record a structured audit event. Sanitizes any raw document text or sensitive data.
        """
        clean_details = self._sanitize_details(details or {})

        event = AuditEvent(
            event_id=f"AUDIT-{uuid.uuid4().hex[:8].upper()}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type=event_type,
            actor=actor,
            action=action,
            resource_id=resource_id,
            details=clean_details,
            severity=severity,
            blocked=blocked
        )

        self._events.append(event)
        if len(self._events) > self._max_in_memory_events:
            self._events.pop(0)

        # Append to disk
        self._write_to_disk(event)
        return event

    def _sanitize_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Strip sensitive document contents or prompt bodies, retaining only metadata."""
        sanitized = {}
        sensitive_keys = {"text", "prompt", "content", "document_text", "raw_content", "body", "secret", "token", "password"}

        for k, v in details.items():
            if k.lower() in sensitive_keys:
                sanitized[f"{k}_length"] = len(str(v))
                sanitized[f"{k}_preview"] = f"{str(v)[:30]}... [REDACTED_FOR_AUDIT]"
            elif isinstance(v, dict):
                sanitized[k] = self._sanitize_details(v)
            else:
                sanitized[k] = v
        return sanitized

    def _write_to_disk(self, event: AuditEvent) -> None:
        """Append audit line in JSON Lines format."""
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event.to_dict()) + "\n")
        except Exception:
            pass

    def get_recent_events(self, limit: int = 50, event_type: Optional[AuditEventType] = None) -> List[AuditEvent]:
        """Retrieve recent audit events for UI dashboard display."""
        filtered = self._events
        if event_type:
            filtered = [e for e in filtered if e.event_type == event_type]
        return filtered[-limit:]

    # Convenience Loggers
    def log_model_selected(self, model_name: str, provider: str = "Local Ollama", parameters: Optional[Dict[str, Any]] = None) -> AuditEvent:
        return self.log_event(
            event_type=AuditEventType.MODEL_SELECTED,
            action=f"Selected local AI model '{model_name}'",
            resource_id=model_name,
            details={"provider": provider, "parameters": parameters or {}},
            severity="INFO"
        )

    def log_tool_executed(self, tool_name: str, execution_time_ms: float, caller: str = "assistant") -> AuditEvent:
        return self.log_event(
            event_type=AuditEventType.TOOL_EXECUTED,
            action=f"Executed tool '{tool_name}'",
            resource_id=tool_name,
            details={"execution_time_ms": round(execution_time_ms, 2), "caller": caller},
            severity="INFO"
        )

    def log_document_processed(self, document_id: str, filename: str, pages_count: int, file_size_bytes: int) -> AuditEvent:
        return self.log_event(
            event_type=AuditEventType.DOCUMENT_PROCESSED,
            action=f"Processed on-premise document '{filename}'",
            resource_id=document_id,
            details={"filename": filename, "pages_count": pages_count, "size_bytes": file_size_bytes},
            severity="INFO"
        )

    def log_file_generated(self, filename: str, file_path: str, size_bytes: int, purpose: str = "Report") -> AuditEvent:
        return self.log_event(
            event_type=AuditEventType.FILE_GENERATED,
            action=f"Generated local file '{filename}'",
            resource_id=filename,
            details={"path": file_path, "size_bytes": size_bytes, "purpose": purpose},
            severity="INFO"
        )

    def log_external_connection_attempt(self, target_url: str, blocked: bool = True, caller: str = "unknown", reason: str = "") -> AuditEvent:
        return self.log_event(
            event_type=AuditEventType.EXTERNAL_CONNECTION_ATTEMPT,
            action=f"External connection attempt to '{target_url}' (Blocked: {blocked})",
            resource_id=target_url,
            details={"target_url": target_url, "reason": reason, "caller": caller},
            severity="SECURITY_ALERT" if blocked else "WARNING",
            blocked=blocked
        )
