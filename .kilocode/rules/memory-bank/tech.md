# Astro AI Predictor Technology Stack

## Dil ve Çalışma Zamanı
- **Python 3.10+**: Tüm backend mantığı ve bilimsel hesaplamalar için ana dil.
- **Node.js**: Frontend build süreçleri (Tailwind CSS) için.

## Framework'ler ve Kütüphaneler
- **Flask (Backend)**: Web sunucusu ve API yönetimi.
- **Tailwind CSS (Frontend)**: Modern ve hızlı UI tasarımı.
- **Semantic UI (Frontend)**: Hazır bileşenler ve estetik dokunuşlar.
- **pyswisseph**: Swiss Ephemeris kütüphanesinin Python wrapper'ı (Astrolojik çekirdek).

## Veritabanı ve Servisler
- **Supabase (PostgreSQL)**: Kullanıcı yönetimi ve veri saklama.
- **Redis**: API yanıtları ve ağır hesaplamalar için cache katmanı.
- **OpenAI API**: Gelişmiş doğum haritası yorumları (GPT-4/GPT-4o).
- **Google Generative AI**: Alternatif/yedek AI modeli (Gemini Pro).

## Altyapı ve Dağıtım
- **Vercel / Netlify**: Frontend ve API dağıtımı için yapılandırma dosyaları mevcut.
- **Gunicorn / Gevent**: Production seviyesi WSGI sunucuları.

## Geliştirme Araçları
- **pip**: Python paket yönetimi.
- **npm**: JavaScript paket yönetimi.
- **python-dotenv**: Environment variables yönetimi.
