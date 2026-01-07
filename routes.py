from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    flash,
    redirect,
    url_for,
    current_app,
    session,
)
import ai_interpretations
from astro_calculations import calculate_astro_data
from datetime import datetime
import json
import logging
from utils import (
    parse_time_flexible,
    convert_times_to_str,
    get_element_class,
    Constants,
)

bp = Blueprint("main", __name__)
logger = logging.getLogger(__name__)

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@bp.route("/results", methods=["GET", "POST"])
def show_results():
    try:
        if request.method == "POST":
            # Formdan gelen verileri al
            data = request.form
            birth_date_str = data["birth_date"]
            birth_time_str = data["birth_time"]
            latitude_str = data["latitude"]
            longitude_str = data["longitude"]
            user_name = data.get("name", "Değerli Danışanım")
            
            # Transit bilgileri (opsiyonel)
            transit_date = data.get("transit_date")
            transit_time = data.get("transit_time")
            transit_lat = data.get("transit_latitude")
            transit_lng = data.get("transit_longitude")
            
            transit_info = None
            if transit_date and transit_time:
                transit_info = {
                    "date": transit_date,
                    "time": transit_time,
                    "latitude": float(transit_lat) if transit_lat else float(latitude_str),
                    "longitude": float(transit_lng) if transit_lng else float(longitude_str)
                }

            # Astrolojik hesaplamaları yap
            birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
            birth_time = parse_time_flexible(birth_time_str)
            
            astro_data = calculate_astro_data(
                birth_date=birth_date,
                birth_time=birth_time,
                latitude=float(latitude_str),
                longitude=float(longitude_str),
                transit_info=transit_info
            )

            if not astro_data or "error" in astro_data:
                flash("Hesaplama sırasında bir hata oluştu.")
                return redirect(url_for("main.dashboard"))

            # Kullanıcı bilgilerini ekle
            astro_data["user_name"] = user_name
            astro_data["birth_info"] = {
                "date": birth_date_str,
                "time": birth_time_str,
                "location": {"latitude": latitude_str, "longitude": longitude_str, "name": data.get("birth_place_suggestion", "")}
            }

            return render_template("new_result.html", astro_data=astro_data)
        
        # GET ise (doğrudan linkle gelindiyse)
        return render_template("new_result.html", astro_data=None)

    except Exception as e:
        logger.error(f"show_results hatası: {str(e)}", exc_info=True)
        flash("Bir hata oluştu.")
        return redirect(url_for("main.dashboard"))

@bp.route("/api/get_ai_interpretation", methods=["POST"])
def api_get_ai_interpretation():
    try:
        data = request.get_json()
        interpretation_type = data.get("interpretation_type", "daily")
        astro_data = data.get("astro_data", {})
        user_name = data.get("user_name", "Değerli Danışanım")
        
        result = ai_interpretations.get_ai_interpretation_engine(astro_data, interpretation_type, user_name)
        return jsonify(result)
    except Exception as e:
        logger.error(f"API hatası: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@bp.route("/settings")
def settings():
    return render_template("settings.html") # Eğer varsa
