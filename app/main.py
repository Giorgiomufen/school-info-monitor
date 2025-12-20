"""
School Info Monitor - Slideshow of school news + bus arrivals
Run: python main.py
View: http://localhost:8000
Settings: http://localhost:8000/settings
"""
import asyncio
import hashlib
import json
import os
import httpx
from bs4 import BeautifulSoup
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import uvicorn

# === CONFIG ===
PORT = 8000
BASE_URL = "https://www.tallinn.ee"
BUS_API_URL = "https://transport.tallinn.ee/siri-stop-departures.php"
SETTINGS_FILE = "settings.json"

# Route destinations (common routes near Lepistiku)
ROUTE_DESTINATIONS = {
    "34": "Veskimetsa",
    "34A": "Veskimetsa",
    "15": "Kopli",
    "4": "Tondi",
    "17": "Kopli",
    "17A": "Kadaka",
    "23": "Kopli",
    "27": "Kopli",
    "32": "Haabersti",
    "47": "Tiskre",
}

# Default settings
DEFAULT_SETTINGS = {
    "demo_mode": False,
    "bus_enabled": True,
    "bus_stop_id": "02601-1",
    "bus_stop_name": "Lepistiku",
    "news_url": "https://www.tallinn.ee/et/group/580/news?news_heading=20315",
    "colors": {
        "lesson": "#ffffff",
        "break": "#22c55e",
        "before_school": "#3b82f6",
        "after_school": "#6b7280"
    },
    "schedule": [
        {"start": "08:00", "end": "08:45", "name": "Period 1"},
        {"start": "08:55", "end": "09:40", "name": "Period 2"},
        {"start": "09:50", "end": "10:35", "name": "Period 3"},
        {"start": "10:45", "end": "11:30", "name": "Period 4"},
        {"start": "12:00", "end": "12:45", "name": "Period 5"},
        {"start": "13:15", "end": "14:00", "name": "Period 6"},
        {"start": "14:10", "end": "14:55", "name": "Period 7"},
        {"start": "15:00", "end": "15:45", "name": "Period 8"},
    ]
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)

settings = load_settings()

# === STATE ===
articles = []
last_content_hash = None
bus_arrivals = []

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


# === NEWS SCRAPER ===
async def check_for_updates():
    """Check if website content changed. Returns HTML if changed, None if same."""
    global last_content_hash
    news_url = settings.get("news_url", DEFAULT_SETTINGS["news_url"])
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(news_url, timeout=30)
            response.raise_for_status()

        content_hash = hashlib.md5(response.text.encode()).hexdigest()

        if content_hash == last_content_hash:
            print("No news changes")
            return None

        last_content_hash = content_hash
        print("News updated")
        return response.text

    except Exception as e:
        print(f"News check error: {e}")
        return None


async def scrape_news(force=False):
    """Scrape news articles from school website."""
    global articles
    news_url = settings.get("news_url", DEFAULT_SETTINGS["news_url"])

    if force:
        async with httpx.AsyncClient() as client:
            response = await client.get(news_url, timeout=30)
            html = response.text
            global last_content_hash
            last_content_hash = hashlib.md5(html.encode()).hexdigest()
    else:
        html = await check_for_updates()
        if html is None:
            return

    try:
        soup = BeautifulSoup(html, "html.parser")
        new_articles = []
        seen = set()

        for link in soup.select("a[href*='/uudis/']"):
            href = link.get("href", "")
            if not href or href in seen:
                continue
            seen.add(href)

            url = BASE_URL + href if not href.startswith("http") else href

            title = ""
            for tag in ["h2", "h3", "h4"]:
                t = link.select_one(tag)
                if t:
                    title = t.get_text(strip=True)
                    break
            if not title:
                texts = [t.strip() for t in link.get_text().split('\n') if t.strip()]
                title = texts[-1] if texts else ""

            if len(title) < 5:
                continue

            image_url = ""
            description = ""
            date = ""

            # Find parent article element
            article = link.find_parent("article")
            if article:
                # Get image
                img = article.select_one(".node__thumbnail img")
                if img:
                    image_url = img.get("src") or img.get("data-src") or ""

                # Get description from .node__content
                content = article.select_one(".node__content")
                if content:
                    description = content.get_text(strip=True)

                # Get date from time.node__date
                time_el = article.select_one("time.node__date")
                if time_el:
                    date = time_el.get_text(strip=True)

            if image_url and not image_url.startswith("http"):
                image_url = BASE_URL + image_url

            new_articles.append({
                "url": url,
                "title": title,
                "image": image_url,
                "description": description,
                "date": date
            })

        if new_articles:
            articles = new_articles
            print(f"Loaded {len(articles)} articles")

    except Exception as e:
        print(f"Scrape error: {e}")


# === BUS ARRIVALS ===
async def fetch_bus_arrivals():
    """Fetch real-time bus arrivals from Tallinn transport API."""
    global bus_arrivals

    # Demo mode for testing (late night when no buses)
    if settings.get("demo_mode", False):
        bus_arrivals = [
            {"type": "Bus", "route": "34", "destination": "Veskimetsa", "minutes": 3, "time": "3 min"},
            {"type": "Bus", "route": "15", "destination": "Kopli", "minutes": 7, "time": "7 min"},
            {"type": "Trolley", "route": "4", "destination": "Tondi", "minutes": 12, "time": "12 min"},
            {"type": "Bus", "route": "34", "destination": "Veskimetsa", "minutes": 18, "time": "18 min"},
        ]
        print("Bus: demo mode")
        return

    bus_stop_id = settings.get("bus_stop_id", DEFAULT_SETTINGS["bus_stop_id"])
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                BUS_API_URL,
                params={"stopid": bus_stop_id},
                timeout=10
            )
            text = response.text

        # Parse CSV: Transport,RouteNum,ExpectedTimeInSeconds,ScheduleTimeInSeconds,Destination,...
        lines = text.strip().split('\n')
        if len(lines) <= 1:
            bus_arrivals = []
            print("No buses currently")
            return

        arrivals = []
        for line in lines[1:]:
            parts = line.split(',')
            if len(parts) >= 4:
                transport_type = parts[0]
                route = parts[1]
                expected_sec = int(parts[2]) if parts[2] else 0
                destination = ROUTE_DESTINATIONS.get(route, "")

                minutes = expected_sec // 60
                type_names = {"1": "Tram", "2": "Trolley", "3": "Bus"}
                type_name = type_names.get(transport_type, "")

                arrivals.append({
                    "type": type_name,
                    "route": route,
                    "destination": destination,
                    "minutes": minutes,
                    "time": f"{minutes} min" if minutes > 0 else "Now"
                })

        arrivals.sort(key=lambda x: x["minutes"])
        bus_arrivals = arrivals[:5]
        print(f"Bus arrivals: {len(bus_arrivals)}")

    except Exception as e:
        print(f"Bus error: {e}")


# === ROUTES ===
@app.get("/")
async def root():
    return FileResponse("../experiments/space-scroll.html")


@app.get("/settings")
async def settings_page():
    return FileResponse("static/settings.html")


@app.get("/api/articles")
async def get_articles():
    return articles


@app.get("/api/bus")
async def get_bus():
    return bus_arrivals


@app.get("/api/settings")
async def get_settings():
    return settings


@app.post("/api/settings")
async def update_settings(request: Request):
    global settings
    new_settings = await request.json()
    settings = new_settings
    save_settings(settings)
    return {"status": "ok"}


@app.get("/api/schedule")
async def get_schedule():
    return settings.get("schedule", DEFAULT_SETTINGS["schedule"])


# === BACKGROUND TASKS ===
async def news_loop():
    """Periodically check for news updates."""
    while True:
        await asyncio.sleep(15 * 60)  # Every 15 minutes
        await scrape_news()


async def bus_loop():
    """Periodically fetch bus arrivals."""
    while True:
        await fetch_bus_arrivals()
        await asyncio.sleep(60)  # Every minute


@app.on_event("startup")
async def startup():
    await scrape_news(force=True)
    await fetch_bus_arrivals()
    asyncio.create_task(news_loop())
    asyncio.create_task(bus_loop())
    print(f"\n  Slideshow: http://localhost:{PORT}/\n")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)


# ============================================================================
# REMOTE CONTROL CODE (for future use) - commented out
# ============================================================================
# See sandbox/remote-control.py for the full implementation
