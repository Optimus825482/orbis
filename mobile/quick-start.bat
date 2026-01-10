@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║         ORBIS Mobile - Quick Start Script                ║
echo ║         Capacitor + AdMob Android Build                  ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

:: Renk kodları için
setlocal enabledelayedexpansion

:: 1. Node.js kontrolü
echo [1/6] Node.js kontrolü...
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [X] HATA: Node.js bulunamadı!
    echo     https://nodejs.org adresinden yükleyin.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set NODE_VER=%%i
echo [✓] Node.js: %NODE_VER%
echo.

:: 2. npm install
echo [2/6] Bağımlılıklar yükleniyor...
if not exist "node_modules" (
    call npm install
    if %ERRORLEVEL% NEQ 0 (
        echo [X] npm install başarısız!
        pause
        exit /b 1
    )
) else (
    echo [✓] node_modules zaten mevcut
)
echo.

:: 3. Android platform kontrolü
echo [3/6] Android platformu kontrol ediliyor...
if not exist "android" (
    echo     Android platformu ekleniyor...
    call npx cap add android
    if %ERRORLEVEL% NEQ 0 (
        echo [X] cap add android başarısız!
        pause
        exit /b 1
    )
) else (
    echo [✓] Android platformu mevcut
)
echo.

:: 4. Config dosyalarını kopyala
echo [4/6] Yapılandırma dosyaları kontrol ediliyor...
if exist "android-config\colors.xml" (
    if not exist "android\app\src\main\res\values\colors.xml" (
        echo     colors.xml kopyalanıyor...
        copy "android-config\colors.xml" "android\app\src\main\res\values\colors.xml" >nul
    )
)
if exist "android-config\strings.xml" (
    echo     strings.xml güncelleniyor...
    copy "android-config\strings.xml" "android\app\src\main\res\values\strings.xml" >nul
)
echo [✓] Yapılandırma dosyaları hazır
echo.

:: 5. Capacitor sync
echo [5/6] Capacitor sync yapılıyor...
call npx cap sync android
if %ERRORLEVEL% NEQ 0 (
    echo [!] Sync uyarısı - devam ediliyor...
)
echo [✓] Sync tamamlandı
echo.

:: 6. Sonuç
echo [6/6] Kurulum tamamlandı!
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                    SONRAKİ ADIMLAR                       ║
echo ╠══════════════════════════════════════════════════════════╣
echo ║                                                          ║
echo ║  1. Android Studio'da aç:                                ║
echo ║     npx cap open android                                 ║
echo ║                                                          ║
echo ║  2. AdMob ID'lerini güncelle:                            ║
echo ║     - android/app/src/main/AndroidManifest.xml           ║
echo ║     - www/js/admob.js                                    ║
echo ║                                                          ║
echo ║  3. Web URL'i güncelle:                                  ║
echo ║     - www/js/app.js → WEB_APP_URL                        ║
echo ║                                                          ║
echo ║  4. Emulator veya cihazda test et                        ║
echo ║                                                          ║
echo ║  5. Release build al:                                    ║
echo ║     cd android && gradlew bundleRelease                  ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

:: Android Studio'yu açmak ister misin?
set /p OPEN_STUDIO="Android Studio'yu şimdi açmak ister misin? (E/H): "
if /i "%OPEN_STUDIO%"=="E" (
    echo.
    echo Android Studio açılıyor...
    call npx cap open android
)

echo.
pause
