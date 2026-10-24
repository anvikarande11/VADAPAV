from pydantic import BaseModel
from typing import List, Optional

class UserSetupModel(BaseModel):
    owner_name: str
    beneficiary_name: str
    guardians: List[str]  # e.g., ["Guardian A", "Guardian B", "Guardian C"]
    threshold: int = 2     # e.g., 2 out of 3

class GuardianApprovalModel(BaseModel):
    guardian_name: str
    approved: bool

class RecoveryTriggerModel(BaseModel):
    owner_name: str