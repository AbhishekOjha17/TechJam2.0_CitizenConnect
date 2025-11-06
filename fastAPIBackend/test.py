import motor.motor_asyncio
import asyncio

MONGO_URI = "mongodb+srv://dhiraj:dhiraj123@pippo.rjbrs.mongodb.net/?retryWrites=true&w=majority"

async def test_connection():
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=10000)
        await client.admin.command("ping")
        print("✅ MongoDB connected successfully!")
    except Exception as e:
        print("❌ MongoDB connection failed:", e)

asyncio.run(test_connection())
