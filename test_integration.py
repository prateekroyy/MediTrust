"""
MediTrust Integration Test
Tests consent + audit + encryption together (MVP demonstration).
"""

import os
import sys
import json
from datetime import datetime

# Ensure test audit path
os.environ["AUDIT_LOG_PATH"] = "test_audit.log"

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.encryption import FileEncryption
from core.consent_service import is_access_allowed
from core.audit import log_access_attempt


def test_integration():
    """Run a minimal integration test aligned with trimmed consent/audit APIs."""
    print("\n" + "=" * 60)
    print("MEDITRUST MINIMAL INTEGRATION TEST")
    print("=" * 60)

    try:
        # Test data
        patient_denied = "PAT-00000"
        patient_allowed = "PAT-12345"
        doctor_id = "DOC-001"
        medical_data = b"Patient: Demo\nDiagnosis: Demo\n"

        print("\n1. ENCRYPTION ROUND-TRIP")
        eb, ek = FileEncryption.encrypt_file(medical_data)
        pt = FileEncryption.decrypt_file(eb, ek)
        assert pt == medical_data
        print("✓ Encryption/decryption working")

        print("\n2. CONSENT CHECKS + AUDIT")

        # Denied attempt
        allowed = is_access_allowed(patient_denied, "doctor", "report")
        assert not allowed
        log_access_attempt(patient_denied, doctor_id, "doctor", action="deny", success=False, metadata={"reason": "No valid consent"})
        print("✓ Denied access logged")

        # Allowed attempt (per demo policy)
        allowed = is_access_allowed(patient_allowed, "doctor", "report")
        assert allowed
        log_access_attempt(patient_allowed, doctor_id, "doctor", action="view_report", success=True, metadata={"reason": "Access granted"})
        print("✓ Allowed access logged")

        # Verify audit log file contains entries
        with open("test_audit.log", "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        assert len(lines) >= 2
        print(f"✓ Audit log has {len(lines)} entries")

        print("\nALL CHECKS PASSED")
        return True

    except AssertionError as e:
        print(f"ASSERTION FAILED: {e}")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False


if __name__ == "__main__":
    success = test_integration()
    sys.exit(0 if success else 1)
