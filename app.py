"""
Minimal MediTrust FastAPI app for the hackathon MVP.

Endpoints:
- GET /health
- POST /reports/access  (consent-checked, audit-logged, in-memory decryption)

Encryption implementation is unchanged and lives in core/encryption.py.
Consent and audit are minimal mocks suitable for demo purposes.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.encryption import FileEncryption, EncryptionError
from core.consent_service import is_access_allowed
from core.audit import log_access_attempt


# Initialize FastAPI app
app = FastAPI(title="MediTrust API", version="0.1.0")

# Allow CORS for demo
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class HealthCheckResponse(BaseModel):
    status: str
    message: str


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    return {"status": "ok", "message": "MediTrust API is running"}


# In-memory demo storage for one encrypted report
_encrypted_reports: dict = {}

# Seed a sample encrypted report at startup for the demo
try:
    sample_plain = b"Demo patient report - confidential"
    eb, ek = FileEncryption.encrypt_file(sample_plain)
    _encrypted_reports["PAT-12345"] = (eb, ek)
except Exception:
    _encrypted_reports = {}


@app.post("/reports/access")
async def access_report(patient_id: str, actor_id: str, actor_role: str, resource_type: str = "report"):
    """Protected endpoint: check consent, log, decrypt in-memory, return bytes."""
    # STEP 1: Check consent BEFORE decryption
    allowed = is_access_allowed(patient_id, actor_role, resource_type)
    if not allowed:
        log_access_attempt(patient_id, actor_id, actor_role, action="deny", success=False, metadata={"reason": "No valid consent"})
        raise HTTPException(status_code=403, detail="Access denied: no valid consent")

    # Retrieve encrypted data (hardcoded demo storage)
    if patient_id not in _encrypted_reports:
        log_access_attempt(patient_id, actor_id, actor_role, action="view_report", success=False, metadata={"reason": "Report not found"})
        raise HTTPException(status_code=404, detail="Report not found")

    encrypted_blob, encrypted_data_key = _encrypted_reports[patient_id]

    try:
        plaintext = FileEncryption.decrypt_file(encrypted_blob, encrypted_data_key)
    except EncryptionError:
        log_access_attempt(patient_id, actor_id, actor_role, action="view_report", success=False, metadata={"reason": "Decryption failed"})
        raise HTTPException(status_code=500, detail="Decryption failed")

    log_access_attempt(patient_id, actor_id, actor_role, action="view_report", success=True, metadata={"reason": "Access granted"})

    return Response(content=plaintext, media_type="application/octet-stream")
