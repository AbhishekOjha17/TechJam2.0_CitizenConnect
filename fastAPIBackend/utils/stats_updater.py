# utils/stats_updater.py
from datetime import datetime
import database
from math import isclose


async def update_global_stats(model_output, service, rating, district):
    db = database.db
    if db is None:
        print("❌ Database not initialized in update_global_stats")
        return

    # 1️⃣ Update GLOBAL stats
    await _update_stats_document(db, "global_stats", "global", None, model_output, service, rating)

    # 2️⃣ Update DISTRICT stats
    district_key = f"district_{district}"
    await _update_stats_document(db, district_key, "district", district, model_output, service, rating)


async def _update_stats_document(db, doc_id, scope, district, model_output, service, rating):
    stats = await db.stats.find_one({"_id": doc_id}) or {}

    # Extract existing stats
    avg_rating_overall = stats.get("avg_rating_overall", 0)
    total_feedback = stats.get("total_feedback_overall", 0)
    ratings_by_service = stats.get("avg_rating_by_service", {})
    s_counts_overall = stats.get("sentiment_counts_overall", {"positive": 0, "neutral": 0, "negative": 0})
    s_counts_by_service = stats.get("sentiment_counts_by_service", {})
    total_feedback_by_service = stats.get("total_feedback_by_service", {})
    timeline = stats.get("feedback_over_time", {})

    # --- Update averages ---
    new_total = total_feedback + 1
    avg_rating_overall = round(((avg_rating_overall * total_feedback) + rating) / new_total, 2)

    # per service average
    prev_rating = ratings_by_service.get(service, rating)
    ratings_by_service[service] = round((prev_rating + rating) / 2, 2)

    # --- Update sentiment counts ---
    s = model_output.get("sentiment", "neutral")
    if s not in s_counts_overall:
        s_counts_overall[s] = 0
    s_counts_overall[s] += 1

    s_counts_by_service.setdefault(service, {"positive": 0, "neutral": 0, "negative": 0})
    s_counts_by_service[service][s] += 1

    # --- Update feedback totals ---
    total_feedback_by_service[service] = total_feedback_by_service.get(service, 0) + 1

    # --- Timeline ---
    today = datetime.utcnow().strftime("%Y-%m-%d")
    timeline[today] = timeline.get(today, 0) + 1

    await db.stats.update_one(
        {"_id": doc_id},
        {"$set": {
            "scope": scope,
            "district": district,
            "avg_rating_overall": avg_rating_overall,
            "avg_rating_by_service": ratings_by_service,
            "sentiment_counts_overall": s_counts_overall,
            "sentiment_counts_by_service": s_counts_by_service,
            "total_feedback_overall": new_total,
            "total_feedback_by_service": total_feedback_by_service,
            "feedback_over_time": timeline,
            "last_updated": datetime.utcnow()
        }},
        upsert=True
    )

    print(f"📊 Updated stats for {scope.upper()} ({district or 'ALL'})")
