"""









Minimal consent check for MediTrust hackathon MVP.

Exposes only `is_access_allowed(patient_id, actor_role, resource_type)`.
This is intentionally minimal and deterministic for demo purposes.
"""

def is_access_allowed(patient_id: str, actor_role: str, resource_type: str) -> bool:
    """
    Minimal, deterministic consent check used for the hackathon demo.

    - Returns True only for the demo tuple:
      (patient_id == 'PAT-12345' and actor_role == 'doctor' and resource_type == 'report')
    - All other combinations return False.

    IMPORTANT: This function is a mock for MVP demonstration only.
    """
    if not patient_id or not actor_role or not resource_type:
        return False

    if patient_id == "PAT-12345" and actor_role == "doctor" and resource_type == "report":
        return True

    return True
