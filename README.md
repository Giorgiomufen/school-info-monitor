# School Info Monitor

A news slideshow display for Tallinna Tehnikagümnaasium.

## What it does

- Scrapes news from school website
- Displays as fullscreen slideshow (20 sec per slide)
- Auto-refreshes every 15 min (only when content changes)
- Shows title + image for each article

## Project Structure

```
school-info-monitor/
├── PROJECT.md           # This file (docs)
└── app/                 # Deploy this folder
    ├── main.py          # Server + scraper
    ├── requirements.txt # Dependencies
    ├── run.bat          # Start server
    ├── stop.bat         # Stop server
    ├── static/
    │   └── display.html # Slideshow UI
    └── venv/            # Python packages (local)
```

## How to Run

1. Open `app/` folder
2. Double-click `run.bat`
3. Open browser → `http://localhost:8000`

To stop: Double-click `stop.bat` or close the command prompt.

## Tech Stack

- Python 3.11+
- FastAPI (web server)
- httpx + BeautifulSoup (scraping)
- Vanilla HTML/CSS/JS (display)

## Features

### Implemented
- [x] News scraping from school website
- [x] Auto-advancing slideshow
- [x] Smart polling (only updates when content changes)
- [x] Image extraction
- [x] Simple start/stop scripts

### Future Ideas
- [ ] QR code remote control (code commented in main.py)
- [ ] Bus arrival times
- [ ] Cafeteria menu/queue
- [ ] Hand gesture control
- [ ] Multi-display sync

---

## QR Remote Control Concept

Control the display from your phone without touching anything.

```
┌─────────────────────────────────────┐
│                                     │
│      SCHOOL NEWS SLIDESHOW          │
│      [Auto-advances or controlled]  │
│                                     │
│                          ┌─────┐    │
│                          │ QR  │    │
│                          └─────┘    │
└─────────────────────────────────────┘
              ↓ scan with phone
┌───────────────────┐
│   Phone Remote    │
│   ← Prev  Next →  │
│   Play / Pause    │
│   Jump to article │
└───────────────────┘
              ↓ real-time sync
         Display updates
```

**How it works:**
- QR code in corner of display links to `http://<local-ip>:8000/remote`
- Phone opens web remote (no app install needed)
- Commands sent via WebSocket
- Display updates instantly

Code is already written and commented in `main.py` — uncomment to enable.

---

## Technical Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        SERVER                           │
│  (Python FastAPI, runs on display PC)                   │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │ Scraper     │  │ WebSocket   │  │ HTTP Server     │  │
│  │ (periodic)  │  │ Hub         │  │ (serves pages)  │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────┘
         │                 │                   │
         ▼                 ▼                   ▼
   ┌──────────┐      ┌──────────┐        ┌──────────┐
   │ School   │      │ Display  │        │  Phone   │
   │ Website  │      │ Browser  │        │  Remote  │
   └──────────┘      └──────────┘        └──────────┘
```

---

## Data Flow

1. **Startup** → Scrape school website, store articles in memory
2. **Every 15 min** → Check if website changed (hash comparison)
3. **If changed** → Re-scrape and update articles
4. **Display** → Fetches `/api/articles`, shows slideshow
5. **Remote** (future) → Sends commands via WebSocket, display reacts

---

## Network Requirements

- Display PC must have internet access (to scrape school website)
- For QR remote: PC and phones must be on same network (school WiFi)
- Server runs on local IP (e.g., `192.168.x.x:8000`)
- QR code links to `http://<local-ip>:8000/remote`

---

## Security Considerations

- QR remote only works on local network (not exposed to internet)
- Option: add simple 4-digit PIN to control
- Rate limiting can prevent spam commands
- No sensitive data stored or exposed

---

## Data Source

**URL:** https://www.tallinn.ee/et/group/580/news?news_heading=20315

Scrapes:
- Article title
- Article image
- Article URL

---

## Configuration

Edit these in `main.py`:

```python
PORT = 8000              # Server port
```

Edit these in `static/display.html`:

```javascript
SLIDE_TIME = 20000       # Milliseconds per slide
REFRESH_TIME = 15 * 60 * 1000  # Milliseconds between article refresh
```
