"""
Redis Session Migration Script
================================

Bu script, filesystem session'lardan Redis session'lara geçiş için kullanılır.

Kullanım:
1. Redis server'ı başlat: redis-server
2. .env dosyasında SESSION_TYPE=redis olarak ayarla
3. Bu script'i çalıştır: python migrate_to_redis.py
4. Mevcut session dosyaları Redis'e aktarılır
5. Yedekleme alınır (migrated_sessions_backup/)

Notlar:
- Flask-Session otomatik olarak Redis kullanacak
- Eski session dosyaları silinmez, yedeklenir
- Redis bağlantısı test edilir
"""

import os
import json
import sys
import shutil
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Environment variables'ı yükle
load_dotenv()


def test_redis_connection():
    """Redis bağlantısını test et."""
    try:
        import redis
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))
        redis_db = os.getenv("REDIS_DB", "0")
        redis_password = os.getenv("REDIS_PASSWORD", "")
        
        # Redis bağlantısı kur
        if redis_password:
            r = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=int(redis_db),
                password=redis_password,
                decode_responses=True
            )
        else:
            r = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=int(redis_db),
                decode_responses=True
            )
        
        # Test ping
        r.ping()
        print("✅ Redis bağlantısı başarılı!")
        print(f"   Host: {redis_host}:{redis_port}, DB: {redis_db}")
        return r
        
    except ImportError:
        print("❌ Redis paketi yüklü değil!")
        print("   Çözüm: pip install redis")
        return None
    except Exception as e:
        print(f"❌ Redis bağlantı hatası: {e}")
        print("   Çözüm: Redis server'ı başlat (redis-server)")
        return None


def migrate_session_files(redis_client=None):
    """Filesystem session dosyalarını Redis'e taşı."""
    session_dir = Path(__file__).parent / "instance" / "sessions"
    
    if not session_dir.exists():
        print("⚠️  Session dosyası bulunamadı, geçiş gerekmiyor.")
        return True
    
    # Session dosyalarını bul
    session_files = list(session_dir.glob("astro_data_*.json"))
    
    if not session_files:
        print("⚠️  Taşınacak session dosyası yok.")
        return True
    
    print(f"📦 {len(session_files)} session dosyası bulundu.")
    
    # Yedekleme dizini oluştur
    backup_dir = Path(__file__).parent / "instance" / "migrated_sessions_backup"
    backup_dir.mkdir(exist_ok=True)
    
    # Session dosyalarını yedekle ve Redis'e yükle
    migrated_count = 0
    failed_count = 0
    
    for session_file in session_files:
        try:
            # Dosyayı oku
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # Session ID'yi çıkar
            session_id = session_file.stem.replace("astro_data_", "")
            
            # Redis'e kaydet (eğer Redis client varsa)
            if redis_client:
                redis_key = f"astro_data_{session_id}"
                # JSON olarak kaydet (Flask-Session pickle kullanıyor ama manuel için JSON)
                redis_client.setex(
                    redis_key,
                    3600,  # 1 saat TTL
                    json.dumps(session_data, ensure_ascii=False)
                )
                print(f"✅ Session {session_id[:8]}... Redis'e aktarıldı")
            else:
                print(f"📋 Session {session_id[:8]}... yedeklendi (Redis aktif değil)")
            
            # Yedekle
            backup_path = backup_dir / session_file.name
            shutil.copy2(session_file, backup_path)
            
            # Orijinali sil (opsiyonel - şimdilik silmiyoruz)
            # session_file.unlink()
            
            migrated_count += 1
            
        except Exception as e:
            print(f"❌ Session {session_file.name} aktarım hatası: {e}")
            failed_count += 1
    
    print(f"\n📊 Özet:")
    print(f"   Başarılı: {migrated_count}")
    print(f"   Başarısız: {failed_count}")
    print(f"   Yedekleme: {backup_dir}")
    
    return failed_count == 0


def verify_redis_config():
    """Redis yapılandırmasını doğrula."""
    session_type = os.getenv("SESSION_TYPE", "filesystem")
    
    if session_type != "redis":
        print(f"⚠️  SESSION_TYPE='{session_type}' - 'redis' olmalı!")
        print("   .env dosyasında SESSION_TYPE=redis olarak ayarlayın")
        return False
    
    print("✅ SESSION_TYPE=redis doğru yapılandırılmış")
    return True


def print_migration_guide():
    """Geçiş rehberini yazdır."""
    print("\n" + "="*70)
    print("REDIS SESSION GEÇİŞ REHBERİ")
    print("="*70)
    print("\n1️⃣  Redis Kurulumu:")
    print("   Windows: chocolatey install redis-64")
    print("   Linux:   sudo apt-get install redis-server")
    print("   macOS:   brew install redis")
    print("   Başlat:  redis-server")
    
    print("\n2️⃣  Python Paketleri:")
    print("   pip install redis Flask-Session")
    
    print("\n3️⃣  .env Dosyası Yapılandırması:")
    print("   SESSION_TYPE=redis")
    print("   REDIS_HOST=localhost")
    print("   REDIS_PORT=6379")
    print("   REDIS_DB=0")
    print("   REDIS_PASSWORD= (opsiyonel)")
    
    print("\n4️⃣  Uygulamayı Başlat:")
    print("   python app.py")
    print("   veya")
    print("   flask run")
    
    print("\n5️⃣  Redis CLI ile Kontrol:")
    print("   redis-cli")
    print("   > KEYS astro_data_*")
    print("   > GET astro_data_<session_id>")
    
    print("\n" + "="*70)


def main():
    """Ana fonksiyon."""
    print("🚀 Redis Session Migration Script")
    print("=" * 70)
    
    # Redis yapılandırmasını kontrol et
    if not verify_redis_config():
        print_migration_guide()
        print("\n⚠️  Lütfen önce .env dosyasını yapılandırın!")
        return False
    
    # Redis bağlantısını test et
    redis_client = test_redis_connection()
    if not redis_client:
        print_migration_guide()
        return False
    
    # Session dosyalarını migrate et
    print("\n📦 Session dosyaları migrate ediliyor...")
    success = migrate_session_files(redis_client)
    
    if success:
        print("\n✅ Migration başarılı!")
        print("\n🎯 Sonraki adımlar:")
        print("   1. Uygulamayı başlat: python app.py")
        print("   2. Test et: Bir hesaplama yap ve session'ı kontrol et")
        print("   3. Redis CLI: redis-cli -> KEYS session:*")
        return True
    else:
        print("\n⚠️  Migration tamamlanamadı!")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  İptal edildi.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Beklenmeyen hata: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
