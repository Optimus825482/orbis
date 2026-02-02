# 🔔 Push Notifications Implementation Plan (v1.2+)

## Overview

ORBIS'te push notifications:
- Günlük astrolojik bildirimler
- Transit uyarıları
- Premium öneriler
- Re-engagement campaigns

---

## 🏗️ Architecture

### Tech Stack
```
Firebase Cloud Messaging (FCM)
├─ Server-side: Flask + Firebase Admin SDK
├─ Client-side: Capacitor Push Plugin
└─ Database: Supabase notification preferences
```

### Flow
```
User → Opt-in → Device Token → Firebase → Backend Queue → Send
                                              ↓
                                    Scheduled (Cron Job)
                                    User Segmentation
                                    A/B Testing
                                    Delivery Tracking
```

---

## 📱 Client Implementation

### Capacitor Plugin Setup

```typescript
// capacitor.config.ts
{
  plugins: {
    PushNotifications: {
      presentationOptions: ["badge", "sound", "alert"],
      defaultChannel: "orbis_notifications"
    }
  }
}
```

### Registration Flow

```typescript
// mobile-bridge.js
async function registerPushNotifications() {
  // 1. Request permission
  const permission = await PushNotifications.requestPermissions();
  
  if (permission.receive !== 'granted') {
    console.log('Push notifications disabled by user');
    return;
  }
  
  // 2. Get device token
  const token = await PushNotifications.getDeliveryToken();
  
  // 3. Send to backend
  await fetch('/api/register_device_token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      device_id: localStorage.getItem('orbis_device_id'),
      token: token.value,
      platform: 'android',
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
    })
  });
  
  // 4. Listen for notifications
  PushNotifications.addListener('pushNotificationReceived', (notification) => {
    handleNotification(notification);
  });
  
  PushNotifications.addListener('pushNotificationActionPerformed', (result) => {
    handleNotificationTap(result);
  });
}
```

---

## 🔄 Backend Implementation

### 1. Device Token Storage

**Supabase Schema:**
```sql
CREATE TABLE notification_tokens (
  id UUID PRIMARY KEY,
  device_id VARCHAR NOT NULL,
  user_email VARCHAR,
  token VARCHAR NOT NULL,
  platform VARCHAR,  -- 'android' | 'ios' | 'web'
  timezone VARCHAR,
  enabled BOOLEAN DEFAULT true,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  last_used_at TIMESTAMP,
  UNIQUE(device_id, platform)
);

CREATE TABLE notification_preferences (
  device_id VARCHAR PRIMARY KEY,
  daily_horoscope BOOLEAN DEFAULT true,
  transit_alerts BOOLEAN DEFAULT true,
  ai_insights BOOLEAN DEFAULT true,
  promotional BOOLEAN DEFAULT false,
  opt_out_until TIMESTAMP,
  language VARCHAR DEFAULT 'tr'
);
```

### 2. Firebase Admin Setup

```python
# config.py
import firebase_admin
from firebase_admin import credentials, messaging

# Initialize
cred = credentials.Certificate('firebase-adminsdk.json')
firebase_admin.initialize_app(cred)
messaging_client = messaging.Client.from_app(firebase_admin.get_app())
```

### 3. Notification Endpoints

```python
# api/notifications.py

@bp.route('/api/register_device_token', methods=['POST'])
def register_device_token():
    """Cihaz token'ını kaydet"""
    data = request.get_json()
    
    db.collection('notification_tokens').document(data['device_id']).set({
        'device_id': data['device_id'],
        'token': data['token'],
        'platform': data['platform'],
        'timezone': data['timezone'],
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    })
    
    return jsonify({
        'success': True,
        'message': 'Token registered'
    })

@bp.route('/api/notification_preferences', methods=['POST'])
def update_notification_preferences():
    """Bildirim tercihlerini güncelle"""
    data = request.get_json()
    device_id = data['device_id']
    
    db.collection('notification_preferences').document(device_id).set({
        'daily_horoscope': data.get('daily_horoscope', True),
        'transit_alerts': data.get('transit_alerts', True),
        'ai_insights': data.get('ai_insights', True),
        'promotional': data.get('promotional', False),
        'language': data.get('language', 'tr'),
        'updated_at': datetime.now()
    })
    
    return jsonify({'success': True})

@bp.route('/api/send_notification', methods=['POST'])
@admin_required  # Sadece admin
def send_notification():
    """Manual bildirim gönder (test için)"""
    data = request.get_json()
    device_id = data['device_id']
    
    # Token al
    token_doc = db.collection('notification_tokens').document(device_id).get()
    if not token_doc.exists:
        return jsonify({'error': 'Device not found'}), 404
    
    token = token_doc.get('token')
    
    # Bildirim gönder
    message = messaging.Message(
        notification=messaging.Notification(
            title=data['title'],
            body=data['body']
        ),
        android=messaging.AndroidConfig(
            priority='high',
            notification=messaging.AndroidNotification(
                click_action='FLUTTER_NOTIFICATION_CLICK',
                sound='default'
            )
        ),
        token=token
    )
    
    response = messaging.send(message)
    
    return jsonify({
        'success': True,
        'message_id': response
    })
```

### 4. Scheduled Notifications (Cron Job)

```python
# services/notification_scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
import firebase_admin
from firebase_admin import messaging

scheduler = BackgroundScheduler()

@scheduler.scheduled_job('cron', hour=8, minute=0)
def send_daily_horoscope():
    """Her sabah 08:00'de günlük burç yorumu gönder"""
    
    preferences = db.collection('notification_preferences').where(
        'daily_horoscope', '==', True
    ).stream()
    
    for pref in preferences:
        device_id = pref.id
        
        # Burç bilgisini al
        usage = db.collection('usage_tracking').document(device_id).get()
        if not usage.exists:
            continue
        
        birth_chart = usage.get('birth_chart')
        if not birth_chart:
            continue
        
        sun_sign = birth_chart['sun_sign']
        
        # AI burç yorumu al
        horoscope = get_ai_horoscope(sun_sign)
        
        # Bildirim gönder
        send_push_notification(
            device_id=device_id,
            title=f"Günün Yıldızları - {sun_sign}",
            body=horoscope[:100] + "...",
            data={
                'action': 'show_horoscope',
                'sign': sun_sign
            }
        )

@scheduler.scheduled_job('cron', hour=6, minute=0)
def send_transit_alerts():
    """Transit uyarıları gönder"""
    
    # Bugünün transit'lerini hesapla
    transits = calculate_today_transits()
    
    for transit in transits:
        if transit['severity'] == 'high':
            # Etkilenen kullanıcıları bul
            affected_users = find_affected_users(transit)
            
            for user_id in affected_users:
                send_push_notification(
                    device_id=user_id,
                    title="Transit Uyarısı",
                    body=f"{transit['planet']} transit: {transit['description']}",
                    data={
                        'action': 'show_transit',
                        'transit_id': transit['id']
                    }
                )

# Başlat
def start_scheduler():
    if not scheduler.running:
        scheduler.start()
```

### 5. Helper Function

```python
def send_push_notification(device_id, title, body, data=None):
    """
    Güvenli bildirim gönderme
    """
    try:
        # Token al
        token_doc = db.collection('notification_tokens').document(device_id).get()
        if not token_doc.exists:
            logger.warning(f"No token for device: {device_id}")
            return False
        
        token = token_doc.get('token')
        
        # Tercih kontrol et
        pref_doc = db.collection('notification_preferences').document(device_id).get()
        if pref_doc.exists and not pref_doc.get('enabled', True):
            logger.info(f"Notifications disabled for device: {device_id}")
            return False
        
        # Bildirim oluştur
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            android=messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    click_action='FLUTTER_NOTIFICATION_CLICK',
                    sound='default'
                )
            ),
            data=data or {},
            token=token
        )
        
        # Gönder
        response = messaging.send(message)
        
        # Analytics
        trackEvent('push_notification_sent', {
            'device_id': device_id,
            'notification_type': data.get('action', 'generic') if data else 'generic',
            'success': True
        })
        
        return True
        
    except messaging.UnregisteredError:
        # Token geçersiz, sil
        db.collection('notification_tokens').document(device_id).delete()
        logger.warning(f"Token deleted (invalid): {device_id}")
        return False
        
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        return False
```

---

## 📊 Notification Types

### 1. Daily Horoscope
```
Title:  "Günün Yıldızları - [Burç]"
Body:   "Bugün sizi neler bekliyor..."
Time:   08:00 AM (kullanıcının timezone'unda)
Freq:   Günlük
```

### 2. Transit Alerts
```
Title:  "Transit Uyarısı"
Body:   "[Gezegen] transit başlıyor..."
Time:   06:00 AM + event time
Freq:   Değişken (transit olduğunda)
```

### 3. AI Insights
```
Title:  "Özel İçgörü"
Body:   "Astrolojik profilinize özel..."
Time:   Random (prime hours)
Freq:   Haftada 2-3 kez
```

### 4. Re-engagement
```
Title:  "Analiz Yaptırdın mı?"
Body:   "Son 7 gündür hiç analiz yapmamışsın..."
Time:   17:00 (akşam)
Freq:   Haftalık (inaktif kullanıcılara)
```

---

## 🎯 Segmentation Strategy

### User Segments
```
Active users (last 7 days)
├─ Daily users → High priority
├─ Weekly users → Medium priority
└─ Inactive 7+ days → Re-engagement

Premium vs Free
├─ Premium: Advanced transits
└─ Free: Basic horoscope only

Engagement level
├─ High (>10 interactions/week)
├─ Medium (3-10 interactions/week)
└─ Low (<3 interactions/week)
```

### Do Not Disturb
```
- Overnight (22:00 - 08:00)
- If opted out
- If uninstalled (token invalid)
- Frequency cap: Max 3/day
```

---

## 📈 Analytics

### Track
```
Event: notification_sent
- notification_type
- device_segment
- timestamp
- timezone

Event: notification_opened
- notification_type
- action_performed
- time_to_open
- device_segment

Event: notification_dismissed
- notification_type
- reason (if available)

Event: notification_failed
- error_code
- notification_type
- token_status
```

### Dashboard Metrics
```
Delivery Rate: 95%+
Open Rate: 20-30% (good mobile app)
Click Rate: 10-15%
Unsubscribe Rate: <5%
```

---

## 🧪 Testing

### Manual Test
```
1. Android Studio emulator
2. Firebase Cloud Messaging Tester
3. Send test notification
4. Verify badge, sound, alert
```

### A/B Testing
```
A: Simple message
B: Personalized message
→ Compare open rates
→ Scale winning variant
```

---

## 🚀 Rollout Plan

### Phase 1: Beta (v1.2)
- [ ] 100 beta testers
- [ ] Daily horoscope only
- [ ] Manual send capability
- [ ] Feedback collection

### Phase 2: Limited (v1.3)
- [ ] All users opt-in
- [ ] All notification types
- [ ] Scheduling enabled
- [ ] A/B testing

### Phase 3: Production (v1.4)
- [ ] Full rollout
- [ ] Advanced segmentation
- [ ] ML-based opt timing
- [ ] Revenue optimization

---

## ⚠️ Compliance

### Privacy
- [ ] User consent before registration
- [ ] Clear opt-out option
- [ ] Privacy policy updated
- [ ] No sensitive data in notification body

### GDPR/KVKK
- [ ] User can request deletion
- [ ] Token cleanup after 30 days (invalid)
- [ ] Data retention policy
- [ ] Compliance audit

---

## 📋 Implementation Checklist

### Backend
- [ ] Database schema (tokens, preferences)
- [ ] Firebase Admin SDK setup
- [ ] /api/register_device_token endpoint
- [ ] /api/notification_preferences endpoint
- [ ] /api/send_notification endpoint (admin)
- [ ] APScheduler integration
- [ ] Scheduled jobs (horoscope, transits)
- [ ] Error handling
- [ ] Analytics integration

### Mobile
- [ ] Push plugin configuration
- [ ] Permission request UI
- [ ] Token registration
- [ ] Notification listener
- [ ] Deep linking (notification tap)
- [ ] Settings UI

### Testing
- [ ] Beta testing (100 users)
- [ ] Load testing (1000+ concurrent)
- [ ] Error scenario testing
- [ ] Token expiration handling
- [ ] Opt-out verification

---

**Version:** 1.2 (Planned - April 2026)  
**Created:** 2026-02-02  
**Status:** READY FOR IMPLEMENTATION
