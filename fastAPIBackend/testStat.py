import asyncio
import random
from datetime import datetime, timedelta, UTC
import database  # 👈 import the module, not db directly

async def insert_random_stats():
    # Ensure DB connection initializes
    await database.connect_to_mongo()

    if database.db is None:
        raise RuntimeError("❌ Database not initialized. Check your MongoDB URI or connection code.")

    db = database.db  # ✅ now get the live, updated db reference

    # Random public services
    services = ["Water Supply", "Electricity", "Roads", "Waste Management", "Public Transport"]

    # Generate random average ratings
    avg_rating_by_service = {
        service: round(random.uniform(1, 5), 2)
        for service in services
    }

    # Random sentiment counts
    sentiment_counts = {
        "positive": random.randint(10, 100),
        "negative": random.randint(10, 100),
        "neutral": random.randint(10, 100),
    }

    # Random feedback over the past week
    feedback_over_time = {}
    for i in range(7):
        date = (datetime.now(UTC) - timedelta(days=i)).strftime("%Y-%m-%d")
        feedback_over_time[date] = random.randint(0, 50)

    # Create the stats document
    stats_doc = {
        "_id": "global_stats",
        "avg_rating_by_service": avg_rating_by_service,
        "sentiment_counts": sentiment_counts,
        "feedback_over_time": feedback_over_time,
        "last_updated": datetime.now(UTC),
    }

    # Upsert (insert or replace existing)
    result = await db["stats"].replace_one({"_id": "global_stats"}, stats_doc, upsert=True)

    print("\n✅ Inserted/Updated Stats Document:")
    print(stats_doc)

    await database.close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(insert_random_stats())
