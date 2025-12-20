# School Info Monitor

## Status: PAUSED

**I am lost.**

I have no idea why I am doing this anymore. I don't get the point. I need a break.

---

## What it is

A display screen for Tallinna Tehnikagümnaasium inspired by SpaceX design. Shows school news, bus arrivals, and a timeline of the school day.

## What it does (currently working)

- News feed with images, descriptions, dates from school website
- Bus arrivals from Tallinn transport API with destinations
- Mission clock countdown to next lesson/break
- Timeline showing school day progress
- Settings page with customization options
- Demo mode with fast time simulation
- Color-coded states (lesson/break/before/after school)

## Tech

- Python FastAPI backend
- Web scraping with httpx + BeautifulSoup
- Vanilla HTML/CSS/JS frontend
- Tallinn Transport SIRI API

## How to run

```
cd app
pip install httpx fastapi uvicorn beautifulsoup4
python main.py
```

Then open http://localhost:8000

Settings: http://localhost:8000/settings (or press S)

---

## The problem

We built features without knowing why.

- Where does this display go?
- Who is it for?
- What problem does it solve?
- Does it need to exist?

We never answered these questions.

---

## What I learned

- FastAPI
- Web scraping
- Real-time APIs
- Frontend/backend integration

That's not nothing.

---

## Next steps

None right now. Taking a break.

If I come back with clarity, maybe continue. If not, that's okay too.
