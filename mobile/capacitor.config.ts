import type { CapacitorConfig } from "@capacitor/cli";

const config: CapacitorConfig = {
  appId: "com.orbis.astrology",
  appName: "ORBIS",
  webDir: "www",

  // Server configuration - Production
  server: {
    // Production URL - Vercel'deki web app
    url: "https://ast-kappa.vercel.app",
    androidScheme: "https",
  },

  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      launchAutoHide: true,
      backgroundColor: "#151022",
      androidSplashResourceName: "splash",
      androidScaleType: "CENTER_CROP",
      showSpinner: false,
      splashFullScreen: true,
      splashImmersive: true,
    },
    StatusBar: {
      style: "DARK",
      backgroundColor: "#151022",
    },
    AdMob: {
      // Test modunda başla - Production'da false yapın
      testingDevices: ["YOUR_DEVICE_ID"],
      initializeForTesting: true,
    },
  },

  android: {
    allowMixedContent: true,
    backgroundColor: "#151022",
  },
};

export default config;
