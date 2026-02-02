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
import re
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

# Default settings
DEFAULT_SETTINGS = {
    "language": "et",
    "demo_mode": False,
    "demo_speed": 60,
    "display_hours": {
        "enabled": True,
        "start": "00:00",
        "end": "23:59"
    },
    "bus_enabled": False,
    "bus_stop_id": "",  # Use SiriID from transport.tallinn.ee/data/stops.txt (e.g., 873 for Lepistiku)
    "bus_stop_name": "",
    "bus_display_windows": [
        {"start": "00:00", "end": "23:59"}
    ],
    "news_url": "https://www.tallinn.ee/et/group/580/news?news_heading=20315",
    "colors": {
        "lesson": "#ff0000",
        "break": "#00db50",
        "before_school": "#333333",
        "after_school": "#333333"
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
    ],
    "substitutions": {
        "enabled": True,
        "url": "https://ttg.edupage.org/substitution/",
        "refresh_minutes": 15,
        "filter_mode": "upcoming",
        "display_windows": [
            {"start": "00:00", "end": "23:59"}
        ]
    },
    "show_credit": True
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
substitutions = []

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
    news_url = settings.get("news_url") or DEFAULT_SETTINGS["news_url"]

    # Skip if no URL configured
    if not news_url or not news_url.startswith(("http://", "https://")):
        return

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

    bus_stop_id = settings.get("bus_stop_id") or DEFAULT_SETTINGS.get("bus_stop_id")
    if not bus_stop_id:
        bus_arrivals = []
        return
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                BUS_API_URL,
                params={"stopid": bus_stop_id},
                timeout=10
            )
            text = response.text

        # Parse response format:
        # Line 1: Header with timestamp
        # Line 2: "stop,{siriId}"
        # Line 3+: "{type},{route},{expectedSec},{scheduledSec},{destination},{secsUntilArrival},{flag}"
        lines = text.strip().split('\n')
        if len(lines) <= 2:
            bus_arrivals = []
            print("No buses currently")
            return

        arrivals = []
        for line in lines[1:]:  # Skip header
            parts = line.split(',')
            # Skip the "stop,X" line
            if parts[0] == "stop":
                continue
            if len(parts) >= 6:
                transport_type = parts[0].lower()  # "bus", "tram", "trolley"
                route = parts[1]
                destination = parts[4] if len(parts) > 4 else ""
                secs_until = int(parts[5]) if parts[5].isdigit() else 0

                minutes = secs_until // 60
                type_names = {"bus": "Bus", "tram": "Tram", "trolley": "Trolley"}
                type_name = type_names.get(transport_type, transport_type.title())

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


# === SUBSTITUTIONS SCRAPER ===
async def fetch_substitutions():
    """Scrape substitutions from EduPage."""
    global substitutions

    sub_settings = settings.get("substitutions", {})
    if not sub_settings.get("enabled", True):
        substitutions = []
        return

    url = sub_settings.get("url") or "https://ttg.edupage.org/substitution/"
    if not url.startswith("http"):
        print("Substitutions: invalid URL")
        return

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            html = response.text

            items = []
            current_teacher = None

            # EduPage embeds data in JavaScript - look for report_html in script
            # The data is HTML-encoded in a React component prop
            report_match = re.search(r'report_html["\']?\s*:\s*["\'](.+?)["\'](?:,|\})', html, re.DOTALL)

            if report_match:
                # Decode the embedded HTML (it's escaped)
                embedded_html = report_match.group(1)
                # Unescape common HTML entities and unicode escapes
                embedded_html = embedded_html.replace('\\u003c', '<').replace('\\u003e', '>')
                embedded_html = embedded_html.replace('\\u0026', '&').replace('\\/', '/')
                embedded_html = embedded_html.replace('\\"', '"').replace("\\'", "'")
                embedded_html = embedded_html.replace('\\n', '\n').replace('\\t', '\t')

                soup = BeautifulSoup(embedded_html, 'html.parser')
            else:
                # Fallback: try parsing the page directly
                soup = BeautifulSoup(html, 'html.parser')

            # Find all table rows in the substitution table
            for row in soup.select('tbody.print-nobreak tr, tr'):
                # Check for teacher header
                header = row.select_one('td.header')
                if header:
                    current_teacher = header.get_text(strip=True)

                # Get period, class/subject, and status
                period_el = row.select_one('td.period span') or row.select_one('td.period')
                what_el = row.select_one('td.what span') or row.select_one('td.what')
                info_el = row.select_one('td.info span') or row.select_one('td.info')

                if period_el and what_el and info_el:
                    period_text = period_el.get_text(strip=True)
                    # Clean up period: remove dots and parentheses like "(2.)" -> "2"
                    period_text = period_text.strip('().').strip()
                    what_text = what_el.get_text(strip=True)
                    info_text = info_el.get_text(strip=True)

                    # Skip empty rows
                    if not period_text or not what_text:
                        continue

                    # Parse class and subject from "8B: Subject"
                    class_name = ""
                    subject = what_text
                    if ':' in what_text:
                        parts = what_text.split(':', 1)
                        class_name = parts[0].strip()
                        subject = parts[1].strip() if len(parts) > 1 else ""

                    # Determine type from status
                    sub_type = "substitute"
                    if "Tühistatud" in info_text or "Cancelled" in info_text:
                        sub_type = "cancelled"
                    elif "Lisatud" in info_text or "Added" in info_text:
                        sub_type = "added"
                    elif "Ruum" in info_text or "Room" in info_text:
                        sub_type = "room_change"

                    # Extract room if present
                    room = None
                    if "Ruum:" in info_text:
                        room = info_text.split("Ruum:")[-1].strip().split(',')[0].strip()
                    elif "Room:" in info_text:
                        room = info_text.split("Room:")[-1].strip().split(',')[0].strip()

                    items.append({
                        "teacher": current_teacher,
                        "period": int(period_text) if period_text.isdigit() else period_text,
                        "class": class_name,
                        "subject": subject,
                        "type": sub_type,
                        "status": info_text,
                        "room": room
                    })

            substitutions = items
            print(f"Substitutions: {len(substitutions)}")

    except Exception as e:
        print(f"Substitutions fetch error: {e}")


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


@app.get("/api/substitutions")
async def get_substitutions():
    return substitutions


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


async def substitutions_loop():
    """Periodically fetch substitutions."""
    while True:
        sub_settings = settings.get("substitutions", {})
        if sub_settings.get("enabled", True):
            await fetch_substitutions()
        interval = sub_settings.get("refresh_minutes", 15) or 15
        await asyncio.sleep(interval * 60)


@app.on_event("startup")
async def startup():
    await scrape_news(force=True)
    await fetch_bus_arrivals()
    await fetch_substitutions()
    asyncio.create_task(news_loop())
    asyncio.create_task(bus_loop())
    asyncio.create_task(substitutions_loop())
    print(f"\n  Slideshow: http://localhost:{PORT}/\n")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)


# ============================================================================
# REMOTE CONTROL CODE (for future use) - commented out
# ============================================================================
# See sandbox/remote-control.py for the full implementation
