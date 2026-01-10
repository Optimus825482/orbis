"""
Kullanım Takip Sistemi
- Günlük ücretsiz yorum limiti
- Premium kullanıcı kontrolü
"""
from datetime import datetime, date
from flask import current_app
import json
import os

class UsageTracker:
    """Kullanıcı kullanım takibi"""
    
    FREE_DAILY_LIMIT = 3  # Günlük ücretsiz yorum sayısı
    
    def __init__(self, storage_path=None):
        self.storage_path = storage_path or "instance/usage_data.json"
        self._ensure_storage()
    
    def _ensure_storage(self):
        """Storage dosyasını oluştur"""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, 'w') as f:
                json.dump({}, f)
    
    def _load_data(self):
        with open(self.storage_path, 'r') as f:
            return json.load(f)
    
    def _save_data(self, data):
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    def get_user_usage(self, device_id: str) -> dict:
        """Kullanıcının bugünkü kullanımını getir"""
        data = self._load_data()
        today = date.today().isoformat()
        
        if device_id not in data:
            data[device_id] = {"usage": {}, "premium": False, "premium_until": None}
            self._save_data(data)
        
        user_data = data[device_id]
        today_usage = user_data.get("usage", {}).get(today, 0)
        
        return {
            "device_id": device_id,
            "today_usage": today_usage,
            "daily_limit": self.FREE_DAILY_LIMIT,
            "remaining": max(0, self.FREE_DAILY_LIMIT - today_usage),
            "is_premium": self._check_premium(user_data),
            "premium_until": user_data.get("premium_until")
        }
    
    def _check_premium(self, user_data: dict) -> bool:
        """Premium durumunu kontrol et"""
        if not user_data.get("premium"):
            return False
        premium_until = user_data.get("premium_until")
        if premium_until:
            return datetime.fromisoformat(premium_until) > datetime.now()
        return False
    
    def can_use_feature(self, device_id: str, feature: str = "interpretation") -> dict:
        """Kullanıcı özelliği kullanabilir mi?"""
        usage = self.get_user_usage(device_id)
        
        if usage["is_premium"]:
            return {"allowed": True, "reason": "premium", "remaining": "unlimited"}
        
        if usage["remaining"] > 0:
            return {"allowed": True, "reason": "free_quota", "remaining": usage["remaining"]}
        
        return {
            "allowed": False, 
            "reason": "limit_reached",
            "message": "Günlük ücretsiz kullanım limitiniz doldu. Premium'a geçin!",
            "remaining": 0
        }
    def record_usage(self, device_id: str, feature: str = "interpretation") -> dict:
        """Kullanımı kaydet"""
        data = self._load_data()
        today = date.today().isoformat()
        
        if device_id not in data:
            data[device_id] = {"usage": {}, "premium": False}
        
        if "usage" not in data[device_id]:
            data[device_id]["usage"] = {}
        
        if today not in data[device_id]["usage"]:
            data[device_id]["usage"][today] = 0
        
        # Premium kullanıcı için limit yok
        if not self._check_premium(data[device_id]):
            data[device_id]["usage"][today] += 1
        
        self._save_data(data)
        return self.get_user_usage(device_id)
    
    def set_premium(self, device_id: str, days: int = 30) -> dict:
        """Kullanıcıyı premium yap"""
        data = self._load_data()
        
        if device_id not in data:
            data[device_id] = {"usage": {}, "premium": False}
        
        from datetime import timedelta
        premium_until = datetime.now() + timedelta(days=days)
        
        data[device_id]["premium"] = True
        data[device_id]["premium_until"] = premium_until.isoformat()
        
        self._save_data(data)
        return {"success": True, "premium_until": premium_until.isoformat()}
    
    def verify_purchase(self, device_id: str, purchase_token: str, product_id: str) -> dict:
        """Google Play satın alma doğrulama (placeholder)"""
        # TODO: Google Play Developer API ile doğrulama
        # Şimdilik basit bir implementasyon
        
        valid_products = {
            "premium_monthly": 30,
            "premium_yearly": 365,
            "premium_lifetime": 36500  # ~100 yıl
        }
        
        if product_id in valid_products:
            return self.set_premium(device_id, valid_products[product_id])
        
        return {"success": False, "error": "Invalid product"}
