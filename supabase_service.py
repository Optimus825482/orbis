from supabase import create_client
from flask import current_app


class SupabaseService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseService, cls).__new__(cls)
            cls._instance._client = None
        return cls._instance

    @property
    def client(self):
        if self._client is None:
            url = current_app.config.get("SUPABASE_URL")
            key = current_app.config.get("SUPABASE_KEY")
            if not url or not key:
                raise ValueError("Supabase URL veya API anahtarı ayarlanmamış")
            self._client = create_client(url, key)
        return self._client

    def register_user(self, email, password, name=None):
        """Yeni bir kullanıcı kaydeder"""
        try:
            # Supabase Auth kullanarak kullanıcı oluştur
            response = self.client.auth.sign_up({
                "email": email,
                "password": password
            })
            
            # Kullanıcı oluşturulduysa ve ID varsa
            if response.user and response.user.id:
                user_id = response.user.id
                
                # İsim varsa, kullanıcı profilini güncelle
                if name:
                    self.client.from_("profiles").insert({
                        "id": user_id,
                        "name": name,
                        "created_at": "now()"
                    }).execute()
                
                return {"success": True, "user_id": user_id}
            return {"success": False, "message": "Kullanıcı kaydı başarısız"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def login_user(self, email, password):
        """Kullanıcı girişi yapar"""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                return {"success": True, "user": response.user, "session": response.session}
            return {"success": False, "message": "Giriş başarısız"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def logout_user(self):
        """Kullanıcı çıkışı yapar"""
        try:
            self.client.auth.sign_out()
            return {"success": True}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_user(self):
        """Mevcut oturumdaki kullanıcıyı döndürür"""
        try:
            user = self.client.auth.get_user()
            return user.user if user else None
        except:
            return None

    def save_birth_data(self, user_id, data):
        """Doğum verilerini kaydeder"""
        try:
            response = self.client.from_("birth_data").insert({
                "user_id": user_id,
                "name": data.get("name"),
                "birth_date": data.get("birth_date"),
                "birth_time": data.get("birth_time"),
                "birth_place": data.get("birth_place"),
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
                "created_at": "now()"
            }).execute()
            
            return {"success": True, "data": response.data}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def save_transit_data(self, user_id, data):
        """Transit verilerini kaydeder"""
        try:
            response = self.client.from_("transit_data").insert({
                "user_id": user_id,
                "transit_date": data.get("transit_date"),
                "transit_time": data.get("transit_time"),
                "transit_place": data.get("transit_place"),
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
                "created_at": "now()"
            }).execute()
            
            return {"success": True, "data": response.data}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def save_calculation_result(self, user_id, birth_data_id, transit_data_id, result_data):
        """Hesaplama sonuçlarını kaydeder"""
        try:
            response = self.client.from_("calculation_results").insert({
                "user_id": user_id,
                "birth_data_id": birth_data_id,
                "transit_data_id": transit_data_id,
                "result_data": result_data,
                "created_at": "now()"
            }).execute()
            
            return {"success": True, "data": response.data}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def save_ai_interpretation(self, user_id, calculation_id, interpretation):
        """Yapay zeka yorumlarını kaydeder"""
        try:
            response = self.client.from_("ai_interpretations").insert({
                "user_id": user_id,
                "calculation_id": calculation_id,
                "interpretation": interpretation,
                "created_at": "now()"
            }).execute()
            
            return {"success": True, "data": response.data}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_user_calculations(self, user_id):
        """Kullanıcının tüm hesaplamalarını getirir"""
        try:
            response = self.client.from_("calculation_results")\
                .select("*, birth_data(*), transit_data(*), ai_interpretations(*)")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .execute()
            
            return {"success": True, "data": response.data}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_calculation_by_id(self, calculation_id):
        """ID'ye göre hesaplama sonucunu getirir"""
        try:
            response = self.client.from_("calculation_results")\
                .select("*, birth_data(*), transit_data(*), ai_interpretations(*)")\
                .eq("id", calculation_id)\
                .single()\
                .execute()
            
            return {"success": True, "data": response.data}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_user_birth_data(self, user_id):
        """Kullanıcının kişisel doğum verilerini getirir"""
        try:
            response = self.client.from_("birth_data")\
                .select("*")\
                .eq("user_id", user_id)\
                .execute()
            
            return {"success": True, "data": response.data}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def update_user_profile(self, user_id, data):
        """Kullanıcı profilini günceller"""
        try:
            response = self.client.from_("profiles")\
                .update(data)\
                .eq("id", user_id)\
                .execute()
            
            return {"success": True, "data": response.data}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def update_birth_data(self, birth_data_id, data):
        """Doğum verilerini günceller"""
        try:
            response = self.client.from_("birth_data")\
                .update(data)\
                .eq("id", birth_data_id)\
                .execute()
            
            return {"success": True, "data": response.data}
        except Exception as e:
            return {"success": False, "message": str(e)} 