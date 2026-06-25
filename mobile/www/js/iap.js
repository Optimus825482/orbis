/**
 * ORBIS In-App Purchase (IAP) Module
 * DEPRECATED: Premium satin alma KALDIRILDI. Uygulama tamamen ucretsiz.
 * Bu modul sadece geriye uyumluluk icin korunuyor — butun metodlar no-op.
 *
 * Eski davranis: capacitor-plugin-cdv-purchase (Google Play Billing).
 * Yeni davranis: Tum premium satin alma / abonelik islemleri devre disi.
 */

const OrbisIAP = {
  // Product IDs - artik kullanilmiyor (geriye uyumluluk)
  PRODUCTS: {
    PREMIUM_MONTHLY: "astro_premium_monthly",
    PREMIUM_YEARLY: "astro_premium_yearly",
    PREMIUM_LIFETIME: "astro_premium_lifetime",
  },

  // Fiyatlar - artik kullanilmiyor
  PRICES: {
    PREMIUM_MONTHLY: "—",
    PREMIUM_YEARLY: "—",
    PREMIUM_LIFETIME: "—",
  },

  // State
  isInitialized: false,
  isPremium: false, // Her zaman false
  purchaseInProgress: false,
  _store: null,
  _Platform: null,
  _ProductType: null,

  /**
   * IAP'i baslat - artik no-op.
   * Premium satin alma kaldirildi. Sadece loglama.
   */
  async initialize() {
    if (this.isInitialized) return;
    console.info("[IAP] DEPRECATED: Premium satin alma kaldirildi. initialize() no-op.");
    this.isInitialized = true;
    this.isPremium = false; // her zaman false
  },

  /**
   * Backend'den fiyatlari cek - DEPRECATED.
   * Premium kaldirildi, fiyat gosterimi yok.
   */
  async loadPricesFromServer() {
    console.info("[IAP] loadPricesFromServer: no-op (premium kaldirildi).");
  },

  /**
   * Abonelik durumunu backend'den kontrol et - no-op.
   */
  async checkSubscriptionStatus() {
    this.isPremium = false;
  },

  async _getIdToken() {
    // DEPRECATED
    return null;
  },

  /**
   * Backend verify-purchase - artik no-op.
   */
  async _verifyWithBackend(transaction) {
    console.info("[IAP] _verifyWithBackend: no-op (premium kaldirildi).");
    return false;
  },

  /**
   * Premium satin al - artik no-op.
   */
  async purchase(productId) {
    console.info("[IAP] purchase: no-op (premium kaldirildi).", productId);
    if (typeof alert !== "undefined") {
      alert("Premium satin alma kaldirildi. Uygulama tamamen ucretsizdir.");
    }
    return { success: false, message: "Premium satin alma kaldirildi. Uygulama tamamen ucretsiz." };
  },

  /**
   * Abonelik geri yukleme - artik no-op.
   */
  async restorePurchases() {
    console.info("[IAP] restorePurchases: no-op (premium kaldirildi).");
    return { success: false, message: "Premium satin alma kaldirildi." };
  },

  /**
   * Premium durumu - her zaman false.
   */
  isPremiumUser() {
    return false;
  },
};

// Global erisim
window.OrbisIAP = OrbisIAP;

// Baslat
document.addEventListener("DOMContentLoaded", () => {
  setTimeout(() => OrbisIAP.initialize(), 2000);
});
