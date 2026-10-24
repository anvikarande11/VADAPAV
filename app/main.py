from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection
from app.routers import recovery
from app.routers import guardians, protection_plan  # Import under a safe, non-conflicting name


app = FastAPI(
    title="Heirloom Protocol Backend",
    description="Trust-Minimized Digital Inheritance Simulation API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(recovery.router)
app.include_router(protection_plan.router)  # Register your new protection plan router
app.include_router(guardians.router)

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Heirloom backend is running with Phase 3 simulation workflows ready!"
    }