# Astro AI Predictor Product

## Neden Bu Proje Var?
Astroloji, binlerce yıldır insanların kendilerini ve evreni anlama çabasının bir parçası olmuştur. Ancak, bir doğum haritasını doğru hesaplamak teknik uzmanlık, onu anlamlı bir şekilde yorumlamak ise derin bir bilgi birikimi gerektirir. Astro AI Predictor, bu süreci demokratikleştirmek ve her kullanıcıya kişiselleştirilmiş, derinlemesine astrolojik analizler sunmak için var.

## Çözülen Problemler
- **Karmaşık Hesaplamalar:** Manuel veya basit araçlarla yapılan hatalı astrolojik hesaplamaların önüne geçerek `pyswisseph` ile bilimsel hassasiyet sağlar.
- **Yüzeysel Yorumlar:** Standart, genel geçer burç yorumları yerine, kullanıcının tam doğum haritasına (evler, açılar, gezegen konumları) dayalı AI destekli derin analizler sunar.
- **Erişilebilirlik:** Astroloji uzmanına ulaşamayan veya kendi haritasını yorumlayamayan kullanıcılara 7/24 rehberlik sağlar.

## Kullanıcı Deneyimi Hedefleri
- **Hız ve Kolaylık:** Kullanıcılar doğum bilgilerini girdikten saniyeler sonra detaylı bir analiz almalıdır.
- **Güvenilirlik:** Hesaplamaların doğruluğu ve AI yorumlarının tutarlılığı kullanıcıya güven vermelidir.
- **Görselleştirme:** Teknik verilerin (gezegen dereceleri vb.) anlaşılır ve estetik bir arayüzle sunulması.
- **Süreklilik:** Kullanıcılar geçmiş analizlerine kolayca ulaşabilmeli ve gelişimlerini takip edebilmelidir.

## İş Akışı
1. Kullanıcı doğum tarihi, saati ve yerini girer.
2. Sistem koordinatları ve Julian gün sayısını hesaplar.
3. Swiss Ephemeris kullanılarak gezegen konumları ve evler belirlenir.
4. Elde edilen teknik veriler (örn: "Güneş Koç'ta 5. evde") AI modeline (GPT-4/Gemini) gönderilir.
5. AI, bu verileri sentezleyerek kullanıcıya özel metinsel bir yorum oluşturur.
6. Sonuçlar kullanıcıya dashboard üzerinden sunulur ve veritabanına kaydedilir.
