"""
Astrology Calculations - Refactored Version
============================================

Bu modül, monolithic calculate_astro_data fonksiyonunu modüler bir class yapısına dönüştürür.
Her hesaplama türü (natal, transit, progression) ayrı metodlarda tutulur.

Kullanım:
    from astro_calculations_refactored import AstroCalculator
    calculator = AstroCalculator()
    result = calculator.calculate_all(birth_date, birth_time, latitude, longitude)
"""

import swisseph as swe
from datetime import datetime, date, time, timedelta
from typing import Dict, Any, Optional, Tuple
import logging
from utils import Constants

logger = logging.getLogger(__name__)


class AstroCalculationError(Exception):
    """Astrolojik hesaplama hatası."""
    pass


class InvalidDateError(AstroCalculationError):
    """Geçersiz tarih hatası."""
    pass


class InvalidCoordinatesError(AstroCalculationError):
    """Geçersiz koordinat hatası."""
    pass


class AstroCalculator:
    """
    Astrolojik hesaplamaları yapan class.
    
    Monolithic calculate_astro_data fonksiyonunun refactor edilmiş hali.
    Her hesaplama türü ayrı bir metodda tutulur, böylece test edilebilir ve yeniden kullanılabilir.
    """
    
    def __init__(self, house_system: bytes = Constants.DEFAULT_HOUSE_SYSTEM):
        """
        AstroCalculator'ı başlat.
        
        Args:
            house_system: Ev sistemi (Porphyry=b"P", Placidus=b"P", Koch=b"K", vb.)
        """
        self.house_system = house_system
        self.swe_julday = None
        self.gmtoff = None
        
        # Ephemeris dosyasını yükle
        try:
            swe.set_ephe_path(None)  # Default path kullan
        except Exception as e:
            logger.warning(f"Ephemeris yüklenirken uyarı: {e}")
    
    def _parse_datetime(
        self, 
        birth_date: Any, 
        birth_time: Any
    ) -> Tuple[date, time]:
        """
        Tarih ve saat objelerini parse et ve doğrula.
        
        Args:
            birth_date: Tarih (str, date, veya datetime)
            birth_time: Saat (str, time, veya datetime)
            
        Returns:
            (date, time) tuple
            
        Raises:
            InvalidDateError: Geçersiz tarih/saat
        """
        # Tarih parse
        if isinstance(birth_date, str):
            try:
                birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
            except ValueError:
                raise InvalidDateError(f"Geçersiz tarih formatı: {birth_date}")
        elif isinstance(birth_date, datetime):
            birth_date = birth_date.date()
        elif not isinstance(birth_date, date):
            raise InvalidDateError(f"Geçersiz tarih tipi: {type(birth_date)}")
        
        # Saat parse
        if isinstance(birth_time, str):
            from utils import parse_time_flexible
            birth_time = parse_time_flexible(birth_time)
        elif isinstance(birth_time, datetime):
            birth_time = birth_time.time()
        elif not isinstance(birth_time, time):
            raise InvalidDateError(f"Geçersiz saat tipi: {type(birth_time)}")
        
        return birth_date, birth_time
    
    def _calculate_julian_day(
        self, 
        birth_date: date, 
        birth_time: time, 
        timezone_offset: float = 3.0
    ) -> float:
        """
        Julian Day'i hesapla.
        
        Args:
            birth_date: Doğum tarihi
            birth_time: Doğum saati
            timezone_offset: Timezone offset (saat)
            
        Returns:
            Julian Day (float)
        """
        # UTC'ye çevir
        birth_datetime = datetime.combine(birth_date, birth_time)
        utc_datetime = birth_datetime - timedelta(hours=timezone_offset)
        
        # Julian Day hesapla
        jd = swe.julday(
            utc_datetime.year,
            utc_datetime.month,
            utc_datetime.day,
            utc_datetime.hour + utc_datetime.minute / 60.0 + utc_datetime.second / 3600.0
        )
        
        return jd
    
    def calculate_natal_chart(
        self,
        julian_day: float,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Natal chart hesapla.
        
        Args:
            julian_day: Julian Day
            latitude: Enlem
            longitude: Boylam
            
        Returns:
            Natal chart verileri
        """
        result = {}
        
        # 1. Gezegen konumlarını hesapla
        planet_positions = self._calculate_planet_positions(julian_day)
        result["natal_planet_positions"] = planet_positions
        
        # 2. Evleri hesapla
        houses = self._calculate_houses(julian_day, latitude, longitude)
        result["natal_houses"] = houses
        
        # 3. Yükselen ve MC'yi hesapla
        ascendant, mc = self._calculate_angles(julian_day, latitude, longitude)
        result["ascendant"] = ascendant
        result["midheaven"] = mc
        
        # 4. Açıları hesapla
        aspects = self._calculate_aspects(planet_positions)
        result["natal_aspects"] = aspects
        
        # 5. Ek puanları hesapla (Lilith, Chiron, vb.)
        additional_points = self._calculate_additional_points(julian_day)
        result["natal_additional_points"] = additional_points
        
        # 6. Element ve quality balance
        element_balance = self._calculate_element_balance(planet_positions)
        result["element_balance"] = element_balance
        
        # 7. Güneş ve Ay burçlarını ekle
        if "Sun" in planet_positions:
            result["sun_sign"] = planet_positions["Sun"]["sign"]
        if "Moon" in planet_positions:
            result["moon_sign"] = planet_positions["Moon"]["sign"]
        
        return result
    
    def _calculate_planet_positions(self, julian_day: float) -> Dict[str, Dict[str, Any]]:
        """
        Gezegen konumlarını hesapla.
        
        Args:
            julian_day: Julian Day
            
        Returns:
            Gezegen konumları dict
        """
        planets = {
            "Sun": 0, "Moon": 1, "Mercury": 2, "Venus": 3, "Mars": 4,
            "Jupiter": 5, "Saturn": 6, "Uranus": 7, "Neptune": 8, "Pluto": 9
        }
        
        positions = {}
        zodiac_signs = Constants.ZODIAC_SIGNS
        
        for planet_name, planet_id in planets.items():
            try:
                # Gezegen pozisyonunu hesapla (heliocentric)
                xx, ret = swe.calc_ut(julian_day, planet_id)
                degree = xx[0] % 360
                
                # Burcu hesapla
                sign_index = int(degree // 30)
                sign = zodiac_signs[sign_index] if 0 <= sign_index < 12 else "Bilinmeyen"
                
                # Ev hesapla (daha sonra houses ile güncellenecek)
                degree_in_sign = degree % 30
                
                positions[planet_name] = {
                    "degree": round(degree, 2),
                    "sign": sign,
                    "position_in_sign": round(degree_in_sign, 2),
                    "retrograde": ret == -1,  # -1: retrograde, 1: direct
                    "house": None  # Daha sonra hesaplanacak
                }
                
            except Exception as e:
                logger.error(f"{planet_name} hesaplanırken hata: {e}")
                positions[planet_name] = {"error": str(e)}
        
        return positions
    
    def _calculate_houses(
        self,
        julian_day: float,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Evleri hesapla.
        
        Args:
            julian_day: Julian Day
            latitude: Enlem
            longitude: Boylam
            
        Returns:
            Ev hesaplamaları
        """
        try:
            houses = swe.houses(julian_day, latitude, longitude, self.house_system)
            
            result = {
                "houses": [],
                "house_system": self.house_system.decode() if isinstance(self.house_system, bytes) else self.house_system
            }
            
            for i, house_cusp in enumerate(houses[0], 1):
                sign_index = int(house_cusp // 30) % 12
                sign = Constants.ZODIAC_SIGNS[sign_index] if 0 <= sign_index < 12 else "Bilinmeyen"
                degree_in_sign = house_cusp % 30
                
                result["houses"].append({
                    "house": i,
                    "cusp": round(house_cusp, 2),
                    "sign": sign,
                    "degree_in_sign": round(degree_in_sign, 2)
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Ev hesaplanırken hata: {e}")
            return {"error": str(e)}
    
    def _calculate_angles(
        self,
        julian_day: float,
        latitude: float,
        longitude: float
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Yükselen ve Midheaven hesapla.
        
        Args:
            julian_day: Julian Day
            latitude: Enlem
            longitude: Boylam
            
        Returns:
            (ascendant, midheaven) tuple
        """
        try:
            houses = swe.houses(julian_day, latitude, longitude, b"P")
            
            # Yükselen = 1. evin ucu
            asc_degree = houses[0][0] % 360
            asc_sign_index = int(asc_degree // 30) % 12
            asc_sign = Constants.ZODIAC_SIGNS[asc_sign_index] if 0 <= asc_sign_index < 12 else "Bilinmeyen"
            
            ascendant = {
                "degree": round(asc_degree, 2),
                "sign": asc_sign,
                "degree_in_sign": round(asc_degree % 30, 2)
            }
            
            # Midheaven = 10. evin ucu
            mc_degree = houses[0][9] % 360
            mc_sign_index = int(mc_degree // 30) % 12
            mc_sign = Constants.ZODIAC_SIGNS[mc_sign_index] if 0 <= mc_sign_index < 12 else "Bilinmeyen"
            
            midheaven = {
                "degree": round(mc_degree, 2),
                "sign": mc_sign,
                "degree_in_sign": round(mc_degree % 30, 2)
            }
            
            return ascendant, midheaven
            
        except Exception as e:
            logger.error(f"Açılar hesaplanırken hata: {e}")
            return {"error": str(e)}, {"error": str(e)}
    
    def _calculate_aspects(
        self,
        planet_positions: Dict[str, Dict[str, Any]],
        orb: float = 8.0
    ) -> list:
        """
        Gezegenler arası açıları hesapla.
        
        Args:
            planet_positions: Gezegen konumları
            orb: Orb derecesi
            
        Returns:
            Açılar listesi
        """
        aspects = []
        aspect_types = {
            "conjunction": 0,
            "opposition": 180,
            "trine": 120,
            "square": 90,
            "sextile": 60
        }
        
        planets = list(planet_positions.keys())
        
        for i in range(len(planets)):
            for j in range(i + 1, len(planets)):
                planet1 = planets[i]
                planet2 = planets[j]
                
                if "error" in planet_positions[planet1] or "error" in planet_positions[planet2]:
                    continue
                
                degree1 = planet_positions[planet1]["degree"]
                degree2 = planet_positions[planet2]["degree"]
                
                diff = abs(degree1 - degree2)
                if diff > 180:
                    diff = 360 - diff
                
                for aspect_name, aspect_angle in aspect_types.items():
                    if abs(diff - aspect_angle) <= orb:
                        aspects.append({
                            "planet1": planet1,
                            "planet2": planet2,
                            "aspect_type": aspect_name,
                            "orb": round(abs(diff - aspect_angle), 2),
                            "degree_diff": round(diff, 2)
                        })
                        break
        
        return aspects
    
    def _calculate_additional_points(self, julian_day: float) -> Dict[str, Any]:
        """
        Ek puanları hesapla (Lilith, Chiron, vb.).
        
        Args:
            julian_day: Julian Day
            
        Returns:
            Ek puanlar
        """
        additional_points = {}
        
        # Lilith (Mean Apogee of the Moon)
        try:
            lilith_deg, ret = swe.calc_ut(julian_day, swe.MEAN_APOG)
            additional_points["lilith"] = {
                "degree": round(lilith_deg[0] % 360, 2),
                "retrograde": ret == -1
            }
        except Exception as e:
            logger.error(f"Lilith hesaplanırken hata: {e}")
        
        # Chiron
        try:
            chiron_deg, ret = swe.calc_ut(julian_day, swe.CHIRON)
            additional_points["chiron"] = {
                "degree": round(chiron_deg[0] % 360, 2),
                "retrograde": ret == -1
            }
        except Exception as e:
            logger.error(f"Chiron hesaplanırken hata: {e}")
        
        return additional_points
    
    def _calculate_element_balance(
        self,
        planet_positions: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Element dengesini hesapla.
        
        Args:
            planet_positions: Gezegen konumları
            
        Returns:
            Element dengesi
        """
        elements = {"fire": 0, "earth": 0, "air": 0, "water": 0}
        
        for planet_name, data in planet_positions.items():
            if "error" in data:
                continue
            
            sign = data.get("sign", "")
            element = None
            
            if sign in Constants.ELEMENT_FIRE:
                element = "fire"
            elif sign in Constants.ELEMENT_EARTH:
                element = "earth"
            elif sign in Constants.ELEMENT_AIR:
                element = "air"
            elif sign in Constants.ELEMENT_WATER:
                element = "water"
            
            if element:
                elements[element] += 1
        
        return elements
    
    def calculate_transit(
        self,
        transit_date: date,
        natal_julian_day: float,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Transit hesapla.
        
        Args:
            transit_date: Transit tarihi
            natal_julian_day: Natal Julian Day
            latitude: Enlem
            longitude: Boylam
            
        Returns:
            Transit verileri
        """
        result = {}
        
        # Transit Julian Day hesapla
        transit_jd = self._calculate_julian_day(transit_date, time(12, 0))
        
        # Transit gezegen konumları
        transit_planets = self._calculate_planet_positions(transit_jd)
        result["transit_positions"] = transit_planets
        
        # Transit evleri
        transit_houses = self._calculate_houses(transit_jd, latitude, longitude)
        result["transit_houses"] = transit_houses
        
        # Transit-Natal açıları
        # Natal gezegenleri hesapla
        natal_planets = self._calculate_planet_positions(natal_julian_day)
        transit_aspects = self._calculate_transit_aspects(transit_planets, natal_planets)
        result["transit_to_natal_aspects"] = transit_aspects
        
        return result
    
    def _calculate_transit_aspects(
        self,
        transit_planets: Dict[str, Dict[str, Any]],
        natal_planets: Dict[str, Dict[str, Any]],
        orb: float = 3.0
    ) -> list:
        """
        Transit-Natal açılarını hesapla.
        
        Args:
            transit_planets: Transit gezegen konumları
            natal_planets: Natal gezegen konumları
            orb: Orb derecesi
            
        Returns:
            Transit-Natal açıları
        """
        aspects = []
        aspect_types = {
            "conjunction": 0,
            "opposition": 180,
            "trine": 120,
            "square": 90,
            "sextile": 60
        }
        
        for transit_planet, transit_data in transit_planets.items():
            if "error" in transit_data:
                continue
            
            for natal_planet, natal_data in natal_planets.items():
                if "error" in natal_data:
                    continue
                
                transit_degree = transit_data["degree"]
                natal_degree = natal_data["degree"]
                
                diff = abs(transit_degree - natal_degree)
                if diff > 180:
                    diff = 360 - diff
                
                for aspect_name, aspect_angle in aspect_types.items():
                    if abs(diff - aspect_angle) <= orb:
                        aspects.append({
                            "transit_planet": transit_planet,
                            "natal_planet": natal_planet,
                            "aspect_type": aspect_name,
                            "orb": round(abs(diff - aspect_angle), 2),
                            "degree_diff": round(diff, 2)
                        })
                        break
        
        return aspects
    
    def calculate_all(
        self,
        birth_date: Any,
        birth_time: Any,
        latitude: float,
        longitude: float,
        transit_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Tüm astrolojik hesaplamaları yap.
        
        Bu fonksiyon, orijinal calculate_astro_data fonksiyonunun yerine geçer.
        Backward compatibility sağlar.
        
        Args:
            birth_date: Doğum tarihi
            birth_time: Doğum saati
            latitude: Enlem
            longitude: Boylam
            transit_info: Transit bilgileri (opsiyonel)
            
        Returns:
            Tüm astrolojik veriler
            
        Raises:
            InvalidDateError: Geçersiz tarih
            InvalidCoordinatesError: Geçersiz koordinat
        """
        try:
            # 1. Validasyon
            if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
                raise InvalidCoordinatesError(f"Geçersiz koordinatlar: Lat={latitude}, Lon={longitude}")
            
            # 2. Datetime parse
            birth_date_obj, birth_time_obj = self._parse_datetime(birth_date, birth_time)
            
            # 3. Julian Day hesapla
            julian_day = self._calculate_julian_day(birth_date_obj, birth_time_obj)
            
            # 4. Natal chart hesapla
            result = self.calculate_natal_chart(julian_day, latitude, longitude)
            
            # 5. Transit hesapla (varsa)
            if transit_info:
                transit_date = transit_info.get("date")
                if transit_date:
                    transit_result = self.calculate_transit(
                        transit_date,
                        julian_day,
                        latitude,
                        longitude
                    )
                    result.update(transit_result)
            
            # 6. Özet yorum ekle
            result["natal_summary_interpretation"] = self._generate_summary(result)
            
            return result
            
        except InvalidDateError as e:
            logger.error(f"Geçersiz tarih: {e}")
            return {"error": str(e)}
        except InvalidCoordinatesError as e:
            logger.error(f"Geçersiz koordinat: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Astrolojik hesaplama hatası: {e}", exc_info=True)
            return {"error": f"Hesaplama hatası: {str(e)}"}
    
    def _generate_summary(self, chart_data: Dict[str, Any]) -> str:
        """
        Hesaplanan chart'tan özet yorum oluştur.
        
        Args:
            chart_data: Chart verileri
            
        Returns:
            Özet yorum
        """
        summary_parts = []
        
        # Güneş burcu
        sun_sign = chart_data.get("sun_sign", "")
        if sun_sign:
            summary_parts.append(f"Güneş burcunuz {sun_sign}.")
        
        # Ay burcu
        moon_sign = chart_data.get("moon_sign", "")
        if moon_sign:
            summary_parts.append(f"Ay burcunuz {moon_sign}.")
        
        # Yükselen
        ascendant = chart_data.get("ascendant", {})
        if isinstance(ascendant, dict) and "sign" in ascendant:
            summary_parts.append(f"Yükselen burcunuz {ascendant['sign']}.")
        
        # Element dengesi
        element_balance = chart_data.get("element_balance", {})
        if element_balance:
            dominant = max(element_balance, key=element_balance.get)
            summary_parts.append(f"Dominant elementiniz {dominant}.")
        
        return " ".join(summary_parts) if summary_parts else "Chart hesaplandı."


# =============================================================================
# BACKWARD COMPATIBILITY WRAPPER
# =============================================================================
def calculate_astro_data(
    birth_date: Any,
    birth_time: Any,
    latitude: float,
    longitude: float,
    elevation_m: float = 0,
    house_system: bytes = b"P",
    transit_info: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Orijinal calculate_astro_data fonksiyonunun backward compatible wrapper'ı.
    
    Bu fonksiyon, AstroCalculator class'ını kullanır ancak orijinal imzayı korur.
    
    Args:
        birth_date: Doğum tarihi
        birth_time: Doğum saati
        latitude: Enlem
        longitude: Boylam
        elevation_m: Yükseklik (kullanılmıyor, backward compatibility için)
        house_system: Ev sistemi
        transit_info: Transit bilgileri
        
    Returns:
        Astrolojik veriler
    """
    calculator = AstroCalculator(house_system=house_system)
    return calculator.calculate_all(
        birth_date=birth_date,
        birth_time=birth_time,
        latitude=latitude,
        longitude=longitude,
        transit_info=transit_info
    )


if __name__ == "__main__":
    # Test
    calculator = AstroCalculator()
    result = calculator.calculate_all(
        birth_date="1990-01-15",
        birth_time="14:30",
        latitude=41.0082,
        longitude=28.9784
    )
    print(f"Test sonucu: {result['sun_sign']}, {result['moon_sign']}")
    print(f"Yükselen: {result['ascendant']['sign']}")
