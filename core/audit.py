"""Minimal audit logger for MediTrust MVP.

Append-only JSON-lines with hashed identifiers.
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path

AUDIT_LOG_PATH = Path(os.getenv("AUDIT_LOG_PATH", "audit.log"))


def _hash_id(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def log_access_attempt(patient_id: str, actor_id: str, actor_role: str, action: str, success: bool, metadata: dict = None):
    """Append a single audit entry to the audit log as a JSON line.

    - Hashes `patient_id` and `actor_id` using SHA-256.
    - Writes to `AUDIT_LOG_PATH` in append mode.
    """
    path = AUDIT_LOG_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "patient_id_hash": _hash_id(patient_id),
        "actor_id_hash": _hash_id(actor_id),
        "actor_role": actor_role,
        "action": action,
        "success": success,
        "metadata": metadata or {}
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


# End of minimal audit logger
