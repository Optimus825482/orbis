@echo off
echo ========================================
echo   ORBIS Mobile Setup Script (Windows)
echo ========================================
echo.

:: Node.js kontrolü
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [HATA] Node.js bulunamadi!
    echo Lutfen https://nodejs.org adresinden yukleyin.
    pause
    exit /b 1
)

echo [1/5] Node.js version:
node --version
echo.

:: Bağımlılıkları yükle
echo [2/5] Bagimliliklar yukleniyor...
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo [HATA] npm install basarisiz!
    pause
    exit /b 1
)
echo.

:: Capacitor sync
echo [3/5] Capacitor sync yapiliyor...
call npx cap sync
echo.

:: Android kontrolü
echo [4/5] Android SDK kontrolu...
if defined ANDROID_HOME (
    echo ANDROID_HOME: %ANDROID_HOME%
) else (
    echo [UYARI] ANDROID_HOME ayarlanmamis!
    echo Android Studio'yu yukleyin ve SDK path'i ayarlayin.
)
echo.

:: Tamamlandı
echo [5/5] Kurulum tamamlandi!
echo.
echo ========================================
echo   Sonraki Adimlar:
echo ========================================
echo.
echo 1. Android Studio'yu acin:
echo    npx cap open android
echo.
echo 2. AdMob ID'lerini guncelleyin:
echo    - www/js/admob.js
echo    - android/app/src/main/AndroidManifest.xml
echo.
echo 3. Web App URL'ini guncelleyin:
echo    - www/js/app.js (WEB_APP_URL)
echo.
echo 4. Build alin:
echo    cd android ^&^& gradlew assembleDebug
echo.
echo ========================================
pause
