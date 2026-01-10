# 🤖 Android Studio Kurulum ve ORBIS Build Rehberi

## 📥 ADIM 1: Android Studio İndirme ve Kurulum

### 1.1 İndirme

1. https://developer.android.com/studio adresine git
2. "Download Android Studio" butonuna tıkla
3. Lisans sözleşmesini kabul et
4. `android-studio-2024.x.x-windows.exe` dosyasını indir (~1GB)

### 1.2 Kurulum

1. İndirilen .exe dosyasını çalıştır
2. "Next" ile devam et
3. Kurulum konumu: `C:\Program Files\Android\Android Studio` (varsayılan)
4. "Install" tıkla ve bekle

### 1.3 İlk Açılış

1. Android Studio'yu başlat
2. "Do not import settings" seç (ilk kurulumsa)
3. Setup Wizard başlayacak:
   - Install Type: **Standard** seç
   - UI Theme: Darcula (koyu) veya Light
   - SDK Components: Hepsini seçili bırak
   - "Finish" tıkla ve SDK indirmesini bekle (~2-3GB)

---

## ⚙️ ADIM 2: SDK ve Araçları Yapılandırma

### 2.1 SDK Manager'ı Aç

1. Android Studio açıkken: `File > Settings` (veya `Ctrl+Alt+S`)
2. Sol menüden: `Appearance & Behavior > System Settings > Android SDK`

### 2.2 SDK Platforms (Gerekli)

"SDK Platforms" sekmesinde şunları işaretle:

- ✅ Android 14.0 (API 34) - Target SDK
- ✅ Android 13.0 (API 33) - Minimum desteklenen

### 2.3 SDK Tools (Gerekli)

"SDK Tools" sekmesinde şunları işaretle:

- ✅ Android SDK Build-Tools 34
- ✅ Android SDK Command-line Tools
- ✅ Android SDK Platform-Tools
- ✅ Android Emulator
- ✅ Google Play services

"Apply" tıkla ve indirmeleri bekle.

### 2.4 Environment Variables (Windows)

1. Windows arama: "Ortam Değişkenleri" veya "Environment Variables"
2. "Sistem ortam değişkenlerini düzenle" aç
3. "Ortam Değişkenleri" butonuna tıkla
4. "Sistem değişkenleri" altında "Yeni" tıkla:

```
Değişken adı: ANDROID_HOME
Değişken değeri: C:\Users\KULLANICI_ADIN\AppData\Local\Android\Sdk
```

5. "Path" değişkenini düzenle ve şunları ekle:

```
%ANDROID_HOME%\platform-tools
%ANDROID_HOME%\tools
%ANDROID_HOME%\tools\bin
```

6. CMD'yi yeniden aç ve test et:

```cmd
adb --version
```

---

## 📱 ADIM 3: ORBIS Projesini Android Studio'da Açma

### 3.1 Capacitor Android Platformunu Ekle

```cmd
cd mobile
npm install
npx cap add android
npx cap sync
```

### 3.2 Android Studio'da Aç

```cmd
npx cap open android
```

Veya manuel:

1. Android Studio'yu aç
2. "Open" seç
3. `mobile/android` klasörünü seç
4. "Trust Project" tıkla

### 3.3 İlk Sync

- Gradle sync otomatik başlayacak
- Sağ altta progress bar'ı takip et
- "Build: Sync" tamamlanana kadar bekle (ilk seferde 5-10 dk)

---

## 🔧 ADIM 4: AdMob Yapılandırması

### 4.1 AndroidManifest.xml Düzenleme

Dosya: `android/app/src/main/AndroidManifest.xml`

`<application>` tag'inin içine ekle:

```xml
<application
    android:allowBackup="true"
    android:icon="@mipmap/ic_launcher"
    android:label="@string/app_name"
    ...>

    <!-- AdMob App ID - Kendi ID'nizi yazın -->
    <meta-data
        android:name="com.google.android.gms.ads.APPLICATION_ID"
        android:value="ca-app-pub-XXXXXXXXXXXXXXXX~XXXXXXXXXX"/>

    <!-- Mevcut activity'ler... -->
</application>
```

### 4.2 build.gradle Kontrolü

Dosya: `android/app/build.gradle`

Dependencies bölümünde AdMob olmalı (Capacitor plugin ekler):

```gradle
dependencies {
    implementation 'com.google.android.gms:play-services-ads:22.6.0'
    // ... diğer dependencies
}
```

---

## 🧪 ADIM 5: Test Etme

### 5.1 Emulator Oluşturma

1. Android Studio'da: `Tools > Device Manager`
2. "Create Device" tıkla
3. Phone kategorisinden "Pixel 7" seç > Next
4. System Image: "API 34" (indir gerekirse) > Next
5. AVD Name: "ORBIS_Test" > Finish

### 5.2 Emulator'da Çalıştırma

1. Üst toolbar'da device dropdown'dan "ORBIS_Test" seç
2. Yeşil "Run" (▶️) butonuna tıkla
3. Build tamamlanınca emulator'da uygulama açılacak

### 5.3 Fiziksel Cihazda Test

1. Telefonda: `Ayarlar > Telefon Hakkında > Yapı Numarası`na 7 kez dokun
2. "Geliştirici seçenekleri" aktif olacak
3. `Ayarlar > Geliştirici Seçenekleri > USB Hata Ayıklama` aç
4. USB ile bilgisayara bağla
5. "USB hata ayıklamaya izin ver" onay ver
6. Android Studio'da cihazın görünmesini bekle
7. Run butonuna tıkla

---

## 📦 ADIM 6: Release Build (Play Store için)

### 6.1 Signing Key Oluşturma

```cmd
cd android
keytool -genkey -v -keystore orbis-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias orbis
```

Sorulara cevap ver:

- Keystore password: (güçlü şifre gir, UNUTMA!)
- Ad Soyad: Erkan ...
- Organizasyon: Orbis Inc.
- Şehir: Istanbul
- Ülke kodu: TR

### 6.2 Signing Config Ekleme

Dosya: `android/app/build.gradle`

```gradle
android {
    ...

    signingConfigs {
        release {
            storeFile file('orbis-release-key.jks')
            storePassword 'KEYSTORE_SIFRESI'
            keyAlias 'orbis'
            keyPassword 'KEY_SIFRESI'
        }
    }

    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
        }
    }
}
```

### 6.3 AAB Build (Play Store)

```cmd
cd android
.\gradlew bundleRelease
```

Çıktı: `android/app/build/outputs/bundle/release/app-release.aab`

### 6.4 APK Build (Test için)

```cmd
cd android
.\gradlew assembleRelease
```

Çıktı: `android/app/build/outputs/apk/release/app-release.apk`

---

## 🚨 Sık Karşılaşılan Hatalar

### Hata: "SDK location not found"

Çözüm: `android/local.properties` dosyası oluştur:

```properties
sdk.dir=C:\\Users\\KULLANICI\\AppData\\Local\\Android\\Sdk
```

### Hata: "Gradle sync failed"

Çözüm:

1. `File > Invalidate Caches > Invalidate and Restart`
2. `Build > Clean Project`
3. `Build > Rebuild Project`

### Hata: "JAVA_HOME not set"

Çözüm: Android Studio'nun JDK'sını kullan:

```
JAVA_HOME=C:\Program Files\Android\Android Studio\jbr
```

### Hata: "minSdk version mismatch"

Çözüm: `android/variables.gradle`:

```gradle
ext {
    minSdkVersion = 22
    targetSdkVersion = 34
    compileSdkVersion = 34
}
```

---

## ✅ Checklist

- [ ] Android Studio kuruldu
- [ ] SDK 33/34 indirildi
- [ ] ANDROID_HOME ayarlandı
- [ ] `npx cap add android` çalıştırıldı
- [ ] Proje Android Studio'da açıldı
- [ ] Gradle sync başarılı
- [ ] AdMob App ID eklendi
- [ ] Emulator/cihazda test edildi
- [ ] Release key oluşturuldu
- [ ] AAB build alındı

---

## 📞 Sonraki Adım

Build başarılı olduktan sonra Play Store'a yükleme için:

1. Google Play Console hesabı aç ($25)
2. Uygulama oluştur
3. AAB dosyasını yükle
4. Store listing doldur
5. İncelemeye gönder

Sorularınız için: Kiro'ya sorun! 🚀
