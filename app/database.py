from motor.motor_asyncio import AsyncIOMotorClient
import certifi
from app.config import settings

class Database:
    client: AsyncIOMotorClient = None

db = Database()

async def connect_to_mongo():
    # Force certifi SSL context and bypass local Windows OpenSSL mismatch
    db.client = AsyncIOMotorClient(
        settings.MONGO_URI,
        tlsCAFile=certifi.where(),
        tlsAllowInvalidCertificates=True
    )
    print("Connected to MongoDB successfully!")

async def close_mongo_connection():
    if db.client:
        db.client.close()
        print("Closed MongoDB connection.")

def get_db():
    return db.client[settings.DB_NAME]