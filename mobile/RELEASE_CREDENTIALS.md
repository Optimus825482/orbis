# 🔐 ORBIS Release Credentials

## Keystore Bilgileri

**⚠️ ÖNEMLİ: Bu dosya GİZLİ tutulmalı, asla git'e commit edilmemeli!**

### Keystore Dosyası
```
Path: D:\astro-ai-predictor\backend\flask_app\mobile\android\app\orbis-release-key.jks
```

### Keystore Password
```
OrbisAstroKeyStore2025!Secure
```

### Key Alias
```
orbis-key
```

### Key Password
```
OrbisKeyPass2025!Secure
```

### Validity
```
25 years
```

### Certificate Information
- **Name:** ORBIS
- **Organization:** ORBIS Development
- **Organization Unit:** ORBIS
- **City:** Istanbul
- **State:** Istanbul
- **Country:** TR

---

## Build Configuration

### key.properties

```properties
storePassword=OrbisAstroKeyStore2025!Secure
keyPassword=OrbisKeyPass2025!Secure
keyAlias=orbis-key
storeFile=app/orbis-release-key.jks
```

---

## Notes

- Created: 2026-02-02
- Version: 1.0.0
- Package Name: com.orbisastro.orbis
- App ID: ca-app-pub-2444093901783574
- AdMob Rewarded Video: ca-app-pub-2444093901783574/9083651006

---

## Instructions

1. **Create Keystore in Android Studio:**
   - Build > Generate Signed Bundle/APK
   - Click "Create new..." keystore
   - Enter all the values above

2. **Create key.properties file:**
   ```bash
   cd D:\astro-ai-predictor\backend\flask_app\mobile\android
   echo "storePassword=OrbisAstroKeyStore2025!Secure" > key.properties
   echo "keyPassword=OrbisKeyPass2025!Secure" >> key.properties
   echo "keyAlias=orbis-key" >> key.properties
   echo "storeFile=app/orbis-release-key.jks" >> key.properties
   ```

3. **Add to .gitignore:**
   ```bash
   echo "key.properties" >> .gitignore
   echo "*.jks" >> .gitignore
   ```

4. **Generate Release AAB:**
   - Build > Generate Signed Bundle/APK
   - Choose "Android App Bundle"
   - Select existing keystore from above path
   - Enter passwords
   - Choose Release build variant
   - Output location: mobile/android/app/release/app-release.aab

---

## 🔗 Google Play Console

- **Developer Account:** To be created
- **Console URL:** https://play.google.com/console
- **App Package Name:** com.orbisastro.orbis
- **Upload Certificate (SHA-1):** [Will be generated after first keystore creation]

---

**Last Updated:** 2026-02-02
