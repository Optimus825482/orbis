# 🛒 In-App Purchase Integration Plan (v1.1+)

## Overview

ORBIS'te Premium subscription (reklamsız kullanım) için In-App Purchase (IAP) entegrasyonu.

---

## 📱 Implementation Strategy

### Phase 1: Backend Setup (Flask)
```
Premium endpoint'leri oluştur
├─ /api/verify_purchase (Google Play satın alma doğrula)
├─ /api/premium_status (Kullanıcı premium mi kontrol)
└─ /api/set_premium (Premium aktive et)
```

### Phase 2: Mobile Integration (Android)
```
Google Play Billing Library
├─ Product ID: "com.orbisastro.premium_monthly"
├─ Price: 9.99 TRY/month
├─ Description: "Reklamsız sınırsız analiz"
└─ Automatic renewal: True
```

### Phase 3: Frontend UI
```
Settings/Paywall screen
├─ Premium benefits showcase
├─ "Get Premium" button
├─ Restore purchase option
└─ Terms & refund policy
```

---

## 🔧 Technical Implementation

### 1. Google Play Console Setup

**Location:** Play Console → Products → In-app products

```
Product Type:       Subscription
Product ID:         premium.monthly
Price:              9.99 TRY (per month)
Title:              ORBIS Premium - Aylık
Description:        Reklamsız sınırsız analiz + AI yorumlar
Subscription:       Monthly (auto-renew)
Billing Cycle:      30 days
Free trial:         Optional (7 days)
```

### 2. Android Integration

**Library:** com.android.billingclient:billing

```gradle
dependencies {
    implementation 'com.android.billingclient:billing:6.2.0'
}
```

**Implementation:**
```typescript
// Mobile app code
import { BillingClient, SkuType } from '@react-native-iap/iap';

// Initialize
const billing = new BillingClient({
    listener: onBillingUpdate,
    enablePendingPurchases: true
});

// Query available products
const products = await billing.queryProducts({
    productIds: ['premium.monthly'],
    type: SkuType.SUBS
});

// Launch purchase flow
const purchase = await billing.launchBillingFlow({
    skuDetails: premiumProduct,
    accountId: user.id
});

// Verify and activate
if (purchase.success) {
    await sendPurchaseTokenToBackend(purchase.token);
}
```

### 3. Backend Verification

**Endpoint:** `/api/verify_purchase`

```python
from flask import request, jsonify
from google.auth.transport import requests
from google.oauth2 import service_account

@app.route('/api/verify_purchase', methods=['POST'])
def verify_purchase():
    """
    Google Play satın almayı doğrula
    
    Request: {
        "device_id": "...",
        "package_name": "com.orbisastro.orbis",
        "subscription_id": "premium.monthly",
        "purchase_token": "...",
        "email": "..."
    }
    """
    data = request.get_json()
    
    # 1. Google Play Developer API ile doğrula
    verification = verify_google_play_purchase(
        package_name=data['package_name'],
        subscription_id=data['subscription_id'],
        purchase_token=data['purchase_token']
    )
    
    if not verification['isValid']:
        return jsonify({
            "success": False,
            "error": "Invalid purchase token"
        }), 400
    
    # 2. Kullanıcıyı Premium yap
    premium_until = verification['expiryTime']
    
    tracker = UsageTracker()
    tracker.set_premium(
        device_id=data['device_id'],
        purchase_token=data['purchase_token'],
        days=30,
        platform='google_play'
    )
    
    # 3. Analytics
    trackEvent('premium_purchased', {
        'device_id': data['device_id'],
        'amount': 9.99,
        'currency': 'TRY',
        'subscription_type': 'monthly'
    })
    
    return jsonify({
        "success": True,
        "premium_until": premium_until.isoformat(),
        "show_premium_modal": False
    })
```

### 4. Database Schema Update

**Supabase/Firebase:**

```sql
-- usage_tracking collection'a ekle
{
    device_id: string (PK),
    premium: boolean,
    premium_until: timestamp,
    purchase_token: string,
    purchase_platform: string,  // "google_play" | "stripe" | "manual"
    subscription_active: boolean,
    last_billing_date: timestamp,
    billing_retry_count: integer
}
```

---

## 💰 Monetization Strategy

### Pricing Options

| Tier | Price | Features | Renewal |
|------|-------|----------|---------|
| Free | 0 | 1 analiz/gün + reklamlar | N/A |
| Premium | 9.99 TRY/ay | Sınırsız + reklamsız | Otomatik |
| Premium | 49.99 TRY/yıl | Sınırsız + reklamsız | Otomatik |
| Lifetime | 99.99 TRY | Sınırsız + reklamsız | Bir kez |

### Revenue Projections

```
Scenario 1 (Conservative):
- 1000 downloads
- 5% conversion to premium
- 50 active subscribers
- Revenue: 50 × 9.99 = 499 TRY/month

Scenario 2 (Aggressive):
- 10,000 downloads
- 10% conversion to premium
- 1000 active subscribers
- Revenue: 1000 × 9.99 = 9,990 TRY/month
```

---

## 🔐 Security Considerations

### Purchase Token Validation
- Always validate on backend
- Never trust client-side validation
- Check signature certificate
- Verify receipt status (ACTIVE, EXPIRED, etc)

### Fraud Prevention
```python
# Rate limit purchase requests
# Prevent duplicate purchases
# Monitor chargeback rates
# Alert on suspicious patterns
```

### Refund Handling
```
Google Play → 7 day refund window
├─ Automatic refund processing
├─ Notification webhook
├─ Premium access revocation
└─ Analytics tracking
```

---

## 📊 Analytics Integration

### Events to Track

```python
# Purchase initiated
trackEvent('premium_purchase_started', {
    'pricing_tier': 'monthly',
    'location': 'settings_screen'
})

# Purchase completed
trackEvent('premium_purchased', {
    'amount': 9.99,
    'currency': 'TRY',
    'subscription_type': 'monthly'
})

# Subscription renewal
trackEvent('subscription_renewed', {
    'amount': 9.99,
    'renewal_count': 3
})

# Subscription cancelled
trackEvent('subscription_cancelled', {
    'days_active': 45,
    'reason': 'user_initiated'
})
```

### User Segmentation
```
Premium users
├─ Premium active (subscription valid)
├─ Premium expired (subscription ended)
├─ Trial users (free trial active)
└─ Churned (cancelled)
```

---

## 🧪 Testing

### Sandbox Testing (Play Console)
```
1. Create test account in Play Console
2. Add test account to tester group
3. Device should see premium product
4. Purchase completes instantly
5. No charge to test account
```

### Test Scenarios
- [ ] Successful purchase
- [ ] Purchase cancellation
- [ ] Subscription renewal
- [ ] Subscription expiration
- [ ] Invalid purchase token
- [ ] Network error handling
- [ ] Duplicate purchase prevention

### Testing Endpoint
```bash
# Test premium check
curl https://ast-kappa.vercel.app/api/premium_status \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"device_id":"test_123"}'

# Response
{
  "is_premium": false,
  "premium_until": null,
  "subscription_active": false
}
```

---

## 📱 UI/UX Flow

### Paywall Screen
```
┌─────────────────────────┐
│   ORBIS Premium         │
├─────────────────────────┤
│                         │
│  ✓ Reklamsız sınırsız   │
│  ✓ Gelişmiş AI yorum    │
│  ✓ Detaylı raporlar     │
│  ✓ Bulut senkronizasyon │
│                         │
│  9.99 TRY / Ay          │
│  [GET PREMIUM BUTTON]   │
│                         │
│  [Restore Purchase]     │
│  [Terms] [Privacy]      │
└─────────────────────────┘
```

### Settings Integration
```
Settings
├─ Account
│   ├─ Premium Status
│   │   ├─ Active until: [date]
│   │   └─ [Manage Subscription]
│   └─ Billing
│       ├─ Payment method
│       └─ Billing history
└─ Subscriptions
    ├─ Monthly Premium
    │   ├─ [Upgrade]
    │   ├─ [Cancel]
    │   └─ [View Details]
    └─ Renewal info
```

---

## 🚀 Deployment Timeline

### v1.0 (Current - Feb 2026)
```
✅ Rewarded ads
✅ Free tier
❌ IAP (not yet)
```

### v1.1 (March 2026)
```
⏳ In-App Purchase integration
  ├─ Backend verification API
  ├─ Mobile purchase flow
  ├─ Paywall UI
  └─ Analytics
```

### v1.2 (April 2026)
```
⏳ Premium features
  ├─ Advanced charts
  ├─ Report export (PDF)
  ├─ Cloud sync
  └─ API access
```

---

## 📋 Implementation Checklist

### Backend
- [ ] `/api/verify_purchase` endpoint
- [ ] `/api/premium_status` endpoint
- [ ] Google Play credentials configured
- [ ] Billing database schema
- [ ] Refund webhook handler
- [ ] Analytics integration

### Mobile
- [ ] Google Play Billing Library integrated
- [ ] Purchase flow UI
- [ ] Paywall screen
- [ ] Restore purchases
- [ ] Error handling
- [ ] Testing completed

### Frontend
- [ ] Settings → Subscription management
- [ ] Paywall screen
- [ ] Ad removal for premium
- [ ] Feature flags
- [ ] Analytics tracking

### Testing
- [ ] Sandbox testing complete
- [ ] All scenarios tested
- [ ] Error cases handled
- [ ] Performance verified

### Compliance
- [ ] Privacy policy updated
- [ ] Terms of service updated
- [ ] Refund policy clear
- [ ] Pricing transparent

---

## 🔗 References

- Google Play Billing: https://developer.android.com/google/play/billing
- Subscription Best Practices: https://developer.android.com/google/play/billing/subscription
- Revenue Management: https://play.google.com/console

---

**Version:** 1.1 (Planned)  
**Created:** 2026-02-02  
**Status:** READY FOR IMPLEMENTATION
