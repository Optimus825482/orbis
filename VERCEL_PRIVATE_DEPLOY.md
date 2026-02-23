# 🚀 VERCEL PRIVATE REPO DEPLOY REHBERİ

## ❌ YANLIŞ: Repo'yu Public Yap
## ✅ DOĞRU: Vercel'e Private Repo Erişimi Ver

Vercel private repolardan deploy edebilir! Repo'yu public yapmanıza gerek yok.

## 📋 ADIM ADIM ÇÖZÜM

### 1. Vercel Dashboard'a Git
```
https://vercel.com/dashboard
```

### 2. GitHub Bağlantısını Kontrol Et

**Yöntem A: Yeni Proje Import Et**
1. Vercel Dashboard > "Add New" > "Project"
2. "Import Git Repository" seç
3. GitHub'ı seç
4. **"Adjust GitHub App Permissions"** veya **"Configure GitHub App"** tıkla
5. Repository access'i ayarla:
   - ✅ "All repositories" VEYA
   - ✅ "Only select repositories" > **orbis** seç
6. Save
7. Vercel'e geri dön, şimdi private repo görünecek

**Yöntem B: Mevcut Proje Varsa**
1. Vercel Project Settings > "Git"
2. "Connect Git Repository" veya "Reconnect"
3. Yukarıdaki adımları takip et

### 3. Environment Variables Ekle (ÖNEMLİ!)

Vercel'de hassas dosyalar environment variable olarak eklenmelidir:

#### A) Vercel Dashboard'da
```
Project Settings > Environment Variables
```

Şunları ekle:

**GOOGLE_APPLICATION_CREDENTIALS_JSON**
```json
{
  "type": "service_account",
  "project_id": "orbis-ffa9e",
  ...
}
```
(firebase-adminsdk JSON içeriğinin TAMAMINI buraya yapıştır)

**GOOGLE_SERVICES_JSON** (Android için)
```json
{
  "project_info": {
    "project_id": "orbis-ffa9e",
    ...
  }
}
```
(google-services.json içeriğinin TAMAMINI buraya yapıştır)

**Diğer Gerekli Variables:**
- `FLASK_SECRET_KEY`: Random bir string
- `DATABASE_URL`: Veritabanı bağlantısı (varsa)
- `API_KEY`: Diğer API key'ler (varsa)

### 4. Build Settings

Vercel'de build ayarları:

**Framework Preset:** Other (veya Flask seç)

**Build Command:**
```bash
pip install -r requirements.txt
```

**Output Directory:**
```
.
```

**Install Command:**
```bash
pip install -r requirements.txt
```

### 5. vercel.json Güncelle

Repository'de vercel.json olmalı (zaten var):

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ],
  "env": {
    "PYTHON_VERSION": "3.9"
  }
}
```

### 6. Firebase Credentials Runtime'da Yükle

Backend kodunda environment variable'dan oku:

**Örnek: `config.py`**
```python
import os
import json
from pathlib import Path

# Vercel'de environment variable'dan oku
FIREBASE_ADMIN_SDK_JSON = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')

if FIREBASE_ADMIN_SDK_JSON:
    # Vercel environment (JSON string)
    import firebase_admin
    from firebase_admin import credentials
    
    cred_dict = json.loads(FIREBASE_ADMIN_SDK_JSON)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
else:
    # Local environment (dosya)
    cred_path = Path.home() / 'orbis-secrets' / 'orbis-ffa9e-firebase-adminsdk.json'
    if cred_path.exists():
        cred = credentials.Certificate(str(cred_path))
        firebase_admin.initialize_app(cred)
    else:
        raise FileNotFoundError("Firebase credentials not found!")
```

### 7. Deploy!

```bash
# Vercel CLI ile (opsiyonel)
npm i -g vercel
vercel login
vercel

# VEYA
# GitHub'a push yap, Vercel otomatik deploy eder
git add .
git commit -m "feat: Vercel deployment yapılandırması"
git push origin main
```

## 🔧 SORUN GİDERME

### "Repository not found" Hatası
```
1. GitHub > Settings > Applications > Vercel
2. "Configure" tıkla
3. Repository access'i kontrol et
4. orbis reposuna erişim ver
5. Save
```

### "Build failed" Hatası
```
1. Vercel Dashboard > Deployment > Logs kontrol et
2. requirements.txt eksik bağımlılık olabilir
3. Python versiyonu uyumlu mu kontrol et
```

### Firebase Credentials Hatası
```
1. Environment Variables doğru eklenmiş mi?
2. JSON formatı doğru mu? (tek satır olarak ekleyin)
3. Kod environment variable'ı okuyor mu?
```

## 🎯 HIZLI KONTROL LİSTESİ

```
☐ Vercel'e GitHub bağlantısı var
☐ Private repo erişimi verildi
☐ Environment variables eklendi:
  ☐ GOOGLE_APPLICATION_CREDENTIALS_JSON
  ☐ GOOGLE_SERVICES_JSON (varsa)
  ☐ FLASK_SECRET_KEY
  ☐ Diğer API key'ler
☐ vercel.json yapılandırıldı
☐ Build ayarları doğru
☐ Kod environment variable'ları okuyor
☐ .gitignore hassas dosyaları exclude ediyor
☐ Deploy test edildi
```

## 📚 ALTERNATIFLER

Eğer Vercel çalışmazsa:

### 1. Railway
```
- Private repo destekler
- Ücretsiz tier var
- Deploy kolay
- https://railway.app
```

### 2. Render
```
- Private repo destekler
- Ücretsiz tier var
- https://render.com
```

### 3. Fly.io
```
- Private repo destekler
- Flask için iyi
- https://fly.io
```

### 4. Azure App Service
```
- Microsoft'un hosting platformu
- GitHub Actions ile entegre
- https://azure.microsoft.com/services/app-service/
```

## 🔐 GÜVENLİK NOTU

**ASLA** şunları yapmayın:
- ❌ Repo'yu hassas dosyalar varken public yapma
- ❌ API key'leri kod içine hard-code etme
- ❌ .env dosyasını commit etme
- ❌ Credentials'ı client-side'a gönderme

**HER ZAMAN** şunları yapın:
- ✅ Environment variables kullan
- ✅ .gitignore güncel tut
- ✅ Secret management servisleri kullan
- ✅ Private repo'da çalış (mümkünse)

---
**Oluşturulma**: 2 Şubat 2026  
**Durum**: 🟢 Hazır - Vercel private repo deploy için
