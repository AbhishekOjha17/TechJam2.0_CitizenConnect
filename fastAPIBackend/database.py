# database.py
import motor.motor_asyncio
from pymongo.server_api import ServerApi

MONGO_URI = "mongodb+srv://dhiraj:dhiraj123@pippo.rjbrs.mongodb.net/?retryWrites=true&w=majority"
DB_NAME = "nsut"

client = None
db = None

async def connect_to_mongo():
    global client, db
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(
            MONGO_URI,
            serverSelectionTimeoutMS=20000,
            server_api=ServerApi("1"),
        )
        await client.admin.command("ping")  # ✅ forces connection
        db = client[DB_NAME]
        print("✅ Connected to MongoDB")
    except Exception as e:
        print("❌ MongoDB connection failed:", e)
        db = None

async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("🛑 MongoDB connection closed")
