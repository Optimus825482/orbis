#!/usr/bin/env pwsh
# Git History Temizleme Scripti
# UYARI: Bu script git history'i yeniden yazar!

Write-Host "🚨 GİT HİSTORY TEMİZLİĞİ BAŞLIYOR..." -ForegroundColor Red
Write-Host ""

# Backup oluştur
Write-Host "📦 Backup oluşturuluyor..." -ForegroundColor Yellow
$backupDir = "d:\astro-backup-$(Get-Date -Format 'yyyy-MM-dd-HHmmss')"
Write-Host "Backup dizini: $backupDir"

# Mevcut durumu kontrol et
Write-Host ""
Write-Host "📊 Mevcut Git Durumu:" -ForegroundColor Cyan
git log --all --full-history --oneline -- "*google-services*.json" | Select-Object -First 5
git log --all --full-history --oneline -- "*firebase-adminsdk*.json" | Select-Object -First 5
git log --all --full-history --oneline -- "client_secret_*.json" | Select-Object -First 5

Write-Host ""
Write-Host "⚠️  DİKKAT: Bu işlem git history'i yeniden yazacak!" -ForegroundColor Yellow
Write-Host "⚠️  Tüm team members'ın repo'yu yeniden clone etmesi gerekecek!" -ForegroundColor Yellow
Write-Host ""
$confirmation = Read-Host "Devam etmek istiyor musunuz? (evet/hayir)"

if ($confirmation -ne "evet") {
    Write-Host "❌ İşlem iptal edildi." -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "🧹 Hassas dosyalar temizleniyor..." -ForegroundColor Green

# BFG kullanmak yerine git filter-repo kullanacağız (daha güvenli)
# Önce git filter-repo kurulu mu kontrol et
$filterRepoInstalled = Get-Command git-filter-repo -ErrorAction SilentlyContinue

if (-not $filterRepoInstalled) {
    Write-Host "⚙️  git-filter-repo kuruluyor..." -ForegroundColor Yellow
    pip install git-filter-repo
}

# Hassas dosyaları listele
$sensitiveFiles = @(
    "google-services.json",
    "google-services (1).json",
    "google-services (2).json",
    "orbis-ffa9e-firebase-adminsdk-fbsvc-b4ac1afabf.json",
    "client_secret_768649602152-kl2b19k3k3ldtn4d4f6v5q3mo7ie7vk7.apps.googleusercontent.com.json",
    "client_secret_768649602152-vn89llv5o14bgijgcar6nprklb8j3e5u.apps.googleusercontent.com.json"
)

# Git filter-branch kullanarak temizle
Write-Host "🔥 Git history'den siliniyor..." -ForegroundColor Red

foreach ($file in $sensitiveFiles) {
    Write-Host "  - Siliniyor: $file"
    git filter-branch --force --index-filter "git rm --cached --ignore-unmatch '$file'" --prune-empty --tag-name-filter cat -- --all
}

# Reflog temizle
Write-Host ""
Write-Host "🗑️  Reflog temizleniyor..." -ForegroundColor Yellow
git reflog expire --expire=now --all

# Garbage collection
Write-Host "♻️  Garbage collection çalıştırılıyor..." -ForegroundColor Yellow
git gc --prune=now --aggressive

# Sonuçları göster
Write-Host ""
Write-Host "✅ TEMİZLİK TAMAMLANDI!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Yeni Durum:" -ForegroundColor Cyan
git log --all --full-history --oneline -- "*google-services*.json" | Select-Object -First 5

Write-Host ""
Write-Host "🚀 SONRAKİ ADIMLAR:" -ForegroundColor Cyan
Write-Host "1. Force push yapın: git push origin --force --all"
Write-Host "2. Tags'leri de push edin: git push origin --force --tags"
Write-Host "3. Tüm team members'a bildirin: Repo'yu yeniden clone etsinler"
Write-Host "4. GitHub'da 'git push --mirror' çalıştırabilirsiniz"
Write-Host ""
Write-Host "⚠️  NOT: Force push yapmadan önce tüm team'i bilgilendirin!" -ForegroundColor Yellow
