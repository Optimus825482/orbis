# ORBIS Mobile Assets

Bu klasöre aşağıdaki dosyaları ekleyin:

## Gerekli Dosyalar

### 1. logo.png

- Boyut: 512x512 px
- Format: PNG (şeffaf arka plan)
- Kullanım: Splash screen, app icon

### 2. splash.png

- Boyut: 2732x2732 px (en büyük iPad için)
- Format: PNG
- Kullanım: Splash screen arka planı

### 3. icon.png

- Boyut: 1024x1024 px
- Format: PNG
- Kullanım: App Store / Play Store ikonu

## Android Specific

Android için ikonlar `android/app/src/main/res/` altında otomatik oluşturulur.

Capacitor ile ikon oluşturmak için:

```bash
npm install -g @capacitor/assets
npx capacitor-assets generate
```

## Mevcut ORBIS Assets

Ana projeden kopyalayabileceğiniz dosyalar:

- `../static/ai-avatar-R.png` → logo.png olarak kullanılabilir
- `../static/all-icons/Android/Icon-512.png` → icon.png
