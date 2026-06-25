/**
 * ORBIS AdMob Integration
 * Banner, Interstitial ve Rewarded Ad yönetimi
 * Admin kullanıcılara reklam gösterilmez
 */

const OrbisAds = {
  // Ad Unit IDs — tek kaynak window.ADMOB_CONFIG (static/js/admob-config.js).
  // Mobile webview bu dosyayı da yüklemeli; yüklenmezse fallback hardcoded.
  AD_UNITS: (window.ADMOB_CONFIG && {
    BANNER: window.ADMOB_CONFIG.bannerId,
    INTERSTITIAL: window.ADMOB_CONFIG.interstitialId,
    REWARDED_INTERSTITIAL: window.ADMOB_CONFIG.rewardedInterstitialId,
    REWARDED_ANALYSIS: window.ADMOB_CONFIG.rewardedAnalysisId,
  }) || {
    BANNER: "ca-app-pub-2444093901783574/1791137239",
    INTERSTITIAL: "ca-app-pub-2444093901783574/8681172156",
    REWARDED_INTERSTITIAL: "ca-app-pub-2444093901783574/9994253824",
    REWARDED_ANALYSIS: "ca-app-pub-2444093901783574/3701964485",
  },

  // App ID — tek kaynak window.ADMOB_CONFIG
  APP_ID: (window.ADMOB_CONFIG && window.ADMOB_CONFIG.appId) || "ca-app-pub-2444093901783574~9279937953",

  // State
  isInitialized: false,
  interstitialLoaded: false,
  rewardedLoaded: false,
  interstitialShowCount: 0,

  // Admin/Premium kontrolü - reklam gösterilmeyecek kullanıcılar
  showAds: true, // Varsayılan: reklam göster
  isAdmin: false,
  isPremium: false,

  /**
   * Kullanıcının reklam durumunu kontrol et
   * @param {string} deviceId - Cihaz ID
   * @param {string} email - Kullanıcı email (Firebase auth'dan)
   */
  async checkAdStatus(deviceId, email) {
    try {
      const response = await fetch(
        "https://app.orbisastro.online/api/monetization/check-usage",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ device_id: deviceId, email: email }),
        },
      );

      if (response.ok) {
        const data = await response.json();
        this.showAds = data.usage?.show_ads !== false;
        this.isAdmin = data.usage?.is_admin === true;
        // Premium kaldirildi: her zaman false
        this.isPremium = false;

        console.log(
          `[AdMob] Ad status - showAds: ${this.showAds}, isAdmin: ${this.isAdmin}, isPremium: ${this.isPremium}`,
        );

        // Admin ise banner'ı gizle
        if (!this.showAds) {
          this.hideBanner();
        }
      }
    } catch (error) {
      console.error("[AdMob] Check ad status error:", error);
      // Hata durumunda varsayılan olarak reklam göster
      this.showAds = true;
    }
  },

  /**
   * AdMob'u başlat
   *
   * ⚠️ KRİTİK: Bu çağrı zorunlu. Yapılmadan prepare/show sessizce başarısız olur
   * → AdMob panelinde "0 istek" gözükür.
   * initializeForTesting:true olursa test reklam yüklenir (NO_FILL);
   * false olursa gerçek reklam yüklenir (production).
   */
  async initialize() {
    if (this.isInitialized) return;

    try {
      // Capacitor AdMob plugin kontrolü
      if (typeof Capacitor === "undefined" || !Capacitor.Plugins.AdMob) {
        console.log("[AdMob] Plugin not available - running in browser?");
        return;
      }

      const { AdMob } = Capacitor.Plugins;

      // AppId sanity check — AndroidManifest'te tanımlı olmalı
      if (!this.APP_ID || !this.APP_ID.startsWith("ca-app-pub-")) {
        console.error("[AdMob] ❌ Geçersiz APP_ID:", this.APP_ID);
        return;
      }

      // AdMob'u initialize et — requestTrackingAuthorization ayrı method
      // (v6 plugin API'si). initializeForTesting:false = production reklam.
      await AdMob.initialize({
        initializeForTesting: false,
        // Çocuk yönelimli değiliz (TR mevzuatı)
        tagForChildDirectedTreatment: false,
        tagForUnderAgeOfConsent: false,
      });

      this.isInitialized = true;
      console.log("[AdMob] ✅ Initialized successfully (appId=" + this.APP_ID + ")");

      // iOS 14+ ATT (App Tracking Transparency) — ayrı method, Android silent.
      try {
        if (typeof AdMob.trackingAuthorizationStatus === "function") {
          const tracking = await AdMob.trackingAuthorizationStatus();
          if (tracking?.status === "notDetermined" && typeof AdMob.requestTrackingAuthorization === "function") {
            await AdMob.requestTrackingAuthorization();
          }
        }
      } catch (e) {
        // iOS dışı platform — silent ignore
      }

      // GDPR/KVKK consent sorgula
      try {
        if (typeof AdMob.requestConsentInfo === "function") {
          const consent = await AdMob.requestConsentInfo({});
          console.log("[AdMob] Consent status:", consent?.status);
          this._consentStatus = consent?.status || "UNKNOWN";
        }
      } catch (e) {
        console.log("[AdMob] Consent info atlandı:", e?.message || e);
        this._consentStatus = "UNKNOWN";
      }

      // Event listeners
      this.setupEventListeners();

      // İlk reklamları yükle
      await this.loadInterstitial();
      await this.loadRewarded();
    } catch (error) {
      console.error("[AdMob] Initialization failed:", error);
    }
  },

  /**
   * Event listener'ları kur
   */
  setupEventListeners() {
    const { AdMob } = Capacitor.Plugins;

    // Interstitial events
    AdMob.addListener("onInterstitialAdLoaded", () => {
      console.log("[AdMob] Interstitial loaded");
      this.interstitialLoaded = true;
    });

    AdMob.addListener("onInterstitialAdFailedToLoad", (error) => {
      console.error("[AdMob] Interstitial failed to load:", error);
      this.interstitialLoaded = false;
      // 30 saniye sonra tekrar dene
      setTimeout(() => this.loadInterstitial(), 30000);
    });

    AdMob.addListener("onInterstitialAdDismissed", () => {
      console.log("[AdMob] Interstitial dismissed");
      this.interstitialLoaded = false;
      this.loadInterstitial(); // Yeni reklam yükle
    });

    // Rewarded events
    AdMob.addListener("onRewardedVideoAdLoaded", () => {
      console.log("[AdMob] Rewarded loaded");
      this.rewardedLoaded = true;
    });

    AdMob.addListener("onRewardedVideoAdFailedToLoad", (error) => {
      console.error("[AdMob] Rewarded failed to load:", error);
      this.rewardedLoaded = false;
      setTimeout(() => this.loadRewarded(), 30000);
    });

    AdMob.addListener("onRewardedVideoAdDismissed", () => {
      console.log("[AdMob] Rewarded dismissed");
      this.rewardedLoaded = false;
      this.loadRewarded();
    });
  },

  /**
   * Banner reklam göster
   * @param {string} position - 'TOP' veya 'BOTTOM'
   */
  async showBanner(position = "BOTTOM") {
    // Admin veya premium kullanıcıya reklam gösterme
    if (!this.showAds) {
      console.log("[AdMob] Ads disabled for this user (admin/premium)");
      return;
    }

    if (!this.isInitialized) {
      console.log("[AdMob] Not initialized");
      return;
    }

    try {
      const { AdMob } = Capacitor.Plugins;

      await AdMob.showBanner({
        adId: this.AD_UNITS.BANNER,
        adSize: "ADAPTIVE_BANNER",
        position: position === "TOP" ? "TOP_CENTER" : "BOTTOM_CENTER",
        margin: 0,
        isTesting: false, // Production mode
      });

      console.log("[AdMob] Banner shown");

      // Banner için padding ekle (banner 60px + bottom nav 80px = 140px)
      // Bottom nav'ın banner ile örtüşmemesi için extra padding
      if (position === "BOTTOM") {
        document.body.style.paddingBottom = "140px";
        // Bottom nav'ı da yukarı kaydır
        const bottomNav = document.querySelector("nav.fixed.bottom-0");
        if (bottomNav) {
          bottomNav.style.bottom = "60px";
        }
      } else {
        document.body.style.paddingTop = "60px";
      }
    } catch (error) {
      console.error("[AdMob] Banner error:", error);
    }
  },

  /**
   * Banner reklamı gizle
   */
  async hideBanner() {
    if (!this.isInitialized) return;

    try {
      const { AdMob } = Capacitor.Plugins;
      await AdMob.hideBanner();
      document.body.style.paddingBottom = "0";
      document.body.style.paddingTop = "0";

      // Bottom nav'ı eski konumuna döndür
      const bottomNav = document.querySelector("nav.fixed.bottom-0");
      if (bottomNav) {
        bottomNav.style.bottom = "0";
      }
    } catch (error) {
      console.error("[AdMob] Hide banner error:", error);
    }
  },

  /**
   * Interstitial reklam yükle
   */
  async loadInterstitial() {
    if (!this.isInitialized) return;

    try {
      const { AdMob } = Capacitor.Plugins;

      await AdMob.prepareInterstitial({
        adId: this.AD_UNITS.INTERSTITIAL,
        isTesting: false, // Production mode
      });
    } catch (error) {
      console.error("[AdMob] Load interstitial error:", error);
    }
  },

  /**
   * Interstitial reklam göster
   * AGRESIF MOD: Her işlemde göster (Premium'a teşvik için)
   */
  async showInterstitial(force = false) {
    // Admin veya premium kullanıcıya reklam gösterme
    if (!this.showAds) {
      console.log("[AdMob] Ads disabled for this user (admin/premium)");
      return false;
    }

    if (!this.isInitialized || !this.interstitialLoaded) {
      console.log("[AdMob] Interstitial not ready");
      return false;
    }

    // AGRESIF MOD: Her seferinde göster (force değilse bile)
    this.interstitialShowCount++;
    console.log(
      "[AdMob] Showing interstitial, count:",
      this.interstitialShowCount,
    );

    try {
      const { AdMob } = Capacitor.Plugins;
      await AdMob.showInterstitial();
      return true;
    } catch (error) {
      console.error("[AdMob] Show interstitial error:", error);
      return false;
    }
  },

  /**
   * Rewarded Video reklam yükle (Analiz için)
   */
  async loadRewarded() {
    if (!this.isInitialized) return;

    try {
      const { AdMob } = Capacitor.Plugins;

      await AdMob.prepareRewardVideoAd({
        adId: this.AD_UNITS.REWARDED_ANALYSIS,  // Rewarded Video ID kullan
        isTesting: false, // Production mode
      });

      this.rewardedLoaded = true;
      console.log("[AdMob] Rewarded loaded successfully");
    } catch (error) {
      console.error("[AdMob] Load rewarded error:", error);
      this.rewardedLoaded = false;
    }
  },

  /**
   * Rewarded reklam göster
   * @returns {Promise<boolean>} Ödül kazanıldı mı
   */
  async showRewarded() {
    // Admin veya premium kullanıcıya reklam gösterme - direkt ödül ver
    if (!this.showAds) {
      console.log(
        "[AdMob] Ads disabled for this user (admin/premium) - granting reward",
      );
      return true; // Admin/premium için direkt ödül ver
    }

    if (!this.isInitialized || !this.rewardedLoaded) {
      console.log("[AdMob] Rewarded not ready");
      return false;
    }

    return new Promise(async (resolve) => {
      try {
        const { AdMob } = Capacitor.Plugins;

        // Ödül event'ini dinle
        const rewardListener = AdMob.addListener(
          "onRewardedVideoAdReward",
          (reward) => {
            console.log("[AdMob] Reward earned:", reward);
            rewardListener.remove();
            resolve(true);
          },
        );

        // Kapatma event'ini dinle (ödül almadan)
        const dismissListener = AdMob.addListener(
          "onRewardedVideoAdDismissed",
          () => {
            dismissListener.remove();
            // Eğer reward gelmemişse false döndür
            setTimeout(() => resolve(false), 100);
          },
        );

        await AdMob.showRewardVideoAd();
      } catch (error) {
        console.error("[AdMob] Show rewarded error:", error);
        resolve(false);
      }
    });
  },

  /**
   * Rewarded reklam hazır mı?
   */
  isRewardedReady() {
    return this.isInitialized && this.rewardedLoaded;
  },
};

// Export for global access
window.OrbisAds = OrbisAds;

// Auto-initialize when Capacitor is ready
document.addEventListener("DOMContentLoaded", () => {
  // AdMob'u başlat
  if (typeof Capacitor !== "undefined" && Capacitor.isNativePlatform()) {
    setTimeout(() => {
      OrbisAds.initialize();
    }, 2000); // Uygulama yüklendikten 2 saniye sonra
  }
});
