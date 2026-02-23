# 🎯 ORBIS Release - Master Checklist

## 📋 RELEASE ÖNCESI KONTROL

### ✅ Backend (Flask API)

- [ ] `monetization/usage_tracker.py` - Timestamp sistemi aktif
- [ ] `/api/record_ad_watch` - `last_ad_watch` kaydediyor
- [ ] `/api/check_usage` - 5 dakika geçerlilik kontrolü yapıyor
- [ ] `requirements.txt` - Tüm dependency'ler listed
- [ ] `.env.production` - Vercel'da doğru environment var

**Doğrulama:**
```bash
# Production backend test
curl https://app.orbisastro.online/api/check_usage -X POST \
  -H "Content-Type: application/json" \
  -d '{"device_id":"test_123"}'
```

---

### ✅ Frontend (Dashboard HTML)

- [ ] `templates/dashboard.html` - Loading overlay placement fixed
- [ ] `static/js/mobile-bridge.js` - Dual analytics aktif
- [ ] `OrbisRewardedAds.showForAnalysis()` - Çalışıyor
- [ ] Console logs - Debug mesajları görülüyor

**Doğrulama:**
```bash
# Browser Console'da şu görülmeli:
[ORBIS] Usage check: {...}
[ORBIS] Rewarded ad result: true
[ORBIS] ✅ Ad watched successfully
[ORBIS] 🔄 Reklam kontrolü tamamlandı, loading başlıyor...
```

---

### ✅ Mobile Capacitor

- [ ] `mobile/capacitor.config.ts` - Package name: `com.orbisastro.orbis`
- [ ] `mobile/android/app/build.gradle` - Version code + name
- [ ] `mobile/package.json` - Version: 1.0.0
- [ ] Signing config - Key.properties template hazır

**Kontrol:**
```bash
cd mobile
npx cap sync android
npx cap open android  # Android Studio açılmalı
```

---

### ✅ AdMob İntegrasyonu

- [ ] AdMob App ID: `ca-app-pub-2444093901783574`
- [ ] Rewarded Video ID: `ca-app-pub-2444093901783574/9083651006`
- [ ] `google-services.json` - Uygulamaya embedded
- [ ] Emülatör'de test edildi

**Test Adımları:**
```
1. Emülatör başlat
2. App açılmalı (Ad Network'ü initialize ediyor)
3. "Analiz Yap" - Rewarded ad göstermeli
4. Ad izleme tamamlandı - Form submit olmalı
```

---

### ✅ Analytics Setup

- [ ] Google Analytics 4 aktif: `G-PLJEZCGT27`
- [ ] Firebase Analytics: Native mobile events
- [ ] Funnel tracking: 4 steps (ad_required → ad_watched → analysis_start → results)
- [ ] Error tracking: Stack traces logged
- [ ] User properties: Device ID, email, premium status

**Kontrol:**
```
Firebase Console → Analytics → Real-time
  - Users online görmeli
  - Events görülmeli
  - Funnels görülmeli
```

---

## 📁 RELEASE BUILD ADIMLAR

### 1️⃣ Keystore Oluştur

**Dosya:** `RELEASE_CREDENTIALS.md`

```bash
# Android Studio → Build → Generate Signed Bundle/APK
# Şifreler: RELEASE_CREDENTIALS.md'den kopyala
# Output: app/release/app-release.aab
```

- [ ] Keystore file created: `app/orbis-release-key.jks`
- [ ] Credentials saved securely
- [ ] `key.properties` file created
- [ ] `.gitignore` updated (key.properties, *.jks)

---

### 2️⃣ Build & Sign

**Dosya:** `build.gradle.signing`

```bash
# gradle wrapper ile build
cd mobile/android
./gradlew clean bundleRelease

# Beklenen output:
# ✓ app/release/app-release.aab (~15-25 MB)
# ✓ app/release/output-metadata.json (signature info)
```

- [ ] AAB successfully built
- [ ] Signing succeeded (no certificate errors)
- [ ] File size reasonable (~15-25 MB)
- [ ] Can upload to Play Console

---

### 3️⃣ Play Console Setup

**Dosya:** `PLAY_STORE_QUICK_GUIDE.md`

```
Play Console → Create App
  ├─ App Name: "ORBIS - Doğum Haritası"
  ├─ Package Name: "com.orbisastro.orbis"
  ├─ Default Language: Turkish
  ├─ App Category: Lifestyle
  └─ Content Rating: Ages 3+
```

- [ ] Developer account created ($25 paid)
- [ ] Application created in Play Console
- [ ] App name + description finalized
- [ ] Package name locked: `com.orbisastro.orbis`

---

### 4️⃣ Graphics & Content

**Dosya Locations:**
```
mobile/play-store/graphics/
  ├─ app-icon-512.png          (512x512)
  ├─ feature-graphic.png       (1024x500)
  └─ screenshot-X.png          (1080x1920+)
```

- [ ] App icon uploaded (512x512 PNG)
- [ ] Feature graphic uploaded (1024x500 PNG)
- [ ] Screenshots uploaded (minimum 2, maximum 8)
- [ ] All graphics pass validation

---

### 5️⃣ Legal & Compliance

**Links (must be LIVE):**
```
https://www.orbisastro.online/legal/privacy      ✓ Privacy Policy
https://www.orbisastro.online/legal/terms         ✓ Terms of Service
https://www.orbisastro.online/legal/kvkk          ✓ KVKK (GDPR-like)
```

- [ ] Privacy Policy accessible & complete
- [ ] Terms of Service defined
- [ ] Contact email provided
- [ ] Data Safety form completed
- [ ] Content Rating Questionnaire done

---

### 6️⃣ AAB Upload & Release

```
Play Console → Internal Testing / Staging → Production
  ├─ Upload AAB
  ├─ Review release notes
  ├─ Wait for Google review (1-3 days)
  ├─ If approved: Roll out to production
  └─ Live within 4 hours
```

- [ ] AAB uploaded successfully
- [ ] Version code: 1
- [ ] Version name: 1.0.0
- [ ] Release notes (TR) added
- [ ] Submitted for review
- [ ] Awaiting Google approval

---

## 🧪 QA TESTING CHECKLIST

### Device Testing
- [ ] Test on physical Android device (API 21+)
- [ ] Test on Android Studio emulator (Pixel 4)
- [ ] All buttons responsive (48px minimum)
- [ ] Forms work without errors
- [ ] Back/Home navigation works

### Feature Testing
- [ ] Google Sign-In works
- [ ] Birth data entry works
- [ ] Location search works + caching
- [ ] Rewarded ads show + close properly
- [ ] Analysis starts after 1 ad watch
- [ ] Results display correctly
- [ ] AI Comments work
- [ ] Cache persists after app restart

### Performance
- [ ] App starts in < 3 seconds
- [ ] No ANR (Application Not Responding) errors
- [ ] Memory usage < 200MB
- [ ] Battery drain acceptable (< 2% per hour idle)

### Security
- [ ] No hardcoded secrets in APK
- [ ] Firebase config secure
- [ ] HTTPS enforced for all requests
- [ ] Keystore password not in code

---

## 📊 MONITORING & ANALYTICS

### Pre-Launch Checks
```
Play Console → Pre-launch Report
  ├─ Crashes: ✓ 0 expected
  ├─ ANR: ✓ 0 expected
  ├─ Permissions: ✓ Network, Location, Calendar
  └─ Supported devices: ✓ 5,000+ (minimum)
```

- [ ] No crashes on pre-launch devices
- [ ] Performance acceptable
- [ ] Required permissions justified

### Post-Launch Monitoring
```
Firebase Console → Crashlytics
  ├─ Monitor daily crashes
  ├─ Check error trends
  └─ Respond to user feedback quickly

Google Analytics
  ├─ Track funnel completion rates
  ├─ Monitor ad watch rates
  ├─ Track analysis completion
  └─ Identify drop-off points
```

- [ ] Daily crash monitoring setup
- [ ] Alerts configured for errors
- [ ] Analytics dashboard viewed
- [ ] Funnel metrics tracked

---

## 🚀 LAUNCH DAY CHECKLIST

### T-0 Minutes (Before Go Live)
- [ ] All team members notified
- [ ] Monitoring dashboards open (Crashlytics, Analytics)
- [ ] Support email monitored
- [ ] Rollback plan ready

### T+0 (Go Live)
- [ ] Click "Roll out to production"
- [ ] Watch for errors in real-time
- [ ] Verify app appears in Play Store within 4 hours

### T+24 Hours (First Day)
- [ ] Check crash rate < 0.1%
- [ ] Monitor user onboarding
- [ ] Check analytics funnel
- [ ] Respond to user reviews/feedback

### T+7 Days (First Week)
- [ ] Review user feedback
- [ ] Monitor crash trends
- [ ] Check feature adoption rates
- [ ] Plan v1.1 improvements

---

## 📝 VERSION MANAGEMENT

### Current Version
```
Version Code: 1
Version Name: 1.0.0
Release Date: 2026-02-02
Status: Ready for submission
```

### Next Version (1.1.0)
```
Planned features:
- [ ] In-App Purchase integration
- [ ] Push Notifications
- [ ] Advanced charts
- [ ] Premium features (no ads, advanced AI)
```

**Update Procedure:**
1. Increment version code (1 → 2)
2. Update version name (1.0.0 → 1.1.0)
3. Update `capacitor.config.ts` + `build.gradle`
4. Build new AAB
5. Upload to Play Console (internal testing first)
6. Submit for review

---

## ✅ FINAL GO/NO-GO DECISION

**BEFORE SUBMISSION:**

| Item | Status | Owner |
|------|--------|-------|
| Backend API tested | ✅ | Backend Team |
| Frontend UI tested | ✅ | Frontend Team |
| Mobile app tested | ⏳ | Mobile Team |
| Analytics verified | ✅ | DevOps |
| Legal docs ready | ✅ | Legal/Admin |
| Play Console setup | ⏳ | Release Manager |
| Graphics uploaded | ⏳ | Design Team |
| Keystore secured | ⏳ | DevOps |

**Decision:**
```
GO / NO-GO → _____________________
Approved by: _____________________
Date: _____________________
```

---

## 🆘 TROUBLESHOOTING

### If AAB build fails:
1. `./gradlew clean`
2. `./gradlew bundleRelease`
3. Check `key.properties` exists
4. Check keystore password correct

### If Play Console rejects AAB:
1. Check minimum SDK (21+)
2. Check targeting API (latest)
3. Check signature certificate
4. Contact Google Play support

### If app crashes on launch:
1. Check Firebase config
2. Check AdMob App ID
3. Check network connectivity
4. Review Crashlytics logs

---

**Created:** 2026-02-02  
**Version:** 1.0  
**Status:** READY FOR SUBMISSION
