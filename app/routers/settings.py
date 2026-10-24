from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.database import db

router = APIRouter(prefix="/api", tags=["Settings"])

class ProtectionPlan(BaseModel):
    owner: str
    beneficiary: str
    instruction: Optional[str] = ""
    threshold: str
    guardians: List[str] = []
    interventionWindow: Optional[str] = "48 hours"

@router.post("/protection-plan")
async def save_protection_plan(plan: ProtectionPlan):
    try:
        # Access your database collection (change 'heirloom_db' to your actual database name if needed)
        database = db.client.get_database("heirloom_db")
        collection = database.get_collection("protection_plans")
        
        # Upsert the plan based on the owner
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
        
        # Fetch the latest plan (or filter by user session)
        plan = await collection.find_one({}, sort=[("_id", -1)])
        if not plan:
            return {}
            
        plan["_id"] = str(plan["_id"]) # Convert ObjectId to string
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))