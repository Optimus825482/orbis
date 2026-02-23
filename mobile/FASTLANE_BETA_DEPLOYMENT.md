# 🚀 ORBIS - Fastlane Beta Deployment Rehberi

## 📋 İÇİNDEKİLER
1. [Genel Bakış](#genel-bakış)
2. [Ön Gereksinimler](#ön-gereksinimler)
3. [Google Play API Kurulumu](#google-play-api-kurulumu)
4. [Beta Build ve Yükleme](#beta-build-ve-yükleme)
5. [Mevcut Lane'ler](#mevcut-laneler)
6. [Sorun Giderme](#sorun-giderme)

---

## 🎯 Genel Bakış

ORBIS Android uygulaması için Fastlane beta deployment altyapısı kurulmuştur. Bu sayede tek komutla:
- ✅ Release AAB/APK oluşturabilir
- ✅ Google Play Store Internal/Alpha/Beta/Production track'e yükleyebilir
- ✅ Version bump yapabilir
- ✅ Metadata senkronize edebilirsiniz

### Klasör Yapısı
```
mobile/android/
├── Gemfile                    # Ruby bağımlılıkları
├── Gemfile.lock               # Sabitlenmiş versiyonlar
└── fastlane/
    ├── Appfile                # Play Store config (package name, json key)
    ├── Fastfile               # Lane tanımları (beta, release, vb.)
    └── metadata/android/
        ├── tr-TR/
        │   ├── title.txt
        │   ├── short_description.txt
        │   ├── full_description.txt
        │   └── changelogs/1.txt
        └── en-US/
            ├── title.txt
            ├── short_description.txt
            ├── full_description.txt
            └── changelogs/1.txt
```

---

## ⚙️ Ön Gereksinimler

| Bileşen | Durum | Notlar |
|---------|-------|-------|
| Ruby 3.3 | ✅ Kurulu | `C:\Ruby33-x64\bin` |
| Bundler | ✅ Kurulu | `gem install bundler` |
| Fastlane 2.232.1 | ✅ Kurulu | `bundle exec fastlane --version` |
| Android SDK | ✅ Mevcut | Android Studio ile |
| Keystore | ✅ Mevcut | `app/orbis-release-key.jks` |
| Play Store Hesabı | ⬜ Gerekli | $25 geliştirici hesabı |
| Google Play API Key | ⬜ Gerekli | Aşağıdaki adımları izle |

---

## 🔑 Google Play API Kurulumu (Zorunlu - Tek Seferlik)

Play Store'a otomatik yükleme yapabilmek için **Google Play Developer API** erişimi gereklidir.

### ADIM 1: Google Cloud Projesi
1. [Google Play Console](https://play.google.com/console) → **Account Details** → Not edin: **Google Cloud Project ID**
2. [Google Play Developer API](https://console.developers.google.com/apis/api/androidpublisher.googleapis.com/) → **ENABLE** butonuna tıklayın

### ADIM 2: Service Account Oluşturun
1. [Google Cloud Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts) → Doğru projeyi seçin
2. **CREATE SERVICE ACCOUNT** tıklayın
3. İsim: `fastlane-supply`
4. **DONE** tıklayın (opsiyonel adımları atlayın)
5. Oluşan email adresini kopyalayın (ör: `fastlane-supply@project-id.iam.gserviceaccount.com`)

### ADIM 3: JSON Key İndirin
1. Oluşturulan service account'un yanındaki **⋮** (3 nokta) → **Manage keys**
2. **ADD KEY** → **Create New Key** → **JSON** seçin → **CREATE**
3. JSON dosyasını indirin

### ADIM 4: JSON Key'i Projeye Ekleyin
```powershell
# İndirilen JSON dosyasını kopyalayın:
Copy-Item "C:\Users\erkan\Downloads\*.json" "D:\astro-ai-predictor\backend\flask_app\mobile\android\fastlane\play-store-credentials.json"
```

> ⚠️ **ÖNEMLİ:** Bu dosyayı `.gitignore`'a eklemeyi UNUTMAYIN! (Credential dosyası halka açık olmamalı)

### ADIM 5: Play Console'da Yetki Verin
1. [Google Play Console](https://play.google.com/console) → **Users and Permissions**
2. **Invite new users** tıklayın
3. Email'e service account email adresini yapıştırın
4. **Account Permissions** → **Admin** seçin (veya gerekli izinleri manuel seçin)
5. **Invite User** tıklayın

### ADIM 6: Bağlantıyı Test Edin
```powershell
cd D:\astro-ai-predictor\backend\flask_app\mobile\android
bundle exec fastlane run validate_play_store_json_key json_key:fastlane/play-store-credentials.json
```

Başarılıysa "Successfully established connection" mesajı göreceksiniz.

---

## 📦 Beta Build ve Yükleme

### Hızlı Başlangıç (Tek Komut)

```powershell
cd D:\astro-ai-predictor\backend\flask_app\mobile\android

# 1. Internal Testing'e beta yükle
bundle exec fastlane beta

# 2. Sadece APK oluştur (yüklemeden)
bundle exec fastlane build_apk

# 3. Sadece AAB oluştur (yüklemeden)
bundle exec fastlane build_aab
```

### Adım Adım Beta Deployment

```powershell
# 1. Android proje dizinine git
cd D:\astro-ai-predictor\backend\flask_app\mobile\android

# 2. Version'ı artır (opsiyonel)
bundle exec fastlane bump_version

# 3. Beta build & yükle
bundle exec fastlane beta
```

### İlk Kez Yüklüyorsanız
> ⚠️ **İLK YÜKLEME:** Google Play Console'da uygulama ilk kez daha önce **manuel olarak** bir APK/AAB yüklenmiş olmalıdır. Fastlane supply, ilk yüklemeyi yapamaz - sadece güncelleme yapabilir.
> 
> İlk yükleme için: Manual olarak Play Console'dan AAB dosyasını yükleyin, sonra Fastlane ile otomatikleştirebilirsiniz.

---

## 🛤️ Mevcut Lane'ler

| Lane | Komut | Açıklama |
|------|-------|----------|
| **beta** | `fastlane beta` | AAB build + Internal Testing'e yükle |
| **build_apk** | `fastlane build_apk` | Sadece Release APK oluştur |
| **build_aab** | `fastlane build_aab` | Sadece Release AAB oluştur |
| **alpha** | `fastlane alpha` | Closed Alpha track'e yükle |
| **open_beta** | `fastlane open_beta` | Open Beta track'e yükle |
| **release** | `fastlane release` | Production'a yükle ⚠️ |
| **promote_to_production** | `fastlane promote_to_production` | Beta → Production promote |
| **sync_metadata** | `fastlane sync_metadata` | Play Store metadata indir |
| **bump_version** | `fastlane bump_version` | Version code + name artır |

### Google Play Track Akışı
```
Internal Testing (internal) → Closed Testing (alpha) → Open Testing (beta) → Production
        ▲                          ▲                         ▲                    ▲
   fastlane beta            fastlane alpha          fastlane open_beta    fastlane release
```

---

## 🔧 Sorun Giderme

### Ruby/Fastlane PATH Sorunu
```powershell
# Ruby PATH'e eklenmemişse:
$env:Path = "C:\Ruby33-x64\bin;" + $env:Path
```

### Gradle Build Hatası
```powershell
# Gradle cache temizle
cd D:\astro-ai-predictor\backend\flask_app\mobile\android
.\gradlew clean
```

### JSON Key Doğrulama
```powershell
bundle exec fastlane run validate_play_store_json_key json_key:fastlane/play-store-credentials.json
```

### Version Code Problemi
Play Store aynı version code'u kabul etmez. Her yüklemeden önce:
```powershell
bundle exec fastlane bump_version
```

### "App not found" Hatası
Play Console'da uygulama `com.orbisastro.orbis` package name ile oluşturulmuş olmalı.

---

## 🔒 Güvenlik Notları

- `play-store-credentials.json` → `.gitignore`'a ekle
- `key.properties` → `.gitignore`'a ekle
- Keystore şifreleri → Environment variable olarak kullan
- Service Account'a minimum gerekli yetki ver

---

## 📞 Komut Referansı

```powershell
# Tüm lane'leri listele
bundle exec fastlane lanes

# Bir action'ın parametrelerini gör
bundle exec fastlane action gradle
bundle exec fastlane action upload_to_play_store

# Dry run (test)
bundle exec fastlane beta --verbose
```

---

*Son güncelleme: 2026-02-23*
*Fastlane: 2.232.1 | Ruby: 3.3.10 | Package: com.orbisastro.orbis*
