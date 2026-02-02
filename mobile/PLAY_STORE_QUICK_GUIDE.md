# 🚀 ORBIS - Play Store Deployment Step-by-Step

## 📋 HAZIR MISINIZ?

Aşağıdaki adımları SIRAyla takip edin. Her adımı tamamladığınızda bir sonrakine geçin.

---

## ✅ ADIM 1: Keystore Oluştur (5 dakika)

### 1.1 Credential Dosyasını Açın
```
File: D:\astro-ai-predictor\backend\flask_app\mobile\RELEASE_CREDENTIALS.md
```

Buradaki şifreler ve bilgileri kullanacaksınız.

### 1.2 Android Studio'da Generate Signed Bundle

1. **Android Studio'yu açın**
   - Proje: `D:\astro-ai-predictor\backend\flask_app\mobile\android`

2. **Build Menu**
   ```
   Build → Generate Signed Bundle / APK
   ```

3. **Android App Bundle Seçin**
   - (Radyo butonu) Android App Bundle (.aab)
   - Next

4. **Keystore Oluştur**
   - (Radyo butonu) Create new...
   
   **Keystore Path:**
   ```
   D:\astro-ai-predictor\backend\flask_app\mobile\android\app\orbis-release-key.jks
   ```
   
   **Keystore Password:**
   ```
   OrbisAstroKeyStore2025!Secure
   ```
   
   **Confirm:** (Aynısını tekrar yazın)

5. **Key Information**
   
   **Alias:**
   ```
   orbis-key
   ```
   
   **Password:**
   ```
   OrbisKeyPass2025!Secure
   ```
   
   **Validity (years):**
   ```
   25
   ```

6. **Certificate**
   
   **First and Last Name:**
   ```
   ORBIS
   ```
   
   **Organizational Unit:**
   ```
   ORBIS Development
   ```
   
   **Organization:**
   ```
   ORBIS Development
   ```
   
   **City or Locality:**
   ```
   Istanbul
   ```
   
   **State or Province:**
   ```
   Istanbul
   ```
   
   **Country Code (XX):**
   ```
   TR
   ```
   
   **OK** butonuna tıklayın

7. **Build Type Seçin**
   - (Radyo butonu) Release
   - Next

8. **Build Variant Seçin**
   - release → Next

9. **Output Yolu**
   - Varsayılan: `mobile/android/app/release/app-release.aab`
   - **Finished** butonuna tıklayın

✅ **Keystore ve AAB başarıyla oluşturuldu!**

---

## ✅ ADIM 2: Build Artifacts Kontrol Et (2 dakika)

Şu dosyaların var olduğunu kontrol edin:

```
✓ D:\astro-ai-predictor\backend\flask_app\mobile\android\app\orbis-release-key.jks
✓ D:\astro-ai-predictor\backend\flask_app\mobile\android\app\release\app-release.aab
```

---

## ✅ ADIM 3: Google Play Console Hesabı (10 dakika)

### 3.1 Geliştirici Hesabı Açın

1. **https://play.google.com/console** git
2. **Sign in with Google** 
   - Gmail hesabınızı kullanın

3. **Create developer account**
   - Adınızı girin
   - Ülke: **Turkey**
   - Email: `[Sizin email]`
   - Telefon: `[Sizin telefon - isteğe bağlı]`
   - **Agree to terms** checkbox işaretle
   - $25 ödeme yap (Kredi kartı gerekli)

4. **Onay Bekle** (genellikle hemen onaylanır)

### 3.2 Uygulamayı Oluştur

1. **Create app** butonuna tıkla

2. **App Details**
   
   **App Name:**
   ```
   ORBIS - Doğum Haritası & Transit Analiz
   ```
   
   **Default Language:**
   ```
   Turkish (Türkçe)
   ```
   
   **App or game:**
   ```
   App
   ```
   
   **Free or Paid:**
   ```
   Free (Ücretsiz)
   ```
   
   **Create** butonuna tıkla

---

## ✅ ADIM 4: App Listing Hazırla (15 dakika)

### 4.1 Ana Bilgiler

**Menu:** Setup → App info

1. **App Name:**
   ```
   ORBIS - Doğum Haritası
   ```

2. **Short description:**
   ```
   Kişiselleştirilmiş astrolojik analiz ve transit rehberi
   ```

3. **Full description:**
   ```
   ORBIS, astrolojik haritanızın derinlemesine analizini yapan akıllı uygulamadır.
   
   ✨ ÖZELLİKLER:
   • Doğum haritası hesaplaması
   • Transit analizi
   • AI destekli astrolojik yorum
   • Günlük ve haftalık rehberlik
   • Kişisel takip ve notlar
   
   🔐 Verileriniz tamamen güvenli ve özel olup, hiçbir üçüncü tarafa paylaşılmaz.
   ```

### 4.2 Kategoriler

**Category:**
```
Lifestyle
```

**Content Rating:**
```
Ages 3+
```

---

## ✅ ADIM 5: Grafikler Yükleme (10 dakika)

**Menu:** Setup → Graphics

Şu dosyaların var olduğundan emin olun:

```
D:\astro-ai-predictor\backend\flask_app\mobile\play-store\graphics\
├── app-icon-512.png         (512x512 PNG - ZORUNLU)
├── feature-graphic.png      (1024x500 PNG - ZORUNLU)
├── screenshot-1.png         (1080x1920 PNG minimum)
├── screenshot-2.png
└── screenshot-3.png
```

Her dosyayı Play Console'a yükleyin.

---

## ✅ ADIM 6: Yasal Belgeler (10 dakika)

**Menu:** Setup → App content

1. **Privacy Policy:**
   ```
   https://www.orbisastro.online/legal/privacy
   ```

2. **Terms of Service:**
   ```
   https://www.orbisastro.online/legal/terms
   ```

3. **Contact Email:**
   ```
   [Sizin admin email]
   ```

### 6.1 Content Rating Questionnaire

1. **Doldur** butonuna tıkla
2. Soruları cevapla (çoğu "No" olacak)
3. **Save** butonuna tıkla

---

## ✅ ADIM 7: AAB Yükleme (5 dakika)

**Menu:** Release → Production

1. **Create new release** butonuna tıkla

2. **Add app bundles:**
   ```
   D:\astro-ai-predictor\backend\flask_app\mobile\android\app\release\app-release.aab
   ```

3. **Release notes (Türkçe):**
   ```
   🎉 ORBIS v1.0.0 - İlk Sürüm
   
   ✨ Özellikler:
   • Doğum haritası analizi
   • Transit takibi
   • AI yorumlar
   • Ödüllü video reklamlar
   
   🐛 İyileştirmeler:
   • Mobil optimizasyon
   • Hız iyileştirmeleri
   • Arayüz tasarımı
   ```

4. **Review release** butonuna tıkla

---

## ✅ ADIM 8: Gözden Geçir ve Gönder (2 dakika)

**Menu:** Setup → Review

Tüm alanları kontrol edin:

- [x] App name
- [x] Description
- [x] Icon
- [x] Screenshots  
- [x] Privacy policy
- [x] Content rating
- [x] AAB uploaded
- [x] Release notes

Hepsi yeşilse → **Submit for review** butonuna tıklayın

---

## ⏳ BEKLEME DÖNEMİ (1-3 gün)

Google'ın inceleme ekibi uygulamayı kontrol edecektir:

- Apk/AAB dosyası analizi
- İçerik kontrolü
- Güvenlik taraması
- Reklam politikası uygunluğu

### Bu Sırada Yapmanız Gerekenler:

1. **Email kontrolü** - Onay/ret cevabını bekleyin
2. **Sorun varsa:** Play Console'da feedback bakın
3. **Ufak değişiklik:** Yeni AAB build'i yöneticiler aracılığıyla gönder

---

## ✅ ONAYLANDIKTAN SONRA (5 dakika)

### 8.1 Yayınla

1. **Setup → Release → Production**
2. **Release notes** kontrol et
3. **Roll out to production** butonuna tıkla
4. **Confirm** butonuna tıkla

### 8.2 Canlıya Çıkma

```
Google Play Store'da 2-4 saat içinde görünür olacaktır
```

---

## 🔗 İLETİŞİM ve DESTEK

- **Play Console Yardım:** https://support.google.com/googleplay
- **Developer Dokümanları:** https://developer.android.com
- **ORBIS Destek:** [Your support email]

---

## ⚠️ ÖNEMLİ NOTLAR

1. **Keystore Şifresi** - ASLA Kaybetmeyin!
   - Eğer kaybedersen, uygulamayı güncelleyemezsin
   - Safe place'e kaydet

2. **Version Code Artışı**
   - Sonraki update: `versionCode: 2`
   - `capacitor.config.ts` + `build.gradle` güncelle

3. **Reklam Politikası**
   - Google AdMob şartlarına uygun (Rewarded Ads)
   - Kullanıcı deneyimini bozmayan (5 dakika arası)

4. **Veri Gizliliği**
   - Kullanıcı verileri server'da şifreli
   - Privacy Policy'de açık ve anlaşılır açıkla

---

**Last Updated:** 2026-02-02  
**Status:** ✅ Yayına hazır  
**Version:** 1.0.0  
**Package:** com.orbisastro.orbis
