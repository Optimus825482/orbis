import type { CapacitorConfig } from "@capacitor/cli";

const config: CapacitorConfig = {
  appId: "com.orbisapp.astrology",
  appName: "ORBIS",
  webDir: "www",

  // Server configuration - Coolify Production URL
  server: {
    // TODO: Coolify URL'ini buraya yaz (örn: https://orbis.yourdomain.com)
    // Şimdilik local test için:
    // url: "http://10.0.2.2:8005", // Android emulator için
    androidScheme: "https",
    cleartext: true, // HTTP için gerekli (development)
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
      testingDevices: [], // Production - boş array
      initializeForTesting: false, // Production mode
    },
    GoogleAuth: {
      scopes: ["profile", "email"],
      serverClientId:
        "768649602152-aous93aj0cnn8bjdsqvjo4t62ip2feci.apps.googleusercontent.com",
      forceCodeForRefreshToken: true,
    },
    PushNotifications: {
      presentationOptions: ["badge", "sound", "alert"],
    },
  },

  android: {
    allowMixedContent: true,
    backgroundColor: "#151022",
  },
};

export default config;
