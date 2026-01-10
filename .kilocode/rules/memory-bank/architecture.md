# Astro AI Predictor Architecture

## Sistem Mimarisi
Uygulama, klasik bir Client-Server mimarisi üzerine kuruludur ve Python/Flask tabanlı bir backend ile HTML/JS tabanlı bir frontend sunar.

### Klasör Yapısı ve Bileşenler
- **Backend (Flask):**
    - `app.py`: Uygulamanın ana giriş noktası ve factory fonksiyonu.
    - `routes.py` (ve `routes/` dizini): API endpoint'leri ve sayfa yönlendirmeleri.
    - `astro_calculations.py`: Swiss Ephemeris (`pyswisseph`) kullanarak teknik astrolojik verilerin hesaplandığı çekirdek modül.
    - `ai_interpretations.py`: OpenAI ve Gemini API'leri ile iletişim kuran yorumlama motoru.
    - `supabase_service.py`: Veritabanı işlemleri (Supabase) için servis katmanı.
    - `cache_config.py`: Redis tabanlı önbellekleme yapılandırması.
- **Frontend:**
    - `templates/`: Jinja2 şablonları (HTML).
    - `static/`: CSS (Tailwind, Semantic UI), JavaScript (`app.js`) ve resim dosyaları.
- **Konfigürasyon:**
    - `config.py`: Ortam değişkenlerine göre (Dev/Prod) uygulama ayarları.
    - `.env`: API anahtarları ve gizli bilgiler.

## Temel Teknik Kararlar
1. **Flask Kullanımı:** Hızlı prototipleme ve Python'un bilimsel kütüphanelerine (numpy, pyswisseph) doğrudan erişim için tercih edildi.
2. **Swiss Ephemeris:** Astrolojik hesaplamalarda endüstri standardı olduğu için hassasiyet amacıyla kullanıldı.
3. **Hibrit AI Yaklaşımı:** Hem OpenAI hem de Google Gemini API'leri yedekli ve maliyet/performans odaklı kullanıma uygun şekilde entegre edildi.
4. **Redis Cache:** Tekrarlanan astrolojik hesaplamaların ve AI yorumlarının performansını artırmak için kullanıldı.
5. **Supabase:** Modern, ölçeklenebilir ve PostgreSQL tabanlı bir "Backend as a Service" (BaaS) çözümü olarak tercih edildi.

## Veri Akışı
1. `Client` (Tarayıcı) → `routes.py` (Request)
2. `routes.py` → `astro_calculations.py` (Teknik veri hesaplama)
3. `astro_calculations.py` → `ai_interpretations.py` (AI yorum talebi)
4. `ai_interpretations.py` → `OpenAI/Gemini` (Yorum oluşturma)
5. `Service Layer` → `Supabase` (Veri saklama)
6. `Server` → `Client` (JSON/HTML Response)

## Kritik Uygulama Yolları
- **Hesaplama Motoru:** `astro_calculations.py` içerisindeki gezegen dereceleri ve ev hesaplama fonksiyonları.
- **Yorumlama Pipeline:** Teknik verinin prompt mühendisliği ile AI'ya aktarıldığı süreç.
- **Kimlik Doğrulama:** Flask-Login/Supabase Auth entegrasyonu.
