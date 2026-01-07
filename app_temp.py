from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    session,
    flash,
    current_app,
)
from flask_session import Session  # Flask-Session modülünü içe aktar
from astro_calculations import calculate_astro_data
import os
from datetime import datetime, date, time
import json
from flask.json.provider import DefaultJSONProvider
import requests
from requests.adapters import HTTPAdapter
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import logging

# from .tts_server import create_tts_app # Replaced by tts_utils
from location_service import LocationService
from dotenv import load_dotenv

# from ai_interpretations import get_hyperbolic_interpretation # Eski importu yorum satırı yap veya sil
from ai_interpretations import (
    get_gemini_interpretation,
)  # Hyperbolic yerine Gemini'yi import et

# Load environment variables (optional, but good practice if .env is used)
load_dotenv()

# Logging yapılandırması
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Flask uygulaması
app = Flask(__name__, static_folder="static", static_url_path="/static")

# Configuration import from config.py
from config import Config

# Apply configuration
app.config.from_object(Config)

# Session configuration - Environment-aware setup
app.config["SESSION_FILE_DIR"] = os.path.join(app.instance_path, "sessions")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_FILE_THRESHOLD"] = 100  # Maksimum session dosyası sayısını azalt
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_NAME"] = "astro_session"
app.config["SESSION_FILE_MODE"] = 0o600  # Session dosyası erişim izinlerini sınırla

# SESSION_COOKIE_SECURE environment'dan gelir (config.py'de ayarlı)

# Create session directory if it doesn't exist
os.makedirs(app.config["SESSION_FILE_DIR"], exist_ok=True)

# Flask-Session başlat
sess = Session()
sess.init_app(app)

HYPERBOLIC_API_KEY = os.getenv(
    "HYPERBOLIC_API_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJpa2luY2l5ZW5pa2l0YXA1NEBnbWFpbC5jb20iLCJpYXQiOjE3MjY5MzkwNjl9.fIXOKvamoJLKvAhpnhl7pelXSwzmXMcNF8ZVR2uQGrY",
)


# JSON serileştirme için özel encoder (eski json.dump için)
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, time):
            return obj.strftime("%H:%M")
        return super().default(obj)


# JSON serileştirme için özel provider (Flask 2.2+ için modern yöntem)
class DateTimeJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, time):
            return obj.strftime("%H:%M")
        return super().default(obj)


# JSON provider'ı kaydet
app.json = DateTimeJSONProvider(app)


# Gezegen sembolü filtresi
def get_planet_symbol(planet_name):
    """Jinja2 filtresi: Gezegen adından sembol döndürür."""
    symbols = {
        "Sun": "☉",
        "Moon": "☽",
        "Mercury": "☿",
        "Venus": "♀",
        "Mars": "♂",
        "Jupiter": "♃",
        "Saturn": "♄",
        "Uranus": "♅",
        "Neptune": "♆",
        "Pluto": "♇",
    }
    return symbols.get(planet_name, planet_name)


# Element sınıfı filtresi
def element_class(sign):
    """Jinja2 filtresi: Burç isminden CSS sınıfı döndürür."""
    element_classes = {
        "Koç": "fire",
        "Aslan": "fire",
        "Yay": "fire",
        "Boğa": "earth",
        "Başak": "earth",
        "Oğlak": "earth",
        "İkizler": "air",
        "Terazi": "air",
        "Kova": "air",
        "Yengeç": "water",
        "Akrep": "water",
        "Balık": "water",
    }
    return element_classes.get(sign, "")


# Zodyak burcu filtresi
def get_zodiac_sign(degree):
    """Jinja2 filtresi: Dereceye göre Zodyak burcunu döndürür."""
    signs = [
        (0, "Koç"), (30, "Boğa"), (60, "İkizler"), (90, "Yengeç"),
        (120, "Aslan"), (150, "Başak"), (180, "Terazi"), (210, "Akrep"),
        (240, "Yay"), (270, "Oğlak"), (300, "Kova"), (330, "Balık")
    ]
    degree = float(degree) % 360  # Dereceyi 0-360 aralığına normalize et
    for sign_degree, sign_name in reversed(signs):
        if degree >= sign_degree:
            return sign_name
    return "Bilinmeyen" # Bu durum normalde oluşmamalı


@app.template_filter("safe_round")
def safe_round(value, decimals=2):
    """Güvenli yuvarlama filtresi."""
    try:
        if value is None:
            return "-"
        val = float(value)
        return round(val, decimals) if not isinstance(val, str) else "-"
    except (ValueError, TypeError):
        return "-"


# Jinja2 filtrelerini kaydet
app.jinja_env.filters["planet_symbol"] = get_planet_symbol 
app.jinja_env.filters["element_class"] = element_class
app.jinja_env.filters["get_zodiac_sign"] = get_zodiac_sign
app.jinja_env.filters["safe_round"] = safe_round


# Ana sayfa
@app.route("/")
def index():
    return render_template(
        "index.html", opencage_api_key=app.config["OPENCAGE_API_KEY"]
    )


# Dashboard
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    return render_template("dashboard.html")


# Hesaplama rotası
@app.route("/perform_calculation", methods=["POST"])
def perform_calculation():
    """Astrolojik hesaplamaları yapar ve sonuçları kaydeder."""
    try:
        if not request.form:
            flash("Form verisi bulunamadı.", "error")
            return redirect(url_for("dashboard"))

        session["calculation_complete"] = True

        data = request.form

        # Form verilerini alırken None kontrolü yap veya varsayılan değer ata
        birth_date_str = data.get("birth_date")
        birth_time_str = data.get("birth_time")
        latitude_str = data.get("latitude")
        longitude_str = data.get("longitude")

        birth_date = None
        if birth_date_str:
            try:
                birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
            except ValueError:
                flash("Geçersiz doğum tarihi formatı.", "error")
                return redirect(url_for("dashboard"))

        birth_time = None
        if birth_time_str:
            try:
                birth_time = datetime.strptime(birth_time_str, "%H:%M").time()
            except ValueError:
                flash("Geçersiz doğum saati formatı.", "error")
                return redirect(url_for("dashboard"))

        latitude = None
        if latitude_str:
            try:
                latitude = float(latitude_str)
            except ValueError:
                flash("Geçersiz enlem formatı.", "error")
                return redirect(url_for("dashboard"))

        longitude = None
        if longitude_str:
            try:
                longitude = float(longitude_str)
            except ValueError:
                flash("Geçersiz boylam formatı.", "error")
                return redirect(url_for("dashboard"))

        # Gerekli alanların dolu olduğunu kontrol et
        if not birth_date or not birth_time or latitude is None or longitude is None:
             flash("Doğum tarihi, saati, enlem ve boylam bilgileri eksik veya hatalı.", "error")
             return redirect(url_for("dashboard"))

        # BirthInfo modelinin import edildiği varsayılarak kullanılıyor
        # birth_info = BirthInfo(
        #     name=data.get("name"),
        #     birth_date=birth_date,
        #     birth_time=birth_time,
        #     birth_place=data.get("birth_place"),
        #     latitude=latitude,
        #     longitude=longitude,
        # )

        # Calculate astro data
        # calculate_astro_data fonksiyonunun datetime objesi beklediği varsayılıyor
        birth_dt_obj = datetime.combine(birth_date, birth_time)
        astro_data = calculate_astro_data(
            birth_date=birth_dt_obj, # datetime objesini gönder
            birth_time=birth_dt_obj.time(), # time objesini gönder (calculate_astro_data'nın beklediği formata göre ayarlanmalı)
            latitude=latitude,
            longitude=longitude,
        )

        # Add name to astro_data
        astro_data["name"] = data.get("name", "Anonymous")

        # Save to session file with proper JSON encoding
        session_dir = os.path.join(app.instance_path, "sessions")
        os.makedirs(session_dir, exist_ok=True)
        # birth_info.id yerine zaman damgası veya başka bir benzersiz tanımlayıcı kullan
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        session_file = os.path.join(session_dir, f"astro_data_{timestamp}.json")

        # Veriyi JSON formatına dönüştürmeden önce houses verilerini düzelt
        result_data = astro_data.copy()
        if "houses" in result_data:
            if "Houses" in result_data["houses"]:
                result_data["houses"]["Houses"] = {
                    str(k): float(v) for k, v in result_data["houses"]["Houses"].items()
                }
            if "house_cusps" in result_data["houses"]:
                result_data["houses"]["house_cusps"] = {
                    str(k): float(v)
                    for k, v in result_data["houses"]["house_cusps"].items()
                }

        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(result_data, f, cls=DateTimeEncoder, ensure_ascii=False, indent=2)

        return redirect(url_for("dashboard"))
    except Exception as e:
        flash(f"Hesaplama sırasında hata oluştu: {str(e)}", "error")
        return redirect(url_for("dashboard"))