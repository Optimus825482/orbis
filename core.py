# -*- coding: utf-8 -*-
import os
import math
import logging
from datetime import datetime, timedelta, date, time
from decimal import Decimal, ROUND_DOWN
import requests
import swisseph as swe

# Logging settings
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constants
RESET = "\033[0m"
BOLD = "\033[1m"
COLOR_LIST = [
    "\033[93m",  # sarı
    "\033[92m",  # yeşil
    "\033[96m",  # cyan
    "\033[95m",  # mor
    "\033[94m",  # mavi
]

# Swiss Ephemeris settings
REMOTE_EPHE_BASE_URL = "https://erkanerdem.net/ephe/"
IS_SERVERLESS = os.environ.get("VERCEL") or os.environ.get("NETLIFY") or os.environ.get("GAE_SERVICE")

if IS_SERVERLESS:
    SWISSEPH_DATA_DIR = "/tmp/ephe"
    logger.info("Serverless ortam algılandı, efemeris dizini /tmp/ephe olarak ayarlandı.")
else:
    SWISSEPH_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ephe")

def ensure_ephe_file(filename):
    """Eğer dosya yerelde yoksa uzak sunucudan indirir."""
    local_path = os.path.join(SWISSEPH_DATA_DIR, filename)
    if not os.path.exists(local_path):
        try:
            remote_url = REMOTE_EPHE_BASE_URL + filename
            logger.info(f"Efemeris dosyası indiriliyor: {filename} ...")
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(remote_url, headers=headers, timeout=30)
            if response.status_code == 200:
                with open(local_path, "wb") as f:
                    f.write(response.content)
                logger.info(f"Başarıyla indirildi: {filename}")
                return True
            else:
                logger.error(f"Dosya indirilemedi ({response.status_code}): {filename}")
        except Exception as e:
            logger.error(f"İndirme hatası ({filename}): {str(e)}")
    return os.path.exists(local_path)

# Initialize Swiss Ephemeris
if not os.path.exists(SWISSEPH_DATA_DIR):
    os.makedirs(SWISSEPH_DATA_DIR, exist_ok=True)

core_files = ["sepl_00.se1", "semo_00.se1", "seas_00.se1"]
for cf in core_files:
    ensure_ephe_file(cf)

swe.set_ephe_path(SWISSEPH_DATA_DIR)
logger.info(f"Swiss Ephemeris veri yolu ayarlandı: {SWISSEPH_DATA_DIR}")

def julday_to_datetime(jd_ut):
    """Julian günü datetime objesine çevirir."""
    try:
        jd_local = jd_ut + 3.0/24.0  # 3 saat ekle (UTC+3)
        day_frac = Decimal(str(jd_local % 1))
        hour = int((day_frac * 24).quantize(Decimal('1.'), rounding=ROUND_DOWN))
        minute = int(((day_frac * 24 - hour) * 60).quantize(Decimal('1.'), rounding=ROUND_DOWN))
        second = int(((day_frac * 24 * 60 - hour * 60 - minute) * 60).quantize(Decimal('1.'), rounding=ROUND_DOWN))
        year, month, day, _ = swe.revjul(jd_local)
        return datetime(year, month, day, hour, minute, second)
    except Exception as e:
        logger.error(f"julday_to_datetime fonksiyonunda hata: {str(e)}", exc_info=True)
        return None

def get_zodiac_sign(degree):
    """Dereceye göre burcu döndürür."""
    zodiac_signs = [
        "Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak",
        "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık",
    ]
    normalized_degree = degree % 360
    if normalized_degree < 0:
        normalized_degree += 360
    sign_index = int(normalized_degree // 30)
    return zodiac_signs[sign_index]

def get_degree_in_sign(degree):
    """Derecenin burç içindeki derecesini döndürür."""
    normalized_degree = degree % 360
    if normalized_degree < 0:
        normalized_degree += 360
    return normalized_degree % 30

def get_decan(degree_in_sign):
    """Burç içindeki dereceye göre dekanı döndürür."""
    return int(degree_in_sign // 10) + 1

def get_element(sign):
    """Burcun elementini döndürür."""
    elements = {
        "Koç": "Ateş", "Aslan": "Ateş", "Yay": "Ateş",
        "Boğa": "Toprak", "Başak": "Toprak", "Oğlak": "Toprak",
        "İkizler": "Hava", "Terazi": "Hava", "Kova": "Hava",
        "Yengeç": "Su", "Akrep": "Su", "Balık": "Su",
    }
    return elements.get(sign, "Bilinmiyor")

def get_modality(sign):
    """Burcun niteliğini (Kardinal, Sabit, Değişken) döndürür."""
    modalities = {
        "Koç": "Kardinal", "Yengeç": "Kardinal", "Terazi": "Kardinal", "Oğlak": "Kardinal",
        "Boğa": "Sabit", "Aslan": "Sabit", "Akrep": "Sabit", "Kova": "Sabit",
        "İkizler": "Değişken", "Başak": "Değişken", "Yay": "Değişken", "Balık": "Değişken",
    }
    return modalities.get(sign, "Bilinmiyor")

def get_polarity(sign):
    """Burcun polaritesini (Erkek/Dişi) döndürür."""
    polarities = {
        "Koç": "Erkek", "İkizler": "Erkek", "Aslan": "Erkek", "Terazi": "Erkek", "Yay": "Erkek", "Kova": "Erkek",
        "Boğa": "Dişi", "Yengeç": "Dişi", "Başak": "Dişi", "Akrep": "Dişi", "Oğlak": "Dişi", "Balık": "Dişi",
    }
    return polarities.get(sign, "Bilinmiyor")

def ensure_json_serializable(obj):
    """Recursively converts objects to JSON serializable types."""
    if isinstance(obj, dict):
        return {str(k): ensure_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [ensure_json_serializable(elem) for elem in obj]
    elif isinstance(obj, tuple):
        return tuple(ensure_json_serializable(elem) for elem in obj)
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    elif isinstance(obj, (datetime, date, time)):
        return obj.isoformat()
    else:
        return str(obj)

def convert_house_data_to_strings(data):
    """Ev verilerini, özellikle cusp listesini string anahtarlı dictionary'ye dönüştürür."""
    if isinstance(data, (list, tuple)):
        return {str(i + 1): round(float(v), 2) for i, v in enumerate(data)}
    elif isinstance(data, dict):
        return {str(k): convert_house_data_to_strings(v) if isinstance(v, (list, tuple, dict)) else v for k, v in data.items()}
    return data
