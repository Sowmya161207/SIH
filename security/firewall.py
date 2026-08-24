"""Data-Leakage Firewall & Outbound Traffic Interceptor.

Enforces strict Sovereign On-Premise boundary:
- Rejects all external cloud AI endpoints (OpenAI, Gemini/Google, Anthropic, Cohere, etc.)
- Allows only local and designated on-premise service endpoints (localhost, 127.0.0.1, internal Docker network)
- Logs and blocks all external connection attempts without leaking sensitive document content.
"""

import ipaddress
import re
import urllib.parse
from typing import Tuple, List, Set, Optional


# Known Cloud AI APIs to explicitly flag and block
KNOWN_CLOUD_AI_DOMAINS = {
    "api.openai.com",
    "generativelanguage.googleapis.com",
    "api.anthropic.com",
    "api.cohere.ai",
    "api.cohere.com",
    "api.mistral.ai",
    "api.together.xyz",
    "api.groq.com",
    "api.perplexity.ai",
    "api.deepseek.com",
    "huggingface.co",
    "api.replicate.com"
}

# Permitted local domains and hostnames
LOCAL_WHITELIST_HOSTS = {
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "::1",
    "host.docker.internal",
    "backend",
    "frontend",
    "ollama",
    "vllm",
    "qdrant",
    "chroma"
}


class DataLeakageFirewall:
    """
    Application-level Outbound Traffic Firewall.

    Note on Security Architecture:
    - Application-Level: This module intercepts, validates, and rejects non-local outbound API calls at runtime.
    - OS/Network-Level: For full physical air-gapping, Docker container network isolation (e.g. `internal: true`)
      or physical network cable disconnection/VLAN air-gapping is used in production at MRPL.
    """

    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
        self.blocked_attempts_count: int = 0
        self.allowed_local_hosts: Set[str] = set(LOCAL_WHITELIST_HOSTS)
        self.blocked_domains: Set[str] = set(KNOWN_CLOUD_AI_DOMAINS)

    def add_allowed_local_host(self, host: str) -> None:
        """Allow a specific local intranet host."""
        self.allowed_local_hosts.add(host.lower().strip())

    def is_local_ip(self, host: str) -> bool:
        """Check if an IP address belongs to RFC 1918 private / loopback ranges."""
        try:
            ip = ipaddress.ip_address(host)
            return ip.is_loopback or ip.is_private or ip.is_link_local
        except ValueError:
            return False

    def validate_destination(self, target: str) -> Tuple[bool, str]:
        """
        Validate whether a target URL or hostname is permitted under sovereign on-premise policy.

        :param target: URL or hostname (e.g., 'http://localhost:11434/api/generate' or 'api.openai.com')
        :return: (is_allowed: bool, reason: str)
        """
        # Parse URL or raw hostname
        if "://" in target:
            parsed = urllib.parse.urlparse(target)
            hostname = parsed.hostname or ""
            port = parsed.port
        else:
            # Strip port if present
            parts = target.split(":")
            hostname = parts[0]
            port = parts[1] if len(parts) > 1 else None

        hostname_clean = hostname.lower().strip()

        if not hostname_clean:
            return False, "Empty destination hostname."

        # 1. Check known cloud AI blacklist
        if hostname_clean in self.blocked_domains or any(hostname_clean.endswith("." + d) for d in self.blocked_domains):
            return False, f"BLOCKED: Destination '{hostname_clean}' is a non-local Cloud AI API."

        # 2. Check local whitelist
        if hostname_clean in self.allowed_local_hosts or hostname_clean.endswith(".local") or hostname_clean.endswith(".internal"):
            return True, f"ALLOWED: Local/Internal service endpoint '{hostname_clean}'."

        # 3. Check private IP ranges (e.g., 127.0.0.1, 192.168.x.x, 10.x.x.x)
        if self.is_local_ip(hostname_clean):
            return True, f"ALLOWED: Private on-premise IP address '{hostname_clean}'."

        # 4. Strict mode: reject any generic public internet domain
        if self.strict_mode:
            return False, f"BLOCKED: External public internet host '{hostname_clean}' prohibited in sovereign mode."

        return True, "ALLOWED"

    def check_and_intercept(self, target: str, caller: str = "unknown") -> bool:
        """
        Inspect an outgoing request. If prohibited, increment counter and return False.
        """
        is_allowed, reason = self.validate_destination(target)
        if not is_allowed:
            self.blocked_attempts_count += 1
            return False
        return True
