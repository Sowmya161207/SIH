"""Schemas for Sovereignty Monitoring, Data-Leakage Firewall, and Security Auditing.

MRPL Sovereign On-Premise AI Workbench (SIH26117).
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timezone


class DeploymentMode(str, Enum):
    LOCAL_AIR_GAPPED = "LOCAL_AIR_GAPPED"
    LOCAL_ON_PREM = "LOCAL_ON_PREM"
    RESTRICTED_INTRANET = "RESTRICTED_INTRANET"

    def __str__(self) -> str:
        return self.value


class SecurityStatus(str, Enum):
    SECURE = "SECURE"
    WARNING = "WARNING"
    ALERT_BLOCKED_EXTERNAL_CALL = "ALERT_BLOCKED_EXTERNAL_CALL"

    def __str__(self) -> str:
        return self.value


class AuditEventType(str, Enum):
    MODEL_SELECTED = "MODEL_SELECTED"
    TOOL_EXECUTED = "TOOL_EXECUTED"
    DOCUMENT_PROCESSED = "DOCUMENT_PROCESSED"
    FILE_GENERATED = "FILE_GENERATED"
    EXTERNAL_CONNECTION_ATTEMPT = "EXTERNAL_CONNECTION_ATTEMPT"
    SYSTEM_EVENT = "SYSTEM_EVENT"

    def __str__(self) -> str:
        return self.value


@dataclass
class AuditEvent:
    event_id: str
    timestamp: str
    event_type: Union[AuditEventType, str]
    actor: str = "system"
    action: str = ""
    resource_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    severity: str = "INFO"               # INFO, WARNING, SECURITY_ALERT, ERROR
    blocked: bool = False

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["event_type"] = str(self.event_type)
        return d


@dataclass
class SovereigntyStatus:
    deployment_mode: Union[DeploymentMode, str] = DeploymentMode.LOCAL_AIR_GAPPED
    external_calls: int = 0
    local_models: List[str] = field(default_factory=lambda: [
        "llama3-8b-instruct (Local Ollama @ localhost:11434)",
        "mistral-7b-instruct (Local vLLM @ localhost:8000)",
        "nomic-embed-text (Local On-Prem Embedder)"
    ])
    local_vector_db: bool = True
    internet_required: bool = False
    security_status: Union[SecurityStatus, str] = SecurityStatus.SECURE
    data_leaving_system: str = "None"
    firewall_active: bool = True
    blocked_attempts: int = 0
    active_local_endpoints: List[str] = field(default_factory=lambda: [
        "http://localhost:8000 (Backend API)",
        "http://localhost:5173 (Frontend UI)",
        "http://localhost:11434 (Local Model Runtime)",
        "http://127.0.0.1:6333 (Local Vector DB)"
    ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "deployment_mode": str(self.deployment_mode),
            "external_calls": self.external_calls,
            "local_models": self.local_models,
            "local_vector_db": self.local_vector_db,
            "internet_required": self.internet_required,
            "security_status": str(self.security_status),
            "data_leaving_system": self.data_leaving_system,
            "firewall_active": self.firewall_active,
            "blocked_attempts": self.blocked_attempts,
            "active_local_endpoints": self.active_local_endpoints,
        }
