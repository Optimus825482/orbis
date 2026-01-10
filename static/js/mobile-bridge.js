/**
 * ORBIS Monetizasyon & Capacitor Bridge
 * Reklam, Kredi ve Premium Sistemi
 *
 * KURALLAR:
 * - Ücretsiz: İlk gün 8 (3 reklamsız + 5 reklamlı), sonra günlük 5 reklamlı
 * - Premium (₺149/ay): 150 kredi dahil, reklamsız, kredi bitince paket al
 */

const OrbisBridge = {
  // ═══════════════════════════════════════════════════════════════
  // YAPILANDIRMA
  // ═══════════════════════════════════════════════════════════════

  CONFIG: {
    // Ücretsiz kullanıcı limitleri
    FREE_FIRST_DAY_TOTAL: 8, // İlk gün toplam
    FREE_FIRST_DAY_NO_AD: 3, // İlk gün reklamsız
    FREE_DAILY_LIMIT: 5, // Sonraki günler (hepsi reklamlı)

    // Premium paketleri
    PREMIUM_PACKAGES: [
      { id: "monthly", name: "Aylık", price: 149, credits: 150, months: 1 },
      { id: "quarterly", name: "3 Aylık", price: 399, credits: 500, months: 3 },
      { id: "biannual", name: "6 Aylık", price: 750, credits: 1000, months: 6 },
      { id: "yearly", name: "Yıllık", price: 1250, credits: 2500, months: 12 },
    ],

    // Kredi paketleri (sadece premium için)
    CREDIT_PACKAGES: [
      { credits: 10, price: 35 },
      { credits: 20, price: 67 },
      { credits: 30, price: 82 },
      { credits: 40, price: 110 },
      { credits: 50, price: 135 },
    ],

    // AdMob ID'leri (Test)
    ADMOB_TEST: {
      APP_ID: "ca-app-pub-3940256099942544~3347511713",
      BANNER: "ca-app-pub-3940256099942544/6300978111",
      INTERSTITIAL: "ca-app-pub-3940256099942544/1033173712",
      REWARDED: "ca-app-pub-3940256099942544/5224354917",
    },

    // AdMob ID'leri (Production)
    ADMOB_PROD: {
      APP_ID: "ca-app-pub-244409390178357~4683309361",
      BANNER: "ca-app-pub-244409390178357/5860659669",
      INTERSTITIAL: "ca-app-pub-244409390178357/8840184408",
      REWARDED: "ca-app-pub-244409390178357/4900939398",
    },

    // Interstitial gösterim aralığı (her X analizde bir)
    INTERSTITIAL_INTERVAL: 3,

    // Test modu
    IS_TESTING: true,
  },

  // ═══════════════════════════════════════════════════════════════
  // STATE
  // ═══════════════════════════════════════════════════════════════

  state: {
    isNative: false,
    isPremium: false,
    credits: 0,
    premiumPackageId: null, // Hangi premium paketi aldı

    // Ücretsiz kullanıcı için
    installDate: null, // İlk kurulum tarihi
    todayUsage: 0, // Bugünkü kullanım
    todayAdsWatched: 0, // Bugün izlenen reklam
    lastUsageDate: null, // Son kullanım tarihi
    totalAnalyses: 0, // Toplam analiz (interstitial için)

    // Premium için
    premiumExpiry: null, // Premium bitiş tarihi
  },

  // ═══════════════════════════════════════════════════════════════
  // BAŞLATMA
  // ═══════════════════════════════════════════════════════════════

  init() {
    console.log("[ORBIS] Monetizasyon sistemi başlatılıyor...");

    // State'i yükle
    this.loadState();

    // Günlük reset kontrolü
    this.checkDailyReset();

    // Native platform kontrolü
    if (typeof Capacitor !== "undefined" && Capacitor.isNativePlatform()) {
      this.state.isNative = true;
      console.log("[ORBIS] Native platform tespit edildi");
      this.initAdMob();
    } else {
      console.log("[ORBIS] Web platform - reklamlar devre dışı");
    }

    // UI güncelle
    this.updateUI();

    console.log("[ORBIS] Durum:", this.getStatusSummary());
  },

  // ═══════════════════════════════════════════════════════════════
  // STATE YÖNETİMİ
  // ═══════════════════════════════════════════════════════════════

  loadState() {
    try {
      const saved = localStorage.getItem("orbis_monetization");
      if (saved) {
        const data = JSON.parse(saved);
        this.state = { ...this.state, ...data };
      }

      // İlk kurulum tarihi yoksa kaydet
      if (!this.state.installDate) {
        this.state.installDate = new Date().toISOString().split("T")[0];
        this.saveState();
      }
    } catch (e) {
      console.error("[ORBIS] State yükleme hatası:", e);
    }
  },

  saveState() {
    try {
      localStorage.setItem("orbis_monetization", JSON.stringify(this.state));
    } catch (e) {
      console.error("[ORBIS] State kaydetme hatası:", e);
    }
  },

  checkDailyReset() {
    const today = new Date().toISOString().split("T")[0];

    if (this.state.lastUsageDate !== today) {
      // Yeni gün - sayaçları sıfırla
      this.state.todayUsage = 0;
      this.state.todayAdsWatched = 0;
      this.state.lastUsageDate = today;
      this.saveState();
      console.log("[ORBIS] Günlük sayaçlar sıfırlandı");
    }
  },

  // ═══════════════════════════════════════════════════════════════
  // DURUM SORGULAMA
  // ═══════════════════════════════════════════════════════════════

  isFirstDay() {
    const today = new Date().toISOString().split("T")[0];
    return this.state.installDate === today;
  },

  getDailyLimit() {
    if (this.state.isPremium) {
      return Infinity; // Premium için limit yok (kredi varsa)
    }
    return this.isFirstDay()
      ? this.CONFIG.FREE_FIRST_DAY_TOTAL
      : this.CONFIG.FREE_DAILY_LIMIT;
  },

  getRemainingToday() {
    if (this.state.isPremium) {
      return this.state.credits;
    }
    return Math.max(0, this.getDailyLimit() - this.state.todayUsage);
  },

  needsAd() {
    if (this.state.isPremium) return false;
    if (!this.isFirstDay()) return true; // İlk gün değilse her zaman reklam
    return this.state.todayUsage >= this.CONFIG.FREE_FIRST_DAY_NO_AD; // İlk 3'ten sonra reklam
  },

  canAnalyze() {
    if (this.state.isPremium) {
      return this.state.credits > 0;
    }
    return this.state.todayUsage < this.getDailyLimit();
  },

  getStatusSummary() {
    return {
      isPremium: this.state.isPremium,
      credits: this.state.credits,
      isFirstDay: this.isFirstDay(),
      todayUsage: this.state.todayUsage,
      remaining: this.getRemainingToday(),
      needsAd: this.needsAd(),
    };
  },

  // ═══════════════════════════════════════════════════════════════
  // ANALİZ İSTEĞİ
  // ═══════════════════════════════════════════════════════════════

  async requestAnalysis(onSuccess, onCancel) {
    console.log("[ORBIS] Analiz isteği...");

    // Analiz yapılabilir mi kontrol et
    if (!this.canAnalyze()) {
      this.showLimitReachedModal();
      if (onCancel) onCancel();
      return;
    }

    // Premium kullanıcı
    if (this.state.isPremium) {
      this.state.credits--;
      this.state.todayUsage++;
      this.state.totalAnalyses++;
      this.saveState();
      this.updateUI();
      console.log("[ORBIS] Premium analiz, kalan kredi:", this.state.credits);
      if (onSuccess) onSuccess();
      return;
    }

    // Ücretsiz kullanıcı - reklam gerekiyor mu?
    if (this.needsAd()) {
      // Reklam izletmemiz lazım
      const adWatched = await this.showRewardedAdFlow();

      if (adWatched) {
        this.state.todayUsage++;
        this.state.todayAdsWatched++;
        this.state.totalAnalyses++;
        this.saveState();
        this.updateUI();

        // Her 3 analizde interstitial göster
        this.showInterstitialAd();

        console.log(
          "[ORBIS] Reklamlı analiz, bugünkü kullanım:",
          this.state.todayUsage
        );
        if (onSuccess) onSuccess();
      } else {
        if (onCancel) onCancel();
      }
    } else {
      // İlk gün, ilk 3 analiz - reklamsız
      this.state.todayUsage++;
      this.state.totalAnalyses++;
      this.saveState();
      this.updateUI();
      console.log(
        "[ORBIS] Ücretsiz analiz (hoşgeldin), bugünkü kullanım:",
        this.state.todayUsage
      );
      if (onSuccess) onSuccess();
    }
  },

  // ═══════════════════════════════════════════════════════════════
  // ADMOB
  // ═══════════════════════════════════════════════════════════════

  async initAdMob() {
    if (!this.state.isNative) return;

    try {
      const { AdMob } = Capacitor.Plugins;
      const adConfig = this.CONFIG.IS_TESTING
        ? this.CONFIG.ADMOB_TEST
        : this.CONFIG.ADMOB_PROD;

      await AdMob.initialize({
        initializeForTesting: this.CONFIG.IS_TESTING,
        testingDevices: [],
      });

      console.log("[ORBIS] AdMob başlatıldı");

      // Reklamları önceden yükle
      await this.loadRewardedAd();
      await this.loadInterstitialAd();

      // Premium değilse banner göster
      if (!this.state.isPremium) {
        this.showBanner();
      }
    } catch (error) {
      console.error("[ORBIS] AdMob başlatma hatası:", error);
    }
  },

  async showBanner() {
    if (!this.state.isNative || this.state.isPremium) return;

    try {
      const { AdMob } = Capacitor.Plugins;
      const adConfig = this.CONFIG.IS_TESTING
        ? this.CONFIG.ADMOB_TEST
        : this.CONFIG.ADMOB_PROD;

      await AdMob.showBanner({
        adId: adConfig.BANNER,
        adSize: "ADAPTIVE_BANNER",
        position: "BOTTOM_CENTER",
        margin: 0,
        isTesting: this.CONFIG.IS_TESTING,
      });

      document.body.style.paddingBottom = "60px";
      console.log("[ORBIS] Banner gösterildi");
    } catch (error) {
      console.error("[ORBIS] Banner hatası:", error);
    }
  },

  async hideBanner() {
    if (!this.state.isNative) return;

    try {
      const { AdMob } = Capacitor.Plugins;
      await AdMob.hideBanner();
      document.body.style.paddingBottom = "0";
    } catch (error) {
      console.error("[ORBIS] Banner gizleme hatası:", error);
    }
  },

  // Interstitial (tam ekran) reklam
  async loadInterstitialAd() {
    if (!this.state.isNative) return;

    try {
      const { AdMob } = Capacitor.Plugins;
      const adConfig = this.CONFIG.IS_TESTING
        ? this.CONFIG.ADMOB_TEST
        : this.CONFIG.ADMOB_PROD;

      await AdMob.prepareInterstitial({
        adId: adConfig.INTERSTITIAL,
        isTesting: this.CONFIG.IS_TESTING,
      });

      console.log("[ORBIS] Interstitial yüklendi");
    } catch (error) {
      console.error("[ORBIS] Interstitial yükleme hatası:", error);
    }
  },

  async showInterstitialAd() {
    if (!this.state.isNative || this.state.isPremium) return;

    // Her X analizde bir göster
    if (this.state.totalAnalyses % this.CONFIG.INTERSTITIAL_INTERVAL !== 0) {
      return;
    }

    try {
      const { AdMob } = Capacitor.Plugins;
      await AdMob.showInterstitial();
      console.log("[ORBIS] Interstitial gösterildi");

      // Yeni interstitial yükle
      this.loadInterstitialAd();
    } catch (error) {
      console.error("[ORBIS] Interstitial gösterme hatası:", error);
    }
  },

  async loadRewardedAd() {
    if (!this.state.isNative) return;

    try {
      const { AdMob } = Capacitor.Plugins;
      const adConfig = this.CONFIG.IS_TESTING
        ? this.CONFIG.ADMOB_TEST
        : this.CONFIG.ADMOB_PROD;

      await AdMob.prepareRewardVideoAd({
        adId: adConfig.REWARDED,
        isTesting: this.CONFIG.IS_TESTING,
      });

      console.log("[ORBIS] Rewarded ad yüklendi");
    } catch (error) {
      console.error("[ORBIS] Rewarded ad yükleme hatası:", error);
    }
  },

  async showRewardedAdFlow() {
    // Önce dialog göster
    const userAccepted = await this.showAdConfirmDialog();
    if (!userAccepted) return false;

    // Native değilse (web test) direkt geç
    if (!this.state.isNative) {
      console.log("[ORBIS] Web platform - reklam simüle edildi");
      return true;
    }

    // Reklamı göster
    return await this.showRewardedAd();
  },

  showAdConfirmDialog() {
    return new Promise((resolve) => {
      const remaining = this.getRemainingToday();
      const message =
        `🎬 Analiz için kısa bir reklam izlemeniz gerekiyor.\n\n` +
        `📊 Bugün kalan hakkınız: ${remaining}\n\n` +
        `💎 Premium ile reklamsız kullanın!\n\n` +
        `Devam etmek istiyor musunuz?`;

      resolve(confirm(message));
    });
  },

  async showRewardedAd() {
    return new Promise(async (resolve) => {
      try {
        const { AdMob } = Capacitor.Plugins;

        const rewardListener = AdMob.addListener(
          "onRewardedVideoAdReward",
          () => {
            console.log("[ORBIS] Ödül kazanıldı!");
            rewardListener.remove();
            resolve(true);
          }
        );

        const dismissListener = AdMob.addListener(
          "onRewardedVideoAdDismissed",
          () => {
            dismissListener.remove();
            setTimeout(() => resolve(false), 100);
          }
        );

        await AdMob.showRewardVideoAd();

        // Yeni reklam yükle
        this.loadRewardedAd();
      } catch (error) {
        console.error("[ORBIS] Rewarded ad gösterme hatası:", error);
        resolve(false);
      }
    });
  },

  // ═══════════════════════════════════════════════════════════════
  // PREMIUM & KREDİ
  // ═══════════════════════════════════════════════════════════════

  showPremiumPackages() {
    let message = `💎 ORBIS PREMIUM PAKETLERİ\n\n`;

    this.CONFIG.PREMIUM_PACKAGES.forEach((pkg, i) => {
      const perMonth = (pkg.price / pkg.months).toFixed(0);
      const perCredit = (pkg.price / pkg.credits).toFixed(2);
      message += `${i + 1}. ${pkg.name}: ₺${pkg.price}\n`;
      message += `   → ${pkg.credits} kredi (₺${perCredit}/kredi)\n`;
      message += `   → ₺${perMonth}/ay\n\n`;
    });

    message += `Satın almak için numara girin (1-${this.CONFIG.PREMIUM_PACKAGES.length}):`;

    const choice = prompt(message);
    if (choice) {
      const index = parseInt(choice) - 1;
      if (index >= 0 && index < this.CONFIG.PREMIUM_PACKAGES.length) {
        this.purchasePremium(index);
      }
    }
  },

  async purchasePremium(packageIndex = 0) {
    const pkg = this.CONFIG.PREMIUM_PACKAGES[packageIndex];
    if (!pkg) return false;

    // TODO: Gerçek In-App Purchase entegrasyonu
    const confirmed = confirm(
      `💎 ORBIS Premium - ${pkg.name}\n\n` +
        `✅ Reklamsız deneyim\n` +
        `✅ ${pkg.credits} analiz kredisi\n` +
        `✅ ${pkg.months} ay geçerlilik\n` +
        `✅ Öncelikli destek\n\n` +
        `Fiyat: ₺${pkg.price}\n\n` +
        `Satın almak istiyor musunuz?`
    );

    if (confirmed) {
      // Test için aktif et
      this.state.isPremium = true;
      this.state.premiumPackageId = pkg.id;
      this.state.credits += pkg.credits;
      this.state.premiumExpiry = new Date(
        Date.now() + pkg.months * 30 * 24 * 60 * 60 * 1000
      ).toISOString();
      this.saveState();

      // Banner'ı gizle
      this.hideBanner();

      this.updateUI();
      alert(
        `🎉 Premium aktivasyonu başarılı!\n\n` +
          `📦 Paket: ${pkg.name}\n` +
          `🎫 ${pkg.credits} kredi hesabınıza eklendi.\n` +
          `📅 Geçerlilik: ${pkg.months} ay`
      );
      return true;
    }

    return false;
  },

  async purchaseCredits(packageIndex) {
    if (!this.state.isPremium) {
      alert("❌ Kredi satın almak için Premium üye olmanız gerekiyor.");
      this.showPremiumPackages();
      return false;
    }

    const pkg = this.CONFIG.CREDIT_PACKAGES[packageIndex];
    if (!pkg) return false;

    // TODO: Gerçek In-App Purchase entegrasyonu
    const confirmed = confirm(
      `🎫 Kredi Paketi\n\n` +
        `${pkg.credits} Kredi = ₺${pkg.price}\n` +
        `(Birim fiyat: ₺${(pkg.price / pkg.credits).toFixed(2)})\n\n` +
        `Satın almak istiyor musunuz?`
    );

    if (confirmed) {
      this.state.credits += pkg.credits;
      this.saveState();
      this.updateUI();
      alert(
        `🎉 ${pkg.credits} kredi hesabınıza eklendi!\n\nToplam: ${this.state.credits} kredi`
      );
      return true;
    }

    return false;
  },

  showCreditPackages() {
    if (!this.state.isPremium) {
      this.showPremiumPromo();
      return;
    }

    let message = `🎫 KREDİ PAKETLERİ\n\nMevcut krediniz: ${this.state.credits}\n\n`;

    this.CONFIG.CREDIT_PACKAGES.forEach((pkg, i) => {
      const unitPrice = (pkg.price / pkg.credits).toFixed(2);
      message += `${i + 1}. ${pkg.credits} Kredi = ₺${
        pkg.price
      } (₺${unitPrice}/adet)\n`;
    });

    message += `\nSatın almak için numara girin (1-${this.CONFIG.CREDIT_PACKAGES.length}):`;

    const choice = prompt(message);
    if (choice) {
      const index = parseInt(choice) - 1;
      if (index >= 0 && index < this.CONFIG.CREDIT_PACKAGES.length) {
        this.purchaseCredits(index);
      }
    }
  },

  // ═══════════════════════════════════════════════════════════════
  // UI & MODALS
  // ═══════════════════════════════════════════════════════════════

  showLimitReachedModal() {
    if (this.state.isPremium) {
      // Premium ama kredi bitti
      const buyMore = confirm(
        `😔 Krediniz bitti!\n\n` +
          `Daha fazla analiz için kredi satın alın.\n\n` +
          `Kredi paketlerini görmek ister misiniz?`
      );

      if (buyMore) {
        this.showCreditPackages();
      }
    } else {
      // Ücretsiz kullanıcı limit doldu
      const goPremium = confirm(
        `⏰ Günlük limitiniz doldu!\n\n` +
          `Bugün ${this.state.todayUsage} analiz yaptınız.\n\n` +
          `💎 Premium ile sınırsız analiz yapın!\n` +
          `• 150 kredi dahil\n` +
          `• Reklamsız deneyim\n` +
          `• Sadece ₺${this.CONFIG.PREMIUM_MONTHLY_PRICE}/ay\n\n` +
          `Premium'a geçmek ister misiniz?`
      );

      if (goPremium) {
        this.purchasePremium();
      }
    }
  },

  showPremiumPromo() {
    const goPremium = confirm(
      `💎 ORBIS Premium\n\n` +
        `✅ ${this.CONFIG.PREMIUM_INCLUDED_CREDITS} analiz kredisi\n` +
        `✅ Reklamsız deneyim\n` +
        `✅ Kredi paketleri satın alabilme\n` +
        `✅ Öncelikli destek\n\n` +
        `Sadece ₺${this.CONFIG.PREMIUM_MONTHLY_PRICE}/ay\n\n` +
        `Premium'a geçmek ister misiniz?`
    );

    if (goPremium) {
      this.purchasePremium();
    }
  },

  updateUI() {
    // Status bar güncelle (varsa)
    const statusEl = document.getElementById("orbis-status");
    if (statusEl) {
      if (this.state.isPremium) {
        statusEl.innerHTML = `💎 Premium | ${this.state.credits} Kredi`;
      } else {
        const remaining = this.getRemainingToday();
        statusEl.innerHTML = `🆓 Ücretsiz | Bugün: ${remaining} hak`;
      }
    }

    // Premium badge (varsa)
    const premiumBadge = document.getElementById("premium-badge");
    if (premiumBadge) {
      premiumBadge.style.display = this.state.isPremium ? "flex" : "none";
    }
  },

  // ═══════════════════════════════════════════════════════════════
  // TEST & DEBUG
  // ═══════════════════════════════════════════════════════════════

  resetAll() {
    if (confirm("⚠️ Tüm veriler sıfırlanacak. Emin misiniz?")) {
      localStorage.removeItem("orbis_monetization");
      location.reload();
    }
  },

  /**
   * Firebase çıkış yapıldığında local state'e dön
   */
  resetToLocal() {
    console.log("[ORBIS] Firebase çıkış - local state'e dönülüyor");

    // Local storage'dan yükle
    this.loadState();

    // UI güncelle
    this.updateUI();

    // Premium değilse banner göster
    if (!this.state.isPremium && this.state.isNative) {
      this.showBanner();
    }
  },

  addTestCredits(amount = 10) {
    this.state.credits += amount;
    this.saveState();
    this.updateUI();
    console.log(
      `[ORBIS] Test: ${amount} kredi eklendi. Toplam: ${this.state.credits}`
    );
  },

  simulateNewDay() {
    this.state.lastUsageDate = "2000-01-01";
    this.checkDailyReset();
    console.log("[ORBIS] Test: Yeni gün simüle edildi");
  },
};

// Global erişim
window.OrbisBridge = OrbisBridge;

// Sayfa yüklendiğinde başlat
document.addEventListener("DOMContentLoaded", () => {
  OrbisBridge.init();
});
