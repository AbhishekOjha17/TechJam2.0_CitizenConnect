# pipeline/process_report.py
from bson import ObjectId
import database  # ✅ import the module, not just the variable
from pipeline.nlp_cleaning import clean_with_nlp
from pipeline.model_output import model_output_from_text
from utils.stats_updater import update_global_stats


async def process_report(report_id: str):
    """
    Background task that processes a report in multiple stages:
    1. Cleans the text using NLP.
    2. Runs model inference on the cleaned text.
    3. Updates aggregate stats in the database.
    """
    db = database.db  # ✅ always get it from the initialized global
    if db is None:
        print("❌ Database not initialized!")
        return

    # --- STEP 0: Fetch report ---
    report = await db.reports.find_one({"_id": ObjectId(report_id)})
    if not report:
        print(f"⚠️ Report {report_id} not found in database")
        return

    print(f"🔄 Processing report {report_id}")

    # --- STEP 1: NLP Cleaning ---
    cleaned = clean_with_nlp(report["comment"])
    await db.reports.update_one(
        {"_id": ObjectId(report_id)},
        {"$set": {"cleaned_comment": cleaned, "processing": 1}}
    )
    print(f"✅ Step 1 complete: cleaned text saved")

    # --- STEP 2: Model Output ---
    model_out = model_output_from_text(cleaned, report.get("rating", 3))
    await db.reports.update_one(
        {"_id": ObjectId(report_id)},
        {"$set": {"_model_output": model_out, "processing": 2}}
    )
    print(f"✅ Step 2 complete: model output saved")

    # --- STEP 3: Update Stats ---
    await update_global_stats(model_out, report["public_service"], report["rating"], report["district"])
    print(f"✅ Step 3 complete: stats updated for {report['public_service']} ({report['district']})")

    print(f"🎉 Report {report_id} fully processed!\n")