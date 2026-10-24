from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.database import db

router = APIRouter(prefix="/api/guardians", tags=["Guardians"])

class GuardianApprovalRequest(BaseModel):
    guardian_name: str
    approved: bool

@router.post("/approve")
async def submit_guardian_approval(payload: GuardianApprovalRequest):
    try:
        if not db or not getattr(db, "client", None):
            raise HTTPException(status_code=500, detail="Database client is not initialized.")

        database = db.client.get_database("heirloom_db")
        collection = database.get_collection("protection_plans")
        
        plan = await collection.find_one({}, sort=[("_id", -1)])
        
        # Safely extract guardians
        trusted_guardians = []
        if plan:
            trusted_guardians = plan.get("trusted_guardians", []) or plan.get("guardians", [])
        
        if not trusted_guardians:
            trusted_guardians = ["Anvi k", "Sai N", "Adi K", "Prachi K"]

        # Case-insensitive and whitespace-safe comparison
        input_normalized = payload.guardian_name.strip().lower()
        guardians_normalized = {g.strip().lower(): g for g in trusted_guardians}

        if input_normalized not in guardians_normalized:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail=f"'{payload.guardian_name}' is not listed in trusted_guardians: {trusted_guardians}"
            )
        
        canonical_name = guardians_normalized[input_normalized]

        approvals_collection = database.get_collection("guardian_approvals")
        await approvals_collection.update_one(
            {"guardian_name": canonical_name},
            {"$set": {"approved": payload.approved}},
            upsert=True
        )
        
        approved_count = await approvals_collection.count_documents({"approved": True})
        
        # Safely parse threshold (handling "string" placeholders or non-numeric values gracefully)
        raw_threshold = plan.get("threshold", 2) if plan else 2
        try:
            threshold = int(raw_threshold)
        except (ValueError, TypeError):
            threshold = 2  # Safe fallback if threshold is saved as text like "string"
        
        threshold_met = approved_count >= threshold

        return {
            "status": "success",
            "message": f"Approval recorded for {canonical_name}.",
            "current_approvals": approved_count,
            "required_threshold": threshold,
            "threshold_met": threshold_met
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Error Exception: {str(e)}")