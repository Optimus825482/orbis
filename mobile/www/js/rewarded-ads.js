/**
 * ORBIS Rewarded Ads System
 * Analiz ve AI yorum için rewarded ad gösterimi
 */

const OrbisRewardedAds = {
  isInitialized: false,
  isAdReady: false,
  currentRewardCallback: null,
  AdMob: null, // AdMob plugin referansı

  /**
   * AdMob plugin'ini al
   */
  getAdMob() {
    if (this.AdMob) return this.AdMob;
    
    // Native ortamda Capacitor.Plugins.AdMob kullan
    if (typeof Capacitor !== 'undefined' && Capacitor.Plugins && Capacitor.Plugins.AdMob) {
      this.AdMob = Capacitor.Plugins.AdMob;
      return this.AdMob;
    }
    
    // Global AdMob varsa (ES module import)
    if (typeof AdMob !== 'undefined') {
      this.AdMob = AdMob;
      return this.AdMob;
    }
    
    return null;
  },

  /**
   * Rewarded ad sistemini başlat
   */
  async init() {
    if (this.isInitialized) {
      console.log("[RewardedAds] ⚠️ Already initialized");
      return;
    }

    try {
      console.log("[RewardedAds] 🚀 Initializing...");
      
      const adMob = this.getAdMob();
      console.log("[RewardedAds] 🔍 AdMob available:", adMob !== null);

      if (!adMob) {
        console.warn("[RewardedAds] ❌ AdMob not available (web environment)");
        return;
      }

      // Rewarded ad hazırla
      await this.prepareRewardedAd();

      this.isInitialized = true;
      console.log("[RewardedAds] ✅ Initialized successfully");
    } catch (error) {
      console.error("[RewardedAds] ❌ Init error:", error);
    }
  },

  /**
   * Rewarded ad hazırla
   */
  async prepareRewardedAd() {
    const adMob = this.getAdMob();
    if (!adMob) return;
    
    try {
      console.log("[RewardedAds] 📦 Preparing rewarded ad...");
      // Ödüllü Video (Rewarded) - Analiz ve AI yorum için
      const adUnitId = "ca-app-pub-2444093901783574/9994253824";

      await adMob.prepareRewardVideoAd({
        adId: adUnitId,
        isTesting: false,
      });

      this.isAdReady = true;
      console.log("[RewardedAds] ✅ Ad prepared and ready");
    } catch (error) {
      console.error("[RewardedAds] ❌ Prepare error:", error);
      this.isAdReady = false;
    }
  },

  /**
   * Rewarded ad göster ve ödül bekle
   * @param {string} purpose - 'analysis' veya 'interpretation'
   * @returns {Promise<boolean>} Ödül kazanıldı mı
   */
  async showRewardedAd(purpose = "analysis") {
    console.log(`[RewardedAds] 🎬 showRewardedAd called for: ${purpose}`);
    console.log(`[RewardedAds] 🔍 isAdReady: ${this.isAdReady}`);

    const adMob = this.getAdMob();
    if (!adMob) {
      console.warn("[RewardedAds] ⚠️ AdMob not available - allowing action");
      return true;
    }

    return new Promise(async (resolve) => {
      try {
        if (!this.isAdReady) {
          console.warn("[RewardedAds] ⚠️ Ad not ready, preparing...");
          await this.prepareRewardedAd();

          if (!this.isAdReady) {
            console.error(
              "[RewardedAds] ❌ Could not prepare ad - fallback to allow",
            );
            // Fallback: Reklam gösterilemezse izin ver (test için)
            resolve(true);
            return;
          }
        }

        console.log("[RewardedAds] ✅ Ad ready, setting up callbacks...");

        // Ödül callback'i ayarla
        this.currentRewardCallback = (rewarded) => {
          console.log(
            `[RewardedAds] 🎁 Reward ${rewarded ? "earned ✅" : "not earned ❌"} for ${purpose}`,
          );
          resolve(rewarded);

          // Yeni reklam hazırla
          setTimeout(() => {
            console.log("[RewardedAds] 📦 Preparing next ad...");
            this.prepareRewardedAd();
          }, 1000);
        };

        // Event listener'ları ekle
        adMob.addListener("onRewardedVideoAdRewarded", () => {
          console.log("[RewardedAds] 🎉 Event: onRewardedVideoAdRewarded");
          if (this.currentRewardCallback) {
            this.currentRewardCallback(true);
            this.currentRewardCallback = null;
          }
        });

        adMob.addListener("onRewardedVideoAdClosed", () => {
          console.log("[RewardedAds] 🚪 Event: onRewardedVideoAdClosed");
          if (this.currentRewardCallback) {
            this.currentRewardCallback(false);
            this.currentRewardCallback = null;
          }
        });

        adMob.addListener("onRewardedVideoAdFailedToLoad", () => {
          console.error(
            "[RewardedAds] ❌ Event: onRewardedVideoAdFailedToLoad",
          );
          if (this.currentRewardCallback) {
            // Fallback: Reklam yüklenemezse izin ver
            this.currentRewardCallback(true);
            this.currentRewardCallback = null;
          }
        });

        // Reklamı göster
        console.log("[RewardedAds] 🎬 Showing ad now...");
        await adMob.showRewardVideoAd();
        this.isAdReady = false;
        console.log("[RewardedAds] ✅ Ad shown, waiting for result...");
      } catch (error) {
        console.error("[RewardedAds] ❌ Show error:", error);
        // Fallback: Hata durumunda izin ver
        resolve(true);
      }
    });
  },

  /**
   * Analiz için rewarded ad göster
   */
  async showForAnalysis() {
    console.log("[RewardedAds] 📊 showForAnalysis called");
    return await this.showRewardedAd("analysis");
  },

  /**
   * AI yorum için rewarded ad göster
   */
  async showForInterpretation() {
    console.log("[RewardedAds] 💬 showForInterpretation called");
    return await this.showRewardedAd("interpretation");
  },
};

// Global erişim
window.OrbisRewardedAds = OrbisRewardedAds;

// Başlat
document.addEventListener("DOMContentLoaded", () => {
  console.log("[RewardedAds] 🚀 DOMContentLoaded - Starting initialization...");
  OrbisRewardedAds.init();
  console.log(
    "[RewardedAds] 🔍 window.OrbisRewardedAds:",
    window.OrbisRewardedAds,
  );
});
