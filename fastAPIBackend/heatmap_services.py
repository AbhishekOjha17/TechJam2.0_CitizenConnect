# heatmap_service.py
import math
import pandas as pd
from pymongo import MongoClient
import folium
from folium.plugins import HeatMap
from fastapi.responses import HTMLResponse

MONGO_URI = "mongodb+srv://dhiraj:dhiraj123@pippo.rjbrs.mongodb.net/?retryWrites=true&w=majority"
DB_NAME = "nsut"
COL_NAME = "reports"

TAG_COLOR = {
    "Water Supply": "blue",
    "Road Maintenance": "red",
    "Garbage": "brown",
    "Electricity": "purple",
    "Drainage": "green",
}

def generate_heatmap_html():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    coll = db[COL_NAME]

    docs = list(coll.find(
        {
            "device_location": {"$exists": True, "$ne": None},
            "public_service": {"$exists": True},
            "district": {"$exists": True}
        },
        {
            "device_location": 1,
            "public_service": 1,
            "district": 1,
            "rating": 1
        }
    ))

    parsed_rows = []
    for d in docs:
        loc = d.get("device_location")
        if not loc:
            continue
        try:
            lat_str, lon_str = loc.split(",")
            lat, lon = float(lat_str.strip()), float(lon_str.strip())
        except Exception:
            continue
        parsed_rows.append({
            "tag": d.get("public_service"),
            "district": d.get("district"),
            "rating": d.get("rating", 0),
            "lat": lat,
            "lon": lon
        })

    if not parsed_rows:
        return HTMLResponse("<h3>No valid location data found.</h3>", status_code=404)

    df = pd.DataFrame(parsed_rows)
    agg_df = (
        df.groupby(["tag", "district"])
        .agg(
            count=("rating", "count"),
            avg_sentiment=("rating", lambda x: round(
                x.apply(lambda r: 1 if r > 3 else (0 if r == 3 else -1)).mean(), 3)
            ),
            sample_lat=("lat", "first"),
            sample_lon=("lon", "first")
        )
        .reset_index()
    )

    lats = agg_df["sample_lat"].tolist()
    lons = agg_df["sample_lon"].tolist()
    center_lat = sum(lats) / len(lats)
    center_lon = sum(lons) / len(lons)

    m = folium.Map(location=[center_lat, center_lon], zoom_start=12)
    heat_points = [[r["lat"], r["lon"], 1] for r in parsed_rows]
    if heat_points:
        HeatMap(heat_points, radius=10, blur=12).add_to(m)

    max_count = agg_df["count"].max()
    for _, row in agg_df.iterrows():
        tag = row["tag"]
        count = row["count"]
        avg_sent = row["avg_sentiment"]
        lat = row["sample_lat"]
        lon = row["sample_lon"]
        radius = max(4, math.sqrt(count) * 4)
        color = TAG_COLOR.get(tag, "gray")

        popup_html = f"<b>{tag}</b><br>District: {row['district']}<br>Count: {count}<br>Avg sentiment: {avg_sent}"
        folium.CircleMarker(
            location=[lat, lon],
            radius=radius,
            color=color,
            fill=True,
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=300)
        ).add_to(m)

    legend_html = """
        <div style="
        position: fixed;
        bottom: 50px;
        left: 10px;
        width: 170px;
        background-color: white;
        border:2px solid grey;
        z-index:9999;
        padding: 10px;
        font-size:14px;
        ">
        <b>Tag legend</b><br>
    """
    for tag, color in TAG_COLOR.items():
        legend_html += f'<i style="background:{color};width:12px;height:12px;display:inline-block;margin-right:6px;"></i>{tag}<br>'
    legend_html += "</div>"
    m.get_root().html.add_child(folium.Element(legend_html))

    html_str = m.get_root().render()
    client.close()

    return HTMLResponse(content=html_str, media_type="text/html")
