# 🚨 ACİL GÜVENLİK TEMİZLİĞİ YAPILACAKLAR LİSTESİ

## ✅ TAMAMLANAN
- [x] Repo private yapıldı

## 🔥 HEMEN YAPILMASI GEREKENLER

### 1. API Key'i Yenile (EN ACIL)
```bash
# Google Cloud Console'dan:
# 1. https://console.cloud.google.com/apis/credentials?project=orbis-ffa9e
# 2. API key'i bul: AIzaSyBqE1fm9Z5_o8NpzUvkY4kfSx-oxXUW2MU
# 3. Edit > Regenerate Key
# 4. Yeni key'i kaydet
```

### 2. Firebase'den Yeni Dosyaları İndir
```bash
# 1. https://console.firebase.google.com/project/orbis-ffa9e/settings/general
# 2. Android app > google-services.json indir
# 3. Dosyaları güncelle
```

### 3. API Key Kısıtlamaları Ekle
- [ ] Application restrictions: Android apps
  - Package name: com.orbis.astrology
  - SHA-1 fingerprint ekle
- [ ] API restrictions: Sadece gerekli API'lar
  - Firebase Authentication
  - Firebase Cloud Messaging
  - Firebase Realtime Database
  - Firebase Storage
  - Firestore
  - (Diğer kullandığınız API'lar)

### 4. Git History'den Temizle
⚠️ DİKKAT: Bu işlem destructive'dir, backup alın!

```bash
# Yöntem 1: BFG Repo-Cleaner (Önerilen)
# https://rtyley.github.io/bfg-repo-cleaner/

# BFG indir
# Sonra:
cd d:\astro-ai-predictor
git clone --mirror https://github.com/Optimus825482/orbis.git orbis-mirror.git
cd orbis-mirror.git

# Hassas dosyaları temizle
java -jar bfg.jar --delete-files google-services.json
java -jar bfg.jar --delete-files "google-services*.json"
java -jar bfg.jar --delete-files "orbis-ffa9e-firebase-adminsdk*.json"
java -jar bfg.jar --delete-files "client_secret_*.json"

# History'i yeniden yaz
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push
git push --force
```

```bash
# Yöntem 2: git filter-branch (Manuel)
cd d:\astro-ai-predictor\backend\flask_app

git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch google-services.json google-services*.json orbis-ffa9e-firebase-adminsdk*.json client_secret_*.json" \
  --prune-empty --tag-name-filter cat -- --all

git push origin --force --all
git push origin --force --tags
```

### 5. .gitignore'u Güncelle
```bash
# Ekle:
google-services.json
google-services*.json
*firebase-adminsdk*.json
client_secret_*.json
.env
.env.local
credentials/
secrets/
```

### 6. Billing ve Kullanım Kontrolü
- [ ] https://console.cloud.google.com/billing/ kontrolü
- [ ] Beklenmedik aktivite var mı?
- [ ] Budget alerts kur (örn: $10/ay)
- [ ] Billing hesabına 2FA ekle

### 7. Güvenlik İyileştirmeleri
- [ ] Firebase Security Rules kontrol et
- [ ] Google Cloud Armor etkinleştir
- [ ] Cloud Logging'i aktif et
- [ ] Eski API key'leri sil
- [ ] Tüm API key'lere restriction ekle
- [ ] 2FA'yı tüm hesaplarda aktif et

### 8. Proje Yapısını Düzenle
```bash
# Hassas dosyaları ayrı bir dizine taşı (repo dışında)
mkdir -p ~/orbis-secrets
mv google-services.json ~/orbis-secrets/
mv orbis-ffa9e-firebase-adminsdk*.json ~/orbis-secrets/
mv client_secret_*.json ~/orbis-secrets/

# Sembolik link oluştur (local development için)
ln -s ~/orbis-secrets/google-services.json .
```

### 9. CI/CD'de Secrets Kullan
- [ ] GitHub Secrets ekle
- [ ] GitHub Actions'da environment variables kullan
- [ ] Asla dosyaları commit'leme

### 10. Takım Eğitimi
- [ ] Tüm geliştiricilere bilgi ver
- [ ] Pre-commit hooks ekle
- [ ] Secret scanning araçları kur

## 📊 RİSK DEĞERLENDİRMESİ

### Yüksek Risk Senaryoları:
1. **API Misuse**: Key kötüye kullanılarak Firebase quota'nız tüketilebilir
2. **Veri Erişimi**: Firebase Security Rules zayıfsa verilere erişilebilir
3. **Maliyet**: Biri key'i kullanarak size fatura çıkarabilir

### Orta Risk Senaryoları:
1. **Analytics Spam**: Fake kullanım verileri
2. **Auth Abuse**: Fake hesap oluşturma

### Şu An Güvenli misiniz?
❌ HAYIR - Key hala aktif ve kullanılabilir
✅ Repo private - Ama history'de hala var
⚠️ API restrictions yoksa herkes kullanabilir

## 🎯 BAŞARI KRİTERLERİ

✅ Tamamlandığında:
- Eski key tamamen devre dışı
- Yeni key'de restriction'lar var
- Git history temiz
- Billing alerts aktif
- .gitignore güncel
- CI/CD secrets kullanıyor

## ⏱️ ÖNCELİK SIRASI

1. **0-15 dk**: API key'i yenile + restrictions ekle
2. **15-30 dk**: Billing kontrol + alerts
3. **30-60 dk**: Git history temizle
4. **1-2 saat**: Proje yapısını düzenle
5. **Sonrası**: Security hardening

## 📞 YARDIM

Sorun yaşarsanız:
- Google Cloud Support: https://cloud.google.com/support
- Firebase Support: https://firebase.google.com/support
- GitHub Support: https://support.github.com/

## 🔐 GELECEKTEKİ ÖNLEMLER

1. **Asla commit etme**: Credentials, keys, secrets
2. **Environment variables kullan**: .env dosyaları
3. **Secret management**: Google Secret Manager, Azure Key Vault
4. **Pre-commit hooks**: git-secrets, detect-secrets
5. **Scanning**: GitHub Advanced Security, GitGuardian
6. **Regular audits**: Ayda bir security review

---
**Son Güncelleme**: 2 Şubat 2026
**Durum**: 🚨 DEVAM EDİYOR - API key hala yenilenmedi
