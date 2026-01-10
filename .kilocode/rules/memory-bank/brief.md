# Astro AI Predictor Brief

Astro AI Predictor, geleneksel astrolojik hesaplamaları modern yapay zeka (AI) yorumlarıyla birleştiren kapsamlı bir web uygulamasıdır. 

## Ana Hedefler
- Kullanıcıların doğum haritalarını (natal chart) ve astrolojik verilerini yüksek hassasiyetle hesaplamak.
- Bu teknik verileri, OpenAI ve Google Gemini gibi gelişmiş dil modellerini kullanarak anlamlı ve kişiselleştirilmiş yorumlara dönüştürmek.
- Kullanıcılara sezgisel bir arayüz üzerinden astrolojik rehberlik sunmak.

## Temel Özellikler
- **Hassas Hesaplamalar:** Swiss Ephemeris (`pyswisseph`) kütüphanesi kullanılarak yapılan gezegen konumları ve ev hesaplamaları.
- **AI Interpretations:** Doğum haritası verilerinin LLM'ler (GPT-4, Gemini) tarafından analiz edilmesi.
- **Kullanıcı Yönetimi:** Kayıt, giriş ve geçmiş hesaplamaların saklanması.
- **Çoklu Dil Desteği:** Özellikle Türkçe dil desteği öncelikli olmak üzere dinamik içerik.
- **Frontend/Backend Senkronizasyonu:** Flask (Python) tabanlı bir backend ile dinamik frontend bileşenleri.

## Kullanılan Teknolojiler
- **Backend:** Python, Flask
- **Frontend:** HTML/CSS (Tailwind CSS, Semantic UI), JavaScript
- **Veritabanı/Servis:** Supabase, Redis (Cache)
- **AI:** OpenAI API, Google Generative AI
- **Hesaplama:** Swiss Ephemeris

## Önemi
Bu proje, kadim astroloji bilgisini modern veri bilimi ve yapay zeka ile buluşturarak, kullanıcıların kendilerini keşfetme yolculuğuna teknolojik bir boyut kazandırır.
