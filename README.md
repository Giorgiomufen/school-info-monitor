# School Info Monitor

SpaceX-inspired info display for Tallinna Tehnikagümnaasium.

## Features

- **News feed** - school news with images, descriptions, dates
- **Bus arrivals** - real-time from Tallinn transport API with destinations
- **Mission clock** - countdown to next lesson/break
- **Timeline** - school day progress (08:00-15:45)
- **Settings page** - customizable via web UI
- **Demo mode** - fast time simulation (60x speed)
- **Color states** - lesson/break/before/after school

## How to Run

1. Double-click `app/run.bat`
2. Open http://localhost:8000
3. Press `S` for settings

## Project Structure

```
school-info-monitor/
├── app/
│   ├── main.py              # Server + scraper + API
│   ├── requirements.txt
│   ├── run.bat              # Start (creates venv automatically)
│   ├── stop.bat
│   └── static/
│       ├── display.html
│       └── settings.html
└── experiments/
    └── space-scroll.html    # Main display (SpaceX style)
```

## Tech Stack

- Python FastAPI
- httpx + BeautifulSoup (scraping)
- Tallinn Transport SIRI API
- Vanilla HTML/CSS/JS

## Settings

Access via http://localhost:8000/settings or press `S`

- Demo mode toggle
- Bus panel on/off
- Bus stop ID/name
- News URL
- Colors for each state
- Schedule times

## API Endpoints

- `GET /` - main display
- `GET /settings` - settings page
- `GET /api/articles` - news data
- `GET /api/bus` - bus arrivals
- `GET /api/settings` - current settings
- `POST /api/settings` - update settings
- `GET /api/schedule` - school schedule

---

Built by Giorgio G. Lelmi
