# 🔑 Google Play API Key Kurulumu — Adım Adım Rehber

> **Amaç:** Google Play Developer API için Service Account oluşturup JSON key'i Fastlane'e bağlamak.  
> **Süre:** ~10 dakika  
> **Tek seferlik:** Bu işlem sadece bir kez yapılır.  
> **Son Durum:** `com.orbisastro.orbis` (Kapalı test) — Play Console'da mevcut ✅

---

## 📋 ADIMLAR ÖZETİ

| # | Adım | Nerede | Süre |
|---|------|--------|------|
| 1 | API erişimi sayfasını aç + Google Cloud projesi bağla | Play Console | 2 dk |
| 2 | Service Account oluştur | Google Cloud Console | 2 dk |
| 3 | JSON Key indir | Google Cloud Console | 1 dk |
| 4 | Play Console'da Service Account'ı yetkilendir | Play Console | 2 dk |
| 5 | JSON Key'i projeye kopyala | Bilgisayar | 1 dk |
| 6 | Bağlantıyı test et | Terminal | 1 dk |
| 7 | Beta yükle | Terminal | 2 dk |

---

## ADIM 1: API Erişimi Sayfasını Aç + Google Cloud Projesi Bağla

### Yol: Ayarlar → Geliştirici hesabı → API erişimi

1. Tarayıcıda aç: **https://play.google.com/console**
2. Sol menüden **Ayarlar** (⚙️) tıkla
3. **Geliştirici hesabı** altında **API erişimi** tıkla

   > ⚠️ "Hesap ayrıntıları" veya "Bağlı hizmetler" DEĞİL → **API erişimi**!
   >
   > Menüde göremiyorsan sayfayı aşağı kaydır. Şu sırada olacak:
   > ```
   > Ayarlar
   >   └── Geliştirici hesabı
   >         ├── Genel
   >         ├── Bağlı hizmetler
   >         ├── E-posta listeleri
   >         ├── ...
   >         └── API erişimi   ← ← ← BURASI
   > ```
   >
   > Hâlâ göremiyorsan direkt bu linki dene:
   > ```
   > https://play.google.com/console/api-access
   > ```

4. Bu sayfada **"Google Cloud projesi bağlama"** bölümünü göreceksin:
   - **Proje zaten bağlıysa:** Proje adı ve ID görünür → not al ve devam et
   - **Proje bağlı değilse:** 
     - **"Mevcut bir Google Cloud projesini bağla"** veya **"Yeni proje oluştur"** tıkla
     - Yeni proje oluşturuyorsan ad olarak `orbis-play-api` gibi bir şey yaz
     - **"Projeyi bağla"** tıkla

5. Proje bağlandıktan sonra aynı sayfada **"Hizmet hesapları"** bölümü görünecek
6. **"Hizmet hesabı oluştur"** linkine tıkla → Google Cloud Console açılacak (ADIM 2'ye geç)

> 📝 **Not al:** `Google Cloud Project ID = ________________________`

---

## ADIM 2: Service Account Oluştur (Google Cloud Console'da)

ADIM 1'deki "Hizmet hesabı oluştur" linki seni otomatik olarak Google Cloud Console'a yönlendirecek.

Eğer yönlendirmediyse bu linki aç:
```
https://console.cloud.google.com/iam-admin/serviceaccounts
```

1. Üstteki proje seçiciden **ADIM 1'de bağladığın proje**yi seç
2. **+ HİZMET HESABI OLUŞTUR** (CREATE SERVICE ACCOUNT) butonuna tıkla
3. Bilgileri doldur:

   | Alan | Değer |
   |------|-------|
   | Hizmet hesabı adı | `fastlane-orbis` |
   | Hizmet hesabı kimliği | (otomatik dolacak: `fastlane-orbis@proje-id.iam.gserviceaccount.com`) |
   | Açıklama | `Fastlane Play Store deployment` |

4. **OLUŞTUR VE DEVAM ET** (CREATE AND CONTINUE) tıkla
5. Rol seçimi adımında **bir şey seçme**, direkt **DEVAM ET** tıkla
6. Son adımda **BİTTİ** (DONE) tıkla

> 📝 **Not al — Email adresi:**  
> `fastlane-orbis@________________________.iam.gserviceaccount.com`

---

## ADIM 3: JSON Key İndir

1. Service Accounts listesinde az önce oluşturduğun **fastlane-orbis** hesabını bul
2. Sağ taraftaki **⋮** (üç nokta) menüsüne tıkla → **Anahtarları yönet** (Manage keys)
3. **ANAHTAR EKLE** (ADD KEY) → **Yeni anahtar oluştur** (Create new key)
4. Anahtar türü: **JSON** seçili olmalı
5. **OLUŞTUR** (CREATE) tıkla
6. JSON dosyası otomatik indirilecek (genelde `Downloads` klasörüne)

> 📁 İndirilen dosya adı şuna benzer:  
> `proje-id-abc123def456.json`

⚠️ **Bu dosyayı güvenli tutun! Tekrar indirilemez. Kaybolursa yeni key oluşturmanız gerekir.**

---

## ADIM 4: Play Console'da Service Account'ı Yetkilendir

### ÖNEMLİ: Bu adım tekrar Play Console'da yapılıyor!

1. **Play Console'a geri dön** → **Ayarlar** → **Geliştirici hesabı** → **API erişimi**
   ```
   https://play.google.com/console/api-access
   ```
2. **"Hizmet hesapları"** bölümünde az önce oluşturduğun `fastlane-orbis` hesabını göreceksin
   - Göremiyorsan **"Hizmet hesaplarını yenile"** (Refresh service accounts) butonuna tıkla
3. `fastlane-orbis` satırında **"Erişim izni ver"** (Grant access) tıkla
4. **Uygulama izinleri** sekmesinde `com.orbisastro.orbis` uygulamasını seç
5. Şu izinleri **işaretle** ✅:

   | İzin | Gerekli mi? |
   |------|-------------|
   | ✅ Uygulama bilgilerini görüntüleme | Evet |
   | ✅ Sürümleri oluşturma, düzenleme ve yayınlama | **Evet (ZORUNLU)** |
   | ✅ Sürüm izlemeyi yönetme | **Evet (ZORUNLU)** |
   | ✅ Ürün listeleme bilgilerini yönetme | Evet |
   | ❌ Üretime yayınlama | Opsiyonel (güvenlik için kapalı bırakılabilir) |

   > 💡 **Kolay yol:** "Admin" seçerseniz tüm izinler verilir, her şey çalışır.

6. **Kullanıcıyı davet et** (Invite user) tıkla
7. **Daveti gönder** (Send invitation) onayla

> ⏳ İzinlerin aktif olması **birkaç dakika** sürebilir.

---

## ADIM 5: JSON Key'i Projeye Kopyala

PowerShell terminalinde şu komutu çalıştır:

```powershell
# İndirilen JSON dosyasını Fastlane klasörüne kopyala
# ÖNEMLİ: Dosya adını kendi indirdiğin dosya adıyla değiştir!

Copy-Item "$HOME\Downloads\INDIRILEN-DOSYA-ADI.json" "D:\astro-ai-predictor\backend\flask_app\mobile\android\fastlane\play-store-credentials.json"
```

**Örnek:**
```powershell
Copy-Item "$HOME\Downloads\orbis-project-abc123.json" "D:\astro-ai-predictor\backend\flask_app\mobile\android\fastlane\play-store-credentials.json"
```

### Doğrulama:
```powershell
# Dosyanın yerinde olduğunu kontrol et
Test-Path "D:\astro-ai-predictor\backend\flask_app\mobile\android\fastlane\play-store-credentials.json"
# True dönmeli ✅
```

> ⚠️ Bu dosya `.gitignore`'a **zaten ekli** — git'e push edilmeyecek ✅

---

## ADIM 6: Bağlantıyı Test Et

```powershell
cd D:\astro-ai-predictor\backend\flask_app\mobile\android

# Ruby PATH'e ekle (gerekirse)
$env:Path = "C:\Ruby33-x64\bin;" + $env:Path

# Google Play bağlantısını doğrula
bundle exec fastlane run validate_play_store_json_key json_key:fastlane/play-store-credentials.json
```

### Beklenen Çıktı:
```
Successfully established connection to Google Play Store.
```

### Hata Alırsan:

| Hata | Çözüm |
|------|-------|
| `Google::Apis::ClientError: forbidden` | ADIM 5'teki izinler henüz aktif olmamış — 5-10 dk bekle |
| `No application was found for the given package name` | Play Console'da `com.orbisastro.orbis` mevcut olmalı (zaten var ✅) |
| `JSON key file not found` | ADIM 6'daki kopyalama yolunu kontrol et |
| `invalid_grant` | Service account email'i Play Console'a eklenmiş mi kontrol et |

---

## ADIM 7: Beta Yükle! 🚀

Bağlantı başarılı olduktan sonra:

```powershell
cd D:\astro-ai-predictor\backend\flask_app\mobile\android

# Version'ı artır (Play Store aynı version code'u kabul etmez)
bundle exec fastlane bump_version

# Internal Testing track'e beta yükle
bundle exec fastlane beta
```

### Bu komut şunları yapar:
1. ✅ Release AAB build eder (signed, minified, shrunk)
2. ✅ Google Play Console'a bağlanır
3. ✅ Internal Testing track'e AAB'yi yükler
4. ✅ Draft release oluşturur

### Yükleme sonrası Play Console'da:
1. **Dahili test** → **Sürümler** sayfasına git
2. Draft durumundaki sürümü **İncele ve yayınla**
3. Test kullanıcılarını ekle (email adresleri)
4. Test bağlantısını paylaş

---

## 🔄 Sonraki Beta Güncellemeleri İçin

Her yeni beta sürümü için sadece:

```powershell
cd D:\astro-ai-predictor\backend\flask_app\mobile\android
$env:Path = "C:\Ruby33-x64\bin;" + $env:Path

bundle exec fastlane bump_version   # Version artır
bundle exec fastlane beta           # Build + yükle
```

Bu kadar! 🎉

---

## 📊 Track Stratejisi

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────┐    ┌──────────────┐
│ Internal Testing │───▶│ Closed Testing   │───▶│ Open Beta   │───▶│ Production   │
│ (fastlane beta)  │    │ (fastlane alpha) │    │(fl open_beta)│   │(fl release)  │
│                  │    │                  │    │              │    │              │
│ • Dahili ekip    │    │ • Seçili test    │    │ • Herkes     │    │ • Canlı      │
│ • Max 100 kişi   │    │   kullanıcıları  │    │   katılabilir│    │ • Tüm dünya  │
│ • İnceleme yok   │    │ • İnceleme yok   │    │ • İnceleme   │    │ • İnceleme   │
└─────────────────┘    └──────────────────┘    └─────────────┘    └──────────────┘
```

**Önerilen akış:**
1. `fastlane beta` → İç test yap
2. Sorun yoksa `fastlane promote_to_production` veya `fastlane release`

---

## ❓ SSS

**S: İlk beta yüklemesinde hata alıyorum?**
C: Play Console'da `com.orbisastro.orbis` için en az bir kez **manuel AAB yüklemiş** olmanız gerekir. Ekran görüntüsüne göre "Kapalı test" aşamasındasınız, yani bu koşul **zaten sağlanmış** ✅

**S: Service Account JSON key'i kaybettim?**
C: Google Cloud Console → Service Accounts → Yeni key oluştur. Eski key otomatik devre dışı kalır.

**S: Version code çakışması alıyorum?**
C: `bundle exec fastlane bump_version` çalıştırarak versionCode'u artırın.

**S: AAB yerine APK yükleyebilir miyim?**
C: Google Play artık AAB zorunlu kılıyor. Fastfile zaten AAB üretiyor.

---

*Hesap ID: 6445672519590242343*  
*Package: com.orbisastro.orbis*  
*Son güncelleme: 2026-02-23*
