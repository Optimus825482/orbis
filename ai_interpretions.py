import os
import google.generativeai as genai
import logging
from dotenv import load_dotenv
from config import Config
import requests  # requests kütüphanesini ekle

logger = logging.getLogger(__name__)

load_dotenv()

# API anahtarını al ve Gemini API yapılandırmasını yap
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise Exception("GEMINI_API_KEY çevresel değişkeni ayarlanmamış!")
genai.configure(api_key=GEMINI_API_KEY)

# Kullanılacak modellerin tanımlamaları
MODELS = {
    "birth_chart": "gemini-2.0-pro-exp-02-05",
    "daily": "gemini-2.0-pro-exp-02-05",
    "detailed": "gemini-2.0-pro-exp-02-05",
    "chat": "gemini-2.0-pro-exp-02-05", # Sohbet için model
}

# Doğum haritası/karakter analizi için prompt:
BIRTH_CHART_PROMPT = """


Hesaplama Sonuçları:
{data}

Yukarıda verilen hesaplamaların sonuçlarını kullanarak.Kişinin. Karakter özelliklerini.Ve. Güçlü yönlerini.Zayıf yönlerini. Ayrıca. Başarılı olduğu an alanlar.Geliştirilmesi gereken alanlar.Ve tüm bu bilgiler ile tüm detayları içeren.Kader çizgisi bağlamada.Kişinin doğum haritasına.Yorumlayınız.

Lütfen bu veriler ışığında samimi ve profesyonel yorumu aşağıda bulunuz.
Yorum oluştururken uyulacak kurallar:
- Asla Burç Gezegen Adı veya Açı Adı Ev vb gibi Astrolojik terim kullanma
- Asla Tasviye verme
- Madde yada numaralandırma kullanma
- Tamamen hesaplamaların sonuçlarına bağlı kal hayali yorum üretme
- Yorumları maddeler halinde değil paragraf olarak oluştur
- Bu kurallara uyarak yorum yaptığından kullancıya bahsetme

"""

# Günlük öngörü için prompt:
DAILY_ANALYSIS_PROMPT = """
Merhaba {user_name},

- Bugüne kadar elde edilmiş tüm astrolojik yorumlama bilgilerine hakim bu alanda 
en güncel bilgileri bilen tecrübeli bir astroloji yorumcusu
 olarak verilen hesaplamaları bir bütün olarak ele alıp birbirleri ile olan 
 etkileşimleri sonucunda etkilerinin azalıp çoğalan durumlarını dikkate alarak ve 
 aynı zaman da yorumlarında astrolojik terim kullanmadan ev gezegen burç adı açı adı sade
  bir dille verilen hesaplamalara bağlı kalarak olayları tahmin ederek kullanıcının bugun yaşayacağı olayları 
  içeren mumkun olan en fazla detaylı bir yorumu oluşturun.
   Yorum oluştururken uyulacak kurallar:
- Asla Burç Gezegen Adı veya Açı Adı Ev vb gibi Astrolojik terim kullanma
- Asla Tasviye verme
- Tamamen hesaplamaların sonuçlarına bağlaı kal hayali yorum üretme
- Madde yada numaralandırma kullanma
- Yorumları maddeler halinde değil paragraf olarak oluştur
- Bu kurallara uyarak yorum yaptığından kullancıya bahsetme

Hesaplama Sonuçları:
{data}

Lütfen günlük yorumunuzu aşağıda bulunuz.
"""

# Detaylı, kapsamlı yorum için prompt:
DETAILED_ANALYSIS_PROMPT = """
Verilen hesaplamaların sonuçlarını bir bütün olarak ele alarak. Birbirleri ile olan Etkileşimlerinin sonucunda ortaya çıkan Enerjiler ışığın 
da meydana gelecek Olayları içeren Yorumu oluştur. Bu yorumu
 oluştururken Herhangi bir astrolojik terim kullanma (Burç gezegen adı açı ya da ev.
  Vesaire gibi).  Sohbet tarzında Ve mümkün olan En fazla 
  detayı vererek Asla hayali olmayan ve tamamen hesaplamalara dayalı Tarih boyunca geçmişten günümüze Elde edilen Tüm astrolojik bilgilerin kullanıldığı Ve özellikle somut olaylar noktasında Tamamen hesaplama Sonuçlarına dayalı Bir Öngörü yorumu oluştur. Bu yorum oluştururken Herhangi bir şekilde Madde madde ya da herhangi bir konu başlığı Altında değil Az önce de belirttiğim Bir sohbet  Tarzı benimseyerek Yorum Oluşturun. Transit, Progresyon, arc ve return ayrıca asteroidler ile harmonic haritalarının sonuçlarını da kullanarak öngörü Yorumu Oluşturun.
Yorum oluştururken uyulacak kurallar:
- Asla Burç Gezegen Adı veya Açı Adı Ev vb gibi Astrolojik terim kullanma
- Asla Tasviye verme
- Tamamen hesaplamaların sonuçlarına bağlaı kal hayali yorum üretme
- Madde yada numaralandırma kullanma
- Yorumları maddeler halinde değil paragraf olarak oluştur
- Bu kurallara uyarak yorum yaptığından kullancıya bahsetme
- cevabı oluştururken mutlaka hesaplamaların sonuçlarına bağlı kal
- maddler halinde değil paragraf olarak yorum yap her paragrafın başında alt başlık kullan

Hesaplama Sonuçları:
{data}

Lütfen detaylı analizinizi aşağıda bulunuz.
"""

# Chat prompt'u ekle
CHAT_PROMPT = """
Astrolojik yorum hakkında bir soru sorulduğunda:
1. Soruyu dikkatlice analiz et
2. Verilen yorumla ilgili bağlantıları kur
3. Astrolojik terimleri kullanmadan, günlük dilde yanıt ver
4. Tavsiye vermek yerine durumları açıkla
5. Yorumu yaparken maddeler halinde değil paragraf olarak yorum yap ve her paragrafın başında alt başlık kullan
6. cevabı oluştururken mutlaka hesaplamaların sonuçlarına bağlı kal

Orijinal Yorum:
{original_interpretation}

Kullanıcı Sorusu:
{user_message}

Lütfen yanıtınızı yukarıdaki kurallara uygun şekilde oluşturun.
"""


def get_gemini_interpretation(data_payload, interpretation_type="birth_chart"):
    try:
        # Yorumlanacak veriyi ve kullanıcı mesajını al
        astro_data_content = data_payload.get("astro_data", {})
        user_name = data_payload.get("user_name", "Kullanıcı")

        # Sohbet için özel veri (sadece 'chat' tipinde relevant)
        original_interpretation_context = data_payload.get("interpretation_context", "")
        user_question = data_payload.get("question", "")

        # Prompt template'ini seçmek için doğrudan 'interpretation_type' parametresini kullan
        if interpretation_type == "birth_chart":
            prompt_content = BIRTH_CHART_PROMPT.format(data=astro_data_content, user_name=user_name)
        elif interpretation_type == "daily":
            prompt_content = DAILY_ANALYSIS_PROMPT.format(data=astro_data_content, user_name=user_name)
        elif interpretation_type == "detailed":
            prompt_content = DETAILED_ANALYSIS_PROMPT.format(data=astro_data_content, user_name=user_name)
        elif interpretation_type == "chat":
            prompt_content = CHAT_PROMPT.format(
                original_interpretation=original_interpretation_context,
                user_message=user_question
            )
        else:
            logger.error(f"Bilinmeyen yorum türü: {interpretation_type}")
            return {"error": f"Bilinmeyen yorum türü: {interpretation_type}"}

        # Hyperbolic API'sine istek gönderme
        url = "https://openrouter.ai/api/v1"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJpa2luY2l5ZW5pa2l0YXA1NEBnbWFpbC5jb20iLCJpYXQiOjE3MjY5MzkwNjl9.fIXOKvamoJLKvAhpnhl7pelXSwzmXMcNF8ZVR2uQGrY",
        }
        
        # Modeli MODELS dict'ten al
        model_name = MODELS.get(interpretation_type, "deepseek-ai/DeepSeek-V3")

        request_data = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt_content, # Oluşturulan prompt'u kullan
                }
            ],
            "model": model_name,
            "max_tokens": 20000,
            "temperature": 0.75,
            "top_p": 0.9,
        }

        response = requests.post(url, headers=headers, json=request_data)
        response_json = response.json()

        if (
            response_json
            and "choices" in response_json
            and len(response_json["choices"]) > 0
        ):
            # Sohbet için 'answer' anahtarını kullanalım, frontend ile uyumlu olması için
            result_key = "answer" if interpretation_type == "chat" else "interpretation"
            interpretation_text = response_json["choices"][0]["message"]["content"]
            return {result_key: interpretation_text}
        else:
            logger.warning(f"Hyperbolic API'den geçerli bir yanıt alınamadı. Yanıt: {response_json}")
            return {"error": "Yapay zekadan geçerli bir yanıt alınamadı."}

    except requests.exceptions.RequestException as e:
        logger.error(f"Hyperbolic API bağlantı hatası: {str(e)}")
        return {"error": f"API bağlantı hatası: {str(e)}"}
    except Exception as e:
        logger.error(f"Hyperbolic API genel hata: {str(e)}")
        return {"error": f"Yorum alınırken bir hata oluştu: {str(e)}"}

# Prompt oluşturma fonksiyonları (create_birth_chart_prompt, create_transits_prompt vb.)
# artık doğrudan get_gemini_interpretation içinde ele alındığı için kaldırılabilir
# veya olduğu gibi bırakılabilir, ancak mevcut mantıkta kullanılmıyorlar.
# Şimdilik yerinde bırakıyorum, ileride temizlenebilirler.

def format_planet_positions(positions):
    return "\n".join(
        [
            f"{planet}: {details['sign']} burcu {details['house']}. evde, "
            f"{details['degree']}° {'(Retrograd)' if details['retrograde'] else ''}"
            for planet, details in positions.items()
        ]
    )


def format_ascendant(ascendant):
    return f"{ascendant['sign']} {ascendant['degree']}° ({ascendant['decan']}. dekan)"


def format_aspects(aspects):
    return "\n".join(
        [
            f"{aspect['planet1']}-{aspect['planet2']}: {aspect['aspect_type']} "
            f"(orb: {aspect['orb']}°)"
            for aspect in aspects
        ]
    )


def format_natal_interpretation(interpretations):
    return "\n".join(interpretations)
