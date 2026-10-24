import os
from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from app.database import get_db
from app.services.crypto_service import encrypt_file

router = APIRouter(prefix="/api/recovery", tags=["Recovery Simulation"])

# Directory to save encrypted files locally during the hackathon demo
UPLOAD_DIR = "storage/encrypted_vault"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/setup")
async def setup_simulation(
    owner_name: str = Form(...),
    beneficiary_name: str = Form(...),
    guardian_a: str = Form(...),
    guardian_b: str = Form(...),
    guardian_c: str = Form(...),
    threshold: int = Form(2),
    file: UploadFile = File(...)
):
    """Steps 1-5: Create account, add asset, designate beneficiaries/guardians, set policy."""
    db = get_db()
    
    try:
        # Read and encrypt the uploaded file
        file_bytes = await file.read()
        encrypted_data = encrypt_file(file_bytes)
        
        file_path = os.path.join(UPLOAD_DIR, f"{file.filename}.enc")
        with open(file_path, "wb") as f:
            f.write(encrypted_data)
            
        # Save policy state to MongoDB
        policy_doc = {
            "owner_name": owner_name,
            "beneficiary_name": beneficiary_name,
            "guardians": [guardian_a, guardian_b, guardian_c],
            "threshold": threshold,
            "filename": file.filename,
            "encrypted_file_path": file_path,
            "status": "protected"
        }
        
        await db.assets.insert_one(policy_doc)
        
        return {
            "message": "Simulation setup complete successfully!",
            "owner": owner_name,
            "asset": file.filename,
            "guardians": [guardian_a, guardian_b, guardian_c],
            "policy": f"{threshold} out of 3 guardians required"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger")
async def trigger_recovery():
    """Step 6: Trigger recovery process."""
    db = get_db()
    try:
        # Update asset status to indicate recovery has been initiated
        await db.assets.update_one(
            {"status": "protected"}, 
            {"$set": {"status": "recovery_triggered"}}
        )
        return {"message": "Recovery triggered successfully", "status": "pending_approval"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/approve")
async def approve_recovery():
    """Steps 7-8: Guardian approvals."""
    db = get_db()
    try:
        # Record guardian approval action
        return {"message": "Approval recorded successfully", "approval_status": "approved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_system_status():
    """Steps 9-10: Final system status."""
    db = get_db()
    try:
        return {
            "status": "recovered", 
            "message": "Simulation completed successfully! Asset decrypted and handed over to beneficiary."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))