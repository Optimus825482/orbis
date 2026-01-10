/**
 * Capacitor Runtime Stub
 * Bu dosya build sırasında gerçek Capacitor runtime ile değiştirilir
 * Development/browser ortamında fallback sağlar
 */

if (typeof Capacitor === "undefined") {
  console.log("[Capacitor] Running in browser mode - using stubs");

  window.Capacitor = {
    isNativePlatform: () => false,
    getPlatform: () => "web",
    Plugins: {
      // Stub plugins for browser testing
      App: {
        addListener: (event, callback) => {
          console.log("[Capacitor Stub] App.addListener:", event);
          return { remove: () => {} };
        },
        exitApp: () => console.log("[Capacitor Stub] App.exitApp"),
      },
      SplashScreen: {
        hide: () => {
          console.log("[Capacitor Stub] SplashScreen.hide");
          return Promise.resolve();
        },
        show: () => {
          console.log("[Capacitor Stub] SplashScreen.show");
          return Promise.resolve();
        },
      },
      StatusBar: {
        setStyle: (options) => {
          console.log("[Capacitor Stub] StatusBar.setStyle:", options);
          return Promise.resolve();
        },
        setBackgroundColor: (options) => {
          console.log(
            "[Capacitor Stub] StatusBar.setBackgroundColor:",
            options
          );
          return Promise.resolve();
        },
      },
      AdMob: {
        initialize: (options) => {
          console.log("[Capacitor Stub] AdMob.initialize:", options);
          return Promise.resolve();
        },
        showBanner: (options) => {
          console.log("[Capacitor Stub] AdMob.showBanner:", options);
          // Show placeholder banner
          const banner = document.getElementById("banner-ad");
          if (banner) {
            banner.style.display = "flex";
            banner.innerHTML = "📢 Test Banner Ad";
          }
          return Promise.resolve();
        },
        hideBanner: () => {
          console.log("[Capacitor Stub] AdMob.hideBanner");
          const banner = document.getElementById("banner-ad");
          if (banner) banner.style.display = "none";
          return Promise.resolve();
        },
        prepareInterstitial: (options) => {
          console.log("[Capacitor Stub] AdMob.prepareInterstitial:", options);
          return Promise.resolve();
        },
        showInterstitial: () => {
          console.log("[Capacitor Stub] AdMob.showInterstitial");
          alert("🎬 Interstitial Ad (Test Mode)");
          return Promise.resolve();
        },
        prepareRewardVideoAd: (options) => {
          console.log("[Capacitor Stub] AdMob.prepareRewardVideoAd:", options);
          return Promise.resolve();
        },
        showRewardVideoAd: () => {
          console.log("[Capacitor Stub] AdMob.showRewardVideoAd");
          const watched = confirm(
            "🎁 Rewarded Ad (Test Mode)\n\nReklamı izlediniz mi?"
          );
          if (watched) {
            // Trigger reward event
            setTimeout(() => {
              window.dispatchEvent(
                new CustomEvent("admob:reward", {
                  detail: { type: "coins", amount: 1 },
                })
              );
            }, 100);
          }
          return Promise.resolve();
        },
        addListener: (event, callback) => {
          console.log("[Capacitor Stub] AdMob.addListener:", event);

          // Simulate events for testing
          if (event === "onInterstitialAdLoaded") {
            setTimeout(() => callback(), 500);
          }
          if (event === "onRewardedVideoAdLoaded") {
            setTimeout(() => callback(), 500);
          }

          return { remove: () => {} };
        },
      },
      Share: {
        share: async (options) => {
          console.log("[Capacitor Stub] Share:", options);
          if (navigator.share) {
            return navigator.share(options);
          }
          alert(`Share:\n${options.title}\n${options.text}\n${options.url}`);
          return Promise.resolve();
        },
      },
    },
  };
}
