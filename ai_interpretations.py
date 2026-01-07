import os
import requests
import logging
from dotenv import load_dotenv
import google.generativeai as genai  # Gemini kütüphanesini import et
import json  # JSON işlemleri için
from openai import OpenAI # OpenRouter için OpenAI kütüphanesini import et

load_dotenv()

# Ayarları yükle fonksiyonu
def load_local_settings():
    settings_path = os.path.join(os.path.dirname(__file__), 'instance', 'settings.json')
    if os.path.exists(settings_path):
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

local_settings = load_local_settings()

HYPERBOLIC_API_KEY = local_settings.get("hyperbolic_api_key") or os.getenv("HYPERBOLIC_API_KEY")
GOOGLE_API_KEY = local_settings.get("llm_api_key") or os.getenv("GOOGLE_API_KEY")
OPENROUTER_API_KEY = local_settings.get("openrouter_api_key") or os.getenv("OPENROUTER_API_KEY")
DEEPSEEK_API_KEY = local_settings.get("deepseek_api_key") or os.getenv("DEEPSEEK_API_KEY")

# Gemini API'yi yapılandır
if GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        # Note: Model adını da ayarlardan çekebiliriz
        model_name = local_settings.get("llm_model", "gemini-3-flash-preview")
        gemini_model = genai.GenerativeModel(model_name)
        logging.info(f"Google Gemini API ({model_name}) başarıyla yapılandırıldı.")
    except Exception as e:
        logging.error(f"Google Gemini API yapılandırma hatası: {e}")
        gemini_model = None
else:
    logging.warning("GOOGLE_API_KEY bulunamadı. Gemini yorumları çalışmayacak.")
    gemini_model = None

# Kullanılabilir modelleri listele (İsteğe bağlı)
# for m in genai.list_models():
#     if 'generateContent' in m.supported_generation_methods:
#         logging.debug(m.name)

MODELS = {
    "birth_chart": "deepseek-ai/DeepSeek-chat",
    "daily": "deepseek-ai/DeepSeek-chat",
    "detailed": "deepseek-ai/DeepSeek-reasoner",
}

# İsteklere eklenecek özel prompt'lar
BIRTH_CHART_PROMPT = """
{user_name}, aşağıdaki doğum haritası bilgilerine göre bir yorum yap:

Gezegenlerin Konumları:
{planet_positions}

Yükselen Burç: {ascendant}

Önemli Açılar:
{aspects}
"""

DAILY_ANALYSIS_PROMPT = """
bugüne kadar elde edilmiş tüm astrolojik yorumlama bilgilerine hakim bu alanda en güncel bilgileri bilen tecrübeli bir astroloji yorumcusu olarak verilen hesaplamaları bir bütün olarak ele alıp birbirleri ile olan etkileşimleri sonucunda etkilerinin azalıp çoğalan durumlarını dikkate alarak ve aynı zaman da yorumlarında kesinlikle ve kati suratte astrolojik terim kullanmadan yani  ev gezegen burç adı açı adı sade bir dille verilen ve tamamen hesaplamalara bağlı kalarak asla hayali olamayan ve kesinlikle olabilecek günlük meydana gelebilecek olayları tahmin ederek kullanıcıya günlük öngörü raporu hazırla asla tavsiye verme kullanıcıya profesyonel bir dille hitap et ve direkt hesaplamalar sonucunda ortaya çıkan enerjilerin meydana getirebileceği olayları anlat.
{data}
"""

DETAILED_ANALYSIS_PROMPT = """
bugüne kadar elde edilmiş tüm astrolojik yorumlama bilgilerine hakim bu alanda en güncel bilgileri bilen tecrübeli bir astroloji yorumcusu olarak verilen hesaplamaları bir bütün olarak ele alıp birbirleri ile olan etkileşimleri sonucunda etkilerinin azalıp çoğalan durumlarını dikkate alarak ve aynı zaman da yorumlarında kesinlikle ve kati suratte astrolojik terim kullanmadan yani ev gezegen burç adı açı adı sade bir dille verilen hesaplamalara bağlı kalarak asla hayali olamayan ve kesinlikle olabilecek gelecek olayları tahmin ederek kullanıcıya gelecek öngörü raporu hazırla asla tavsiye verme kullanıcıya profesyonel bir dille hitap et ve direkt hesaplamalar sonucunda ortaya çıkan enerjilerin meydana getirebileceği olayları anlat.
{data}
"""

# Tematik Analiz Promptları
CAREER_ANALYSIS_PROMPT = """
bugüne kadar elde edilmiş tüm astrolojik yorumlama bilgilerine hakim bu alanda en güncel bilgileri bilen tecrübeli bir astroloji yorumcusu olarak verilen hesaplamaları bir bütün olarak ele alıp birbirleri ile olan etkileşimleri sonucunda etkilerinin azalıp çoğalan durumlarını dikkate alarak ve aynı zaman da yorumlarında kesinlikle ve kati suratte astrolojik terim kullanmadan yani ev gezegen burç adı açı adı sade bir dille verilen hesaplamalara bağlı kalarak olayları tahmin ederek kullanıcıya gelecek öngörü raporu hazırla {user_name} için Kariyer ve İş Hayatı üzerine odaklı bir analiz yap. kullanıcıya profesyonel bir dille hitap et ve direkt hesaplamalar sonucunda ortaya çıkan enerjilerin meydana getirebileceği olayları anlat.
Özellikle Dasamsa (D10) haritası, MC noktası, Satürn ve Jüpiter konumlarını dikkate alarak yorumlarını oluştur.
Veriler: {data}
"""

LOVE_ANALYSIS_PROMPT = """
bugüne kadar elde edilmiş tüm astrolojik yorumlama bilgilerine hakim bu alanda en güncel bilgileri bilen tecrübeli bir astroloji yorumcusu olarak verilen hesaplamaları bir bütün olarak ele alıp birbirleri ile olan etkileşimleri sonucunda etkilerinin azalıp çoğalan durumlarını dikkate alarak ve aynı zaman da yorumlarında kesinlikle ve kati suratte astrolojik terim kullanmadan yani ev gezegen burç adı açı adı sade bir dille verilen hesaplamalara bağlı kalarak olayları tahmin ederek kullanıcıya gelecek öngörü raporu hazırla {user_name} için Aşk, Evlilik ve Sosyal İlişkiler üzerine odaklı bir analiz yap. kullanıcıya profesyonel bir dille hitap et ve direkt hesaplamalar sonucunda ortaya çıkan enerjilerin meydana getirebileceği olayları anlat.
Navamsa (D9) haritası, 5. ve 7. evler, Venüs ve Mars konumlarını sentezleyerek duygusal ihtiyaçlar, partner uyumu ve uzun vadeli bağlılık potansiyelini yorumla.
Veriler: {data}
"""

FINANCE_ANALYSIS_PROMPT = """
bugüne kadar elde edilmiş tüm astrolojik yorumlama bilgilerine hakim bu alanda en güncel bilgileri bilen tecrübeli bir astroloji yorumcusu olarak verilen hesaplamaları bir bütün olarak ele alıp birbirleri ile olan etkileşimleri sonucunda etkilerinin azalıp çoğalan durumlarını dikkate alarak ve aynı zaman da yorumlarında kesinlikle ve kati suratte astrolojik terim kullanmadan yani ev gezegen burç adı açı adı sade bir dille verilen hesaplamalara bağlı kalarak olayları tahmin ederek kullanıcıya gelecek öngörü raporu hazırla {user_name} için Maddi Kaynaklar ve Varlık Bilinci üzerine derinlemesine bir analiz yap. kullanıcıya profesyonel bir dille hitap et ve direkt hesaplamalar sonucunda ortaya çıkan enerjilerin meydan a getirebileceği olayları anlat.
H16 haritası, 2. ve 4. evler, Şans Noktası (PoF) ve Jüpiter'in etkilerini birleştirerek kazanç yolları ve varlık yönetimi konusunda rehberlik sağla.
Veriler: {data}
"""

HEALTH_ANALYSIS_PROMPT = """
bugüne kadar elde edilmiş tüm astrolojik yorumlama bilgilerine hakim bu alanda en güncel bilgileri bilen tecrübeli bir astroloji yorumcusu olarak verilen hesaplamaları bir bütün olarak ele alıp birbirleri ile olan etkileşimleri sonucunda etkilerinin azalıp çoğalan durumlarını dikkate alarak ve aynı zaman da yorumlarında kesinlikle ve kati suratte astrolojik terim kullanmadan yani ev gezegen burç adı açı adı sade bir dille verilen hesaplamalara bağlı kalarak olayları tahmin ederek kullanıcıya gelecek öngörü raporu hazırla {user_name} için Sağlık ve Psikolojik Esenlik üzerine bir yorum hazırla. kullanıcıya profesyonel bir dille hitap et ve direkt hesaplamalar sonucunda ortaya çıkan enerjilerin meydana getirebileceği olayları anlat.
H20 haritası, 6., 8. ve 12. evlerin durumunu inceleyerek ruhsal ve bedensel dengeyi korumak için önerilerde bulun. (Not: Tıbbi tavsiye olmadığını hatırlat).
Veriler: {data}
"""

KARMA_ANALYSIS_PROMPT = """
bugüne kadar elde edilmiş tüm astrolojik yorumlama bilgilerine hakim bu alanda en güncel bilgileri bilen tecrübeli bir astroloji yorumcusu olarak verilen hesaplamaları bir bütün olarak ele alıp birbirleri ile olan etkileşimleri sonucunda etkilerinin azalıp çoğalan durumlarını dikkate alarak ve aynı zaman da yorumlarında kesinlikle ve kati suratte astrolojik terim kullanmadan yani ev gezegen burç adı açı adı sade bir dille verilen hesaplamalara bağlı kalarak olayları tahmin ederek kullanıcıya gelecek öngörü raporu hazırla {user_name} için Ruhsal Görevler, Karma ve Geçmiş Yaşam etkileri üzerine analiz yap. kullanıcıya profesyonel bir dille hitap et ve direkt hesaplamalar sonucunda ortaya çıkan enerjilerin meydana getirebileceği olayları anlat.
H30, H40 ve H45 haritaları ile Ay Düğümleri (KAD/GAD) ve Satürn'ün konumlarını ele alarak ruhun bu yaşamdaki tekamül yolculuğunu yorumla.
Veriler: {data}
"""

# Transit analizi için iyileştirilmiş prompt
TRANSIT_ANALYSIS_PROMPT = """
bugüne kadar elde edilmiş tüm astrolojik yorumlama bilgilerine hakim bu alanda en güncel bilgileri bilen tecrübeli bir astroloji yorumcusu olarak verilen hesaplamaları bir bütün olarak ele alıp birbirleri ile olan etkileşimleri sonucunda etkilerinin azalıp çoğalan durumlarını dikkate alarak ve aynı zaman da yorumlarında kesinlikle ve kati suratte astrolojik terim kullanmadan yani ev gezegen burç adı açı adı sade bir dille verilen hesaplamalara bağlı kalarak olayları tahmin ederek kullanıcıya gelecek öngörü raporu hazırla kullanıcıya profesyonel bir dille hitap et ve direkt hesaplamalar sonucunda ortaya çıkan enerjilerin meydana getirebileceği olayları anlat.

**Veriler:**

**Doğum Haritası Gezegenleri ve Evleri:**
{natal_planets}

**Güncel Transit Gezegenleri ve Evleri:**
{transit_planets}

**Önemli Transit-Natal Açıları:**
{transit_aspects}
"""

CHAT_PROMPT = """
{original_interpretation}

{user_message}
"""


def prepare_interpretation_prompt(astro_data, interpretation_type, user_name):
    """Farklı yorum türleri için merkezi prompt hazırlayıcı."""
    
    # Tür eşleştirmeleri (Normalleştirme)
    type_map = {
        "birth_chart": "natal",
        "relationship": "love",
        "transits": "transit",
        "timing": "transit"
    }
    norm_type = type_map.get(interpretation_type, interpretation_type)
    
    # Data Hazırlama
    data_summary = str(astro_data)
    if isinstance(astro_data, dict):
        # Eğer veri çok büyükse veya özel bir temizlik gerekiyorsa burası genişletilebilir
        # Şimdilik genel analizler için tüm veriyi string olarak gönderiyoruz (JSON formatında daha iyi olabilir)
        data_summary = json.dumps(astro_data, indent=2, ensure_ascii=False, default=str)

    # Prompt Seçimi
    if norm_type == "daily":
        return DAILY_ANALYSIS_PROMPT.format(data=data_summary)
    
    elif norm_type == "natal":
        # Detaylı natal verisi formatlama
        planet_positions_str = ""
        if isinstance(astro_data, dict):
            for planet, details in astro_data.get("planet_positions", {}).items():
                if isinstance(details, dict) and 'degree' in details:
                    planet_positions_str += f"- {planet}: {details['degree']:.2f}° {details.get('sign', '')}\n"
        
        asc_info = astro_data.get("ascendant", {}) if isinstance(astro_data, dict) else {}
        ascendant_str = f"{asc_info.get('sign', 'Bilinmiyor')} {asc_info.get('degree', 0):.2f}°" if isinstance(asc_info, dict) else "Bilinmiyor"
        
        aspects_str = ""
        if isinstance(astro_data, dict):
            for aspect in astro_data.get("aspects", []):
                aspects_str += f"- {aspect.get('planet1')} {aspect.get('aspect_type')} {aspect.get('planet2')} (Orb: {aspect.get('orb', 0):.2f})\n"
        
        return DETAILED_ANALYSIS_PROMPT.format(data=f"Gezegenler:\n{planet_positions_str}\nYükselen: {ascendant_str}\nAçılar:\n{aspects_str}")

    elif norm_type == "transit":
        # Transit Verisi Formatlama
        natal_planets_str = ""
        transit_planets_str = ""
        transit_aspects_str = ""
        
        if isinstance(astro_data, dict):
            # Natal
            for planet, details in astro_data.get("planet_positions", {}).items():
                 if isinstance(details, dict):
                    natal_planets_str += f"- {planet}: {details.get('degree', '?'):.2f}° {details.get('sign', '?')} ({details.get('house', '?')}. Ev)\n"
            
            # Transit
            tp = astro_data.get("transit_positions", {})
            if not tp: tp = astro_data.get("transit_planet_positions", {})
            for planet, details in tp.items():
                if isinstance(details, dict):
                    retro = "R" if details.get("retrograde", False) else ""
                    transit_planets_str += f"- {planet}: {details.get('longitude', details.get('degree', '?')):.2f}° {details.get('sign', '?')} ({details.get('house', '?')}. Ev) {retro}\n"
            
            # Açıları
            ta = astro_data.get("transit_to_natal_aspects", [])
            if not ta: ta = astro_data.get("transit_natal_aspects", [])
            for aspect in ta:
                if isinstance(aspect, dict):
                    transit_aspects_str += f"- Transit {aspect.get('transit_planet', aspect.get('planet', '?'))} {aspect.get('aspect', aspect.get('aspect_type', '?'))} Natal {aspect.get('natal_planet', aspect.get('planet2', '?'))} (Orb: {aspect.get('orb', 0):.2f}°)\n"

        return TRANSIT_ANALYSIS_PROMPT.format(
            natal_planets=natal_planets_str or "Veri yok",
            transit_planets=transit_planets_str or "Veri yok",
            transit_aspects=transit_aspects_str or "Veri yok"
        )

    elif norm_type == "detailed":
        return DETAILED_ANALYSIS_PROMPT.format(data=data_summary)
    
    elif norm_type == "career":
        return CAREER_ANALYSIS_PROMPT.format(user_name=user_name, data=data_summary)
    
    elif norm_type == "love":
        return LOVE_ANALYSIS_PROMPT.format(user_name=user_name, data=data_summary)
    
    elif norm_type == "finance":
        return FINANCE_ANALYSIS_PROMPT.format(user_name=user_name, data=data_summary)
    
    elif norm_type == "health":
        return HEALTH_ANALYSIS_PROMPT.format(user_name=user_name, data=data_summary)
    
    elif norm_type == "karma":
        return KARMA_ANALYSIS_PROMPT.format(user_name=user_name, data=data_summary)

    # Varsayılan
    return f"Sen profesyonel bir astrologsun. {user_name} için detaylı bir analiz yap. Veriler: {data_summary}"




def get_deepseek_interpretation(astro_data, interpretation_type, user_name="Değerli Danışanım"):
    """Doğrudan DeepSeek API kullanarak astrolojik yorum alır."""
    if not DEEPSEEK_API_KEY:
        return {"success": False, "error": "DeepSeek API key missing"}

    try:
        # Merkezi prompt hazırlayıcıyı kullan
        prompt = prepare_interpretation_prompt(astro_data, interpretation_type, user_name)

        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "Sen dünyanın en iyi astroloğusun. Teknik terim kullanmadan, sade ve anlaşılır bir dille yorum yaparsın."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }

        response = requests.post("https://api.deepseek.com/chat/completions", json=payload, headers=headers, timeout=60)
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            return {"success": True, "interpretation": content.strip()}
        else:
            raise Exception(f"DeepSeek API Error: {response.status_code}")

    except Exception as e:
        logging.error(f"DeepSeek API hatası: {e}")
        return {"success": False, "error": str(e)}


def get_hyperbolic_interpretation(
    data, provider, user_name="Değerli Danışanım", session_id=None
):
    """
    Verilen astrolojik hesaplama verilerine ve seçilen provider türüne göre uygun prompt u oluşturur,
    Hyperbolic API üzerinden AI yorumunu alır ve sonucu döndürür.
    """
    try:
        logging.debug(f"AI yorum isteği - Type: {provider}")
        
        # Sohbet (Chat) kontrolü
        if provider.endswith("_chat"):
            prompt = CHAT_PROMPT.format(
                original_interpretation=data.get("last_interpretation", "")
                if isinstance(data, dict)
                else "",
                user_message=data if isinstance(data, str) else data.get("message", ""),
            )
        else:
            # Merkezi prompt hazırlayıcıyı kullan
            prompt = prepare_interpretation_prompt(data, provider, user_name)
            logging.debug(f"Generated prompt: {prompt[:200]}...")

        headers = {
            "Authorization": f"Bearer {HYPERBOLIC_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "deepseek-ai/DeepSeek-V3-0324",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 40282,
            "temperature": 0.87,
            "top_p": 0.9,
        }

        response = requests.post(
            "https://api.hyperbolic.xyz/v1/chat/completions",
            json=payload,
            headers=headers,
        )

        if response.status_code != 200:
            raise Exception(f"Hyperbolic API hatası: {response.text}")

        response_data = response.json()
        interpretation = response_data["choices"][0]["message"]["content"]

        return {"success": True, "interpretation": interpretation}
    except Exception as e:
        logging.error(f"Hyperbolic API Hatası: {str(e)}")
        return {"success": False, "error": str(e)}


def get_ai_interpretation_engine(
    astro_data, interpretation_type, user_name="Değerli Danışanım"
):
    """Ana Yorum Motoru: DeepSeek [BİRİNCİL] -> Gemini -> OpenRouter."""
    
    # --- 1. DeepSeek (Doğrudan) Dene ---
    if DEEPSEEK_API_KEY:
        try:
            logging.info("DeepSeek-V3 (Chat) ile yorum oluşturuluyor...")
            ds_result = get_deepseek_interpretation(astro_data, interpretation_type, user_name)
            if ds_result.get("success"):
                ds_result["interpretation"] += "\n\n--- [DeepSeek-V3]"
                return ds_result
        except Exception as e:
            logging.warning(f"DeepSeek başarısız: {e}")

    # --- 2. Gemini API Dene ---
    if gemini_model:
        try:
            logging.info("Gemini ile yorum oluşturuluyor...")
            # Merkezi prompt hazırlayıcıyı kullan
            prompt = prepare_interpretation_prompt(astro_data, interpretation_type, user_name)

            response = gemini_model.generate_content(prompt)
            if response and response.text:
                interpretation = response.text.strip() + "\n\n--- [Google Gemini]"
                return {"success": True, "interpretation": interpretation}
        except Exception as e:
            logging.warning(f"Gemini başarısız: {e}")

    # --- 3. OpenRouter Dene ---
    if OPENROUTER_API_KEY:
        try:
            logging.info("OpenRouter ile yorum oluşturuluyor...")
            client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)
            
            # Merkezi prompt hazırlayıcıyı kullan
            prompt_or = prepare_interpretation_prompt(astro_data, interpretation_type, user_name)
            
            completion = client.chat.completions.create(
                model="xiaomi/mimo-v2-flash:free",
                messages=[{"role": "user", "content": prompt_or}]
            )
            if completion.choices[0].message.content:
                interpretation = completion.choices[0].message.content.strip() + "\n\n--- [OpenRouter / Xiaomi Mimo]"
                return {"success": True, "interpretation": interpretation}
        except Exception as e:
            logging.error(f"OpenRouter başarısız: {e}")

    return {"success": False, "error": "Tüm LLM servisleri başarısız oldu."}
