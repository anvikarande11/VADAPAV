from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
from app.database import db
from app.services.trigger_engine import BackendTriggerEngine

router = APIRouter(prefix="/api", tags=["Protection Plan"])
trigger_engine = BackendTriggerEngine()

class ProtectionPlan(BaseModel):
    owner: str
    beneficiary: str
    handover_instructions: Optional[str] = ""
    threshold: str
    trusted_guardians: List[str] = []
    interventionWindow: Optional[str] = "48"
    last_check_in: Optional[str] = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    state: Optional[str] = "ACTIVE"

class HeartbeatRequest(BaseModel):
    owner: str

@router.post("/protection-plan")
async def save_protection_plan(plan: ProtectionPlan):
    try:
        database = db.client.get_database("heirloom_db")
        collection = database.get_collection("protection_plans")
        
        # Check if plan already exists to preserve its original last_check_in if updating
        existing_plan = await collection.find_one({"owner": plan.owner})
        if existing_plan and "last_check_in" in existing_plan:
            plan.last_check_in = existing_plan["last_check_in"]
            plan.state = existing_plan.get("state", "ACTIVE")

        await collection.update_one(
            {"owner": plan.owner}, 
            {"$set": plan.dict()}, 
            upsert=True
        )
        
        return {"success": True, "message": "Protection plan saved successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/protection-plan")
async def get_protection_plan():
    try:
        database = db.client.get_database("heirloom_db")
        collection = database.get_collection("protection_plans")
        
        plan = await collection.find_one({}, sort=[("_id", -1)])
        if not plan:
            return {}
            
        plan["_id"] = str(plan["_id"])
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/protection-plan/heartbeat")
async def record_heartbeat(data: HeartbeatRequest):
    """
    Resets the user's dead man's switch timer back to ACTIVE and updates last_check_in.
    """
    try:
        database = db.client.get_database("heirloom_db")
        collection = database.get_collection("protection_plans")
        
        current_utc_time = datetime.now(timezone.utc).isoformat()
        
        result = await collection.update_one(
            {"owner": data.owner},
            {"$set": {"last_check_in": current_utc_time, "state": "ACTIVE"}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Protection plan not found for this owner.")

        return {
            "success": True,
            "message": "Heartbeat recorded successfully. Timer reset.",
            "lastCheckIn": current_utc_time,
            "newState": "ACTIVE"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/protection-plan/status/{owner}")
async def get_plan_status(owner: str):
    """
    Evaluates the live dead man's switch state of a user's protection plan based on elapsed time.
    """
    try:
        database = db.client.get_database("heirloom_db")
        collection = database.get_collection("protection_plans")
        
        plan = await collection.find_one({"owner": owner})
        if not plan:
            raise HTTPException(status_code=404, detail="Protection plan not found.")
            
        # Fallback to current time if last_check_in is missing
        last_check_in = plan.get("last_check_in", datetime.now(timezone.utc).isoformat())
        
        evaluation = trigger_engine.evaluate_plan_state(last_check_in)
        
        # Optionally sync the evaluated state back to DB if it changed
        if plan.get("state") != evaluation["current_state"]:
            await collection.update_one(
                {"owner": owner},
                {"$set": {"state": evaluation["current_state"]}}
            )

        return {
            "owner": owner,
            "evaluation": evaluation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))