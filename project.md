# School Info Monitor

## Status: Active

SpaceX-inspired info display for Tallinna Tehnikagümnaasium.

---

## Features

- News feed with images, descriptions, dates from school website
- Bus arrivals from Tallinn transport API with destinations
- Mission clock countdown to next lesson/break
  - Shows current time when more than 2 hours until school
- Timeline showing school day progress
- Substitutions panel (EduPage scraping) with time-based filtering
  - Filter modes: all, upcoming only, next lesson only
  - Display time windows
- Settings page with customization options
- Demo mode with adjustable speed for testing
- Color-coded states (lesson/break/before/after school)
- i18n support (English, Estonian)
- Display hours (configurable sleep schedule)

## Tech

- Python FastAPI backend
- Web scraping with httpx + BeautifulSoup
- Vanilla HTML/CSS/JS frontend
- Tallinn Transport SIRI API

## How to run

```
Double-click app/run.bat
```

Or manually:
```
cd app
pip install httpx fastapi uvicorn beautifulsoup4
python main.py
```

Then open http://localhost:8000

Settings: http://localhost:8000/settings (or press S)

---

## Future ideas

- Social media feed (Instagram/Facebook)
- Countdown to next holiday/event
- Student achievements / spotlights
- Sports games schedule
- Club meeting reminders
