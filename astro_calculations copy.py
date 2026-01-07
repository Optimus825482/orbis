# -*- coding: utf-8 -*-
"""
Astrolojik hesaplamalar için Swisseph kütüphanesini kullanan modül.
Tecrübeli bir yazılım mühendisi ve astroloji uzmanı tarafından gözden
geçirilmiş ve güncellenmiştir.
"""
import math
from flask import jsonify
import swisseph as swe
from datetime import datetime, timedelta, date, time
import logging
from decimal import Decimal, ROUND_DOWN

def julday_to_datetime(jd_ut):
    """Julian günü datetime objesine çevirir."""
    try:
        # Julian günü UT'den yerel zamana çevir (GMT+3 için)
        jd_local = jd_ut + 3.0/24.0  # 3 saat ekle (UTC+3)
        
        # Decimal kullanarak hassas hesaplama yap
        day_frac = Decimal(str(jd_local % 1))
        hour = int((day_frac * 24).quantize(Decimal('1.'), rounding=ROUND_DOWN))
        minute = int(((day_frac * 24 - hour) * 60).quantize(Decimal('1.'), rounding=ROUND_DOWN))
        second = int(((day_frac * 24 * 60 - hour * 60 - minute) * 60).quantize(Decimal('1.'), rounding=ROUND_DOWN))
        
        # swe.revjul fonksiyonu ile tarihi al (yıl, ay, gün)
        year, month, day, _ = swe.revjul(jd_local)
        
        return datetime(year, month, day, hour, minute, second)
    except Exception as e:
        logger.error(f"julday_to_datetime fonksiyonunda hata: {str(e)}", exc_info=True)
        return None

# Logging ayarları
# Daha detaylı log için level=logging.DEBUG yapabilirsiniz.
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Swiss Ephemeris dosya yolunu ayarla (Efemeris verisinin bulunduğu dizin)
# swe.set_ephe_path("ephe")
# Eğer 'ephe' dizini projenizle aynı seviyedeyse veya sistemde SWISSEPH_DATA
# environment variable'ı ayarlıysa bu satıra gerek kalmaz.
# Özel bir dizin belirtmek isterseniz bu satırı kullanın ve 'ephe' yerine dizin yolunu yazın.
SWISSEPH_DATA = "C:\\ephe" # Örnek dizin, kendi dizininizi ayarlayın
swe.set_ephe_path(SWISSEPH_DATA)


def convert_house_data_to_strings(data):
    """Ev verilerini, özellikle cusp listesini string anahtarlı dictionary'ye dönüştürür."""
    if isinstance(data, (list, tuple)):
        # Liste formatını {1: degree, 2: degree, ...} formatına çevir
        return {str(i + 1): round(float(v), 2) for i, v in enumerate(data)}
    elif isinstance(data, dict):
        # Dictionary içinde nested liste/tuple/dict varsa onları da çevir
        return {str(k): convert_house_data_to_strings(v) if isinstance(v, (list, tuple, dict)) else v for k, v in data.items()}
    return data


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
    # logger.debug(f"{degree:.2f} derece burcu: {zodiac_signs[sign_index]}")
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


def get_house_number(longitude, house_cusps):
    """Bir boylamın (longitude) hangi evde olduğunu belirler.
    House cusps dict'i { '1': degree, '2': degree, ... '12': degree } formatında olmalıdır."""
    lon = longitude % 360
    if lon < 0: lon += 360

    # Ev cusp derecelerini al ve 0-360 arasına normalize et
    # house_cusps dictionary'sinin string key'lere sahip olduğu varsayılır.
    try:
        cusps = [float(house_cusps[str(i + 1)]) % 360 for i in range(12)]
    except (KeyError, ValueError, TypeError):
        logger.error("Geçersiz ev cusp verisi formatı, ev numarası belirlenemiyor.")
        return 0 # Hata durumunda 0 döndür

    # Ev 1'den başlayarak kontrol et
    for i in range(12):
        # Mevcut evin başlagıç cuspu (i+1. ev = i. indexteki cusp)
        current_cusp = cusps[i]
        # Sonraki evin başlagıç cuspu (i+2. ev = (i+1). indexteki cusp, 12'den sonra 1'e döner)
        next_cusp = cusps[(i + 1) % 12]

        # Normal durum (cusplar art arda)
        if current_cusp < next_cusp:
            if current_cusp <= lon < next_cusp:
                return i + 1
        # Wrap-around durumu (örn. 12. ev 270 derece Başak'tan başlar, 1. ev 15 derece Akrep'e gider)
        else: # next_cusp < current_cusp (0/360 sınırını geçti)
            if lon >= current_cusp or lon < next_cusp:
                 return i + 1

    # Bu noktaya gelinmemeli, ancak fallback olarak House 1 döndürebiliriz
    # Eğer boylam tam olarak son cusp üzerindeyse son eve ait olmalı.
    # Yukarıdaki >= kullanımı bu durumu ele alır.
    # Eğer hala bulunamadıysa, cusplarda bir sorun olabilir veya boylam çok hassas bir noktada.
    # logger.warning(f"Boylam ({lon:.2f}) için ev belirlenemedi, varsayılan 1. ev atanıyor. Cusps: {cusps}")
    return 1 # Fallback


# Evlerin hesaplanması
def calculate_houses(dt_object, latitude, longitude, house_system=b"P"):
    """Doğum tarihi, saati ve konuma göre evleri hesaplar.
    dt_object: datetime objesi (Yerel saat)
    latitude: float
    longitude: float
    house_system: bytes (örn. b"P" Placidus, b"R" Regiomontanus, vb.)
    """
    try:
        if isinstance(dt_object, datetime):
            # Swisseph UT Julian günü bekler.
            # Giriş dt_object'in yerel saat olduğunu varsayalım ve UTC'ye dönüştürelim.
            # Türkiye için sabit GMT+3 farkı varsayımı:
            dt_utc = dt_object - timedelta(hours=3) # UTC+3 Local -> UTC
            
            jd_ut = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                            dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0)
        else:
            raise TypeError("dt_object must be a datetime.datetime object")

        # houses_ex daha detaylı bilgi verir (asc, mc, vs.)
        # (cusps, ascmc) = swe.houses(jd_ut, float(latitude), float(longitude), house_system)
        (cusps, ascmc) = swe.houses_ex(jd_ut, float(latitude), float(longitude), house_system)


        # Ev tepelerini ve önemli noktaları al
        # houses_ex'in cusps sonucu 0-11 indexleri 1-12. ev cusplarıdır
        # ascmc sonucu indexleri: 0=Asc, 1=MC, 2=ARMC (Aries Point), 3=Vertex
        # Cuspları 0-360 arasına normalize edelim (swe genellikle bunu yapar ama emin olalım)
        house_cusps_list = [c % 360 for c in list(cusps)[:12]] # Sadece ilk 12 cusp

        # Ev pozisyonlarını dictionary'ye dönüştür (anahtarlar string olmalı)
        house_cusps = {str(i + 1): round(house_cusps_list[i], 2) for i in range(12)}


        # Yükselen (Ascendant), MC, Vertex gibi noktaları ekle
        # ascmc listesinden gelen değerleri de 0-360 arasına normalize edelim
        ascmc_list = [a % 360 for a in list(ascmc)[:4]] # Sadece ilk 4 (Asc, MC, ARMC, Vertex)

        important_angles = {
            "ascendant": round(ascmc_list[0], 2),
            "mc": round(ascmc_list[1], 2),
            "armc": round(ascmc_list[2], 2),
            "vertex": round(ascmc_list[3], 2),
        }

        logger.debug(f"Hesaplanan evler (cusps): {house_cusps}")
        logger.debug(f"Hesaplanan önemli açılar: {important_angles}")

        result = {
            "house_cusps": house_cusps, # 1-12 ev başlangıçları
            "important_angles": important_angles, # Asc, MC, ARMC, Vertex
            "house_system": house_system.decode('utf-8') if isinstance(house_system, bytes) else str(house_system),
        }

        return result

    except Exception as e:
        logger.error(f"calculate_houses fonksiyonunda hata: {str(e)}", exc_info=True)
        # Hata durumunda boş veya tanımlı bir yapı döndür
        return {"house_cusps": {str(i+1): 0.0 for i in range(12)}, "important_angles": {"ascendant": 0.0, "mc": 0.0, "armc": 0.0, "vertex": 0.0}, "house_system": house_system.decode('utf-8') if isinstance(house_system, bytes) else str(house_system), "error": str(e)}


# Gezegen pozisyonları (derece, burç, retrograd, hız ve ev bilgileri)
def calculate_celestial_positions(dt_object, house_cusps, celestial_bodies_ids):
    """Belirli bir datetime objesi, ev cuspları ve göksel cisim ID'leri listesi için pozisyonları hesaplar.
    dt_object: datetime objesi (Yerel saat)
    house_cusps: calculate_houses'dan dönen house_cusps dict'i
    celestial_bodies_ids: { "İsim": swe.ID } formatında dict.
    """
    try:
        dt_utc = dt_object - timedelta(hours=3) # UTC+3 Local -> UTC
        jd_ut = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                           dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0)

        positions = {}
        for name, planet_id in celestial_bodies_ids.items():
            try:
                # Vulkanus (id 17) swisseph default kurulumda olmayabilir, atla
                if planet_id == 17: # swe.VULKANUS
                     # logger.debug("Vulkanus hesaplanması atlandı (ID 17 genellikle standart efemerislerde bulunmaz).")
                     continue

                # swe.calc_ut UT Julian günü bekler
                # pozisyon [lon, lat, dist, speed in lon, speed in lat, speed in dist]
                # FLG_SWIEPH varsayılan bayraklar için iyi bir başlangıçtır.
                pos_result = swe.calc_ut(jd_ut, planet_id, swe.FLG_SWIEPH)

                # Hata kontrolü
                if not pos_result or not pos_result[0]:
                     # logger.debug(f"{name} pozisyonu hesaplanamadı veya hata oluştu: {pos_result[1] if pos_result else 'Unknown error'}")
                     positions[name] = {
                        "degree": 0.0, "sign": "Bilinmiyor", "retrograde": False,
                        "house": 0, "speed": 0.0, "latitude": 0.0, "distance": 0.0, "error": pos_result[1] if pos_result else "Unknown error"
                     }
                     continue

                pos = pos_result[0]
                lon = pos[0]
                lat = pos[1]
                dist = pos[2]
                speed = pos[3] # Hız boylamda (longitude)

                is_retrograde = speed < 0

                # Ev belirleme (calculate_houses'dan gelen house_cusps dict'i kullanılır)
                house_num = get_house_number(lon, house_cusps) # house_cusps boşsa veya hatalıysa 0 dönebilir

                positions[name] = {
                    "degree": round(lon % 360, 2), # Dereceyi 0-360 arasına normalize et
                    "sign": get_zodiac_sign(lon),
                    "retrograde": is_retrograde,
                    "house": house_num,
                    "speed": round(speed, 4),
                    "latitude": round(lat, 4),
                    "distance": round(dist, 4),
                    "degree_in_sign": round(get_degree_in_sign(lon), 2),
                    "decan": get_decan(get_degree_in_sign(lon))
                }

            except Exception as e:
                logger.error(f"{name} hesaplanırken hata: {str(e)}", exc_info=True)
                positions[name] = {
                    "degree": 0.0, "sign": "Bilinmiyor", "retrograde": False,
                    "house": 0, "speed": 0.0, "latitude": 0.0, "distance": 0.0, "error": str(e)
                }

        return positions

    except Exception as e:
        logger.error(
            f"calculate_celestial_positions fonksiyonunda hata: {str(e)}", exc_info=True
        )
        return {} # Hata durumunda boş sözlük döndür


# Natal Gezegen Pozisyonları (calculate_celestial_positions kullanılır)
def calculate_natal_planet_positions(birth_dt, natal_house_cusps):
    """Natal gezegen pozisyonlarını hesaplar."""
    planet_ids = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY,
        "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER,
        "Saturn": swe.SATURN, "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE,
        "Pluto": swe.PLUTO,
    }
    logger.info("Natal gezegen pozisyonları hesaplanıyor...")
    positions = calculate_celestial_positions(birth_dt, natal_house_cusps, planet_ids)
    logger.info(f"Natal gezegen pozisyonları hesaplandı ({len(positions)} adet).")
    return positions

# Natal Ekstra Noktalar Pozisyonları (calculate_celestial_positions kullanılır)
def calculate_natal_additional_points(birth_dt, natal_house_cusps):
    """Natal ekstra noktaların (asteroidler, düğümler, lilith, uranian vb.) pozisyonlarını hesaplar."""
    point_ids = {
        "Chiron": swe.CHIRON, "Ceres": swe.CERES, "Pallas": swe.PALLAS,
        "Juno": swe.JUNO, "Vesta": swe.VESTA,
        "Mean_Node": swe.MEAN_NODE, "True_Node": swe.TRUE_NODE,
        "Mean_Lilith": swe.MEAN_APOG, "True_Lilith": swe.OSCU_APOG,
        # Uranian/Hamburg planets (bazıları standar efemeriste olmayabilir)
        "Cupido": swe.CUPIDO, "Hades": swe.HADES, "Zeus": swe.ZEUS,
        "Kronos": swe.KRONOS, "Apollon": swe.APOLLON, "Admetos": swe.ADMETOS,
        "Vulkanus": swe.VULKANUS, "Poseidon": swe.POSEIDON,
    }
    logger.info("Natal ekstra noktalar pozisyonları hesaplanıyor...")
    positions = calculate_celestial_positions(birth_dt, natal_house_cusps, point_ids)
    logger.info(f"Natal ekstra noktalar pozisyonları hesaplandı ({len(positions)} adet).")
    return positions


# Natal veya transit-natal açı hesaplamaları
def calculate_aspects(positions1, positions2=None, orb=None):
    """İki set pozisyon arasındaki (natal-natal veya transit-natal) açıları hesaplar.

    Args:
        positions1 (dict): Gezegen/nokta pozisyonları dict'i (örn. natal pozisyonlar)
        positions2 (dict, optional): İki set pozisyonları (örn. transit pozisyonları).
                                     None ise positions1 kendi içinde kıyaslanır (natal-natal).
        orb (dict, optional): Açı tipleri için özel orb değerleri (örn. {"Conjunction": 8, ...}).
                              Yoksa varsayılanlar kullanılır.

    Returns:
        list: Bulunan açıların listesi [{planet1, planet2, aspect_type, orb}, ...]
    """
    try:
        # Varsayılan orb değerleri (daha esnek olabilir veya yapılandırılabilir)
        default_orbs = {
            "Conjunction": 8.0, "Opposition": 8.0, "Trine": 8.0, "Square": 8.0, "Sextile": 6.0,
            # Minör açılar için daha küçük orb kullanılabilir
            "Quincunx": 2.0, "Semisextile": 1.0, "Semisquare": 2.0, "Sesquiquadrate": 2.0,
        }
        orbs_to_use = orb if isinstance(orb, dict) else default_orbs

        aspects_list = []
        # Sadece 'degree' anahtarı olan geçerli pozisyonları al
        valid_positions1 = {k: v for k, v in positions1.items() if isinstance(v, dict) and 'degree' in v}
        valid_positions2 = {k: v for k, v in (positions2.items() if positions2 is not None else positions1.items()) if isinstance(v, dict) and 'degree' in v}


        planets1_keys = list(valid_positions1.keys())
        planets2_keys = list(valid_positions2.keys())


        # Açı dereceleri
        aspect_degrees = {
            "Conjunction": 0.0, "Sextile": 60.0, "Square": 90.0, "Trine": 120.0, "Opposition": 180.0,
            "Quincunx": 150.0, "Semisextile": 30.0, "Semisquare": 45.0, "Sesquiquadrate": 135.0,
        }

        for p1_key in planets1_keys:
            deg1 = valid_positions1[p1_key]['degree'] % 360 # Normalize

            for p2_key in planets2_keys:
                 deg2 = valid_positions2[p2_key]['degree'] % 360 # Normalize

                 # Natal-natal kıyaslama yapılıyorsa aynı gezegeni veya çiftleri atla (Sun-Moon vs Moon-Sun)
                 if positions2 is None and p1_key >= p2_key:
                     continue

                 # Açı farkını hesapla (0-180 derece aralığında)
                 diff = abs(deg1 - deg2)
                 aspect_diff = min(diff, 360 - diff) # En kısa yay

                 found_aspect = None
                 min_orb = float('inf')

                 for aspect_name, ideal_degree in aspect_degrees.items():
                    current_orb_limit = orbs_to_use.get(aspect_name, 0.0) # Orb limitini al
                    if current_orb_limit <= 0: continue # Orb 0 veya negatifse bu açıyı kontrol etme

                    # Açı farkını ideal dereceye göre orb içinde mi kontrol et
                    # Farklı açı tipleri için farklı kontrol yöntemleri olabilir, özellikle 0/180 çevresi
                    orb_value = abs(aspect_diff - ideal_degree)

                    # Kavuşum (0) ve Karşıt (180) özel kontrolü (0-360 farkı üzerinden)
                    if aspect_name == "Conjunction":
                        orb_value = min(abs(deg1 - deg2), 360 - abs(deg1 - deg2)) # 0'a yakınlık
                    elif aspect_name == "Opposition":
                        orb_value = min(abs(deg1 - deg2 - 180) % 360, abs(deg1 - deg2 + 180) % 360) # 180'e yakınlık


                    if orb_value <= current_orb_limit:
                        # Birden fazla orb içinde olabilir, en küçüğünü al (hassas açı)
                        if orb_value < min_orb:
                            min_orb = orb_value
                            found_aspect = {
                                "planet1": p1_key,
                                "planet2": p2_key,
                                "aspect_type": aspect_name,
                                "orb": round(orb_value, 2),
                                "exact_difference_0_180": round(aspect_diff, 2) # 0-180 fark
                            }

                 if found_aspect:
                     aspects_list.append(found_aspect)


        # Orb'a göre sırala
        aspects_list = sorted(aspects_list, key=lambda x: x["orb"])

        logger.info(f"Hesaplanan açı sayısı: {len(aspects_list)}")
        # logger.debug(f"Hesaplanan açılar: {aspects_list}")
        return aspects_list

    except Exception as e:
        logger.error(f"calculate_aspects fonksiyonunda hata: {str(e)}", exc_info=True)
        return [] # Hata durumunda boş liste döndür


# Burcun elementini belirleyen fonksiyon
def get_element(sign):
    """Burcun elementini döndürür."""
    elements = {
        "Koç": "Ateş", "Aslan": "Ateş", "Yay": "Ateş",
        "Boğa": "Toprak", "Başak": "Toprak", "Oğlak": "Toprak",
        "İkizler": "Hava", "Terazi": "Hava", "Kova": "Hava",
        "Yengeç": "Su", "Akrep": "Su", "Balık": "Su",
    }
    return elements.get(sign, "Bilinmiyor")

# Burcun niteliğini belirleyen fonksiyon (Kardinal, Sabit, Değişken)
def get_modality(sign):
    """Burcun niteliğini (Kardinal, Sabit, Değişken) döndürür."""
    modalities = {
        "Koç": "Kardinal", "Yengeç": "Kardinal", "Terazi": "Kardinal", "Oğlak": "Kardinal",
        "Boğa": "Sabit", "Aslan": "Sabit", "Akrep": "Sabit", "Kova": "Sabit",
        "İkizler": "Değişken", "Başak": "Değişken", "Yay": "Değişken", "Balık": "Değişken",
    }
    return modalities.get(sign, "Bilinmiyor")

# Burcun polaritesini belirleyen fonksiyon (Erkek/Pozitif, Dişi/Negatif)
def get_polarity(sign):
    """Burcun polaritesini (Erkek/Dişi) döndürür."""
    polarities = {
        "Koç": "Erkek", "İkizler": "Erkek", "Aslan": "Erkek", "Terazi": "Erkek", "Yay": "Erkek", "Kova": "Erkek",
        "Boğa": "Dişi", "Yengeç": "Dişi", "Başak": "Dişi", "Akrep": "Dişi", "Oğlak": "Dişi", "Balık": "Dişi",
    }
    return polarities.get(sign, "Bilinmiyor")


# Natal harita özet yorumunun oluşturulması (Basit versiyon)
def get_natal_summary(natal_planet_positions, natal_houses_data, birth_dt):
    """Natal harita için özet bir yorum metni listesi oluşturur."""
    try:
        interpretations = []

        # Ascendant bilgisi (important_angles içinde olması beklenir)
        # Hata durumunda None gelirse kontrol edelim
        ascendant_deg = natal_houses_data.get("important_angles", {}).get("ascendant")
        if ascendant_deg is not None:
             ascendant_sign = get_zodiac_sign(ascendant_deg)
             ascendant_deg_in_sign = get_degree_in_sign(ascendant_deg)
             ascendant_decan = get_decan(ascendant_deg_in_sign)
             interpretations.append(f"Yükselen: {ascendant_sign} {ascendant_deg_in_sign:.2f}° ({ascendant_decan}. dekan)")
        else:
             interpretations.append("Yükselen burç hesaplanamadı.")


        # Güneş ve Ay bilgisi
        sun_pos = natal_planet_positions.get("Sun")
        moon_pos = natal_planet_positions.get("Moon")
        if sun_pos and moon_pos and 'sign' in sun_pos and 'sign' in moon_pos:
            sun_sign = sun_pos["sign"]
            moon_sign = moon_pos["sign"]
            sun_house = sun_pos.get("house", "Bilinmiyor")
            moon_house = moon_pos.get("house", "Bilinmiyor")
            interpretations.append(f"Güneş ({sun_sign} - {sun_house}. ev) ve Ay ({moon_sign} - {moon_house}. ev) pozisyonları temel karakterinizi ve duygusal ihtiyaçlarınızı gösterir.")
            interpretations.append(f"Güneş-Ay kombinasyonu: {sun_sign} / {moon_sign}.")
        else:
             interpretations.append("Güneş veya Ay pozisyonu hesaplanamadı.")


        # Element ve Nitelik dağılımı
        elements = {"Ateş": 0, "Toprak": 0, "Hava": 0, "Su": 0}
        modalities = {"Kardinal": 0, "Sabit": 0, "Değişken": 0}
        polarities = {"Erkek": 0, "Dişi": 0}

        # Ana gezegenleri kullanarak dağılımı hesapla (Uranüs, Neptün, Plüton da dahil edilebilir isteğe bağlı)
        planets_for_distribution = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"] # Tüm gezegenleri dahil edelim

        for planet in planets_for_distribution:
             if planet in natal_planet_positions and 'sign' in natal_planet_positions[planet]:
                  sign = natal_planet_positions[planet]["sign"]
                  elements[get_element(sign)] += 1
                  modalities[get_modality(sign)] += 1
                  polarities[get_polarity(sign)] += 1

        # Baskın element/nitelik/polarite kontrolü (en az bir gezegen olmalı)
        dominant_element = max(elements.items(), key=lambda x: x[1]) if any(elements.values()) else ("Bilinmiyor", 0)
        dominant_modality = max(modalities.items(), key=lambda x: x[1]) if any(modalities.values()) else ("Bilinmiyor", 0)
        dominant_polarity = max(polarities.items(), key=lambda x: x[1]) if any(polarities.values()) else ("Bilinmiyor", 0)

        if dominant_element[1] > 0: interpretations.append(f"Baskın Element: {dominant_element[0]} ({dominant_element[1]} gezegen).")
        interpretations.append(f"Element Dağılımı: Ateş: {elements['Ateş']}, Toprak: {elements['Toprak']}, Hava: {elements['Hava']}, Su: {elements['Su']}.")
        if dominant_modality[1] > 0: interpretations.append(f"Baskın Nitelik: {dominant_modality[0]} ({dominant_modality[1]} gezegen).")
        interpretations.append(f"Nitelik Dağılımı: Kardinal: {modalities['Kardinal']}, Sabit: {modalities['Sabit']}, Değişken: {modalities['Değişken']}.")
        if dominant_polarity[1] > 0: interpretations.append(f"Baskın Polarite: {dominant_polarity[0]} ({dominant_polarity[1]} gezegen).")


        # Retrograd gezegenler
        retrogrades = [
            planet
            for planet, details in natal_planet_positions.items()
            if details.get("retrograde", False) is True # retrograde key'i varsa ve True ise
        ]
        if retrogrades:
            interpretations.append(f"Retrograd gezegenler: {', '.join(retrogrades)}.")
        # else: # Retrograd gezegen olmaması da bir bilgidir, ama yorumu uzatmamak için sadece varsa ekleyelim.
        #    interpretations.append("Natal haritada retrograd gezegen yok.")

        # Evlerdeki gezegen yoğunluğu
        houses_dict = {i: [] for i in range(1, 13)}
        # Hem gezegenleri hem de ek noktaları evlere dağıtalım
        all_natal_celestial_bodies = {}
        all_natal_celestial_bodies.update(natal_planet_positions)
        # Uranian gezegenleri hariç diğer ek noktaları dahil edelim (Çok fazla uranian evi kalabalıklaştırabilir)
        points_to_include_in_houses = ["Chiron", "Ceres", "Pallas", "Juno", "Vesta", "True_Node", "Mean_Node", "True_Lilith", "Mean_Lilith"]
        
        natal_additional_points = calculate_natal_additional_points(birth_dt, natal_houses_data["house_cusps"])
        # Ek noktaları da dahil et
        # Ek noktaları natal_planet_positions ile birleştiriyoruz
        
        
        for point_name in points_to_include_in_houses:
             if point_name in natal_additional_points:
                 all_natal_celestial_bodies[point_name] = natal_additional_points[point_name]


        for body_name, details in all_natal_celestial_bodies.items():
            if "house" in details and isinstance(details["house"], int) and 1 <= details["house"] <= 12:
                houses_dict[details["house"]].append(body_name)

        populated_houses = {house: p for house, p in houses_dict.items() if p}
        for house in sorted(populated_houses.keys()):
            interpretations.append(f"{house}. Ev: {', '.join(populated_houses[house])}.")

        logger.info("Natal özet yorum oluşturuldu.")
        # logger.debug(f"Natal yorum: {interpretations}")
        return interpretations

    except Exception as e:
        logger.error(f"Natal özet yorum oluşturma hatası: {str(e)}", exc_info=True)
        return ["Yorum oluşturulurken bir hata oluştu."]


# Vimshottari Dasa hesaplaması (Basit/Tahmini model, detaylı için Jyotish kütüphanesi gerekir)
# NOT: Bu implementasyon standart Vimshottari Dasa'nın basitleştirilmiş bir versiyonudur.
# Doğum anındaki Ay'ın Nakshatra'sına göre Dasa başlangıcını bulur ve bugüne kadar ilerletir.
# Hassas hesaplamalar için tam bir Jyotish kütüphanesi (örn. Akhila, PJV) gerekebilir.
def get_vimshottari_dasa(birth_dt, natal_moon_degree):
    """Vimshottari Dasa periyotlarını hesaplar."""
    try:
        # Dasa Periyotları (Yıl olarak)
        dasa_years = {
            "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
            "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17,
        }
        dasa_order = [
            "Ketu", "Venus", "Sun", "Moon", "Mars",
            "Rahu", "Jupiter", "Saturn", "Mercury",
        ] # Ketu'dan başlayan sıra

        if natal_moon_degree is None:
             return {"error": "Ay pozisyonu bulunamadığı için Vimshottari Dasa hesaplanamadı."}

        # Ay'ın hangi Nakshatra'da olduğunu bul (360 derece / 27 Nakshatra = ~13.3333 derece/Nakshatra)
        # Nakshatra pozisyonu 0'dan başlar (Aswini 0-13.33...)
        nakshatra_span = 360/27.0
        nakshatra_degree = natal_moon_degree % 360
        if nakshatra_degree < 0: nakshatra_degree += 360

        nakshatra_index_at_birth = int(nakshatra_degree / nakshatra_span) # 0-26 arası index

        # Nakshatra Yöneticileri Sırası (Ay'ın konumuna göre Dasa başlangıcı)
        # Aswini -> Ketu, Bharani -> Venus, Krittika -> Sun ... Revati -> Mercury
        # Bu sıra 9 gezegen için 3 kere tekrarlanır. Nakshatra indexine göre yönetici:
        dasa_lords_by_nakshatra_index = [
            "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
            "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
            "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
        ] # 27 nakshatra için 9 yöneticinin tekrarı
        start_dasa_lord = dasa_lords_by_nakshatra_index[nakshatra_index_at_birth]
        start_dasa_index_in_order = dasa_order.index(start_dasa_lord)

        # Doğum anında mevcut Dasa periyodunun ne kadarının geçtiğini hesapla
        degree_in_nakshatra = nakshatra_degree % nakshatra_span # Ay'ın Nakshatra içindeki derecesi
        # Nakshatra'nın kalan kısmı, doğum anındaki Dasa'nın kalan periyodunu belirler
        # Bu, Ay'ın Nakshatra'ya giriş derecesi değil, Nakshatra'nın başlangıcından itibaren geçen derecedir.
        # Kalan derece = (Nakshatra'nın tam derecesi - Nakshatra içinde geçen derece)
        remaining_degree_in_nakshatra = nakshatra_span - degree_in_nakshatra

        # Kalan Dasa periyodu (doğum anında) = (Nakshatra'nın kalan derecesi / Nakshatra'nın tam derecesi) * O Dasa'nın tam periyodu
        remaining_dasa_at_birth_years = (remaining_degree_in_nakshatra / nakshatra_span) * dasa_years[start_dasa_lord]

        # Doğum anındaki Dasa'nın bitiş tarihini hesapla
        start_dasa_end_date = birth_dt + timedelta(days=remaining_dasa_at_birth_years * 365.25)

        current_dasa_lord = start_dasa_lord
        current_dasa_start_date = birth_dt # Başlangıç tarihi doğum tarihi
        current_dasa_end_date = start_dasa_end_date
        dasa_cycle_index = start_dasa_index_in_order # Ana Dasa döngüsündeki index

        # Şu anki tarihe kadar hangi Dasa'ların geçtiğini bul
        now = datetime.now()
        while now >= current_dasa_end_date:
            # Bir sonraki Dasa'ya geç
            dasa_cycle_index = (dasa_cycle_index + 1) % 9
            current_dasa_lord = dasa_order[dasa_cycle_index]
            current_dasa_start_date = current_dasa_end_date # Yeni Dasa, eskisinin bittiği gün başlar
            current_dasa_duration_years = dasa_years[current_dasa_lord]
            current_dasa_end_date = current_dasa_start_date + timedelta(days=current_dasa_duration_years * 365.25) # Yeni Dasa'nın bitişi

        # Mevcut Ana Dasa'nın detaylarını bulduk. Şimdi Antardasa (Bhukti) hesapla
        # Antardasa (Bhukti) döngüsü, Ana Dasa lordunun kendi Antardasası ile başlar
        # Dasa sırasını Ana Dasa lordu ile başlat
        bhukti_order = dasa_order[dasa_cycle_index:] + dasa_order[:dasa_cycle_index]

        bhukti_total_years_passed_in_dasa = 0 # Ana Dasa periyodu içinde geçen bhukti süreleri toplamı (yıl)
        current_bhukti_lord = bhukti_order[0] # Varsayılan olarak ilk bhukti lordu (Ana Dasa lordu)
        current_bhukti_start_date = current_dasa_start_date # İlk bhukti ana dasa ile başlar
        current_bhukti_end_date = None # Başlangıçta bilinmiyor

        # Ana Dasa'nın toplam süresi (gün olarak)
        current_dasa_total_days = (current_dasa_end_date - current_dasa_start_date).days

        for bhukti_lord in bhukti_order:
            # Antardasa süresi (gün olarak) = (Ana Dasa Süresi (gün) * Antardasa Lordunun Süresi (yıl)) / Toplam Dasa Süresi (120 yıl)
            bhukti_duration_days = (current_dasa_total_days * dasa_years[bhukti_lord]) / 120.0

            current_bhukti_end_date = current_bhukti_start_date + timedelta(days=bhukti_duration_days)

            if now < current_bhukti_end_date:
                 current_bhukti_lord = bhukti_lord
                 break # Bhukti bulundu

            current_bhukti_start_date = current_bhukti_end_date # Sonraki bhukti şimdikinin bittiği yerden başlar


        # Kalan süreyi hesapla (gün olarak)
        remaining_in_current_bhukti_days = (current_bhukti_end_date - now).days if current_bhukti_end_date else 0
        remaining_in_current_dasa_days = (current_dasa_end_date - now).days if current_dasa_end_date else 0


        return {
            "main_dasa_lord": current_dasa_lord,
            "sub_dasa_lord": current_bhukti_lord,
            "main_dasa_start_date": current_dasa_start_date.strftime("%Y-%m-%d"),
            "main_dasa_end_date": current_dasa_end_date.strftime("%Y-%m-%d"),
            "sub_dasa_start_date": current_bhukti_start_date.strftime("%Y-%m-%d") if current_bhukti_start_date else "N/A",
            "sub_dasa_end_date": current_bhukti_end_date.strftime("%Y-%m-%d") if current_bhukti_end_date else "N/A",
            "remaining_days_in_main_dasa": remaining_in_current_dasa_days,
            "remaining_days_in_sub_dasa": remaining_in_current_bhukti_days,
            "note": "Bu Vimshottari Dasa hesaplaması basitleştirilmiştir ve hassasiyet için tam bir Jyotish kütüphanesi gerekebilir."
        }

    except Exception as e:
        logger.error(f"Vimshottari Dasa hesaplama hatası: {str(e)}", exc_info=True)
        return {"error": f"Vimshottari Dasa hesaplama hatası: {str(e)}"}

# Firdaria periyotları hesaplaması
def get_firdaria_period(birth_dt, natal_sun_pos, natal_houses_data):
    """Doğum tarihine ve Güneş'in evine göre Firdaria periyotlarını hesaplar."""
    try:
        # Gündüz veya Gece doğumu kontrolü
        # Güneş 1. evden 6. eve kadar ise gündüz, 7. evden 12. eve kadar ise gece kabul edilir.
        sun_house = natal_sun_pos.get("house") if natal_sun_pos else None

        if sun_house is None or sun_house == 0:
             # Eğer güneşin evi hesaplanamadıysa veya geçersizse, saati kullanarak kaba bir tahmin yapalım.
             # Ancak ev daha doğrudur. Loglama ile uyarı verelim.
             logger.warning(f"Güneş evi belirlenemedi ({sun_house}), Firdaria için kaba saat tahmini kullanılıyor.")
             is_daytime_birth = 6 <= birth_dt.hour < 18
        else:
             is_daytime_birth = 1 <= sun_house <= 6


        # Firdaria Süreleri (Yıl olarak)
        period_years = {
            "Sun": 10, "Venus": 8, "Mercury": 13, "Moon": 9,
            "Saturn": 11, "Jupiter": 12, "Mars": 7,
            # Kuzey ve Güney Düğümleri de dahil edilebilir (standart 7 gezegen sisteminde yok)
            # "North Node": 3, "South Node": 2, # Toplam 75 yıl olur
        }
        total_cycle_years = sum(period_years.values()) # 72 yıl (7 gezegen için)

        # Firdaria Sırası (Gündüz ve Gece doğumuna göre)
        # 7 gezegenli sistem
        firdaria_sequence_day = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]
        firdaria_sequence_night = ["Moon", "Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury"] # Bu sıra doğrudur

        # Doğum tarihinden bugüne kadar geçen gün sayısı
        age_in_days = (datetime.now() - birth_dt).days
        age_in_years = age_in_days / 365.25 # Geçen yaklaşık yıl

        # Hangi ana periyotta olduğunu bul (72 yıllık döngüler halinde)
        current_sequence = firdaria_sequence_day if is_daytime_birth else firdaria_sequence_night
        years_passed_in_total_cycles = int(age_in_years / total_cycle_years) * total_cycle_years # Tam döngülerde geçen yıl
        years_passed_in_current_cycle = age_in_years - years_passed_in_total_cycles # Mevcut döngüde geçen yıl

        accumulated_years_in_cycle = 0 # Mevcut döngü içinde biriken yıl
        main_ruler = None
        main_period_start_date = None
        main_period_end_date = None


        for i, planet in enumerate(current_sequence):
            duration = period_years[planet]

            if years_passed_in_current_cycle < accumulated_years_in_cycle + duration:
                main_ruler = planet
                # Ana periyot başlangıç tarihi = Doğum tarihi + (Tam döngüler * 72 yıl + Mevcut döngüde bu periyottan önceki süre) gün
                total_days_before_main_period = (years_passed_in_total_cycles + accumulated_years_in_cycle) * 365.25
                main_period_start_date = birth_dt + timedelta(days = total_days_before_main_period)
                main_period_end_date = main_period_start_date + timedelta(days = duration * 365.25) # Ana periyot bitiş tarihi

                # Alt periyodu (Sub-ruler) hesapla
                # Alt periyot döngüsü Ana Periyot yöneticisi ile başlar
                sub_sequence_start_index = current_sequence.index(main_ruler)
                sub_sequence = current_sequence[sub_sequence_start_index:] + current_sequence[:sub_sequence_start_index]

                # Ana periyot içinde geçen gün sayısı
                days_passed_in_main_period = (datetime.now() - main_period_start_date).days

                accumulated_sub_days = 0 # Ana periyot içinde biriken alt periyot günleri
                sub_ruler = None
                sub_period_start_date = main_period_start_date # İlk alt periyot ana periyotla başlar
                sub_period_end_date = None

                for sub_planet in sub_sequence:
                    # Alt periyot süresi (gün olarak) = (Ana Periyot Süresi (gün) * Alt Periyot Lordunun Süresi (yıl)) / Toplam Döngü Süresi (72 yıl)
                    sub_duration_days = ((main_period_end_date - main_period_start_date).days * period_years[sub_planet]) / total_cycle_years

                    sub_period_end_date = sub_period_start_date + timedelta(days=sub_duration_days)

                    if datetime.now() < sub_period_end_date:
                        sub_ruler = sub_planet
                        break # Alt periyot bulundu

                    sub_period_start_date = sub_period_end_date # Sonraki alt periyot şimdikinin bittiği yerden başlar

                break # Ana periyot bulundu

            accumulated_years_in_cycle += duration


        if main_ruler and sub_ruler and main_period_start_date and main_period_end_date and sub_period_start_date and sub_period_end_date:
            remaining_in_main_period_days = (main_period_end_date - datetime.now()).days
            remaining_in_sub_period_days = (sub_period_end_date - datetime.now()).days

            logger.info(f"Firdaria hesaplandı: Ana: {main_ruler}, Alt: {sub_ruler}")
            return {
                "main_ruler": main_ruler,
                "sub_ruler": sub_ruler,
                "main_period_start_date": main_period_start_date.strftime("%Y-%m-%d"),
                "main_period_end_date": main_period_end_date.strftime("%Y-%m-%d"),
                "sub_period_start_date": sub_period_start_date.strftime("%Y-%m-%d"),
                "sub_period_end_date": sub_period_end_date.strftime("%Y-%m-%d"),
                "remaining_days_in_main_period": remaining_in_main_period_days,
                "remaining_days_in_sub_period": remaining_in_sub_period_days,
                "is_daytime_birth": is_daytime_birth,
                "note": "Bu Firdaria hesaplaması 7 gezegenli 72 yıllık döngüyü varsayar. Diğer sistemler (örn. düğümler dahil) farklı olabilir."
            }
        else:
            logger.warning("Firdaria periyodu bulunamadı. Hesaplamada bir hata olabilir.")
            return {"error": "Firdaria periyodu hesaplanamadı."}


    except Exception as e:
        logger.error(f"Firdaria hesaplama hatası: {str(e)}", exc_info=True)
        return {"error": f"Firdaria hesaplama hatası: {str(e)}"}


# Harmonik harita hesaplaması (Herhangi bir harmonik sayı için)
def get_harmonic_chart(dt_object, harmonic_number, celestial_bodies_positions):
    """Belirli bir datetime objesi ve N. harmonik sayı için gezegen pozisyonlarını hesaplar.
    celestial_bodies_positions: { "İsim": {"degree": X, ...} } formatında dict.
    """
    try:
        if not isinstance(harmonic_number, int) or harmonic_number <= 0:
             raise ValueError("Harmonik sayı pozitif bir tam sayı olmalıdır.")

        harmonic_positions = {}
        for name, data in celestial_bodies_positions.items():
             if 'degree' not in data:
                 logger.warning(f"Harmonik {harmonic_number} için {name} pozisyonu (degree) eksik, atlandı.")
                 continue
             lon = data['degree']

             # Harmonik derece = (Natal Derece * Harmonik Sayı) % 360
             harmonic_degree = (lon * harmonic_number) % 360
             if harmonic_degree < 0: harmonic_degree += 360

             harmonic_positions[name] = {
                 "degree": round(harmonic_degree, 2),
                 "sign": get_zodiac_sign(harmonic_degree),
                 "degree_in_sign": round(get_degree_in_sign(harmonic_degree), 2)
             }
             # logger.debug(f"H{harmonic_number} {name}: {harmonic_positions[name]['degree']:.2f}° {harmonic_positions[name]['sign']}")

        logger.info(f"Harmonik H{harmonic_number} haritası hesaplandı ({len(harmonic_positions)} adet).")
        return harmonic_positions

    except Exception as e:
        logger.error(f"get_harmonic_chart ({harmonic_number}) fonksiyonunda hata: {str(e)}", exc_info=True)
        return {}

# Derin harmonik analiz (Birden çok harmonik)
def calculate_deep_harmonic_analysis(birth_dt, natal_celestial_positions):
    """Doğum tarihine göre çeşitli N. harmonik haritaların gezegen pozisyonlarını hesaplar.
    natal_celestial_positions: { "İsim": {"degree": X, ...} } formatında dict. (Tüm natal noktalar)
    """
    try:
        logger.info("Derin harmonik analiz hesaplanıyor...")

        # Harmonik sayıları ve anlamları
        harmonics_to_calculate = {
            7: {"name": "Saptamsa (D7)", "details": "Çocuklar, yaratıcılık, torunlar"},
            9: {"name": "Navamsa (D9)", "details": "Evlilik, partner, dharma, ruhsal yolculuk"},
            10: {"name": "Dasamsa (D10)", "details": "Kariyer, meslek, toplumsal statü"},
            12: {"name": "Dvadasamsa (D12)", "details": "Ebeveynler, geçmiş yaşamlar"},
            16: {"name": "Shodasamsa (D16)", "details": "Taşıtlar, gayrimenkul, genel mutluluk/üzüntü"},
            20: {"name": "Vimsamsa (D20)", "details": "Ruhsal gelişim, ibadet, inanç"},
            24: {"name": "Chaturvimsamsa (D24)", "details": "Eğitim, bilgi, öğrenme"},
            27: {"name": "Nakshatramsa (D27) / Bhamsa", "details": "Güç, zayıflık, fiziksel dayanıklılık"},
            30: {"name": "Trimsamsa (D30)", "details": "Zorluklar, talihsizlikler, hastalıklar"},
            40: {"name": "Khavedamsa (D40)", "details": "Kişinin 'iyi' ve 'kötü' eylemleri, ruhsal yolculuk"},
            45: {"name": "Akshavedamsa (D45)", "details": "Genel kader, karakter, ahlak"},
            # Diğer Batı harmonikleri eklenebilir (örn. 4, 5, 8, 11, 13, 14, 15)
        }

        deep_harmonic_analysis = {}

        for harmonic_number, info in harmonics_to_calculate.items():
            # calculate_celestial_positions'ı her harmonik için tekrar çağırmak yerine,
            # natal pozisyonları alıp harmonik dönüşümü yapmak daha verimli.
            harmonic_positions = get_harmonic_chart(birth_dt, harmonic_number, natal_celestial_positions) # Burada natal_celestial_positions kullanılır

            deep_harmonic_analysis[f"H{harmonic_number}"] = {
                "name": info["name"],
                "details": info["details"],
                "planet_positions": harmonic_positions,
            }

        logger.info(f"Derin harmonik analiz tamamlandı ({len(deep_harmonic_analysis)} harmonik hesaplandı).")
        return deep_harmonic_analysis

    except Exception as e:
        logger.error(f"calculate_deep_harmonic_analysis fonksiyonunda hata: {str(e)}", exc_info=True)
        return {}


# Transit gezegen pozisyonlarının hesaplanması (Belirli bir tarih/saat için)
# calculate_celestial_positions kullanılır
def get_transit_positions(transit_dt, latitude, longitude):
    """Belirli bir transit tarihi, saati ve konuma göre gezegen pozisyonlarını hesaplar."""
    try:
        logger.info(f"Transit gezegen pozisyonları hesaplanıyor: {transit_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        # Transit anı için evleri hesapla (transit evler için konuma ihtiyaç duyarız)
        transit_houses_data = calculate_houses(transit_dt, latitude, longitude, b"P")
        transit_house_cusps = transit_houses_data.get("house_cusps", {})

        if not transit_house_cusps or any(v is None for v in transit_house_cusps.values()): # Geçersiz cusp kontrolü
             logger.warning("Transit ev pozisyonları hesaplanamadı veya eksik.")
             # Devam etmek için boş cusp dict kullan, bu durumda ev bilgisi doğru olmaz
             transit_house_cusps = {str(i+1): 0.0 for i in range(12)}


        planet_ids = {
            "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY,
            "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER,
            "Saturn": swe.SATURN, "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE,
            "Pluto": swe.PLUTO,
             "True_Node": swe.TRUE_NODE, # Transit Düğümler
        }

        # calculate_celestial_positions'ı kullanarak transit pozisyonlarını hesapla
        transit_positions = calculate_celestial_positions(transit_dt, transit_house_cusps, planet_ids)


        logger.info(f"Transit gezegen pozisyonları hesaplandı ({len(transit_positions)} adet).")
        return transit_positions, transit_houses_data # Transit pozisyonları ve Transit ev verisini döndür

    except Exception as e:
        logger.error(f"get_transit_positions fonksiyonunda hata: {str(e)}", exc_info=True)
        return {}, {} # Hata durumunda boş sözlükler döndür


# İkincil (sekonder) progresyonların hesaplanması
# calculate_celestial_positions kullanılır
def calculate_secondary_progressions(birth_dt, current_dt, latitude, longitude):
    """Doğum ve güncel tarihe göre ikincil progresyon pozisyonlarını hesaplar."""
    try:
        logger.info(f"Sekonder Progresyon pozisyonları hesaplanıyor ({current_dt.strftime('%Y-%m-%d %H:%M:%S')}).")
        # İkincil Progresyon: Doğumdan sonraki her 1 gün, yaşamdaki 1 yıla eşittir.
        # Progresif Julian Günü (UT) = Natal Julian Günü (UT) + Yaş (gün olarak)

        dt_utc_birth = birth_dt - timedelta(hours=3) # Varsayım: UTC+3 Local -> UTC
        jd_ut_birth = swe.julday(dt_utc_birth.year, dt_utc_birth.month, dt_utc_birth.day,
                                 dt_utc_birth.hour + dt_utc_birth.minute/60.0 + dt_utc_birth.second/3600.0)

        # Yaş (gün olarak). datetime.date() kullanarak sadece gün farkını alalım.
        age_in_days = (current_dt.date() - birth_dt.date()).days

        # Progresif Julian Günü (UT)
        jd_progression_ut = jd_ut_birth + age_in_days # Bu UT progresyon JD'sidir.

        # Progresif evleri hesapla (latitude ve longitude'a ihtiyaç duyar)
        # Progresif evler genellikle doğum yerel saati ve progresif tarih/saat JD'si ile hesaplanır.
        # Progresif Tarih/Saat: birth_dt + age_in_days
        prog_dt = datetime(birth_dt.year, birth_dt.month, birth_dt.day, birth_dt.hour, birth_dt.minute) + timedelta(days=age_in_days)

        # calculate_houses fonksiyonunu kullanarak progresif evleri hesapla
        # Bu fonksiyon zaten UTC+3 düzeltmesini içeriyor varsayımıyla kullanalım:
        prog_houses_data = calculate_houses(prog_dt, latitude, longitude, b"P")
        prog_house_cusps = prog_houses_data.get("house_cusps", {})
        if not prog_house_cusps or any(v is None for v in prog_house_cusps.values()): # Geçersiz cusp kontrolü
             logger.warning("Progresif ev pozisyonları hesaplanamadı veya eksik.")
             prog_house_cusps = {str(i+1): 0.0 for i in range(12)} # Fallback


        celestial_bodies_ids = {
            "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY,
            "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER,
            "Saturn": swe.SATURN, "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE,
            "Pluto": swe.PLUTO,
             "True_Node": swe.TRUE_NODE, # Progresif Düğümler de hesaplanabilir
        }

        progressed_positions = {}
        for planet_name, planet_id in celestial_bodies_ids.items():
            try:
                # swe.calc_ut progresif JD'yi kullanır
                pos_result = swe.calc_ut(jd_progression_ut, planet_id, swe.FLG_SWIEPH)

                # Hata kontrolü
                if not pos_result or not pos_result[0]:
                     logger.warning(f"Sekonder Progresyon {planet_name} pozisyonu hesaplanamadı veya hata oluştu: {pos_result[1] if pos_result else 'Unknown error'}")
                     progressed_positions[planet_name] = {
                         "degree": 0.0, "sign": "Bilinmiyor", "retrograde": False,
                         "house": 0, "speed": 0.0, "latitude": 0.0, "distance": 0.0, "error": pos_result[1] if pos_result else "Unknown error"
                     }
                     continue


                pos = pos_result[0]
                lon = pos[0]
                lat = pos[1]
                dist = pos[2]
                speed = pos[3]

                is_retrograde = speed < 0

                # Progresif ev belirleme (prog_house_cusps kullanılır)
                house_num = get_house_number(lon, prog_house_cusps) if prog_house_cusps else 0 # Ev cuspları yoksa ev 0

                progressed_positions[planet_name] = {
                    "degree": round(lon % 360, 2), # Dereceyi 0-360 arasına normalize et
                    "sign": get_zodiac_sign(lon),
                    "retrograde": is_retrograde,
                    "house": house_num, # Progresif ev bilgisi
                    "speed": round(speed, 4),
                    "latitude": round(lat, 4),
                    "distance": round(dist, 4),
                    "degree_in_sign": round(get_degree_in_sign(lon), 2),
                    "decan": get_decan(get_degree_in_sign(lon))
                }
                # logger.debug(f"Sekonder Progresyon {planet_name}: {progressed_positions[planet_name]}")

            except Exception as e:
                logger.error(f"Sekonder Progresyon {planet_name} hesaplanırken hata: {str(e)}", exc_info=True)
                progressed_positions[planet_name] = {
                     "degree": 0.0, "sign": "Bilinmiyor", "retrograde": False,
                     "house": 0, "speed": 0.0, "latitude": 0.0, "distance": 0.0, "error": str(e)
                }
                continue


        logger.info(f"Sekonder Progresyon pozisyonları hesaplandı ({len(progressed_positions)} adet).")
        return progressed_positions, prog_houses_data # Progresif pozisyonları ve ev verisini döndür

    except Exception as e:
        logger.error(f"calculate_secondary_progressions fonksiyonunda hata: {str(e)}", exc_info=True)
        return {}, {} # Hata durumunda boş sözlükler döndür


# Solar Arc progresyon hesaplaması
def get_solar_arc_progressions(birth_dt, current_dt, natal_planet_positions):
    """Doğum ve güncel tarihe göre Solar Arc progresyon pozisyonlarını hesaplar.
    Natal gezegen pozisyonlarına solar arc derecesini ekler."""
    try:
        logger.info("Solar Arc Progresyon pozisyonları hesaplanıyor...")
        dt_utc_birth = birth_dt - timedelta(hours=3) # Varsayım: UTC+3 Local -> UTC
        jd_ut_birth = swe.julday(dt_utc_birth.year, dt_utc_birth.month, dt_utc_birth.day,
                                 dt_utc_birth.hour + dt_utc_birth.minute/60.0 + dt_utc_birth.second/3600.0)

        # Solar Arc derecesi = Doğum anı UT Güneş boylamı ile Şu anki tarih UT Güneş boylamı arasındaki fark
        # Progresif Güneş konumu için secondary progression'daki progressed_positions'dan Sun'ı alabiliriz.
        # Natal Güneş pozisyonunu al
        natal_sun_pos = natal_planet_positions.get("Sun")
        if not natal_sun_pos or 'degree' not in natal_sun_pos:
             logger.error("Natal Güneş pozisyonu bulunamadı, Solar Arc hesaplanamıyor.")
             return {"error": "Natal Güneş pozisyonu eksik."}
        natal_sun_degree = natal_sun_pos['degree']

        # İkincil Progresif Güneş pozisyonunu hesapla (Progresif JD'yi kullanarak)
        # Yaş (gün olarak)
        age_in_days = (current_dt.date() - birth_dt.date()).days # Sadece gün farkı alalım
        jd_progression_ut = jd_ut_birth + age_in_days # Bu UT progresyon JD'sidir.

        prog_sun_pos_result = swe.calc_ut(jd_progression_ut, swe.SUN, swe.FLG_SWIEPH)
        if not prog_sun_pos_result or not prog_sun_pos_result[0]:
            logger.error("Progresif Güneş pozisyonu hesaplanamadı, Solar Arc hesaplanamıyor.")
            return {"error": "Progresif Güneş pozisyonu eksik."}

        prog_sun_degree = prog_sun_pos_result[0][0] % 360

        # Solar Arc = Progresif Güneş Derecesi - Natal Güneş Derecesi
        solar_arc_degree = prog_sun_degree - natal_sun_degree
        # Ark derecesini -180 ile +180 arasına normalize et (bu, arc'ın yönünü gösterir)
        if solar_arc_degree > 180: solar_arc_degree -= 360
        if solar_arc_degree < -180: solar_arc_degree += 360

        logger.info(f"Hesaplanan Solar Arc derecesi: {solar_arc_degree:.2f}°")


        solar_arc_positions = {}
        # Natal pozisyonlara solar arc derecesini ekle
        for planet_name, natal_data in natal_planet_positions.items():
             if 'degree' not in natal_data: continue
             natal_deg = natal_data['degree'] % 360
             sa_deg = (natal_deg + solar_arc_degree) % 360
             if sa_deg < 0: sa_deg += 360

             solar_arc_positions[planet_name] = {
                "degree": round(sa_deg, 2),
                "sign": get_zodiac_sign(sa_deg),
                "degree_in_sign": round(get_degree_in_sign(sa_deg), 2),
                "solar_arc_applied": round(solar_arc_degree, 2) # Uygulanan arc derecesi
             }
             # logger.debug(f"SA {planet_name}: {solar_arc_positions[planet_name]}")

        logger.info("Solar Arc Progresyon pozisyonları hesaplandı.")
        return solar_arc_positions

    except Exception as e:
        logger.error(f"get_solar_arc_progressions fonksiyonunda hata: {str(e)}", exc_info=True)
        return {}


# Solar Return haritası hesaplaması
def calculate_solar_return_chart(birth_dt, current_dt, latitude, longitude):
    """Doğum tarihi ve güncel tarihe göre en yakın Solar Return (Güneş Dönüşü) tarihini bulur
    ve o tarihteki gezegen pozisyonlarını hesaplar."""
    try:
        logger.info("Solar Return hesaplaması başlıyor...")
        dt_utc_birth = birth_dt - timedelta(hours=3) # Varsayım: UTC+3 Local -> UTC
        jd_ut_birth = swe.julday(dt_utc_birth.year, dt_utc_birth.month, dt_utc_birth.day,
                                 dt_utc_birth.hour + dt_utc_birth.minute / 60.0 + dt_utc_birth.second / 3600.0)

        # Natal Güneş boylamını al
        natal_sun_long = swe.calc_ut(jd_ut_birth, swe.SUN, swe.FLG_SWIEPH)[0][0]

        # Solar Return, Güneş'in tam natal pozisyonuna döndüğü andır.
        # Güncel tarihten sonraki ilk Güneş dönüşünü bulalım.
        # Arama başlangıç tarihi: Mevcut yılın doğum günü civarı, geçmişteyse gelecek yılın aynı tarihi
        test_dt_start = datetime(current_dt.year, birth_dt.month, birth_dt.day, birth_dt.hour, birth_dt.minute)
        if test_dt_start < current_dt:
             test_dt_start = test_dt_start.replace(year=current_dt.year + 1)

        jd_test_start = swe.julday(test_dt_start.year, test_dt_start.month, test_dt_start.day,
                                     test_dt_start.hour + test_dt_start.minute/60.0 + test_dt_start.second/3600.0)

        # swe.solve_event ile hedef boylama ulaşma eventini bulalım (SWE_EVENT_BEGTRANSIT gibi eventler gezegenler arası ilişki için)
        # Belirli bir boylama ulaşma event'i için swe.soltime veya iterative arama daha uygun.
        # swe.soltime(tjd_ut, geopos, direction, rsmi, semc, serr)
        # rsmi: SWE_SMI_SUN, direction: 0 (any)
        # swe.soltime ile Güneş'in transitini bulabiliriz (doğuş, batış gibi), ama belirli bir boylama ulaşmayı bulmaz.

        # Hassas arama (iteratif) ile Güneş'in natal boylamına ulaştığı zamanı bulalım.
        solar_return_dt = None
        jd_current_test = jd_test_start
        tolerance = 0.0001 # Derece cinsinden tolerans (çok küçük olmalı)
        max_iterations = 50 # Güvenlik sınırı

        for i in range(max_iterations):
             # Güneş'in pozisyonunu ve hızını al
             pos_result = swe.calc_ut(jd_current_test, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SPEED) # Hızı da al

             if not pos_result or not pos_result[0]:
                  logger.warning(f"Solar Return aramasında {i}. iterasyonda Güneş pozisyonu hesaplanamadı.")
                  break # Hata olursa döngüden çık

             current_sun_long = pos_result[0][0]
             current_sun_speed = pos_result[0][3] # Derece/gün cinsinden hız

             if abs(current_sun_speed) < 0.01: # Hız çok düşükse veya 0'a yakınsa (retrograde vs.)
                  logger.warning("Solar Return aramasında Güneş hızı sıfıra yakın, hesaplama durduruldu.")
                  break


             # Natal boylam ile mevcut boylam arasındaki farkı hesapla
             diff = (natal_sun_long - current_sun_long) % 360
             # En kısa farkı al (-180 ile +180 aralığında)
             if diff > 180: diff -= 360
             if diff < -180: diff += 360

             # Eğer fark tolerans içindeyse, zamanı bulduk
             if abs(diff) < tolerance:
                 solar_return_dt = julday_to_datetime(jd_current_test)
                 break

             # Farkı kapatmak için gereken zamanı hesapla (gün olarak)
             # Zaman değişimi = Fark / Hız
             time_change_days = diff / current_sun_speed

             # Yeni test Julian günü
             jd_current_test += time_change_days

             # Arama aralığı dışına çıkmamaya dikkat edilebilir, ancak iterasyon sayısı genelde yeterlidir.
             # if jd_current_test > swe.julday(test_dt_start.year + 2, 1, 1, 0): # Örneğin 2 yıl sonrasından fazla gitmesin
             #      logger.warning("Solar Return aramasında aralık dışına çıkıldı, hassas zaman bulunamadı.")
             #      break


        if solar_return_dt is None:
             logger.warning("Solar Return tarihi hassas olarak bulunamadı, en yakın değer kullanılıyor.")
             # Son bulunan jd_current_test en yakın değer olmalı
             solar_return_dt = swe.julday_to_datetime(jd_current_test)


        logger.info(f"Solar Return tarihi bulundu: {solar_return_dt.strftime('%Y-%m-%d %H:%M:%S')}")

        # Solar Return anındaki evleri hesapla (lokasyon natal lokasyon)
        solar_return_houses_data = calculate_houses(solar_return_dt, latitude, longitude, b"P")
        solar_return_house_cusps = solar_return_houses_data.get("house_cusps", {})

        if not solar_return_house_cusps:
             logger.warning("Solar Return ev pozisyonları hesaplanamadı.")
             solar_return_house_cusps = {str(i+1): 0.0 for i in range(12)} # Fallback

        # Gezegen ve Ek nokta pozisyonlarını hesapla (Solar Return anı ve lokasyonu için)
        planet_ids = {
            "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY,
            "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER,
            "Saturn": swe.SATURN, "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE,
            "Pluto": swe.PLUTO,
             "True_Node": swe.TRUE_NODE,
        }
        additional_point_ids = {
            "Chiron": swe.CHIRON, "Ceres": swe.CERES, "Pallas": swe.PALLAS,
            "Juno": swe.JUNO, "Vesta": swe.VESTA,
            "Mean_Node": swe.MEAN_NODE, # True_Node zaten planet_ids'de var
            "Mean_Lilith": swe.MEAN_APOG, "True_Lilith": swe.OSCU_APOG,
             # Uranianları dahil etmeyelim SR haritasında
        }

        solar_return_planet_positions = calculate_celestial_positions(solar_return_dt, solar_return_house_cusps, planet_ids)
        solar_return_additional_points = calculate_celestial_positions(solar_return_dt, solar_return_house_cusps, additional_point_ids)

        # Sonuç sözlüğünü oluştur
        solar_return_chart_data = {
            "datetime": solar_return_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "location": {"latitude": latitude, "longitude": longitude},
            "planet_positions": solar_return_planet_positions,
            "additional_points": solar_return_additional_points,
            "houses": solar_return_houses_data
        }

        logger.info("Solar Return haritası hesaplaması tamamlandı.")
        return solar_return_chart_data

    except Exception as e:
        logger.error(f"calculate_solar_return_chart fonksiyonunda hata: {str(e)}", exc_info=True)
        return {} # Hata durumunda boş sözlük döndür


# Lunar Return haritası hesaplaması
def calculate_lunar_return_chart(birth_dt, current_dt, latitude, longitude):
    """Doğum tarihi ve güncel tarihe göre en yakın Lunar Return (Ay Dönüşü) tarihini bulur
    ve o tarihteki gezegen pozisyonlarını hesaplar."""
    try:
        logger.info("Lunar Return hesaplaması başlıyor...")
        dt_utc_birth = birth_dt - timedelta(hours=3) # Varsayım: UTC+3 Local -> UTC
        jd_ut_birth = swe.julday(dt_utc_birth.year, dt_utc_birth.month, dt_utc_birth.day,
                                 dt_utc_birth.hour + dt_utc_birth.minute / 60.0 + dt_utc_birth.second / 3600.0)

        # Natal Ay boylamını al
        natal_moon_long = swe.calc_ut(jd_ut_birth, swe.MOON, swe.FLG_SWIEPH)[0][0]

        # Lunar Return, Ay'ın tam natal pozisyonuna döndüğü andır. Yaklaşık her 27.3 günde bir.
        # Güncel tarihten sonraki ilk Ay dönüşünü bulalım.
        # Arama başlangıç tarihi: Güncel tarihten birkaç gün öncesi (örneğin 30 gün)
        test_dt_start = current_dt - timedelta(days=30)

        jd_test_start = swe.julday(test_dt_start.year, test_dt_start.month, test_dt_start.day,
                                     test_dt_start.hour + test_dt_start.minute/60.0 + test_dt_start.second/3600.0)

        # Hassas arama (iteratif) ile Ay'ın natal boylamına ulaştığı zamanı bulalım.
        lunar_return_dt = None
        jd_current_test = jd_test_start
        tolerance = 0.0001 # Derece cinsinden tolerans (çok küçük olmalı)
        max_iterations = 100 # Ay daha hızlı hareket eder, daha fazla iterasyon gerekebilir

        for i in range(max_iterations):
             # Ay'ın pozisyonunu ve hızını al
             pos_result = swe.calc_ut(jd_current_test, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SPEED) # Hızı da al

             if not pos_result or not pos_result[0]:
                  logger.warning(f"Lunar Return aramasında {i}. iterasyonda Ay pozisyonu hesaplanamadı.")
                  break # Hata olursa döngüden çık

             current_moon_long = pos_result[0][0]
             current_moon_speed = pos_result[0][3] # Derece/gün cinsinden hız

             if abs(current_moon_speed) < 0.1: # Hız çok düşükse veya 0'a yakınsa (retrograde nadir ama olabilir)
                  logger.warning("Lunar Return aramasında Ay hızı sıfıra yakın, hesaplama durduruldu.")
                  break


             # Natal boylam ile mevcut boylam arasındaki farkı hesapla
             diff = (natal_moon_long - current_moon_long) % 360
             # En kısa farkı al (-180 ile +180 aralığında)
             if diff > 180: diff -= 360
             if diff < -180: diff += 360

             # Eğer fark tolerans içindeyse, zamanı bulduk
             if abs(diff) < tolerance:
                 lunar_return_dt = julday_to_datetime(jd_current_test)
                 break

             # Farkı kapatmak için gereken zamanı hesapla (gün olarak)
             # Zaman değişimi = Fark / Hız
             time_change_days = diff / current_moon_speed

             # Yeni test Julian günü
             jd_current_test += time_change_days

             # Arama aralığı dışına çıkmamaya dikkat edilebilir. Genellikle 30 gün yeterli arama aralığı sağlar.
             # Eğer test_dt_start'tan 30 günden fazla ileri gittiyse
             # if jd_current_test > swe.julday(test_dt_start.year, test_dt_start.month, test_dt_start.day + 30, 0):
             #     logger.warning("Lunar Return aramasında aralık dışına çıkıldı, hassas zaman bulunamadı.")
             #     break


        if lunar_return_dt is None:
             logger.warning("Lunar Return tarihi hassas olarak bulunamadı, en yakın değer kullanılıyor.")
             # Son bulunan jd_current_test en yakın değer olmalı
             lunar_return_dt = swe.julday_to_datetime(jd_current_test)

        # Bulunan Lunar Return tarihi current_dt'den önceyse, bir sonraki dönüşü bulalım.
        # Bu basit bir kontrol, daha sofistike arama algoritmaları daha verimli olabilir.
        # Ancak iteratif yöntem genellikle en yakın çözümü bulur.
        # Eğer bulunan tarih bugünden eskiyse, test_dt_start'ı bulunan tarihten sonraya ayarlayıp tekrar arama yapılabilir.
        # Veya basitçe, eğer LR tarihi current_dt'den eskiyse, 27.3 gün (yaklaşık Ay döngüsü) ekleyerek bir sonraki LR'yi tahmin edip o civarda hassas arama yapılabilir.
        # Şimdilik bulunan tarihi kullanıyoruz, eğer logic güncel sonrası ilk LR'yi bulmaksa, başlangıç aralığı güncel tarihten başlamalıdır.
        # Önceki kod test_dt_start = current_dt - timedelta(days=15) kullanıyordu, bu bugünden önceki LR'yi bulabilir.
        # test_dt_start = current_dt # Eğer her zaman "şu anki tarihten sonraki ilk" LR isteniyorsa

        # Basitlik adına, bulunan tarihi kullanıyoruz. Eğer birden fazla LR periyodu gerekirse bu kısım güncellenmeli.


        logger.info(f"Lunar Return tarihi bulundu: {lunar_return_dt.strftime('%Y-%m-%d %H:%M:%S')}")

        # Lunar Return anındaki evleri hesapla (lokasyon natal lokasyon)
        lunar_return_houses_data = calculate_houses(lunar_return_dt, latitude, longitude, b"P")
        lunar_return_house_cusps = lunar_return_houses_data.get("house_cusps", {})

        if not lunar_return_house_cusps:
             logger.warning("Lunar Return ev pozisyonları hesaplanamadı.")
             lunar_return_house_cusps = {str(i+1): 0.0 for i in range(12)} # Fallback

        # Gezegen ve Ek nokta pozisyonlarını hesapla (Lunar Return anı ve lokasyonu için)
        planet_ids = {
            "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY,
            "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER,
            "Saturn": swe.SATURN, "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE,
            "Pluto": swe.PLUTO,
             "True_Node": swe.TRUE_NODE,
        }
        additional_point_ids = {
            "Chiron": swe.CHIRON, "Ceres": swe.CERES, "Pallas": swe.PALLAS,
            "Juno": swe.JUNO, "Vesta": swe.VESTA,
             "Mean_Node": swe.MEAN_NODE,
            "Mean_Lilith": swe.MEAN_APOG, "True_Lilith": swe.OSCU_APOG,
             # Uranianları dahil etmeyelim LR haritasında
        }

        lunar_return_planet_positions = calculate_celestial_positions(lunar_return_dt, lunar_return_house_cusps, planet_ids)
        lunar_return_additional_points = calculate_celestial_positions(lunar_return_dt, lunar_return_house_cusps, additional_point_ids)


        # Sonuç sözlüğünü oluştur
        lunar_return_chart_data = {
            "datetime": lunar_return_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "location": {"latitude": latitude, "longitude": longitude},
            "planet_positions": lunar_return_planet_positions,
             "additional_points": lunar_return_additional_points,
            "houses": lunar_return_houses_data
        }

        logger.info("Lunar Return haritası hesaplaması tamamlandı.")
        return lunar_return_chart_data

    except Exception as e:
        logger.error(f"calculate_lunar_return_chart fonksiyonunda hata: {str(e)}", exc_info=True)
        return {} # Hata durumunda boş sözlük döndür


# Sabit yıldızların hesaplanması
def calculate_fixed_stars(birth_dt):
    """Doğum tarihine göre sabit yıldızların pozisyonlarını hesaplar"""
    try:
        logger.info("Sabit yıldız pozisyonları hesaplanıyor...")
        dt_utc = birth_dt - timedelta(hours=3) # Varsayım: UTC+3 Local -> UTC
        jd_ut = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                           dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0)


        # Swisseph'in desteklediği yaygın sabit yıldızların listesi
        # İsimlerin swe.fixstar veya swe.fixstar2_ut tarafından tanınması gerekir.
        # Tam liste için swisseph belgelerine ve fixstars.cat dosyasına bakılmalıdır.
        # Bazı isimler birden fazla kelime içerir ve boşluklar alt çizgi (_) ile değiştirilmelidir
        # veya swe'nin beklediği tam format kullanılmalıdır.
        # Önceki listedeki bazı isimler (Draco, Hyades, Pleiades, Praesepe, Sirius B, Procyon B, Deneb Okab, Formalhaut)
        # doğrudan tanınmıyor olabilir veya farklı bir yazılıma sahiptir.
        # Daha güvenli olması için yaygın ve bilinen isimleri kullanalım ve hata yakalamayı sürdürelim.
        fixed_stars_list_safe = [
            "Aldebaran", "Antares", "Regulus", "Spica", "Sirius", "Vega",
            "Fomalhaut", "Pollux", "Castor", "Procyon", "Algol", "Deneb_Algedi", # Boşlukları alt çizgi yapalım
            "Scheat", "Markab", "Capella", "Rigel", "Betelgeuse", "Bellatrix",
            "Alnilam", "Alnitak", "Saiph", "Polaris", "Kochab", "Alcyone",
            "Asellus_Borealis", "Asellus_Australis", "Acubens", "Canopus", "Miaplacidus", "Suhail",
            "Avior", "Wezen", "Aludra", "Alphard", "Alphecca", "Unukalhai", "Rasalhague",
            "Shaula", "Lesath", "Kaus_Australis", "Nunki", "Ascella", "Deneb_Adige",
            "Sador", "Albireo", "Altair", "Algedi", "Nashira", "Sadalmelek", "Sadal_Suud",
            "Formalhaut" # Formalhaut'u tekrar ekleyelim, belki farklı yazılımı denerken çalışır
        ]


        results = {}
        for star_name_raw in fixed_stars_list_safe:
            # swe fonksiyonları genellikle küçük harf ve alt çizgi ile çalışır
            star_name = star_name_raw.lower().replace(" ", "_") # Boşlukları alt çizgiye çevir

            try:
                # swe.fixstar(starname, tjd_ut, iflags)
                # returns ((lon, lat, dist), mag, serr) - Bu format magnitude'u veriyor
                pos_result_mag = swe.fixstar(star_name, jd_ut, swe.FLG_SWIEPH)

                # Hata kontrolü: pos_result_mag None değilse ve ilk elemanı (konum tuple) None değilse
                if not pos_result_mag or not pos_result_mag[0]:
                     # logger.debug(f"Sabit yıldız '{star_name_raw}' pozisyonu hesaplanamadı veya bulunamadı (pos_result_mag[0] None).")
                     continue # Bulunamazsa atla

                pos_tuple = pos_result_mag[0] # (lon, lat, dist)
                degree = pos_tuple[0] % 360 # Tam boylam, 0-360 normalize
                if degree < 0: degree += 360
                latitude = pos_tuple[1] # Ekliptik enlem

                # Magnitude kontrolü: pos_result_mag en az 2 elemanlı mı ve 2. eleman sayısal mı?
                magnitude = None
                if len(pos_result_mag) > 1:
                    if isinstance(pos_result_mag[1], (int, float)):
                        magnitude = float(pos_result_mag[1])
                    # else: # Eğer sayısal değilse, muhtemelen serr stringidir. Hata yakalandığında loglanır.
                         # logger.warning(f"Sabit yıldız '{star_name_raw}' için magnitude sayısal değil: {pos_result_mag[1]}.")


                sign = get_zodiac_sign(degree)

                results[star_name_raw] = { # Orijinal ismi kaydet
                    "degree": round(degree, 2), # Tam boylam
                    "sign": sign,
                    "degree_in_sign": round(get_degree_in_sign(degree), 2), # Burç içindeki derece
                    "latitude": round(latitude, 4), # Ekliptik enlem
                    "magnitude": round(magnitude, 2) if magnitude is not None else None,
                }
                # logger.debug(f"{star_name_raw} pozisyonu hesaplandı: {results[star_name_raw]}")

            except swe.Error as e:
                # Swisseph'in kendi hatasını yakala (örn. yıldız bulunamadı)
                logger.debug(f"Sabit yıldız {star_name_raw} hesaplanırken Swisseph hatası: {str(e)}")
                continue # Hata olursa atla

            except Exception as e:
                # Diğer olası hataları yakala (örn. TypeError)
                logger.error(f"Sabit yıldız {star_name_raw} hesaplanırken beklenmedik hata: {str(e)}", exc_info=True)
                continue # Hata olursa atla

        logger.info(f"Sabit yıldızların hesaplanması tamamlandı ({len(results)} adet).")
        return results

    except Exception as e:
        logger.error(f"calculate_fixed_stars fonksiyonunda genel hata: {str(e)}", exc_info=True)
        return {}


# Eclipse (Tutulma) hesaplaması - Doğum tarihi civarında veya güncel tarih civarında
def find_eclipses_in_range(start_dt, end_dt):
    """Verilen tarih aralığında Güneş ve Ay tutulmalarını bulur."""
    try:
        logger.info(f"Tutulmalar aranıyor: {start_dt.strftime('%Y-%m-%d')} - {end_dt.strftime('%Y-%m-%d')}")
        # Arama için başlangıç ve bitiş Julian günlerini al
        # Tutulma ararken genellikle UT kullanılır.
        jd_start_ut = swe.julday(start_dt.year, start_dt.month, start_dt.day, 0)
        jd_end_ut = swe.julday(end_dt.year, end_dt.month, end_dt.day, 0)

        eclipses_list = []
        current_jd_ut = jd_start_ut

        # swe.lun_eclipse_when ve swe.solar_eclipse_when bir sonraki veya önceki tutulmayı bulur.
        # Belirli bir aralıktaki tüm tutulmaları bulmak için bir döngü içinde bu fonksiyonları kullanalım.

        # Maksimum arama iterasyonunu sınırlayalım (Gün sayısı * 2 veya daha fazla)
        max_iterations = int((jd_end_ut - jd_start_ut + 1) * 3) + 10 # Günde 2'den fazla tutulma olmaz, ama güvenlik için 3 katı + 10

        # SWE_ECL_ANY = 0 bayrağı herhangi bir tutulma tipini bulur.
        # SWE_ECL_TOTAL = 1, SWE_ECL_ANNULAR = 2, SWE_ECL_PARTIAL = 4, SWE_ECL_PENUMBRAL = 8
        # Kombinasyonlar mümkündür: SWE_ECL_TOTAL | SWE_ECL_PARTIAL gibi.
        # Genel bir arama için SWE_ECL_ANY kullanalım.
        # Konum [0,0,0] veya None, global tutulma zamanını verir.
        geopos_global = [0.0, 0.0, 0.0]
        etype_any = 0 # SWE_ECL_ANY

        for i in range(max_iterations):
             # Bir sonraki Ay tutulmasını bul
             # swe.lun_eclipse_when(tjd_start, iflags, etype, geopos, backwards)
             # returns (tjd_event, geolon, geolat, altitude, type, magnitude, saros, serr)
             res_lunar = swe.lun_eclipse_when(current_jd_ut, swe.FLG_SWIEPH, 0) # 0: forward search

             # Bir sonraki Güneş tutulmasını bul
             # swe.sol_eclipse_when_glob(tjd_ut, iflags, eclflag, backwards)
             # returns (tjd_event, eclflag, maximum_eclipse, saros, serr)
             res_solar = swe.sol_eclipse_when_glob(current_jd_ut, swe.FLG_SWIEPH, 0) # 0: forward search

             # Bulunan tutulmaların Julian günlerini al (eğer bulunduysa)
             jd_next_lunar = res_lunar[0] if res_lunar and len(res_lunar) > 0 and isinstance(res_lunar[0], (int, float)) else -1
             jd_next_solar = res_solar[0] if res_solar and len(res_solar) > 0 and isinstance(res_solar[0], (int, float)) else -1

             # Bulunan tutulmaları karşılaştır ve zaman çizelgesinde bir sonraki olanı seç
             found_eclipse_jd = -1
             eclipse_info = None # Tutulma detaylarını saklamak için

             if jd_next_lunar != -1 and (jd_next_solar == -1 or jd_next_lunar < jd_next_solar):
                 found_eclipse_jd = jd_next_lunar
                 eclipse_info = {
                     "type": "Lunar",
                     "magnitude": res_lunar[5] if res_lunar and len(res_lunar)>5 else None, # Magnitude
                     "saros": res_lunar[6] if res_lunar and len(res_lunar)>6 else None, # Saros number
                     "event_type_flag": res_lunar[4] if res_lunar and len(res_lunar)>4 else None, # SWE_ECL_PENUMBRAL etc.
                 }

             elif jd_next_solar != -1:
                  found_eclipse_jd = jd_next_solar
                  eclipse_info = {
                      "type": "Solar",
                      "magnitude": res_solar[2] if res_solar and len(res_solar)>2 else None, # Maximum eclipse
                      "saros": res_solar[3] if res_solar and len(res_solar)>3 else None, # Saros number
                      "event_type_flag": res_solar[1] if res_solar and len(res_solar)>1 else None, # SWE_ECL_TOTAL, SWE_ECL_ANNULAR, SWE_ECL_PARTIAL
                  }
                  # Güneş tutulması tipi adını ekleyelim
                  type_flag = eclipse_info.get("event_type_flag")
                  ecl_type_name = "Total" if type_flag == swe.ECL_TOTAL else "Annular" if type_flag == swe.ECL_ANNULAR else "Partial" if type_flag == swe.ECL_PARTIAL else "Unknown"
                  eclipse_info["type_name"] = ecl_type_name


             # Bulunan tutulma aralık dışındaysa veya hiç tutulma bulunamadıysa döngüyü sonlandır
             if found_eclipse_jd == -1 or found_eclipse_jd >= jd_end_ut: # >= end_dt olmalı
                 break

             # Tutulma aralık içindeyse listeye ekle
             # swe.revjul returns a tuple (year, month, day, hour, minute, second, microsecond)
             # We need to convert this to a datetime object
             year, month, day, hour_float = swe.revjul(found_eclipse_jd, swe.GREG_CAL)
             hour = int(hour_float)
             minute = int((hour_float - hour) * 60)
             second = int(((hour_float - hour) * 60 - minute) * 60)
             eclipse_dt = datetime(year, month, day, hour, minute, second)

             eclipses_list.append({
                 "datetime": eclipse_dt.strftime("%Y-%m-%d %H:%M:%S"),
                 "eclipse_type": eclipse_info.get("type_name", "Unknown") if eclipse_info else "Unknown",
                 "details": eclipse_info if eclipse_info else {} # Tüm detayları ekleyelim
             })

             # Arama başlangıç noktasını bulunan tutulmadan sonrasına taşı
             # Bulunan JD'nin hemen sonrasından aramaya devam etmeliyiz.
             current_jd_ut = found_eclipse_jd + 0.000001 # Çok küçük bir zaman dilimi sonrası


        logger.info(f"Tutulma arama tamamlandı. Bulunan tutulma sayısı: {len(eclipses_list)}")
        return eclipses_list

    except Exception as e:
        logger.error(f"find_eclipses_in_range fonksiyonunda hata: {str(e)}", exc_info=True)
        return []


# Antiscia ve Contra-antiscia hesaplaması (Doğum anı için)
def calculate_antiscia(natal_celestial_positions, orb=1.0):
    """Gezegenlerin antiscia (karşıt dekan) ve contra-antiscia (karşıt burçta aynı dekan) noktalarını ve bağlantılarını hesaplar.

    Args:
        natal_celestial_positions (dict): Natal gezegen/nokta konumları
        orb (float): Maksimum tolerans derecesi (default 1°)

    Returns:
        dict: Her gezegen/nokta için antiscia/contra-antiscia bilgileri ve bağlantılar
    """
    try:
        # Sadece 'degree' anahtarı olan geçerli pozisyonları al
        valid_positions = {k: v for k, v in natal_celestial_positions.items() if isinstance(v, dict) and 'degree' in v}

        results = {}

        # Pozisyonları normalize et (0-360)
        normalized_positions = {
            p: data['degree'] % 360 for p, data in valid_positions.items()
        }

        for planet1, deg1 in normalized_positions.items():
            # Antiscia noktası hesapla: (180 - deg1) % 360
            antiscia_deg = (180 - deg1) % 360
            if antiscia_deg < 0: antiscia_deg += 360

            # Contra-antiscia noktası hesapla: (360 - deg1) % 360
            contra_antiscia_deg = (360 - deg1) % 360
            if contra_antiscia_deg < 0: contra_antiscia_deg += 360


            antiscia_connections = []
            contra_antiscia_connections = []

            # Diğer gezegen/noktalarla bağlantıları kontrol et
            for planet2, deg2 in normalized_positions.items():
                if planet1 == planet2:
                    continue # Kendisiyle kıyaslama yapma

                # Antiscia bağlantısı kontrolü: deg2, antiscia_deg'e orb kadar yakın mı?
                diff_antiscia = abs(deg2 - antiscia_deg)
                orb_antiscia_value = min(diff_antiscia, 360 - diff_antiscia) # En kısa yay

                if orb_antiscia_value <= orb:
                     antiscia_connections.append({
                         "planet": planet2,
                         "degree": round(deg2, 2),
                         "sign": get_zodiac_sign(deg2),
                         "orb": round(orb_antiscia_value, 2)
                     })

                # Contra-antiscia bağlantısı kontrolü: deg2, contra_antiscia_deg'e orb kadar yakın mı?
                diff_contra_antiscia = abs(deg2 - contra_antiscia_deg)
                orb_contra_antiscia_value = min(diff_contra_antiscia, 360 - diff_contra_antiscia) # En kısa yay

                if orb_contra_antiscia_value <= orb:
                    contra_antiscia_connections.append({
                        "planet": planet2,
                        "degree": round(deg2, 2),
                        "sign": get_zodiac_sign(deg2),
                        "orb": round(orb_contra_antiscia_value, 2)
                    })


            results[planet1] = {
                "original_degree": round(deg1, 2),
                "original_sign": get_zodiac_sign(deg1),
                "antiscia": {
                    "degree": round(antiscia_deg, 2),
                    "sign": get_zodiac_sign(antiscia_deg),
                    "connections": sorted(antiscia_connections, key=lambda x: x['orb']) # Orba göre sırala
                },
                "contra_antiscia": {
                    "degree": round(contra_antiscia_deg, 2),
                    "sign": get_zodiac_sign(contra_antiscia_deg),
                    "connections": sorted(contra_antiscia_connections, key=lambda x: x['orb']) # Orba göre sırala
                }
            }

            # logger.debug(f"{planet1} antiscia/contra-antiscia hesaplandı.")

        logger.info(f"Antiscia/Contra-antiscia hesaplaması tamamlandı ({len(results)} gezegen/nokta için).")
        return results

    except Exception as e:
        logger.error(f"Antiscia/Contra-antiscia hesaplama hatası: {str(e)}", exc_info=True)
        return {}


# Dignity ve Debility skorlarının hesaplanması (Geleneksel yöneticilik, yücelim vb.)
def calculate_dignity_scores(natal_planet_positions):
    """Gezegenlerin basit dignity (yönetim, yücelim) skorlarını hesaplar.
    Ana gezegenler için hesaplama yapar."""
    try:
        # Yöneticilik (Rulership)
        rulerships = {
            "Sun": ["Aslan"], "Moon": ["Yengeç"], "Mercury": ["İkizler", "Başak"],
            "Venus": ["Boğa", "Terazi"], "Mars": ["Koç", "Akrep"],
            "Jupiter": ["Yay", "Balık"], "Saturn": ["Oğlak", "Kova"],
        }
        # Yücelim (Exaltation)
        exaltations = {
            "Sun": "Koç", "Moon": "Boğa", "Mercury": "Kova", # Farklı kaynaklarda Merkür Başak veya Kova olabilir
            "Venus": "Balık", "Mars": "Oğlak", "Jupiter": "Yengeç", "Saturn": "Terazi",
        }
        # Helper to get sign degree
        def get_zodiac_sign_degree_value(sign_name):
             zodiac_signs = ["Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak","Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"]
             try:
                 return zodiac_signs.index(sign_name) * 30
             except ValueError:
                 return None

        # Zarar (Detriment)
        detriment_signs = calculate_detriment_signs() # Zararı hesaplamak için yardımcı fonksiyon
        # Düşüş (Fall)
        fall_signs = {
             planet: get_zodiac_sign((degree + 180) % 360) if (degree := get_zodiac_sign_degree_value(exaltations[planet])) is not None else None
             for planet in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"] # Yücelimin 180 derece karşısı (Ana gezegenler için)
        }


        dignity_scores = {}
        # Ana gezegenleri kontrol et
        planets_to_check = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

        for planet in planets_to_check:
            if planet not in natal_planet_positions or 'degree' not in natal_planet_positions[planet] or 'sign' not in natal_planet_positions[planet]:
                 logger.warning(f"{planet} pozisyonu dignity için bulunamadı veya eksik.")
                 continue

            pos = natal_planet_positions[planet]['degree']
            sign = natal_planet_positions[planet]['sign']
            score = 0
            status = "Peregrine" # Başka bir dignity durumu yoksa

            # Yönetici (+5)
            if sign in rulerships.get(planet, []):
                score += 5
                status = "Yönetici"

            # Yücelimde (+4)
            if exaltations.get(planet) == sign:
                # Yücelim derecesi de kontrol edilebilir hassasiyet için (örn. Güneş 19 Koç)
                # Şimdilik sadece burç kontrolü yapalım
                score += 4
                if status != "Yönetici": # Yönetici aynı zamanda yücelimde olamaz (Nadiren istisnai durumlar olabilir)
                    status = "Yücelimde"

            # Zararda (-5)
            if sign in detriment_signs.get(planet, []):
                 score -= 5
                 status = "Zararda"

            # Düşüşte (-4)
            if fall_signs.get(planet) == sign:
                 score -= 4
                     
                     

            # Triplicity, Term, Face gibi diğer dignity'ler eklenebilir
            # ... (Daha gelişmiş bir dignity tablosu ve hesaplama gerekir)


            dignity_scores[planet] = {
                "degree": round(pos, 2),
                "sign": sign,
                "score_basic": score, # Sadece yöneticilik/yücelim/zarar/düşüş skorunu tutalım
                "status_basic": status, # En yüksek dignity/debility durumu
            }
            # logger.debug(f"{planet} dignity: {dignity_scores[planet]}")

        logger.info(f"Basit Dignity skorları hesaplandı ({len(dignity_scores)} gezegen için).")
        return dignity_scores

    except Exception as e:
        logger.error(f"Dignity skorları hesaplama hatası: {str(e)}", exc_info=True)
        return {}


def calculate_zodiac_sign_degree():
    """Burç derecelerini hesaplar ve döndürür."""
    try:
        zodiac_signs = ["Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak",
                        "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"]
        zodiac_sign_degrees = {sign: i * 30 for i, sign in enumerate(zodiac_signs)}
        return zodiac_sign_degrees
    except Exception as e:
        logger.error(f"Burç dereceleri hesaplama hatası: {str(e)}")
        return {}

def calculate_detriment_signs():
    """Zarar (Detriment) burçlarını hesaplar ve döndürür."""
    try:
        detriment_signs = {
            "Sun": ["Kova", "Terazi"],
            "Moon": ["Oğlak", "Akrep"],
            "Mercury": ["Yay", "Balık"],
            "Venus": ["Koç", "Başak"],
            "Mars": ["Boğa", "Terazi"],
            "Jupiter": ["İkizler", "Başak"],
            "Saturn": ["Aslan", "Yengeç"]
        }
        return detriment_signs
    except Exception as e:
        logger.error(f"Zarar burçları hesaplama hatası: {str(e)}")
        return {}   

# Midpoint tekniklerinin hesaplanması
def get_midpoint_aspects(natal_celestial_positions, orb=2.0):
    """Natal haritadaki göksel cisim çiftlerinin midpointlerini ve bu midpointlerin
    diğer göksel cisimlere olan açılarını hesaplar."""
    try:
        # Sadece 'degree' anahtarı olan geçerli pozisyonları al
        valid_positions = {k: v for k, v in natal_celestial_positions.items() if isinstance(v, dict) and 'degree' in v}

        midpoint_results = {
            "midpoints": [], # Tüm nokta çiftleri için midpoints ve açıları
        }

        points_keys = list(valid_positions.keys())

        for i in range(len(points_keys)):
            for j in range(i + 1, len(points_keys)): # Çiftleri tekrar etmeden al
                p1_key = points_keys[i]
                p2_key = points_keys[j]
                deg1 = valid_positions[p1_key]['degree'] % 360
                deg2 = valid_positions[p2_key]['degree'] % 360


                # Midpoint hesaplama (kısa yay)
                midpoint_deg = (deg1 + deg2) / 2.0
                # İki nokta arasındaki en kısa yayın ortası
                # Örn: 10 ve 300. Fark 290. Kısa yay farkı 70. Midpoint: (10+300)/2 = 155.
                # Bu 155 derecesi, 10 ile 300 arasındaki uzun yay üzerindedir.
                # Kısa yay üzerindeki midpoint: (10+300)/2 + 180 = 335 (yanlış!)
                # Doğru kısa yay midpoint:
                # Eğer fark > 180 ise, diğer yöndeki ortalamayı al veya (A+B)/2 + 180 yap
                diff = abs(deg1 - deg2)
                if diff > 180:
                     midpoint_deg = (deg1 + deg2 + 360) / 2.0 # Birine 360 ekle
                else:
                     midpoint_deg = (deg1 + deg2) / 2.0

                midpoint_deg = midpoint_deg % 360
                if midpoint_deg < 0: midpoint_deg += 360


                midpoint_sign = get_zodiac_sign(midpoint_deg)

                normalized_positions = calculate_normalized_positions(valid_positions)
                # Bu midpointe diğer gezegen/noktaların açılarını kontrol et
                aspects = []
                for p3_key, deg3 in normalized_positions.items():
                    # Aynı gezegenler midpointe açı yapamaz
                    # Hem p1 hem p2 hem de p3 aynı olabilir (örn. Asc/MC midpointi Asc'ye açısı)
                    # Ama p3 p1 veya p2 ise anlamlı açı olmaz.
                    if p3_key == p1_key or p3_key == p2_key:
                        continue

                    # Midpoint ve gezegen arasındaki açı farkı
                    # Midpoint açıları genellikle 8. harmonik (45 derece) ve 16. harmonik (22.5 derece) açılarıdır.
                    # Yani 0, 45, 90, 135, 180 derecelik açılara bakılır (ve bunların 22.5 derece sapmaları).
                    # Açı farkını 0-180 arasına normalize et (Midpoint açıları 0-180 aralığında değerlendirilir).
                    aspect_deg_diff = abs(midpoint_deg - deg3) % 180


                    # Başlıca Midpoint Açıları (0, 45, 90, 135, 180)
                    # Orb genellikle 1-2 derece kullanılır. Orb parametresini kullanalım.

                    min_orb_found = float('inf')
                    best_aspect_type = None

                    # Kontrol edilecek açı tipleri ve ideal dereceleri
                    midpoint_aspect_degrees = {
                        "Conjunction/Opposition": 0.0, # 0 ve 180 aynı anlamdadır midpointe göre
                        "Semisquare/Sesquiquadrate": 45.0, # 45 ve 135 aynı anlamdadır midpointe göre
                        "Square": 90.0,
                    }

                    for aspect_name_group, ideal_degree in midpoint_aspect_degrees.items():
                         # Açı farkının ideale yakınlığını kontrol et (orb içinde mi)
                         # Açı farkı mod 180 alındığından, 0 ve 180, 45 ve 135 aynı uzaklıkta olur.
                         # Örneğin, 10 derece midpointe 5 derece açı yapan gezegen: fark 5 (0'a yakın) veya fark 175 (180'e yakın). İkisi de Con/Opp olarak yorumlanır.
                         # 55 derece açı yapan gezegen: fark 55 (45'e yakın) veya fark 125 (135'e yakın). İkisi de Semisquare/Sesquiquadrate olarak yorumlanır.

                         current_orb = orb # Tüm midpoint açıları için aynı orb kullanılıyor varsayımı

                         orb_value = abs(aspect_deg_diff - ideal_degree) % 90 # 0-90 arasına çekip 0 veya 90'a yakınlık kontrolü

                         # Daha basit kontrol: doğrudan orb aralığında mı?
                         is_aspect = False
                         actual_orb_value = float('inf')

                         if abs(aspect_deg_diff - 0) <= orb or abs(aspect_deg_diff - 180) <= orb: # Con/Opp
                              is_aspect = True
                              actual_orb_value = min(abs(aspect_deg_diff - 0), abs(aspect_deg_diff - 180)) % 180 # Tam orb değeri

                         elif abs(aspect_deg_diff - 90) <= orb: # Square
                              is_aspect = True
                              actual_orb_value = abs(aspect_deg_diff - 90) # Tam orb değeri

                         elif abs(aspect_deg_diff - 45) <= orb: # Semisquare
                              is_aspect = True
                              actual_orb_value = abs(aspect_deg_diff - 45) # Tam orb değeri

                         elif abs(aspect_deg_diff - 135) <= orb: # Sesquiquadrate
                              is_aspect = True
                              actual_orb_value = abs(aspect_deg_diff - 135) # Tam orb değeri


                         if is_aspect:
                             # En küçük orb ile bulunan açıyı kaydet
                             if actual_orb_value < min_orb_found:
                                 min_orb_found = actual_orb_value
                                 best_aspect_type = "" # Açı tipini aşağıda belirleyelim

                                 if abs(aspect_deg_diff - 0) == min_orb_found or abs(aspect_deg_diff - 180) == min_orb_found:
                                      best_aspect_type = "Conjunction/Opposition"
                                 elif abs(aspect_deg_diff - 90) == min_orb_found:
                                      best_aspect_type = "Square"
                                 elif abs(aspect_deg_diff - 45) == min_orb_found:
                                      best_aspect_type = "Semisquare"
                                 elif abs(aspect_deg_diff - 135) == min_orb_found:
                                      best_aspect_type = "Sesquiquadrate"
                                 # Minör midpoint açıları da eklenebilir (22.5, 67.5, 112.5, 157.5) vb.


                    if best_aspect_type:
                         aspects.append(
                             {
                                 "celestial_body": p3_key, # Hangi göksel cisim midpointe açı yapıyor
                                 "aspect_type": best_aspect_type,
                                 "orb": round(min_orb_found, 2), # En küçük orb
                                 "actual_difference_0_180": round(aspect_deg_diff, 2) # 0-180 arasındaki fark
                             }
                         )

                # Bu midpoint çiftinin bilgilerini ve açılarını ekle
                if aspects: # Sadece açı yapan midpointleri listelemek daha faydalı olabilir
                     midpoint_results["midpoints"].append(
                         {
                             "celestial_bodies": [p1_key, p2_key],
                             "midpoint_degree": round(midpoint_deg, 2),
                             "midpoint_sign": midpoint_sign,
                             "midpoint_degree_in_sign": round(get_degree_in_sign(midpoint_deg), 2),
                             "aspects_to_other_bodies": sorted(aspects, key=lambda x: x['orb']) # Orba göre sırala
                         }
                     )
                # else: # Açı yapmayan midpointleri de listelemek isterseniz
                #      midpoint_results["midpoints"].append(
                #          {
                #              "celestial_bodies": [p1_key, p2_key],
                #              "midpoint_degree": round(midpoint_deg, 2),
                #              "midpoint_sign": midpoint_sign,
                #              "midpoint_degree_in_sign": round(get_degree_in_sign(midpoint_deg), 2),
                #              "aspects_to_other_bodies": [] # Açı yok
                #          }
                #      )


        # Midpointleri hangi noktalara açı yaptıklarına göre sıralayabiliriz
        # Veya sadece orb'a göre sıralaabiliriz (en dar açılar önce)
        # Önce midpoint çiftlerini, sonra içindeki açıları sıraladık. Bu haliyle bırakalım.
        # breakpoint()
        # logger.info(f"Midpoint hesaplamaları tamamlandı ({len(midpoint_results['midpoints'])} açı yapan midpoint çifti).")
        return midpoint_results

    except Exception as e:
        logger.error(
            f"get_midpoint_aspects fonksiyonunda hata: {str(e)}",
            exc_info=True
        )
        return {"midpoints": []}


def calculate_normalized_positions(natal_celestial_positions):
    """Natal haritadaki göksel cisimlerin pozisyonlarını normalize eder (0-360 aralığına çeker)."""
    try:
        # Sadece 'degree' anahtarı olan geçerli pozisyonları al
        valid_positions = {k: v for k, v in natal_celestial_positions.items() if isinstance(v, dict) and 'degree' in v}

        normalized_positions = {
            p: data['degree'] % 360 for p, data in valid_positions.items()
        }

        logger.info(f"Pozisyonlar normalize edildi ({len(normalized_positions)} gezegen/nokta için).")
        return normalized_positions

    except Exception as e:
        logger.error(f"Pozisyonları normalize etme hatası: {str(e)}", exc_info=True)
        return {}

# Progressed Moon Phase hesaplaması
def calculate_progressed_moon_phase(progressed_positions):
    """Progressed Sun ve Moon pozisyonlarına göre progressed Ay fazını hesaplar."""
    try:
        prog_sun_pos = progressed_positions.get("Sun")
        prog_moon_pos = progressed_positions.get("Moon")

        if not prog_sun_pos or not prog_moon_pos or 'degree' not in prog_sun_pos or 'degree' not in prog_moon_pos:
            logger.error("Progressed Moon Phase hesaplama için progressed Güneş veya Ay pozisyonu eksik.")
            return {"error": "Progressed Güneş veya Ay pozisyonu eksik."}

        prog_sun_deg = prog_sun_pos['degree']
        prog_moon_deg = prog_moon_pos['degree']


        # Ay ile Güneş arasındaki açı farkını bul (0-360 arası normalize edilir)
        phase_angle = (prog_moon_deg - prog_sun_deg) % 360
        if phase_angle < 0: phase_angle += 360


        # Faz gününü hesapla (yaklaşık 29.53 günlük sinodik dönem üzerinden)
        phase_day = round((phase_angle / 360) * 29.53059, 1)

        # Ay fazını açıya göre belirle (Natal Lunation Cycle ile aynı fazlar)
        if 0 <= phase_angle < 45:
            phase = "Yeni Ay (New Moon)"
        elif 45 <= phase_angle < 90:
            phase = "Hilal (Crescent Moon)"
        elif 90 <= phase_angle < 135:
            phase = "İlk Dördün (First Quarter)"
        elif 135 <= phase_angle < 180:
            phase = "Şişen Ay (Gibbous Moon)"
        elif 180 <= phase_angle < 225:
            phase = "Dolunay (Full Moon)"
        elif 225 <= phase_angle < 270:
            phase = "Dağılma (Disseminating Moon)"
        elif 270 <= phase_angle < 315:
            phase = "Son Dördün (Last Quarter)"
        elif 315 <= phase_angle < 360:
            phase = "Balsamik Ay (Balsamic Moon)"
        else:
            phase = "Bilinmeyen Faz"


        result = {
            "phase_name": phase,
            "phase_angle": round(phase_angle, 2),
            "phase_day_approx": phase_day # Bu progressed günler değil, sinodik gün sayısıdır
        }

        logger.info(f"Progressed Moon Phase hesaplandı: {result}")
        return result

    except Exception as e:
        logger.error(f"Progressed Moon Phase hesaplama hatası: {str(e)}", exc_info=True)
        return {"error": str(e)}

# Azimuth ve Altitude hesaplaması (Belirli bir andaki göksel cisimlerin horizon üzerindeki pozisyonları)
def calculate_azimuth_altitude_for_bodies(dt_object, latitude, longitude, elevation_m, celestial_positions):
    """Belirli bir datetime, konum ve yükseklik için göksel cisimlerin Azimuth ve Altitude (Ufuk) koordinatlarını hesaplar.
    celestial_positions: { "İsim": {"degree": X, "latitude": Y, "distance": Z} } formatında dict.
    """
    try:
        logger.info("Göksel cisimlerin Azimuth ve Altitude hesaplanıyor...")
        dt_utc = dt_object - timedelta(hours=3) # Varsayım: UTC+3 Local -> UTC
        jd_ut = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                           dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0)

        geopos = [longitude, latitude, elevation_m] # [boylam, enlem, yükseklik metre]

        azalt_positions = {}

        # Sadece 'degree', 'latitude', 'distance' anahtarları olan geçerli pozisyonları al
        valid_positions = {k: v for k, v in celestial_positions.items() if isinstance(v, dict) and 'degree' in v and 'latitude' in v and 'distance' in v}


        for body_name, data in valid_positions.items():
            try:
                # Gezegenin ekliptik pozisyonunu kullan (lon, lat, dist)
                # calculate_celestial_positions'tan gelen veriyi kullanabiliriz.
                ecl_lon = data['degree']
                ecl_lat = data['latitude']
                ecl_dist = data['distance']
                ecl_coords = [ecl_lon, ecl_lat, ecl_dist]

                # Ecliptic koordinatlardan Horizon koordinatlarına dönüştür (azimuth, altitude)
                # swe.azalt(tjd_ut, SWE_ECL2HOR, geopos, atpress, attemp, xin)
                # xin: [lon, lat, dist] from swe.calc_ut
                # atpress, attemp: Atmosfer basıncı ve sıcaklığı, kırılma (refraction) için kullanılır. Varsayılan 0 kırılma yok.
                # Kırılma dahil: atpress=1013.25 (deniz seviyesi), attemp=15 (Celsius)
                atpress = 1013.25
                attemp = 15.0
                azalt_result = swe.azalt(jd_ut, swe.ECL2HOR, geopos, atpress, attemp, ecl_coords)

                # result: (azimuth, true_altitude, apparent_altitude)
                if azalt_result and len(azalt_result) >= 3:
                    azimuth = azalt_result[0]
                    true_altitude = azalt_result[1]
                    apparent_altitude = azalt_result[2]

                    azalt_positions[body_name] = {
                        "azimuth": round(azimuth, 2), # Kuzey 0, Doğu 90, Güney 180, Batı 270
                        "true_altitude": round(true_altitude, 2), # Kırılma düzeltilmemiş
                        "apparent_altitude": round(apparent_altitude, 2), # Kırılma düzeltilmiş
                        "is_above_horizon": apparent_altitude > 0 # Ufuk üzerinde mi? (Kırılma dahil)
                    }
                    # logger.debug(f"{body_name} Az/Alt: {azalt_positions[body_name]}")

                else:
                     logger.warning(f"{body_name} Azimuth/Altitude hesaplanamadı.")
                     azalt_positions[body_name] = {"azimuth": None, "true_altitude": None, "apparent_altitude": None, "is_above_horizon": False, "error": "Calculation failed"}


            except Exception as e:
                logger.error(f"{body_name} Azimuth/Altitude hesaplanırken hata: {str(e)}", exc_info=True)
                azalt_positions[body_name] = {"azimuth": None, "true_altitude": None, "apparent_altitude": None, "is_above_horizon": False, "error": str(e)}
                continue

        logger.info(f"Azimuth ve Altitude hesaplamaları tamamlandı ({len(azalt_positions)} cisim için).")
        return azalt_positions

    except Exception as e:
        logger.error(f"calculate_azimuth_altitude_for_bodies fonksiyonunda hata: {str(e)}", exc_info=True)
        return {}


# Refraction hesaplaması (Yardımcı fonksiyon, doğrudan kullanılmayabilir)
def calculate_refraction(altitude, atpress=1013.25, attemp=15.0, flag=True):
    """Calculate refraction correction.

    Args:
        altitude (float): True or apparent altitude in degrees
        atpress (float): Atmospheric pressure in mbar/hPa
        attemp (float): Atmospheric temperature in Celsius
        flag (bool): True for true->apparent, False for apparent->true

    Returns:
        float: Converted altitude in degrees
    """
    try:
        # altitude float olmalı
        if not isinstance(altitude, (int, float)):
             return None

        return swe.refrac(
            float(altitude), float(atpress), float(attemp), swe.TRUE_TO_APP if flag else swe.APP_TO_TRUE
        )
    except Exception as e:
        logger.error(f"Refraction calculation error: {str(e)}")
        return None

# JSON uyumluluğu için yardımcı fonksiyon
def ensure_json_serializable(obj):
    """Recursively converts objects to JSON serializable types."""
    if isinstance(obj, dict):
        return {str(k): ensure_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [ensure_json_serializable(elem) for elem in obj]
    elif isinstance(obj, tuple):
        return tuple(ensure_json_serializable(elem) for elem in obj) # Tuple'lar genellikle JSON'da liste olur ama burada tuple olarak bırakalım
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    elif isinstance(obj, (datetime, date, time)):
        return obj.isoformat() # Tarih/saat objelerini ISO formatında stringe çevir
    # Diğer olası Swisseph çıktı tipleri (örn. swe.error) veya hata objeleri stringe çevrilsin
    else:
        return str(obj)


#------------------------------------------------------------------------------
# Ana Hesaplama Fonksiyonu
#------------------------------------------------------------------------------

def calculate_astro_data(birth_date, birth_time, latitude, longitude, elevation_m=0, house_system=b"P", transit_info=None):
    """
    Verilen doğum tarihi, saati, konumu ve ev sistemine göre kapsamlı astrolojik veriyi hesaplar.

    Args:
        birth_date (str or date): Doğum tarihi (YYYY-MM-DD formatı veya date objesi)
        birth_time (str or time): Doğum saati (HH:MM formatı veya time objesi)
        latitude (float): Doğum yeri enlemi
        longitude (float): Doğum yeri boylamı
        elevation_m (float, optional): Doğum yeri yüksekliği metre cinsinden. Varsayılan 0.
        house_system (bytes or str, optional): Ev sistemi (örn. b"P" Porphyry, "R" Regiomontanus). Varsayılan Porphyry.
        transit_info (dict, optional): Transit hesaplamaları için özel bilgiler.
                                     {'date': 'YYYY-MM-DD', 'time': 'HH:MM:SS', 'latitude': float, 'longitude': float}
                                     formatında olabilir.

    Returns:
        dict: Kapsamlı astrolojik hesaplama sonuçlarını içeren sözlük.
    """
    logger.info(f"Astrolojik hesaplamalar başlatılıyor: {birth_date} {birth_time} @ Lat {latitude}, Lon {longitude}, Elev {elevation_m}m, System {house_system}")
    if transit_info:
        logger.info(f"Sağlanan transit bilgisi: {transit_info}")

    try:
        # Giriş verilerini standart formatlara dönüştür
        if isinstance(birth_date, str):
            date_obj = datetime.strptime(birth_date, "%Y-%m-%d").date()
        elif isinstance(birth_date, date):
            date_obj = birth_date
        else:
            raise TypeError("birth_date string (YYYY-MM-DD) veya date objesi olmalıdır.")

        if isinstance(birth_time, str):
            try:
                # Hem HH:MM:SS hem de HH:MM formatını den
                try:
                    time_obj = datetime.strptime(birth_time, "%H:%M:%S").time()
                except ValueError:
                    time_obj = datetime.strptime(birth_time, "%H:%M").time()
            except ValueError:
                 # Saati parse edemezse varsayılan bir saat kullan (örn. 12:00)
                 logger.warning(f"Doğum saati '{birth_time}' parse edilemedi, varsayılan 12:00:00 kullanılıyor.")
                 time_obj = time(12, 0, 0)
        elif isinstance(birth_time, time):
            time_obj = birth_time
        else:
             # Saat bilgisi yoksa veya geçersizse 12:00 kullan
             logger.warning(f"Doğum saati geçersiz veya belirtilmedi, varsayılan 12:00:00 kullanılıyor.")
             time_obj = time(12, 0, 0)

        # house_system string ise bytes'a çevir
        if isinstance(house_system, str):
            house_system_bytes = house_system.encode('utf-8')
        elif isinstance(house_system, bytes):
            house_system_bytes = house_system
        else:
             logger.warning(f"Ev sistemi '{house_system}' geçersiz, varsayılan 'P' kullanılıyor.")
             house_system_bytes = b"P"


        # Doğum tarihi ve saatini birleştir (datetime objesi)
        birth_dt = datetime.combine(date_obj, time_obj)

        # Transit hesaplamaları için kullanılacak tarih, saat ve konumu belirle
        ref_dt_for_calculations = datetime.now()
        ref_lat_for_calculations = float(latitude)
        ref_lon_for_calculations = float(longitude)

        if transit_info and isinstance(transit_info, dict):
            transit_date_str = transit_info.get('date')
            transit_time_str = transit_info.get('time', '12:00:00') # Saat yoksa öğlen 12 varsay
            transit_lat_str = transit_info.get('latitude')
            transit_lon_str = transit_info.get('longitude')

            parsed_transit_dt = None
            if transit_date_str:
                try:
                    transit_dt_date_part = datetime.strptime(transit_date_str, "%Y-%m-%d").date()
                    try:
                        transit_dt_time_part = datetime.strptime(transit_time_str, "%H:%M:%S").time()
                    except ValueError:
                        try:
                            transit_dt_time_part = datetime.strptime(transit_time_str, "%H:%M").time()
                        except ValueError:
                            logger.warning(f"Transit saati '{transit_time_str}' parse edilemedi, varsayılan 12:00:00 kullanılıyor.")
                            transit_dt_time_part = time(12,0,0)
                    parsed_transit_dt = datetime.combine(transit_dt_date_part, transit_dt_time_part)
                    ref_dt_for_calculations = parsed_transit_dt
                    logger.info(f"Transit hesaplamaları için referans tarih/saat olarak {ref_dt_for_calculations} kullanılacak.")
                except ValueError:
                    logger.warning(f"Sağlanan transit tarihi '{transit_date_str}' geçersiz. Varsayılan (mevcut zaman) kullanılacak.")

            if transit_lat_str is not None:
                try:
                    ref_lat_for_calculations = float(transit_lat_str)
                    logger.info(f"Transit hesaplamaları için referans enlem olarak {ref_lat_for_calculations} kullanılacak.")
                except ValueError:
                    logger.warning(f"Sağlanan transit enlemi '{transit_lat_str}' geçersiz. Varsayılan (natal enlem) kullanılacak.")
            
            if transit_lon_str is not None:
                try:
                    ref_lon_for_calculations = float(transit_lon_str)
                    logger.info(f"Transit hesaplamaları için referans boylam olarak {ref_lon_for_calculations} kullanılacak.")
                except ValueError:
                    logger.warning(f"Sağlanan transit boylamı '{transit_lon_str}' geçersiz. Varsayılan (natal boylam) kullanılacak.")

        # Sonuç sözlüğünü oluştur
        result = {
            "birth_info": {
                "datetime": birth_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "location": {
                    "latitude": float(latitude),
                    "longitude": float(longitude),
                    "elevation_m": float(elevation_m) if elevation_m is not None else 0.0,
                },
                "house_system": house_system_bytes.decode('utf-8'),
                # Varsayımsal UTC offset bilgisini ekle (eğer kullanılıyorsa)
                "assumed_utc_offset_for_jd_calc": "+3 hours" # Eğer GMT+3 Local -> UT dönüşümü yapılıyorsa
            }
        }

        # --- Natal Harita Hesaplamaları ---

        # Evleri ve Önemli Açıları Hesapla
        natal_houses_data = calculate_houses(birth_dt, latitude, longitude, house_system_bytes)
        result["natal_houses"] = natal_houses_data
        # Ev cusplarının dictionary olduğundan ve string key'lere sahip olduğundan emin olalım
        if "house_cusps" in result["natal_houses"]:
            result["natal_houses"]["house_cusps"] = convert_house_data_to_strings(result["natal_houses"]["house_cusps"])

        # Yükselen derecesini ana veri yapısından al (eğer hesaplandıysa)
        natal_asc_degree = natal_houses_data.get("important_angles", {}).get("ascendant")
        # ASC detayını ayrı bir key olarak da ekleyebiliriz
        if natal_asc_degree is not None:
             result["natal_ascendant"] = {
                 "degree": natal_asc_degree,
                 "sign": get_zodiac_sign(natal_asc_degree),
                 "degree_in_sign": round(get_degree_in_sign(natal_asc_degree), 2),
                 "decan": get_decan(get_degree_in_sign(natal_asc_degree))
             }
        else:
             result["natal_ascendant"] = {"error": "Ascendant hesaplanamadı."}


        # Gezegen Pozisyonlarını Hesapla (Ev bilgisi calculate_houses'dan gelen cusp'larla belirlenir)
        natal_planet_positions = calculate_natal_planet_positions(birth_dt, natal_houses_data.get("house_cusps", {}))
        result["natal_planet_positions"] = natal_planet_positions

        # Ekstra Noktaları (Asteroid, Uranian, Düğümler, Lilith vb.) Hesapla
        natal_additional_points = calculate_natal_additional_points(birth_dt, natal_houses_data.get("house_cusps", {}))
        result["natal_additional_points"] = natal_additional_points

        # Natal Gezegenler ve Ek Noktaları Birleştir (Açı, Antiscia, Midpoint hesaplamaları için uygun format)
        all_natal_celestial_positions = {}
        all_natal_celestial_positions.update(natal_planet_positions)
        all_natal_celestial_positions.update(natal_additional_points)
        # Asc, MC gibi önemli noktaları da bu birleşik dictionary'ye ekleyelim (açı vb. hesaplamaları için)
        if natal_houses_data.get("important_angles"):
             for angle_name, angle_deg in natal_houses_data["important_angles"].items():
                 # Sadece derece varsa ekle
                 if angle_deg is not None:
                     all_natal_celestial_positions[angle_name.capitalize()] = {
                         "degree": angle_deg,
                         "sign": get_zodiac_sign(angle_deg),
                         "degree_in_sign": round(get_degree_in_sign(angle_deg), 2),
                         "is_angle": True, # Bu bir açı, gezegen değil
                         # Diğer bilgiler (retrograd, hız, ev, lat, dist) açılar için anlamlı değildir.
                     }


        # Natal-Natal Açıları Hesapla
        natal_aspects = calculate_aspects(all_natal_celestial_positions)
        result["natal_aspects"] = natal_aspects


        # Azimuth/Altitude Hesapla (Natal Gezegenler için)
        # elevation_m parametresinin kullanıldığından emin ol. Sadece ana gezegenler için yapalım.
        natal_azimuth_altitude = calculate_azimuth_altitude_for_bodies(
            birth_dt, latitude, longitude, elevation_m, natal_planet_positions
        )
        result["natal_azimuth_altitude"] = natal_azimuth_altitude


        # Sabit Yıldızları Hesapla
        natal_fixed_stars = calculate_fixed_stars(birth_dt)
        result["natal_fixed_stars"] = natal_fixed_stars

        # Antiscia ve Contra-antiscia Hesapla (Tüm natal noktalar için)
        natal_antiscia = calculate_antiscia(all_natal_celestial_positions)
        result["natal_antiscia"] = natal_antiscia

        # Dignity ve Debility Skorlarını Hesapla (Sadece ana gezegenler için)
        natal_dignity_scores = calculate_dignity_scores(natal_planet_positions)
        result["natal_dignity_scores"] = natal_dignity_scores

        # Part of Fortune Hesapla (Natal gezegen pozisyonları ve Asc derecesi gerekli)
        if natal_asc_degree is not None and natal_planet_positions.get("Sun") and natal_planet_positions.get("Moon"):
            natal_part_of_fortune = calculate_part_of_fortune(
                birth_dt, latitude, longitude, natal_planet_positions, natal_asc_degree
            )
            result["natal_part_of_fortune"] = natal_part_of_fortune
        else:
            result["natal_part_of_fortune"] = {"error": "Part of Fortune hesaplama için gerekli veriler eksik (Asc, Güneş veya Ay)."}


        # Arap Noktalarını Hesapla (Natal gezegen pozisyonları ve Asc derecesi gerekli)
        # calculate_arabic_parts fonksiyonu tüm gerekli gezegenleri kontrol eder
        if natal_asc_degree is not None:
             natal_arabic_parts = calculate_arabic_parts(
                 birth_dt, natal_planet_positions, natal_asc_degree
             )
             result["natal_arabic_parts"] = natal_arabic_parts
        else:
             result["natal_arabic_parts"] = {"error": "Ascendant hesaplanamadığı için Arap Noktaları hesaplanamadı."}

        # Lunation Cycle Hesapla (Doğum anı)
        if natal_planet_positions.get("Sun") and natal_planet_positions.get("Moon"):
             natal_lunation_cycle = calculate_lunation_cycle(birth_dt, natal_planet_positions)
             result["natal_lunation_cycle"] = natal_lunation_cycle
        else:
             result["natal_lunation_cycle"] = {"error": "Lunation Cycle hesaplama için Güneş veya Ay pozisyonu eksik."}

        # Deklinasyonları Hesapla (Sadece ana gezegenler için)
        natal_declinations = calculate_declinations(birth_dt, natal_planet_positions)
        result["natal_declinations"] = natal_declinations

        # Midpoint Analizi Hesapla (Tüm natal noktalar için)
        natal_midpoint_analysis = get_midpoint_aspects(all_natal_celestial_positions)
        result["natal_midpoint_analysis"] = natal_midpoint_analysis

        # Derin Harmonik Analiz Hesapla (Tüm natal noktalar için)
        deep_harmonic_analysis = calculate_deep_harmonic_analysis(birth_dt, all_natal_celestial_positions)
        result["deep_harmonic_analysis"] = deep_harmonic_analysis
        # Navamsa (H9) genellikle ayrıca istenir, derin analiz içinden çekebiliriz
        result["navamsa_chart"] = deep_harmonic_analysis.get("H9", {})


        # Vimshottari Dasa Hesapla (Natal Ay derecesi gerekli)
        if natal_planet_positions.get("Moon"):
             natal_moon_degree = natal_planet_positions["Moon"].get("degree")
             vimshottari_dasa = get_vimshottari_dasa(birth_dt, natal_moon_degree)
             result["vimshottari_dasa"] = vimshottari_dasa
        else:
             result["vimshottari_dasa"] = {"error": "Ay pozisyonu eksik, Vimshottari Dasa hesaplanamadı."}


        # Firdaria Periyotları Hesapla (Natal Güneş pozisyonu gerekli)
        if natal_planet_positions.get("Sun"):
             natal_sun_pos = natal_planet_positions["Sun"]
             firdaria_periods = get_firdaria_period(birth_dt, natal_sun_pos, natal_houses_data)
             result["firdaria_periods"] = firdaria_periods
        else:
             result["firdaria_periods"] = {"error": "Güneş pozisyonu eksik, Firdaria periyotları hesaplanamadı."}


        # Natal Özet Yorumu Oluştur
        natal_summary_interpretation = get_natal_summary(natal_planet_positions, natal_houses_data, birth_dt)
        result["natal_summary_interpretation"] = natal_summary_interpretation


        # Tutulmaları Bul (Doğum tarihi civarında)
        # Arama aralığını belirle (örn. 1 yıl öncesi ve sonrası)
        eclipse_search_start_birth = birth_dt - timedelta(days=365)
        eclipse_search_end_birth = birth_dt + timedelta(days=365)
        eclipses_nearby_birth = find_eclipses_in_range(eclipse_search_start_birth, eclipse_search_end_birth)
        result["eclipses_nearby_birth"] = eclipses_nearby_birth


        # --- Transit ve Progresyon Hesaplamaları (Güncel Tarihe Göre) ---

        current_dt = datetime.now()
        result["current_datetime"] = {"datetime_str": current_dt.strftime("%Y-%m-%d %H:%M:%S")}

        # Transit Pozisyonlarını Hesapla (Güncel tarih ve konuma göre)
        transit_positions, transit_houses_data = get_transit_positions(current_dt, latitude, longitude)
        result["transit_positions"] = transit_positions
        result["transit_houses"] = transit_houses_data
        # Transit ev cusplarının dictionary olduğundan ve string key'lere sahip olduğundan emin olalım
        if "house_cusps" in result["transit_houses"]:
            result["transit_houses"]["house_cusps"] = convert_house_data_to_strings(result["transit_houses"]["house_cusps"])

        # Transit Azimuth/Altitude Hesapla (Sadece transit gezegenler için)
        transit_azimuth_altitude = calculate_azimuth_altitude_for_bodies(
            current_dt, latitude, longitude, elevation_m, transit_positions
        )
        result["transit_azimuth_altitude"] = transit_azimuth_altitude


        # Transit-Natal Açıları Hesapla
        # Transit pozisyonları (gezegenler) vs Tümü natal noktalar (gezegenler, ek noktalar, açılar)
        transit_to_natal_aspects = calculate_aspects(transit_positions, all_natal_celestial_positions)
        result["transit_to_natal_aspects"] = transit_to_natal_aspects


        # Sekonder (İkincil) Progresyonları Hesapla
        secondary_progressions, progressed_houses_data = calculate_secondary_progressions(
            birth_dt, current_dt, latitude, longitude
        )
        result["secondary_progressions"] = secondary_progressions
        result["progressed_houses"] = progressed_houses_data
         # Progresif ev cusplarının dictionary olduğundan ve string key'lere sahip olduğundan emin olalım
        if "house_cusps" in result["progressed_houses"]:
            result["progressed_houses"]["house_cusps"] = convert_house_data_to_strings(result["progressed_houses"]["house_cusps"])

        # Progresif Ay Fazı Hesapla (Secondary Progressions'dan alınan Güneş ve Ay ile)
        progressed_moon_phase = calculate_progressed_moon_phase(secondary_progressions)
        result["progressed_moon_phase"] = progressed_moon_phase

        # Solar Arc Progresyonları Hesapla (Natal pozisyonlara solar arc eklenir)
        # Natal gezegen pozisyonları gerekli
        solar_arc_progressions = get_solar_arc_progressions(birth_dt, current_dt, natal_planet_positions)
        result["solar_arc_progressions"] = solar_arc_progressions


        # Solar Return Haritası Hesapla (Güncel yıla göre)
        solar_return_chart_data = calculate_solar_return_chart(birth_dt, current_dt, latitude, longitude)
        result["solar_return_chart"] = solar_return_chart_data

        # Lunar Return Haritası Hesapla (Güncel tarihten sonraki ilk)
        lunar_return_chart_data = calculate_lunar_return_chart(birth_dt, current_dt, latitude, longitude)
        result["lunar_return_chart"] = lunar_return_chart_data

        # Tutulmaları Bul (Güncel tarih civarında)
        # Arama aralığını belirle (örn. 6 ay öncesi ve sonrası)
        eclipse_search_start_current = current_dt - timedelta(days=180)
        eclipse_search_end_current = current_dt + timedelta(days=180)
        eclipses_nearby_current = find_eclipses_in_range(eclipse_search_start_current, eclipse_search_end_current)
        result["eclipses_nearby_current"] = eclipses_nearby_current


        logger.info("Astrolojik hesaplamalar tamamlandı.")

        # Sonucu JSON uyumlu hale getirmek için recursive fonksiyonu kullan
        final_result = ensure_json_serializable(result)

        logger.info("Astrolojik hesaplama modu tamamlandı.")
        print("Astrolojik hesaplama sonucu:", final_result)
        
        return final_result

    except Exception as e:
        logger.error(f"Genel hesaplama fonksiyonunda kritik hata: {str(e)}", exc_info=True)
        # Ana fonksiyonda hata olursa bir hata nesnesi döndür
        return {"error": f"Hesaplamalar sırasında kritik bir hata oluştu: {str(e)}"}

def calculate_house_for_degree(degree, birth_dt, latitude, longitude, house_system=b"P"):
    """
    Verilen derecenin hangi evde olduğunu hesaplar.
    
    Args:
        degree (float): Hesaplanacak derece (0-360)
        birth_dt (datetime): Doğum tarihi ve saati
        latitude (float): Enlem
        longitude (float): Boylam
        house_system (bytes): Ev sistemi (default: b"P" Porphyry)
        
    Returns:
        int: Ev numarası (1-12)
    """
    try:
        # Ev cusplarını hesapla
        houses = swe.houses(birth_dt, latitude, longitude, house_system)
        cusps = houses[0]  # Ev başlangıç dereceleri
        
        # Derecenin hangi evde olduğunu bul
        for i in range(12):
            start = cusps[i]
            end = cusps[i+1] if i < 11 else cusps[0]
            
            if start <= degree < end or (i == 11 and degree >= start):
                return i + 1
            elif start > end and (degree >= start or degree < end):
                return i + 1
                
        return 1  # Varsayılan olarak 1. ev
    
    except Exception as e:
        logger.error(f"Ev hesaplama hatası: {str(e)}")
        return 1  # Hata durumunda varsayılan 1. ev




def calculate_lunation_cycle(birth_dt, natal_planet_positions):
    """
    Doğum anındaki Ay fazını hesaplar.
    
    Args:
        birth_dt (datetime): Doğum tarihi ve saati
        natal_planet_positions (dict): Natal gezegen pozisyonları
        
    Returns:
        dict: Ay fazı bilgileri
    """
    try:
        # Güneş ve Ay pozisyonlarını al
        sun_pos = natal_planet_positions.get("Sun", {})
        moon_pos = natal_planet_positions.get("Moon", {})
        
        if not sun_pos or not moon_pos:
            return {"error": "Güneş veya Ay pozisyonu eksik"}
            
        sun_degree = sun_pos.get("degree", 0)
        moon_degree = moon_pos.get("degree", 0)
        
        # Faz açısını hesapla
        prog_sun_deg = (sun_degree + 360) % 360
        prog_moon_deg = (moon_degree + 360) % 360

        phase_angle = (prog_moon_deg - prog_sun_deg) % 360
        phase_angle_in_sign = get_degree_in_sign(phase_angle)
        phase_sign = get_zodiac_sign(phase_angle)
        phase_degree_in_sign = round(phase_angle % 30, 2)
        phase_name = get_phase_name(phase_angle)
        return {
            "phase_angle": phase_angle,
            "phase_sign": phase_sign,
            "phase_degree_in_sign": phase_degree_in_sign,
            "phase_name": phase_name
        }
    except Exception as e:
        logger.error(f"Ay fazı hesaplama hatası: {str(e)}")
        return {"error": f"Ay fazı hesaplanamadı: {str(e)}"}


def calculate_declinations(birth_dt, natal_planet_positions):
    """
    Verilen doğum tarihi ve gezegen pozisyonlarına göre deklinasyonları hesaplar.
    
    Args:
        birth_dt (datetime): Doğum tarihi ve saati
        natal_planet_positions (dict): Natal gezegen pozisyonları
    Returns:
        dict: Deklinasyon bilgileri
    """
    try:
        declinations = {}
        for planet, pos in natal_planet_positions.items():
            if "degree" in pos:
                degree = pos["degree"]
                # Deklinasyon hesaplama formülü (basit bir örnek)
                declination = round(math.sin(math.radians(degree)) * 90, 2)  # Basit bir formül
                declinations[planet] = {
                    "declination": declination,
                    "sign": get_zodiac_sign(declination),
                    "degree_in_sign": round(get_degree_in_sign(declination), 2)
                }
        return declinations
    except Exception as e:
        logger.error(f"Deklinasyon hesaplama hatası: {str(e)}")
        return {"error": f"Deklinasyon hesaplanamadı: {str(e)}"}
def get_phase_name(phase_angle):
    """
    Faz açısına göre Ay fazını isimlendirir.
    
    Args:
        phase_angle (float): Faz açısı (0-360)
        
    Returns:
        str: Ay fazı ismi
    """
    if phase_angle < 0 or phase_angle >= 360:
        raise ValueError("Faz açısı 0 ile 360 arasında olmalıdır.")
    
    if phase_angle < 45:
        return "Yeni Ay"
    elif phase_angle < 135:
        return "İlk Dördün"
    elif phase_angle < 225:
        return "Dolunay"
    elif phase_angle < 315:
        return "Son Dördün"
    else:
        return "Yeni Ay"


def calculate_part_of_fortune(birth_dt, latitude, longitude, natal_planet_positions, asc_degree):
    """
    Part of Fortune pozisyonunu hesaplar.
    
    Args:
        birth_dt (datetime): Doğum tarihi ve saati
        latitude (float): Doğum yeri enlemi
        longitude (float): Doğum yeri boylamı
        natal_planet_positions (dict): Natal gezegen pozisyonları
        asc_degree (float): Yükselen burç derecesi
        
    Returns:
        dict: Part of Fortune pozisyon bilgileri
    """
    try:
        # Güneş ve Ay pozisyonlarını al
        sun_pos = natal_planet_positions.get("Sun", {})
        moon_pos = natal_planet_positions.get("Moon", {})
        
        if not sun_pos or not moon_pos:
            return {"error": "Güneş veya Ay pozisyonu eksik"}
            
        sun_degree = sun_pos.get("degree", 0)
        moon_degree = moon_pos.get("degree", 0)
        
        # Part of Fortune formülü: ASC + Moon - Sun (Gündüz doğumlar için)
        # Gece doğumlar için: ASC + Sun - Moon
        is_daytime = birth_dt.hour >= 6 and birth_dt.hour < 18
        if is_daytime:
            pof_degree = (asc_degree + moon_degree - sun_degree) % 360
        else:
            pof_degree = (asc_degree + sun_degree - moon_degree) % 360
            
        return {
            "degree": pof_degree,
            "sign": get_zodiac_sign(pof_degree),
            "degree_in_sign": round(get_degree_in_sign(pof_degree), 2),
            "house": calculate_house_for_degree(pof_degree, birth_dt, latitude, longitude)
        }
        
    except Exception as e:
        logger.error(f"Part of Fortune hesaplama hatası: {str(e)}")
        return {"error": f"Part of Fortune hesaplanamadı: {str(e)}"}

def calculate_arabic_parts(birth_dt, natal_planet_positions, asc_degree):
    """
    Arap Noktalarını hesaplar.
    
    Args:
        birth_dt (datetime): Doğum tarihi ve saati
        natal_planet_positions (dict): Natal gezegen pozisyonları
        asc_degree (float): Yükselen burç derecesi
        
    Returns:
        dict: Arap Noktası pozisyon bilgileri
    """
    try:
        arabic_parts = {}
        
        # Güneş ve Ay pozisyonlarını al
        sun_pos = natal_planet_positions.get("Sun", {})
        moon_pos = natal_planet_positions.get("Moon", {})
        
        if not sun_pos or not moon_pos:
            return {"error": "Güneş veya Ay pozisyonu eksik"}
            
        sun_degree = sun_pos.get("degree", 0)
        moon_degree = moon_pos.get("degree", 0)
        
        # Arap Noktası formülü: ASC + Moon - Sun (Gündüz doğumlar için)
        # Gece doğumlar için: ASC + Sun - Moon
        is_daytime = birth_dt.hour >= 6 and birth_dt.hour < 18
        if is_daytime:
            part_of_fortune_degree = (asc_degree + moon_degree - sun_degree) % 360
        else:
            part_of_fortune_degree = (asc_degree + sun_degree - moon_degree) % 360
            
        latitude = birth_dt.latitude if hasattr(birth_dt, 'latitude') else 0
        longitude = birth_dt.longitude if hasattr(birth_dt, 'longitude') else 0
        # Part of Fortune hesapla
        # Part of Fortune formülü: ASC + Moon - Sun (Gündüz doğumlar için)
        # Gece doğumlar için: ASC + Sun - Moon
        # Güneş ve Ay pozisyonlarını al
        # Güneş ve Ay pozisyonlarını al
        # Güneş ve Ay pozisyonlarını al    
        arabic_parts["Part of Fortune"] = {
            "degree": part_of_fortune_degree,
            "sign": get_zodiac_sign(part_of_fortune_degree),
            "degree_in_sign": round(get_degree_in_sign(part_of_fortune_degree), 2),
            "house": calculate_house_for_degree(part_of_fortune_degree, birth_dt, latitude, longitude)
        }
        
        # Diğer Arap Noktaları hesaplamaları burada yapılabilir
        
        return arabic_parts
        
    except Exception as e:
        logger.error(f"Arap Noktası hesaplama hatası: {str(e)}")
        return {"error": f"Arap Noktası hesaplanamadı: {str(e)}"}


# Dosya sonu işareti (isteğe bağlı)
#------------------------------------------------------------------------------