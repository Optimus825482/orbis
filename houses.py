# -*- coding: utf-8 -*-
import logging
import swisseph as swe
from datetime import timedelta
from core import get_zodiac_sign, get_degree_in_sign, get_decan

logger = logging.getLogger(__name__)

def get_house_number(longitude, house_cusps):
    """Bir boylamın (longitude) hangi evde olduğunu belirler.
    House cusps dict'i { '1': degree, '2': degree, ... '12': degree } formatında olmalıdır."""
    lon = longitude % 360
    if lon < 0: lon += 360

    try:
        cusps = [float(house_cusps[str(i + 1)]) % 360 for i in range(12)]
    except (KeyError, ValueError, TypeError):
        logger.error("Geçersiz ev cusp verisi formatı, ev numarası belirlenemiyor.")
        return 0

    for i in range(12):
        current_cusp = cusps[i]
        next_cusp = cusps[(i + 1) % 12]

        if current_cusp < next_cusp:
            if current_cusp <= lon < next_cusp:
                return i + 1
        else: # next_cusp < current_cusp (0/360 sınırını geçti)
            if lon >= current_cusp or lon < next_cusp:
                 return i + 1
    return 1

def calculate_houses(dt_object, latitude, longitude, house_system=b"P"):
    """Doğum tarihi, saati ve konuma göre evleri hesaplar."""
    try:
        # Türkiye için sabit GMT+3 farkı varsayımı:
        dt_utc = dt_object - timedelta(hours=3) # UTC+3 Local -> UTC
        hour_decimal = dt_utc.hour + (dt_utc.minute / 60.0) + (dt_utc.second / 3600.0)
        jd_ut = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour_decimal)

        (cusps, ascmc) = swe.houses_ex(jd_ut, float(latitude), float(longitude), house_system)

        house_cusps_list = [c % 360 for c in list(cusps)[:12]]
        house_cusps = {str(i + 1): round(house_cusps_list[i], 2) for i in range(12)}

        ascmc_list = [a % 360 for a in list(ascmc)[:4]]

        important_angles = {
            "ascendant": round(ascmc_list[0], 2),
            "mc": round(ascmc_list[1], 2),
            "armc": round(ascmc_list[2], 2),
            "vertex": round(ascmc_list[3], 2),
        }

        return {
            "house_cusps": house_cusps,
            "important_angles": important_angles,
            "house_system": house_system.decode('utf-8') if isinstance(house_system, bytes) else str(house_system),
        }

    except Exception as e:
        logger.error(f"calculate_houses fonksiyonunda hata: {str(e)}", exc_info=True)
        return {
            "house_cusps": {str(i+1): 0.0 for i in range(12)},
            "important_angles": {"ascendant": 0.0, "mc": 0.0, "armc": 0.0, "vertex": 0.0},
            "house_system": house_system.decode('utf-8') if isinstance(house_system, bytes) else str(house_system),
            "error": str(e)
        }

def calculate_house_for_degree(degree, birth_dt, latitude, longitude, house_system=b"P"):
    """Verilen derecenin hangi evde olduğunu hesaplar."""
    try:
        houses_data = calculate_houses(birth_dt, latitude, longitude, house_system)
        return get_house_number(degree, houses_data["house_cusps"])
    except Exception as e:
        logger.error(f"Ev hesaplama hatası: {str(e)}")
        return 1
