# School Info Monitor

SpaceX-inspired info display for Tallinna Tehnikagümnaasium.

## Features

- **News feed** - scraped from school website with images and descriptions
- **Bus arrivals** - real-time from Tallinn transport API with urgency colors (yellow/red)
- **Mission clock** - countdown to next lesson/break, shows current time when idle
- **Timeline** - school day progress (08:00-15:45)
- **Substitutions panel** - schedule changes from EduPage with filtering
- **Settings page** - customizable via web UI
- **Demo mode** - fast time simulation for testing
- **Color states** - lesson/break/before/after school
- **Multi-language** - English and Estonian (i18n)
- **Display windows** - show/hide panels during specific hours
- **Creator credit** - customizable "Made by" text on display

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
│   ├── settings.json        # User settings (auto-created)
│   └── static/
│       ├── settings.html
│       └── i18n.js          # Internationalization module
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

- Language (English / Eesti)
- Demo mode toggle + speed
- Display hours (auto sleep)
- Bus panel on/off with display windows and urgency thresholds
- Substitutions panel with filter modes
- News URL
- Colors for each state
- Schedule times

## API Endpoints

- `GET /` - main display
- `GET /settings` - settings page
- `GET /api/articles` - news data
- `GET /api/bus` - bus arrivals
- `GET /api/substitutions` - schedule changes
- `GET /api/settings` - current settings
- `POST /api/settings` - update settings
- `GET /api/schedule` - school schedule

## Adding Languages

To add a new language (e.g., Russian):

1. In `app/static/i18n.js`, add to `languages`: `ru: { name: 'Russian', nativeName: 'Русский' }`
2. Add a `ru: { ... }` translations object with all keys
3. Add `<option value="ru">Русский</option>` to the language selector in `settings.html`

---

Built by Giorgio G. Lelmi
