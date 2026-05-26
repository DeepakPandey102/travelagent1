import streamlit as st
import os
import json
import requests
from datetime import datetime, date
from serpapi.google_search import GoogleSearch
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.serpapi import SerpApiTools

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="DEEPAK'S TRAVEL – AI Travel Concierge",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────
# API KEYS
# ─────────────────────────────────────────────
import os
import streamlit as st

# ─────────────────────────────────────────────
# SECURE API KEYS (Pulled from Streamlit Secrets)
# ─────────────────────────────────────────────
# If running locally, it falls back to empty strings or local env vars
GOOGLE_API_KEY   = st.secrets.get("GOOGLE_API_KEY", os.environ.get("GOOGLE_API_KEY", ""))
SERPAPI_API_KEY  = st.secrets.get("SERPAPI_API_KEY", os.environ.get("SERPAPI_API_KEY", ""))
UNSPLASH_KEY     = st.secrets.get("UNSPLASH_KEY", "client_id=jxIjm4v_bglM6mYKVgnLFrOmobHSRiixe8dKyqS4_B4")

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
# ─────────────────────────────────────────────
# SESSION STATE BOOT
# ─────────────────────────────────────────────
for k, v in {
    "nav": "🏠 Home",
    "plan_ready": False,
    "best_flights": [],
    "research_text": "",
    "hotel_text": "",
    "itinerary_text": "",
    "weather_text": "",
    "destination_images": [],
    "airport_images": [],
    "poi_images": [],
    "source": "ICN",
    "destination": "NRT",
    "departure_date": date.today(),
    "return_date": date.today(),
    "days": 5,
    "activities": "Local historical spots, food street tours, safe nightlife, local beaches, shopping hubs.",
    "special_notes": "No dietary restrictions, prefer walking-friendly areas",
    "max_budget": 3000,
    "budget_tier": "Standard/Mid-range",
    "hotel_stars": "4⭐ Premium Hotels",
    "flight_class": "Economy Class",
    "transit_style": "Mixed (Trains & Occasional Rideshare)",
    "travel_theme": "Solo Traveler",
    "currency": "USD ($)",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────
# GLOBAL CSS — "Noir Atlas" aesthetic
# deep navy / slate + electric amber accents
# editorial layout, Playfair + DM Sans
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,400&family=DM+Sans:wght@300;400;500;600&family=DM+Mono&display=swap');

/* ── RESET & BASE ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; }

html, .stApp {
    background: #0b0f1a !important;
    color: #e8e4dc !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none; }

/* ── NAVBAR ── */
.voyager-nav {
    position: sticky;
    top: 0;
    z-index: 999;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 48px;
    height: 64px;
    background: rgba(11,15,26,0.92);
    backdrop-filter: blur(16px);
    border-bottom: 1px solid rgba(255,180,0,0.12);
}
.nav-logo {
    font-family: 'Playfair Display', serif;
    font-size: 22px;
    font-weight: 700;
    letter-spacing: -0.5px;
    color: #f5c842;
}
.nav-links { display: flex; gap: 6px; }
.nav-btn {
    background: none;
    border: none;
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 13px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    color: #9ba4b8;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
}
.nav-btn:hover { color: #f5c842; background: rgba(245,200,66,0.06); }
.nav-btn.active { color: #f5c842; background: rgba(245,200,66,0.1); border: 1px solid rgba(245,200,66,0.2); }

/* ── PAGE WRAPPER ── */
.page-wrap { padding: 48px 64px; max-width: 1400px; margin: 0 auto; }

/* ── HERO ── */
.hero {
    position: relative;
    border-radius: 24px;
    overflow: hidden;
    height: 480px;
    margin-bottom: 60px;
    background: linear-gradient(135deg, #0f1628 0%, #1a2540 50%, #0f1628 100%);
    display: flex; align-items: center;
}
.hero-bg {
    position: absolute; inset: 0;
    background: url('https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=1400&auto=format&fit=crop') center/cover no-repeat;
    opacity: 0.18;
}
.hero-content { position: relative; z-index: 2; padding: 64px; }
.hero-eyebrow {
    font-size: 11px; letter-spacing: 4px; text-transform: uppercase;
    color: #f5c842; margin-bottom: 16px; font-weight: 600;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 64px; line-height: 1.05;
    color: #f0ebe0;
    margin-bottom: 20px;
}
.hero-title em { color: #f5c842; font-style: italic; }
.hero-sub { font-size: 16px; color: #7a8499; max-width: 480px; line-height: 1.7; }

/* ── SECTION LABELS ── */
.section-eyebrow {
    font-size: 10px; letter-spacing: 5px; text-transform: uppercase;
    color: #f5c842; margin-bottom: 10px; font-weight: 600;
}
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 36px; color: #f0ebe0;
    margin-bottom: 32px; line-height: 1.2;
}

/* ── CARDS ── */
.card {
    background: #111826;
    border: 1px solid #1e2535;
    border-radius: 16px;
    padding: 28px;
    transition: transform 0.2s, border-color 0.2s;
}
.card:hover { transform: translateY(-3px); border-color: rgba(245,200,66,0.3); }

/* ── FLIGHT CARD ── */
.flight-card {
    background: #111826;
    border: 1px solid #1e2535;
    border-radius: 16px;
    padding: 24px;
    height: 100%;
}
.airline-pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(245,200,66,0.1);
    border: 1px solid rgba(245,200,66,0.2);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 12px; font-weight: 600; color: #f5c842;
    margin-bottom: 18px;
}
.flight-route { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.airport-code { font-size: 28px; font-weight: 700; color: #f0ebe0; font-family: 'DM Mono', monospace; }
.route-line {
    flex: 1; height: 1px; background: linear-gradient(90deg, #f5c842, #2d3a56);
    position: relative;
}
.route-line::after { content: '✈'; position: absolute; right: -8px; top: -10px; font-size: 14px; color: #f5c842; }
.flight-meta { font-size: 13px; color: #5a6580; margin-bottom: 4px; }
.flight-price-big { font-size: 36px; font-weight: 700; color: #4ade80; margin-top: 12px; }
.flight-price-sub { font-size: 12px; color: #5a6580; }
.flight-badge {
    display: inline-block; background: rgba(74,222,128,0.1);
    border: 1px solid rgba(74,222,128,0.2); border-radius: 6px;
    padding: 3px 10px; font-size: 11px; color: #4ade80; margin-top: 8px;
}

/* ── IMAGE GRID ── */
.img-grid { display: grid; gap: 12px; }
.img-grid-3 { grid-template-columns: repeat(3, 1fr); }
.img-grid-4 { grid-template-columns: repeat(4, 1fr); }
.img-tile {
    border-radius: 12px; overflow: hidden;
    position: relative; aspect-ratio: 4/3;
    background: #1a2235;
}
.img-tile img { width: 100%; height: 100%; object-fit: cover; }
.img-tile-tall { aspect-ratio: 3/4; }
.img-label {
    position: absolute; bottom: 10px; left: 10px;
    background: rgba(0,0,0,0.7); backdrop-filter: blur(8px);
    border-radius: 6px; padding: 4px 10px;
    font-size: 12px; color: #f0ebe0; font-weight: 500;
}

/* ── STAT CHIPS ── */
.stat-row { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 32px; }
.stat-chip {
    background: #111826; border: 1px solid #1e2535;
    border-radius: 12px; padding: 16px 24px; flex: 1; min-width: 140px;
}
.stat-chip-label { font-size: 11px; color: #5a6580; text-transform: uppercase; letter-spacing: 2px; }
.stat-chip-value { font-size: 24px; font-weight: 700; color: #f5c842; margin-top: 4px; }
.stat-chip-sub { font-size: 12px; color: #5a6580; }

/* ── INPUT OVERRIDES ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stDateInput > div > div > input {
    background: #111826 !important;
    border: 1px solid #1e2535 !important;
    border-radius: 10px !important;
    color: #e8e4dc !important;
    padding: 12px 16px !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: rgba(245,200,66,0.5) !important;
    box-shadow: 0 0 0 3px rgba(245,200,66,0.08) !important;
}
.stSelectbox > div > div, .stTextArea > div > div > textarea {
    background: #111826 !important;
    border: 1px solid #1e2535 !important;
    border-radius: 10px !important;
    color: #e8e4dc !important;
}
.stSlider > div { color: #e8e4dc !important; }
div[data-baseweb="slider"] div { background: #f5c842 !important; }
label { color: #9ba4b8 !important; font-size: 13px !important; font-weight: 500 !important; }

/* ── GO BUTTON ── */
.stButton > button {
    background: linear-gradient(135deg, #f5c842, #e6a800) !important;
    color: #0b0f1a !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 16px 40px !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    font-family: 'DM Sans', sans-serif !important;
    letter-spacing: 0.5px !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(245,200,66,0.3) !important;
}

/* ── DIVIDER ── */
hr { border-color: #1e2535 !important; margin: 40px 0 !important; }

/* ── ALERT / INFO ── */
.stAlert { background: #111826 !important; border-radius: 12px !important; border-left-color: #f5c842 !important; }
.stSuccess { border-left-color: #4ade80 !important; }

/* ── WEATHER WIDGET ── */
.weather-card {
    background: linear-gradient(135deg, #111826, #0f1e38);
    border: 1px solid #1e2535;
    border-radius: 16px; padding: 24px;
    display: flex; align-items: center; gap: 24px;
}
.weather-temp { font-size: 48px; font-weight: 700; color: #f5c842; }
.weather-desc { font-size: 14px; color: #7a8499; }

/* ── POI GRID ── */
.poi-card {
    background: #111826; border: 1px solid #1e2535;
    border-radius: 16px; overflow: hidden;
    transition: transform 0.2s, border-color 0.2s;
}
.poi-card:hover { transform: translateY(-4px); border-color: rgba(245,200,66,0.3); }
.poi-img { width: 100%; height: 180px; object-fit: cover; background: #1a2235; }
.poi-body { padding: 16px; }
.poi-title { font-weight: 600; color: #f0ebe0; margin-bottom: 4px; font-size: 15px; }
.poi-tag { font-size: 11px; color: #f5c842; text-transform: uppercase; letter-spacing: 2px; }

/* ── ITINERARY ── */
.day-block {
    border-left: 3px solid #f5c842;
    padding-left: 24px;
    margin-bottom: 32px;
}
.day-label {
    font-size: 11px; letter-spacing: 4px; text-transform: uppercase;
    color: #f5c842; margin-bottom: 6px;
}
.day-title {
    font-family: 'Playfair Display', serif;
    font-size: 22px; color: #f0ebe0; margin-bottom: 12px;
}

/* ── SPINNER OVERRIDE ── */
.stSpinner { color: #f5c842 !important; }

/* ── RESPONSIVE ── */
@media (max-width: 900px) {
    .page-wrap { padding: 24px 20px; }
    .hero-title { font-size: 36px; }
    .hero-content { padding: 32px; }
    .voyager-nav { padding: 0 20px; }
    .img-grid-3, .img-grid-4 { grid-template-columns: repeat(2, 1fr); }
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
AIRPORT_NAMES = {
    "ICN": "Incheon Intl, Seoul", "NRT": "Narita Intl, Tokyo",
    "HND": "Haneda, Tokyo", "JFK": "John F. Kennedy, New York",
    "LHR": "Heathrow, London", "CDG": "Charles de Gaulle, Paris",
    "DXB": "Dubai Intl", "SIN": "Changi, Singapore",
    "BKK": "Suvarnabhumi, Bangkok", "HKG": "Hong Kong Intl",
    "SYD": "Kingsford Smith, Sydney", "LAX": "Los Angeles Intl",
    "ORD": "O'Hare, Chicago", "MIA": "Miami Intl",
    "AMS": "Schiphol, Amsterdam", "FCO": "Fiumicino, Rome",
    "BCN": "El Prat, Barcelona", "IST": "Istanbul Intl",
}

CITY_NAMES = {
    "NRT": "Tokyo", "HND": "Tokyo", "ICN": "Seoul", "JFK": "New York",
    "LHR": "London", "CDG": "Paris", "DXB": "Dubai", "SIN": "Singapore",
    "BKK": "Bangkok", "HKG": "Hong Kong", "SYD": "Sydney", "LAX": "Los Angeles",
    "ORD": "Chicago", "MIA": "Miami", "AMS": "Amsterdam", "FCO": "Rome",
    "BCN": "Barcelona", "IST": "Istanbul",
}

def airport_label(code):
    return AIRPORT_NAMES.get(code.upper(), f"{code} International Airport")

def city_name(code):
    return CITY_NAMES.get(code.upper(), code)

def fmt_dt(s):
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M"):
        try:
            return datetime.strptime(s, fmt).strftime("%b %d · %I:%M %p")
        except: pass
    return s or "N/A"

def currency_sym(c):
    return c.split("(")[1].replace(")", "").strip() if "(" in c else "$"

def fetch_unsplash(query, count=4):
    try:
        url = f"https://api.unsplash.com/search/photos?query={query}&per_page={count}&orientation=landscape&{UNSPLASH_KEY}"
        r = requests.get(url, timeout=8)
        data = r.json()
        return [p["urls"]["regular"] for p in data.get("results", [])]
    except:
        return []

def fetch_flights_live(src, dst, dep, ret):
    params = {
        "engine": "google_flights",
        "departure_id": src,
        "arrival_id": dst,
        "outbound_date": str(dep),
        "return_date": str(ret),
        "currency": "USD",
        "hl": "en",
        "api_key": SERPAPI_API_KEY
    }
    result = GoogleSearch(params).get_dict()
    return result.get("best_flights", [])[:4] + result.get("other_flights", [])[:2]

def get_weather(city):
    try:
        url = f"https://wttr.in/{city}?format=j1"
        r = requests.get(url, timeout=6)
        d = r.json()
        cur = d["current_condition"][0]
        temp_c = int(cur["temp_C"])
        desc = cur["weatherDesc"][0]["value"]
        feel = int(cur["FeelsLikeC"])
        humid = cur["humidity"]
        # 3-day
        forecasts = []
        for day in d["weather"][:3]:
            dt = day["date"]
            hi = day["maxtempC"]; lo = day["mintempC"]
            forecasts.append({"date": dt, "hi": hi, "lo": lo, "desc": day["hourly"][4]["weatherDesc"][0]["value"]})
        return {"temp_c": temp_c, "desc": desc, "feel": feel, "humid": humid, "forecast": forecasts, "city": city}
    except Exception as e:
        return None

# ─────────────────────────────────────────────
# NAVBAR (rendered via HTML + st.radio hack)
# ─────────────────────────────────────────────
NAV_ITEMS = ["🏠 Home", "🌅 Discover", "✈️ Plan Trip", "🗺️ Itinerary", "🌤️ Weather"]

st.markdown("""
<div class='voyager-nav'>
  <div class='nav-logo'>✦ IT_COVERGENCE</div>
</div>
""", unsafe_allow_html=True)

# Use columns as nav buttons
nav_cols = st.columns([2] + [1]*len(NAV_ITEMS) + [2])
for i, item in enumerate(NAV_ITEMS):
    with nav_cols[i+1]:
        is_active = st.session_state.nav == item
        if st.button(item, key=f"nav_{i}", use_container_width=True):
            st.session_state.nav = item
            st.rerun()

nav = st.session_state.nav

# ─────────────────────────────────────────────
# PAGE: HOME
# ─────────────────────────────────────────────
if nav == "🏠 Home":
    st.markdown("<div class='page-wrap'>", unsafe_allow_html=True)

    st.markdown("""
    <div class='hero'>
        <div class='hero-bg'></div>
        <div class='hero-content'>
            <div class='hero-eyebrow'>AI-Powered Travel Intelligence</div>
            <div class='hero-title'>Plan your next<br><em>masterpiece</em><br>journey.</div>
            <div class='hero-sub'>Real-time flights, curated itineraries, live weather, and AI-generated travel plans — all in one place.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Quick-start cards
    st.markdown("<div class='section-eyebrow'>WHAT YOU CAN DO</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Everything your trip needs</div>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    features = [
        ("✈️", "Live Flights", "Real-time prices from Google Flights via SerpAPI — updated every search."),
        ("🏙️", "Destination Photos", "Curated imagery of your destination city, airport, and attractions."),
        ("🤖", "AI Itinerary", "Gemini-powered day-by-day schedule with cost forecasting."),
        ("🌤️", "Live Weather", "Current conditions + 3-day forecast for your destination."),
    ]
    for col, (icon, title, desc) in zip([c1, c2, c3, c4], features):
        with col:
            st.markdown(f"""
            <div class='card'>
                <div style='font-size:32px;margin-bottom:12px'>{icon}</div>
                <div style='font-weight:700;font-size:17px;color:#f0ebe0;margin-bottom:8px'>{title}</div>
                <div style='font-size:13px;color:#5a6580;line-height:1.6'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Popular routes
    st.markdown("<div class='section-eyebrow'>POPULAR ROUTES</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Trending destinations</div>", unsafe_allow_html=True)

    routes = [
        ("Seoul → Tokyo", "ICN", "NRT", "~2h 30m", "From $180"),
        ("New York → London", "JFK", "LHR", "~7h 10m", "From $490"),
        ("Singapore → Bangkok", "SIN", "BKK", "~2h 20m", "From $95"),
        ("Dubai → Paris", "DXB", "CDG", "~7h 30m", "From $420"),
    ]
    rc1, rc2, rc3, rc4 = st.columns(4)
    for col, (name, src, dst, dur, price) in zip([rc1, rc2, rc3, rc4], routes):
        with col:
            st.markdown(f"""
            <div class='card' style='cursor:pointer'>
                <div style='font-size:13px;color:#5a6580;margin-bottom:6px'>{dur}</div>
                <div style='font-family:Playfair Display,serif;font-size:19px;color:#f0ebe0;margin-bottom:8px'>{name}</div>
                <div style='font-size:12px;color:#4ade80;font-weight:600'>{price}</div>
                <div style='font-size:11px;color:#2d3a56;margin-top:8px;font-family:DM Mono,monospace'>{src} → {dst}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE: DISCOVER (Images)
# ─────────────────────────────────────────────
elif nav == "🌅 Discover":
    st.markdown("<div class='page-wrap'>", unsafe_allow_html=True)
    
    dst = st.session_state.destination
    src = st.session_state.source
    city = city_name(dst)
    origin_city = city_name(src)

    st.markdown(f"<div class='section-eyebrow'>DESTINATION VISUAL GUIDE</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='section-title'>Explore <em style='color:#f5c842'>{city}</em></div>", unsafe_allow_html=True)

    # If no destination set, prompt
    if dst == "NRT" and not st.session_state.destination_images:
        st.info("ℹ️ Set your destination in **Plan Trip** first, then come back here for photos. Showing Tokyo for now.")

    with st.spinner("Loading destination imagery..."):
        if not st.session_state.destination_images:
            st.session_state.destination_images = fetch_unsplash(f"{city} city travel", 6)
        if not st.session_state.airport_images:
            st.session_state.airport_images = fetch_unsplash(f"{city} airport terminal", 3)
        if not st.session_state.poi_images:
            st.session_state.poi_images = fetch_unsplash(f"{city} landmarks attractions", 6)

    dest_imgs = st.session_state.destination_images
    airport_imgs = st.session_state.airport_images
    poi_imgs = st.session_state.poi_images

    # Hero destination mosaic
    if dest_imgs:
        st.markdown("<div class='section-eyebrow' style='margin-top:0'>CITY OVERVIEW</div>", unsafe_allow_html=True)
        if len(dest_imgs) >= 3:
            col_big, col_small = st.columns([2, 1])
            with col_big:
                st.markdown(f"""
                <div style='border-radius:16px;overflow:hidden;height:360px;'>
                    <img src='{dest_imgs[0]}' style='width:100%;height:100%;object-fit:cover;'/>
                </div>""", unsafe_allow_html=True)
            with col_small:
                for img in dest_imgs[1:3]:
                    st.markdown(f"""
                    <div style='border-radius:12px;overflow:hidden;height:170px;margin-bottom:8px;'>
                        <img src='{img}' style='width:100%;height:100%;object-fit:cover;'/>
                    </div>""", unsafe_allow_html=True)

        if len(dest_imgs) > 3:
            st.markdown("<br>", unsafe_allow_html=True)
            cols = st.columns(len(dest_imgs[3:]))
            for col, img in zip(cols, dest_imgs[3:]):
                with col:
                    st.markdown(f"""
                    <div style='border-radius:12px;overflow:hidden;height:160px;'>
                        <img src='{img}' style='width:100%;height:100%;object-fit:cover;'/>
                    </div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Airport section
    st.markdown(f"<div class='section-eyebrow'>WHERE YOU'LL LAND</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='section-title'>{airport_label(dst)}</div>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class='card' style='display:flex;gap:20px;align-items:center;margin-bottom:20px'>
        <div style='font-size:48px'>🛬</div>
        <div>
            <div style='font-size:22px;font-weight:700;color:#f0ebe0;font-family:DM Mono,monospace'>{dst}</div>
            <div style='font-size:14px;color:#7a8499;margin-top:4px'>{airport_label(dst)}</div>
            <div style='font-size:12px;color:#5a6580;margin-top:8px'>Departing from: <strong style='color:#f5c842'>{airport_label(src)} ({src})</strong></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if airport_imgs:
        cols = st.columns(3)
        for col, img in zip(cols, airport_imgs):
            with col:
                st.markdown(f"""
                <div style='border-radius:12px;overflow:hidden;height:200px;'>
                    <img src='{img}' style='width:100%;height:100%;object-fit:cover;'/>
                </div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Points of interest
    st.markdown(f"<div class='section-eyebrow'>PLACES TO VISIT</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='section-title'>Top attractions in {city}</div>", unsafe_allow_html=True)
    
    if poi_imgs:
        poi_cols = st.columns(3)
        poi_titles = ["Historic District", "Cultural Landmark", "Local Market", "Scenic Viewpoint", "Food Quarter", "Hidden Gem"]
        for i, (col, img) in enumerate(zip(poi_cols * 2, poi_imgs)):
            with col:
                st.markdown(f"""
                <div class='poi-card' style='margin-bottom:16px'>
                    <img src='{img}' class='poi-img'/>
                    <div class='poi-body'>
                        <div class='poi-tag'>{["🏛️ Heritage","🎭 Culture","🍜 Food","🌅 Scenic","🛍️ Shopping","💎 Hidden"][i % 6]}</div>
                        <div class='poi-title'>{poi_titles[i % len(poi_titles)]}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE: PLAN TRIP
# ─────────────────────────────────────────────
elif nav == "✈️ Plan Trip":
    st.markdown("<div class='page-wrap'>", unsafe_allow_html=True)

    st.markdown("<div class='section-eyebrow'>TRIP CONFIGURATION</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Set your parameters</div>", unsafe_allow_html=True)

    # Route
    st.markdown("""<div style='font-size:13px;color:#f5c842;font-weight:600;letter-spacing:3px;text-transform:uppercase;margin-bottom:16px'>ROUTE & DATES</div>""", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        src_in = st.text_input("🛫 Origin Airport Code", st.session_state.source, key="src_input")
    with c2:
        dst_in = st.text_input("🛬 Destination Airport Code", st.session_state.destination, key="dst_input")
    with c3:
        days_in = st.slider("Trip Duration (days)", 1, 21, st.session_state.days)

    c4, c5, c6 = st.columns(3)
    with c4:
        dep_date = st.date_input("Departure Date", st.session_state.departure_date)
    with c5:
        ret_date = st.date_input("Return Date", st.session_state.return_date)
    with c6:
        theme = st.selectbox("Travel Style", ["Solo Traveler", "Couple Getaway", "Family Vacation", "Adventure Group"], 
                             index=["Solo Traveler", "Couple Getaway", "Family Vacation", "Adventure Group"].index(st.session_state.travel_theme))

    st.markdown("<hr>", unsafe_allow_html=True)

    # Budget
    st.markdown("""<div style='font-size:13px;color:#f5c842;font-weight:600;letter-spacing:3px;text-transform:uppercase;margin-bottom:16px'>BUDGET & COMFORT</div>""", unsafe_allow_html=True)
    b1, b2, b3, b4 = st.columns(4)
    with b1:
        currency = st.selectbox("Currency", ["USD ($)", "EUR (€)", "KRW (₩)", "JPY (¥)", "GBP (£)"],
                                index=["USD ($)", "EUR (€)", "KRW (₩)", "JPY (¥)", "GBP (£)"].index(st.session_state.currency) 
                                      if st.session_state.currency in ["USD ($)", "EUR (€)", "KRW (₩)", "JPY (¥)", "GBP (£)"] else 0)
    with b2:
        max_budget = st.number_input("Max Budget", 100, 200000, st.session_state.max_budget, step=100)
    with b3:
        budget_tier = st.selectbox("Budget Tier", ["Economy/Backpacker", "Standard/Mid-range", "Premium/Luxury"],
                                   index=["Economy/Backpacker", "Standard/Mid-range", "Premium/Luxury"].index(st.session_state.budget_tier))
    with b4:
        flight_class = st.selectbox("Cabin Class", ["Economy Class", "Premium Economy", "Business Class", "First Class"],
                                    index=["Economy Class", "Premium Economy", "Business Class", "First Class"].index(st.session_state.flight_class))

    h1, h2 = st.columns(2)
    with h1:
        hotel_stars = st.selectbox("Hotel Standard", ["Hostels / Guesthouses", "3⭐ Comfort Stays", "4⭐ Premium Hotels", "5⭐ Luxury Resorts"],
                                   index=["Hostels / Guesthouses", "3⭐ Comfort Stays", "4⭐ Premium Hotels", "5⭐ Luxury Resorts"].index(st.session_state.hotel_stars))
    with h2:
        transit_style = st.selectbox("Local Transport", ["Public Transport Only", "Mixed (Trains & Rideshare)", "Private Taxis / Car Rental"],
                                     index=["Public Transport Only", "Mixed (Trains & Rideshare)", "Private Taxis / Car Rental"].index(st.session_state.transit_style) 
                                           if st.session_state.transit_style in ["Public Transport Only", "Mixed (Trains & Rideshare)", "Private Taxis / Car Rental"] else 1)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Interests
    st.markdown("""<div style='font-size:13px;color:#f5c842;font-weight:600;letter-spacing:3px;text-transform:uppercase;margin-bottom:16px'>INTERESTS & NOTES</div>""", unsafe_allow_html=True)
    i1, i2 = st.columns(2)
    with i1:
        activities = st.text_area("Core interests & must-see spots", st.session_state.activities, height=100)
    with i2:
        special_notes = st.text_input("Special requirements (optional)", st.session_state.special_notes)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── GO BUTTON ──
    if st.button("🚀 Generate Full Travel Plan", use_container_width=False):
        # Save to session
        st.session_state.source       = src_in.upper().strip()
        st.session_state.destination  = dst_in.upper().strip()
        st.session_state.days         = days_in
        st.session_state.departure_date = dep_date
        st.session_state.return_date   = ret_date
        st.session_state.travel_theme  = theme
        st.session_state.currency      = currency
        st.session_state.max_budget    = max_budget
        st.session_state.budget_tier   = budget_tier
        st.session_state.flight_class  = flight_class
        st.session_state.hotel_stars   = hotel_stars
        st.session_state.transit_style = transit_style
        st.session_state.activities    = activities
        st.session_state.special_notes = special_notes
        # Reset images so they reload with new destination
        st.session_state.destination_images = []
        st.session_state.airport_images = []
        st.session_state.poi_images = []

        sym = currency_sym(currency)
        dest_city = city_name(dst_in.upper().strip())

        # STEP 1: Flights
        with st.spinner("✈️  Fetching live flight prices from Google Flights..."):
            try:
                st.session_state.best_flights = fetch_flights_live(
                    src_in.upper(), dst_in.upper(), dep_date, ret_date)
            except Exception as e:
                st.error(f"Flight error: {e}")
                st.session_state.best_flights = []

        # ── Retry helper for Gemini 503 / high-demand errors ──
        import time

        # Model priority list: try in order until one succeeds
        GEMINI_MODELS = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]

        def run_agent_with_retry(agent_name, instructions, prompt, tools=None, max_retries=3):
            """Try each model in GEMINI_MODELS with exponential back-off on 503."""
            last_err = None
            for model_id in GEMINI_MODELS:
                for attempt in range(max_retries):
                    try:
                        kwargs = dict(
                            name=agent_name,
                            model=Gemini(id=model_id),
                            instructions=instructions,
                        )
                        if tools:
                            kwargs["tools"] = tools
                        agent = Agent(**kwargs)
                        res = agent.run(prompt, stream=False)
                        return res.content  # success
                    except Exception as e:
                        last_err = e
                        err_str = str(e)
                        # 503 / high demand → wait and retry
                        if "503" in err_str or "UNAVAILABLE" in err_str or "high demand" in err_str.lower():
                            wait = 2 ** attempt  # 1s, 2s, 4s
                            time.sleep(wait)
                            continue
                        # Any other error: skip to next model immediately
                        break
            return f"⚠️ All models unavailable. Last error: {last_err}"

        # STEP 2: Research
        with st.spinner("🔍  Researching attractions and admission prices..."):
            st.session_state.research_text = run_agent_with_retry(
                agent_name="Research Agent",
                instructions=f"Expert destination researcher. Provide top sites and ticket costs for {dst_in}. Use currency {sym}. Structured markdown, no greeting.",
                prompt=f"Top attractions + admission prices in {dest_city}. {activities}. {special_notes}. Currency: {sym}.",
                tools=[SerpApiTools(api_key=SERPAPI_API_KEY)],
            )

        # STEP 3: Hotels
        with st.spinner("🏨  Evaluating hotels and dining options..."):
            st.session_state.hotel_text = run_agent_with_retry(
                agent_name="Hotel Agent",
                instructions=f"Hospitality agent. Find lodging + dining for {dest_city}. Tier: {hotel_stars}/{budget_tier}. Prices in {sym}. Clean markdown.",
                prompt=f"Hotels and restaurants in {dest_city} for {hotel_stars}, budget tier {budget_tier}. Prices in {sym}.",
                tools=[SerpApiTools(api_key=SERPAPI_API_KEY)],
            )

        # STEP 4: Planner
        with st.spinner("🗺️  Building your personalised itinerary..."):
            st.session_state.itinerary_text = run_agent_with_retry(
                agent_name="Planner Agent",
                instructions=f"""Master Cost & Logistics Planner. Synthesize data into a premium plan.
RULES:
1. Start with '## 💰 TRIP EXPENSE SUMMARY' markdown table: Flights, Lodging, Transit, Food, Activities, Grand Total (max {sym}{max_budget}).
2. Day-by-day schedule with [Cost: {sym}XX] tags.
3. Transit style: {transit_style}. Cabin: {flight_class}. Theme: {theme}.""",
                prompt=f"{days_in}-day plan for {dest_city}. Currency {sym}. Budget {sym}{max_budget}.\nActivities: {st.session_state.research_text}\nLodging: {st.session_state.hotel_text}",
            )

        # STEP 5: Weather
        with st.spinner("🌤️  Fetching live weather data..."):
            wdata = get_weather(dest_city)
            if wdata:
                st.session_state.weather_text = wdata
            else:
                st.session_state.weather_text = None

        st.session_state.plan_ready = True
        st.success("✅ Plan generated! Navigate to **Itinerary** and **Weather** tabs.")
        st.rerun()

    # ── LIVE FLIGHTS PANEL (shown after search) ──
    if st.session_state.plan_ready and st.session_state.best_flights:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div class='section-eyebrow'>LIVE RESULTS</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Available flights</div>", unsafe_allow_html=True)

        flights = st.session_state.best_flights[:4]
        cols = st.columns(min(len(flights), 4))
        for i, (col, flight) in enumerate(zip(cols, flights)):
            with col:
                try:
                    price    = flight.get("price", "N/A")
                    duration = flight.get("total_duration", "?")
                    flist    = flight.get("flights", [{}])
                    airline  = flist[0].get("airline", "Unknown")
                    dep      = flist[0].get("departure_airport", {})
                    arr      = flist[-1].get("arrival_airport", {})
                    stops    = max(0, len(flist) - 1)
                    stop_txt = "Non-stop" if stops == 0 else f"{stops} stop{'s' if stops>1 else ''}"
                    best_tag = "<div class='flight-badge'>⭐ Best Value</div>" if i == 0 else ""
                    
                    dep_code = dep.get("id", st.session_state.source)
                    arr_code = arr.get("id", st.session_state.destination)

                    st.markdown(f"""
                    <div class='flight-card'>
                        <div class='airline-pill'>✈ {airline}</div>
                        <div class='flight-route'>
                            <div class='airport-code'>{dep_code}</div>
                            <div class='route-line'></div>
                            <div class='airport-code'>{arr_code}</div>
                        </div>
                        <div class='flight-meta'>{fmt_dt(dep.get("time",""))} → {fmt_dt(arr.get("time",""))}</div>
                        <div class='flight-meta'>{duration} min · {stop_txt}</div>
                        <div class='flight-price-big'>${price}</div>
                        <div class='flight-price-sub'>USD · round trip</div>
                        {best_tag}
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE: ITINERARY
# ─────────────────────────────────────────────
elif nav == "🗺️ Itinerary":
    st.markdown("<div class='page-wrap'>", unsafe_allow_html=True)

    city = city_name(st.session_state.destination)
    sym  = currency_sym(st.session_state.currency)

    st.markdown("<div class='section-eyebrow'>AI-GENERATED PLAN</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='section-title'>Your {st.session_state.days}-day {city} itinerary</div>", unsafe_allow_html=True)

    if not st.session_state.plan_ready:
        st.info("👉 Go to **Plan Trip** and hit Generate to create your itinerary.")
    else:
        # Stats row
        st.markdown(f"""
        <div class='stat-row'>
            <div class='stat-chip'>
                <div class='stat-chip-label'>Destination</div>
                <div class='stat-chip-value' style='font-size:18px'>{city}</div>
            </div>
            <div class='stat-chip'>
                <div class='stat-chip-label'>Duration</div>
                <div class='stat-chip-value'>{st.session_state.days}d</div>
            </div>
            <div class='stat-chip'>
                <div class='stat-chip-label'>Max Budget</div>
                <div class='stat-chip-value'>{sym}{st.session_state.max_budget:,}</div>
            </div>
            <div class='stat-chip'>
                <div class='stat-chip-label'>Style</div>
                <div class='stat-chip-value' style='font-size:15px'>{st.session_state.travel_theme}</div>
            </div>
            <div class='stat-chip'>
                <div class='stat-chip-label'>Cabin</div>
                <div class='stat-chip-value' style='font-size:15px'>{st.session_state.flight_class}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Hotel info
        if st.session_state.hotel_text:
            with st.expander("🏨 Lodging & Dining Options", expanded=False):
                st.markdown(f"""<div class='card'>{st.session_state.hotel_text}</div>""", unsafe_allow_html=True)

        # Main itinerary
        st.markdown("""<div style='font-size:13px;color:#f5c842;font-weight:600;letter-spacing:3px;text-transform:uppercase;margin:24px 0 16px'>FULL SCHEDULE & COST BREAKDOWN</div>""", unsafe_allow_html=True)
        st.markdown(f"<div class='card'>{st.session_state.itinerary_text}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE: WEATHER
# ─────────────────────────────────────────────
elif nav == "🌤️ Weather":
    st.markdown("<div class='page-wrap'>", unsafe_allow_html=True)

    city = city_name(st.session_state.destination)

    st.markdown("<div class='section-eyebrow'>LIVE CONDITIONS</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='section-title'>Weather in {city}</div>", unsafe_allow_html=True)

    if not st.session_state.plan_ready or not st.session_state.weather_text:
        # Try fetching live even without full plan
        with st.spinner("Fetching live weather..."):
            wdata = get_weather(city)
            if wdata:
                st.session_state.weather_text = wdata
    
    wdata = st.session_state.weather_text

    if wdata and isinstance(wdata, dict):
        w1, w2, w3 = st.columns(3)
        with w1:
            st.markdown(f"""
            <div class='card' style='text-align:center'>
                <div style='font-size:11px;letter-spacing:4px;color:#5a6580;text-transform:uppercase;margin-bottom:12px'>NOW</div>
                <div style='font-size:72px;font-weight:700;color:#f5c842'>{wdata["temp_c"]}°</div>
                <div style='font-size:16px;color:#9ba4b8;margin-top:8px'>{wdata["desc"]}</div>
                <div style='font-size:13px;color:#5a6580;margin-top:6px'>Feels like {wdata["feel"]}°C</div>
            </div>""", unsafe_allow_html=True)
        with w2:
            st.markdown(f"""
            <div class='card'>
                <div style='font-size:11px;letter-spacing:4px;color:#5a6580;text-transform:uppercase;margin-bottom:16px'>CONDITIONS</div>
                <div style='display:flex;justify-content:space-between;margin-bottom:12px'>
                    <span style='color:#5a6580'>Humidity</span>
                    <span style='color:#f0ebe0;font-weight:600'>{wdata["humid"]}%</span>
                </div>
                <div style='display:flex;justify-content:space-between;margin-bottom:12px'>
                    <span style='color:#5a6580'>Description</span>
                    <span style='color:#f0ebe0;font-weight:600'>{wdata["desc"]}</span>
                </div>
                <div style='display:flex;justify-content:space-between'>
                    <span style='color:#5a6580'>Feels Like</span>
                    <span style='color:#f0ebe0;font-weight:600'>{wdata["feel"]}°C</span>
                </div>
            </div>""", unsafe_allow_html=True)
        with w3:
            packing = []
            tc = wdata["temp_c"]
            if tc < 10: packing = ["🧥 Heavy coat", "🧣 Scarf & gloves", "👢 Warm boots"]
            elif tc < 18: packing = ["🧥 Light jacket", "👖 Long trousers", "👟 Closed shoes"]
            elif tc < 26: packing = ["👕 Light layers", "👟 Comfortable shoes", "🕶️ Sunglasses"]
            else: packing = ["👕 Breathable clothing", "🧴 Sunscreen SPF50+", "💧 Hydration bottle"]
            items_html = "".join(f"<div style='margin-bottom:8px;color:#e8e4dc;font-size:13px'>{p}</div>" for p in packing)
            st.markdown(f"""
            <div class='card'>
                <div style='font-size:11px;letter-spacing:4px;color:#5a6580;text-transform:uppercase;margin-bottom:16px'>PACKING TIPS</div>
                {items_html}
            </div>""", unsafe_allow_html=True)

        # 3-day forecast
        if wdata.get("forecast"):
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("<div class='section-eyebrow'>3-DAY FORECAST</div>", unsafe_allow_html=True)
            fcols = st.columns(3)
            icons = ["🌤️", "⛅", "🌥️", "🌧️", "⛈️", "🌩️", "☀️"]
            for col, day in zip(fcols, wdata["forecast"]):
                with col:
                    st.markdown(f"""
                    <div class='card' style='text-align:center'>
                        <div style='font-size:11px;color:#5a6580;margin-bottom:8px'>{day["date"]}</div>
                        <div style='font-size:36px;margin-bottom:8px'>☁️</div>
                        <div style='font-size:13px;color:#9ba4b8;margin-bottom:12px'>{day["desc"]}</div>
                        <div style='display:flex;justify-content:center;gap:16px'>
                            <span style='color:#f5c842;font-weight:700'>{day["hi"]}°</span>
                            <span style='color:#5a6580'>{day["lo"]}°</span>
                        </div>
                    </div>""", unsafe_allow_html=True)
    else:
        st.info(f"Live weather data for {city} will appear after you generate a plan, or it failed to load. Try again.")
        if st.button("🔄 Retry Weather"):
            st.session_state.weather_text = None
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
