# ORBIS - Kaderin Geometrisi

## Project Purpose
ORBIS is a Progressive Web App (PWA) that combines astrological data with AI analysis. It calculates high-precision sky maps using `pyswisseph` and interprets them using various AI models (Google Gemini, DeepSeek, OpenRouter).

## Tech Stack
- **Backend:** Python Flask (stateless/serverless compatible)
- **Calculation Engine:** `pyswisseph` (Swiss Ephemeris)
- **AI Hub:** Google Gemini, DeepSeek, OpenRouter API
- **Frontend:** ORBIS Premium Design System, Tailwind CSS, Vanilla CSS, Alpine.js
- **PWA:** manifest.json, sw.js
- **Data Persistence:** Client-side `localStorage` (Privacy focused)

## Key Files
- `app.py`: Application entry point
- `astro_calculations.py`: High-precision astrological calculations
- `ai_interpretations.py`: AI-based analysis logic
- `routes.py`: Flask route definitions
- `env_config.py`: Environment and API configuration
- `static/orb.mp4`: Central animation
- `templates/layout.html`: PWA structure and navigation
- `templates/new_result.html`: Result display center (Summary, Chart, AI)
