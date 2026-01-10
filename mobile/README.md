# ORBIS Mobile App

Capacitor ile oluşturulmuş Android uygulaması. AdMob reklam entegrasyonu içerir.

## 🚀 Kurulum

### Gereksinimler

- Node.js 18+
- Android Studio (Arctic Fox veya üzeri)
- JDK 17
- Android SDK (API 33+)

### Adımlar

```bash
# 1. Bağımlılıkları yükle
cd mobile
npm install

# 2. Capacitor'ı başlat
npx cap init ORBIS com.orbis.astrology --web-dir=www

# 3. Android platformunu ekle
npx cap add android

# 4. Sync yap
npx cap sync

# 5. Android Studio'da aç
npx cap open android
```

## 📱 AdMob Yapılandırması

### 1. AdMob Hesabı Oluştur

1. [AdMob Console](https://admob.google.com)'a git
2. Yeni uygulama ekle (Android)
3. Ad Unit'leri oluştur:
   - Banner
   - Interstitial
   - Rewarded

### 2. Ad Unit ID'lerini Güncelle

`www/js/admob.js` dosyasında:

```javascript
AD_UNITS: {
  BANNER: 'ca-app-pub-XXXXXXXX/XXXXXXXXXX',
  INTERSTITIAL: 'ca-app-pub-XXXXXXXX/XXXXXXXXXX',
  REWARDED: 'ca-app-pub-XXXXXXXX/XXXXXXXXXX',
}
```

### 3. AndroidManifest.xml Güncelle

`android/app/src/main/AndroidManifest.xml`:

```xml
<manifest>
  <application>
    <!-- AdMob App ID -->
    <meta-data
      android:name="com.google.android.gms.ads.APPLICATION_ID"
      android:value="ca-app-pub-XXXXXXXXXXXXXXXX~XXXXXXXXXX"/>
  </application>
</manifest>
```

## 🔧 Web App URL Yapılandırması

`www/js/app.js` dosyasında production URL'inizi güncelleyin:

```javascript
WEB_APP_URL: 'https://your-orbis-app.vercel.app',
```

## 📦 Build & Release

### Debug APK

```bash
cd android
./gradlew assembleDebug
# APK: android/app/build/outputs/apk/debug/app-debug.apk
```

### Release AAB (Play Store için)

```bash
cd android
./gradlew bundleRelease
# AAB: android/app/build/outputs/bundle/release/app-release.aab
```

### Signing Key Oluştur

```bash
keytool -genkey -v -keystore orbis-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias orbis
```

## 🎯 Reklam Stratejisi

| Reklam Tipi  | Gösterim Zamanı | Sıklık              |
| ------------ | --------------- | ------------------- |
| Banner       | Sürekli (alt)   | Her zaman           |
| Interstitial | Analiz sonrası  | Her 3 analizde 1    |
| Rewarded     | Premium özellik | Kullanıcı isteğiyle |

## 📋 Play Store Checklist

- [ ] Privacy Policy sayfası (zorunlu)
- [ ] App ikonu (512x512)
- [ ] Feature graphic (1024x500)
- [ ] Screenshots (en az 2)
- [ ] Uygulama açıklaması (Türkçe/İngilizce)
- [ ] Content rating anketi
- [ ] Target audience seçimi
- [ ] Data safety form

## 🔗 Faydalı Linkler

- [Capacitor Docs](https://capacitorjs.com/docs)
- [AdMob Plugin](https://github.com/nicholasbraun/capacitor-admob)
- [Play Console](https://play.google.com/console)
- [AdMob Console](https://admob.google.com)

## 📞 Destek

Sorularınız için: support@orbis.app
