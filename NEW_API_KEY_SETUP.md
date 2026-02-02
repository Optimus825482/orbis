# 🔐 YENİ API KEY KURULUM REHBERİ

## ✅ Tamamlanan Adımlar
- [x] Eski API key silindi
- [x] Yeni API key oluşturuldu
- [x] .gitignore güncellendi

## 📥 ŞİMDİ YAPILACAKLAR

### 1. Firebase'den Yeni Dosyaları İndir

#### A) google-services.json (Android)
```
1. https://console.firebase.google.com/project/orbis-ffa9e/settings/general
2. "Your apps" bölümüne git
3. Android app'i bul (com.orbis.astrology veya com.orbisastro.orbis)
4. ⚙️ (Settings) > google-services.json
5. "Download google-services.json" butonuna bas
6. İndirilen dosyayı şu konumlara kopyala:
   - d:\astro-ai-predictor\backend\flask_app\google-services.json
   - d:\astro-ai-predictor\backend\flask_app\mobile\android\app\google-services.json
```

#### B) Firebase Admin SDK (Backend)
```
1. https://console.firebase.google.com/project/orbis-ffa9e/settings/serviceaccounts/adminsdk
2. "Generate new private key" butonuna bas
3. İndirilen dosyayı şu şekilde yeniden adlandır:
   orbis-ffa9e-firebase-adminsdk-YENI.json
4. Dosyayı GÜVENLİ BİR YERE taşı (repo DIŞINDA):
   - C:\Users\<USERNAME>\orbis-secrets\
   - Veya başka güvenli bir dizin
```

#### C) OAuth Client Secrets (Varsa)
```
1. https://console.cloud.google.com/apis/credentials?project=orbis-ffa9e
2. OAuth 2.0 Client IDs bölümünü kontrol et
3. Gerekirse yeni client secret indir
```

### 2. Dosyaları Güvenli Şekilde Sakla

```powershell
# Güvenli dizin oluştur
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\orbis-secrets"

# İndirdiğin dosyaları buraya taşı
Move-Item -Path "Downloads\google-services.json" -Destination "$env:USERPROFILE\orbis-secrets\"
Move-Item -Path "Downloads\orbis-ffa9e-firebase-adminsdk-*.json" -Destination "$env:USERPROFILE\orbis-secrets\"

# Development için environment variable kullan
[Environment]::SetEnvironmentVariable("FIREBASE_ADMIN_SDK_PATH", "$env:USERPROFILE\orbis-secrets\orbis-ffa9e-firebase-adminsdk-YENI.json", "User")
[Environment]::SetEnvironmentVariable("GOOGLE_SERVICES_JSON_PATH", "$env:USERPROFILE\orbis-secrets\google-services.json", "User")
```

### 3. Uygulamada Güncelle

#### Backend (Flask)
`config.py` veya ilgili dosyada:

```python
import os
from pathlib import Path

# Environment variable'dan oku
FIREBASE_ADMIN_SDK = os.getenv(
    'FIREBASE_ADMIN_SDK_PATH',
    Path.home() / 'orbis-secrets' / 'orbis-ffa9e-firebase-adminsdk-YENI.json'
)

# Dosya kontrolü
if not Path(FIREBASE_ADMIN_SDK).exists():
    raise FileNotFoundError(
        f"Firebase Admin SDK not found at {FIREBASE_ADMIN_SDK}\n"
        "Download from: https://console.firebase.google.com/project/orbis-ffa9e/settings/serviceaccounts/adminsdk"
    )
```

#### Android
google-services.json dosyasını şuraya koyun:
```
mobile/android/app/google-services.json
```

Gradle otomatik olarak okur.

### 4. Git History Temizliği

```powershell
# Script'i çalıştır
cd d:\astro-ai-predictor\backend\flask_app
.\cleanup-git-history.ps1

# Veya manuel:
git filter-branch --force --index-filter `
  "git rm --cached --ignore-unmatch google-services.json google-services*.json *firebase-adminsdk*.json client_secret_*.json" `
  --prune-empty --tag-name-filter cat -- --all

git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

### 5. Force Push (DİKKATLİ!)

⚠️ **UYARI**: Eğer başka geliştiriciler varsa önce onları bilgilendir!

```powershell
# Remote'u kontrol et
git remote -v

# Force push
git push origin --force --all
git push origin --force --tags
```

### 6. GitHub Secrets (CI/CD için)

Eğer GitHub Actions kullanıyorsanız:

```
1. Repository Settings > Secrets and variables > Actions
2. New repository secret
3. Şunları ekle:
   - FIREBASE_ADMIN_SDK: Firebase admin SDK JSON'unun içeriği
   - GOOGLE_SERVICES_JSON: google-services.json içeriği
   - API_KEY: Yeni API key (eğer backend'de kullanılıyorsa)
```

GitHub Actions workflow'unda:
```yaml
- name: Create google-services.json
  run: |
    echo '${{ secrets.GOOGLE_SERVICES_JSON }}' > mobile/android/app/google-services.json

- name: Create Firebase Admin SDK
  run: |
    echo '${{ secrets.FIREBASE_ADMIN_SDK }}' > firebase-adminsdk.json
```

### 7. API Key Restrictions Kontrolü

Google Cloud Console'da kontrol et:
```
https://console.cloud.google.com/apis/credentials?project=orbis-ffa9e
```

Yeni API key için:
- ✅ Application restrictions: Android apps
- ✅ Package name: com.orbis.astrology VEYA com.orbisastro.orbis
- ✅ SHA-1 fingerprint: Uygulamanın signing key'inden
- ✅ API restrictions: Sadece gerekli API'lar seçili

### 8. Test Et

```powershell
# Backend'i test et
cd d:\astro-ai-predictor\backend\flask_app
python run.py

# Android build test
cd mobile/android
./gradlew assembleDebug

# API key'in çalışıp çalışmadığını test et
# Firebase Authentication, Storage, vs.
```

### 9. Dokümantasyon Güncelle

README.md'ye ekle:
```markdown
## 🔐 Güvenlik Notları

### Hassas Dosyalar
Aşağıdaki dosyalar GİZLİDİR ve asla commit edilmemelidir:
- google-services.json
- *-firebase-adminsdk-*.json  
- client_secret_*.json
- .env

### Kurulum
1. Firebase Console'dan google-services.json indir
2. `$HOME/orbis-secrets/` dizinine kopyala
3. Environment variable'ları ayarla (bkz: env.example)

### Daha Fazla Bilgi
Bkz: SECURITY_CLEANUP.md
```

## ✅ KONTROL LİSTESİ

Tamamlandıkça işaretle:

```
☐ Yeni google-services.json indirildi
☐ Yeni Firebase Admin SDK indirildi
☐ Dosyalar güvenli dizine taşındı
☐ Backend kodu güncellendi (environment variables)
☐ Android app test edildi
☐ Git history temizlendi
☐ Force push yapıldı
☐ GitHub Secrets eklendi (varsa CI/CD)
☐ API key restrictions kontrol edildi
☐ Billing alerts kuruldu
☐ Firebase Security Rules kontrol edildi
☐ README.md güncellendi
☐ Team'e bildirim yapıldı
```

## 🚨 SORUN GİDERME

### "google-services.json not found"
```powershell
# Dosyanın doğru yerde olduğunu kontrol et
Test-Path "mobile/android/app/google-services.json"

# Yoksa Firebase'den indir
```

### "API key restrictions" hatası
```
1. Google Cloud Console > Credentials
2. API key'i bul
3. "Edit" > "Application restrictions"
4. Package name ve SHA-1 fingerprint doğru mu kontrol et
```

### SHA-1 Fingerprint Nasıl Bulunur?

Debug key için:
```powershell
cd mobile/android
./gradlew signingReport
```

Release key için:
```powershell
keytool -list -v -keystore your-keystore.jks -alias your-alias
```

### Git History Temizliği Başarısız
```powershell
# Alternatif: BFG Repo-Cleaner
# https://rtyley.github.io/bfg-repo-cleaner/

java -jar bfg.jar --delete-files google-services.json
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

## 📞 YARDIM

Takıldığınız yer olursa:
- Firebase Docs: https://firebase.google.com/docs
- Google Cloud Support: https://cloud.google.com/support
- Stack Overflow: https://stackoverflow.com/questions/tagged/firebase

---
**Oluşturulma**: 2 Şubat 2026  
**Durum**: 🟡 Devam Ediyor - Dosyalar henüz indirilmedi
