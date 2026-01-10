"""
ORBIS Push Notification Routes
FCM token kaydetme ve push gönderme endpoint'leri
"""

from flask import Blueprint, request, jsonify
from services.firebase_service import firebase_service

push_bp = Blueprint('push', __name__, url_prefix='/api/push')


@push_bp.route('/register-token', methods=['POST'])
def register_token():
    """
    FCM token'ı kaydet
    
    Body:
        {
            "userId": "firebase_user_id",
            "token": "fcm_device_token",
            "platform": "web" | "android" | "ios"
        }
    """
    try:
        data = request.get_json()
        
        user_id = data.get('userId')
        token = data.get('token')
        platform = data.get('platform', 'web')
        
        if not user_id or not token:
            return jsonify({
                'success': False,
                'error': 'userId ve token gerekli'
            }), 400
        
        success = firebase_service.save_fcm_token(user_id, token, platform)
        
        # Premium kullanıcıları topic'e ekle
        # (Bu bilgi frontend'den gelmeli veya Firestore'dan kontrol edilmeli)
        firebase_service.subscribe_to_topic([token], 'all_users')
        
        return jsonify({
            'success': success,
            'message': 'Token kaydedildi' if success else 'Token kaydedilemedi'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@push_bp.route('/subscribe-topic', methods=['POST'])
def subscribe_topic():
    """
    Kullanıcıyı bir topic'e abone et
    
    Body:
        {
            "token": "fcm_device_token",
            "topic": "daily_horoscope" | "premium_users" | "all_users"
        }
    """
    try:
        data = request.get_json()
        
        token = data.get('token')
        topic = data.get('topic')
        
        if not token or not topic:
            return jsonify({
                'success': False,
                'error': 'token ve topic gerekli'
            }), 400
        
        # Güvenlik: Sadece izin verilen topic'ler
        allowed_topics = ['all_users', 'daily_horoscope', 'weekly_horoscope', 'premium_users']
        if topic not in allowed_topics:
            return jsonify({
                'success': False,
                'error': 'Geçersiz topic'
            }), 400
        
        success = firebase_service.subscribe_to_topic([token], topic)
        
        return jsonify({
            'success': success,
            'message': f'{topic} topic\'ine abone olundu' if success else 'Abone olunamadı'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@push_bp.route('/unsubscribe-topic', methods=['POST'])
def unsubscribe_topic():
    """Kullanıcıyı bir topic'ten çıkar"""
    try:
        data = request.get_json()
        
        token = data.get('token')
        topic = data.get('topic')
        
        if not token or not topic:
            return jsonify({
                'success': False,
                'error': 'token ve topic gerekli'
            }), 400
        
        success = firebase_service.unsubscribe_from_topic([token], topic)
        
        return jsonify({
            'success': success
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ═══════════════════════════════════════════════════════════════
# ADMIN ENDPOINTS (Güvenli ortamdan çağrılmalı)
# ═══════════════════════════════════════════════════════════════

@push_bp.route('/send-to-user', methods=['POST'])
def send_to_user():
    """
    Belirli bir kullanıcıya push gönder (Admin)
    
    Body:
        {
            "userId": "firebase_user_id",
            "title": "Bildirim Başlığı",
            "body": "Bildirim içeriği",
            "data": {"key": "value"}  // opsiyonel
        }
    """
    # TODO: Admin authentication ekle
    try:
        data = request.get_json()
        
        user_id = data.get('userId')
        title = data.get('title')
        body = data.get('body')
        extra_data = data.get('data', {})
        
        if not all([user_id, title, body]):
            return jsonify({
                'success': False,
                'error': 'userId, title ve body gerekli'
            }), 400
        
        # Kullanıcının token'larını al
        tokens = firebase_service.get_user_tokens(user_id)
        
        if not tokens:
            return jsonify({
                'success': False,
                'error': 'Kullanıcının kayıtlı token\'ı yok'
            }), 404
        
        # Push gönder
        if len(tokens) == 1:
            result = firebase_service.send_push(tokens[0], title, body, extra_data)
            success = result is not None
        else:
            result = firebase_service.send_push_to_multiple(tokens, title, body, extra_data)
            success = result.get('success_count', 0) > 0
        
        return jsonify({
            'success': success,
            'result': result if isinstance(result, dict) else {'messageId': result}
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@push_bp.route('/send-to-topic', methods=['POST'])
def send_to_topic():
    """
    Bir topic'e push gönder (Admin)
    
    Body:
        {
            "topic": "all_users" | "premium_users" | "daily_horoscope",
            "title": "Bildirim Başlığı",
            "body": "Bildirim içeriği"
        }
    """
    # TODO: Admin authentication ekle
    try:
        data = request.get_json()
        
        topic = data.get('topic')
        title = data.get('title')
        body = data.get('body')
        extra_data = data.get('data', {})
        
        if not all([topic, title, body]):
            return jsonify({
                'success': False,
                'error': 'topic, title ve body gerekli'
            }), 400
        
        result = firebase_service.send_push_to_topic(topic, title, body, extra_data)
        
        return jsonify({
            'success': result is not None,
            'messageId': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@push_bp.route('/broadcast', methods=['POST'])
def broadcast():
    """
    Tüm kullanıcılara push gönder (Admin)
    """
    # TODO: Admin authentication ekle
    try:
        data = request.get_json()
        
        title = data.get('title')
        body = data.get('body')
        
        if not all([title, body]):
            return jsonify({
                'success': False,
                'error': 'title ve body gerekli'
            }), 400
        
        result = firebase_service.send_push_to_topic('all_users', title, body)
        
        return jsonify({
            'success': result is not None,
            'messageId': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
