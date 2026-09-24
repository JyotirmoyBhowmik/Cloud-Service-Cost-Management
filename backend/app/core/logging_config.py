"""
Structured JSON Logging & PII/Secret Redaction Module
Complies with Rule 4.1 (JSON format with contextual attributes) and Rule 4.3 (PII/Secret masking).
"""

import json
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict


# Regex patterns for sensitive data masking
REDACTION_PATTERNS = [
    (re.compile(r'(?i)(bearer\s+)[a-zA-Z0-9_\-\.]+'), r'\1[REDACTED_TOKEN]'),
    (re.compile(r'(?i)("?(?:password|client_secret|secret_key|private_key|api_key|token)"?\s*[:=]\s*"?)[^"\s,]+("?)'), r'\1[REDACTED]\2'),
    (re.compile(r'\b(?:\d{4}[ -]?){3}\d{4}\b'), '[REDACTED_CREDIT_CARD]'),
    (re.compile(r'-----BEGIN [A-Z ]+ PRIVATE KEY-----[^-]+-----END [A-Z ]+ PRIVATE KEY-----', re.DOTALL), '[REDACTED_PRIVATE_KEY]'),
]


def redact_sensitive_data(text: str) -> str:
    """Masks secrets, private keys, tokens, and PII from log output."""
    if not isinstance(text, str):
        text = str(text)
    for pattern, replacement in REDACTION_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


class JSONFormatter(logging.Formatter):
    """
    Formats log records into structured JSON strings with mandatory telemetry metadata:
    - timestamp (ISO-8601 UTC)
    - level
    - service_name
    - function_name
    - correlation_id
    - message (sanitized)
    """

    def __init__(self, service_name: str = "cloudscope-backend"):
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        correlation_id = getattr(record, "correlation_id", "SYS-NONE")
        
        log_payload: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service_name": self.service_name,
            "module": record.module,
            "function_name": record.funcName,
            "line_no": record.lineno,
            "correlation_id": correlation_id,
            "message": redact_sensitive_data(record.getMessage()),
        }

        # Include custom extra metadata if present
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            # Sanitize values inside extra_data
            clean_extra = {}
            for k, v in record.extra_data.items():
                clean_extra[k] = redact_sensitive_data(str(v)) if isinstance(v, (str, bytes)) else v
            log_payload["extra"] = clean_extra

        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_payload)


def configure_logging(level: int = logging.INFO) -> None:
    """Configures root logger with JSONFormatter."""
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(console_handler)

    # Silence noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)


logger = logging.getLogger("cloudscope")
