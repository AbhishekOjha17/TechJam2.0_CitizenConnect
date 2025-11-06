# main.py
from fastapi import FastAPI, BackgroundTasks, HTTPException, UploadFile, File, Form,  Query 
from typing import Optional
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from models import Report, Stats
import database
from pipeline.process_report import process_report
import os, json, uuid
from datetime import datetime
from fastapi.responses import HTMLResponse


from heatmap_services import generate_heatmap_html




app = FastAPI(title="Public Service Feedback API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "storage"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/storage", StaticFiles(directory="storage"), name="storage")


@app.post("/report")
async def create_report(
    background_tasks: BackgroundTasks,
    report: str = Form(...),               # JSON string version of Report
    imgFile: UploadFile = File(None)       # optional file
):
    try:
        if database.db is None:
            raise HTTPException(status_code=500, detail="Database not initialized")

        # Parse stringified JSON into Pydantic model
        report_data = json.loads(report)
        report_obj = Report(**report_data)

        # Handle the optional image
        if imgFile:
            extension = os.path.splitext(imgFile.filename)[1]
            unique_name = f"{uuid.uuid4().hex}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{extension}"
            file_path = os.path.join(UPLOAD_DIR, unique_name)

            # Save image locally
            with open(file_path, "wb") as f:
                f.write(await imgFile.read())

            # Save public path in the model
            report_obj.imgUrl = f"/storage/{unique_name}"

        # ✅ Now use your original line
        data = report_obj.dict()

        result = await database.db.reports.insert_one(data)
        background_tasks.add_task(process_report, str(result.inserted_id))

        return {"message": "Report queued for processing", "id": str(result.inserted_id)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("startup")
async def startup_db_client():
    await database.connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await database.close_mongo_connection()


@app.get("/reports/processed")
async def get_processed_reports(limit: int = 50):
    cursor = database.db.reports.find({"processing": 2}, {"_id": 0}).limit(limit)
    return await cursor.to_list(length=limit)


@app.get("/reports/status")
async def report_status():
    total = await database.db.reports.count_documents({})
    pending = await database.db.reports.count_documents({"processing": {"$lt": 2}})
    processed = total - pending
    return {"total": total, "pending": pending, "processed": processed}


@app.get("/analytics")
async def get_analytics(
    scope: str = Query("global", enum=["global", "district"]),
    district: Optional[str] = Query(None, description="Name of district (required if scope=district)")
):
    db = database.db
    if db is None:
        return {"error": "Database not initialized"}

    if scope == "global":
        stats = await db.stats.find_one({"_id": "global_stats"})
    elif scope == "district":
        if not district:
            return {"error": "Missing 'district' query param for district scope"}
        stats = await db.stats.find_one({"_id": f"district_{district}"})
    else:
        return {"error": "Invalid scope. Use 'global' or 'district'."}

    if not stats:
        return {"message": f"No analytics found for {scope}{' - ' + district if district else ''}"}

    # Convert Mongo document to Pydantic model, then to dict
    parsed_stats = Stats(**stats)
    return parsed_stats.dict()



@app.get("/heatmap", response_class=HTMLResponse)
async def get_heatmap():
    """
    Generates and returns an HTML heatmap directly in the response.
    """
    return generate_heatmap_html()