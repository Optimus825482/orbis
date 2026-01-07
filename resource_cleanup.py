"""
Resource Cleanup and Memory Management
========================================

Bu modül, memory leak'leri önlemek ve kaynakları temizlemek için araçlar içerir.
Context-aware HTTP session, session file cleanup, ve database connection pooling.

Kullanım:
    from resource_cleanup import cleanup_session_files, init_cleanup_scheduler
    init_cleanup_scheduler(app)
"""

import os
import shutil
import logging
import atexit
from pathlib import Path
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from flask import g, current_app
from typing import Optional
import threading

logger = logging.getLogger(__name__)


# =============================================================================
# SESSION FILE CLEANUP
# =============================================================================
class SessionFileCleanup:
    """
    Session dosyalarını temizleyen class.
    
    Eski session dosyalarını otomatik olarak siler.
    """
    
    def __init__(self, session_dir: str, max_age_hours: int = 24):
        """
        SessionFileCleanup'u başlat.
        
        Args:
            session_dir: Session dosyalarının bulunduğu dizin
            max_age_hours: Maksimum dosya yaşı (saat)
        """
        self.session_dir = Path(session_dir)
        self.max_age = timedelta(hours=max_age_hours)
        self.lock = threading.Lock()
    
    def cleanup_old_sessions(self) -> dict:
        """
        Eski session dosyalarını temizle.
        
        Returns:
            Cleanup istatistikleri
        """
        if not self.session_dir.exists():
            logger.debug(f"Session directory not found: {self.session_dir}")
            return {"deleted": 0, "kept": 0, "errors": 0}
        
        deleted = 0
        kept = 0
        errors = 0
        cutoff_time = datetime.now() - self.max_age
        
        with self.lock:
            try:
                for session_file in self.session_dir.glob("astro_data_*.json"):
                    try:
                        # Dosya yaşını kontrol et
                        file_mtime = datetime.fromtimestamp(session_file.stat().st_mtime)
                        
                        if file_mtime < cutoff_time:
                            # Eski dosyayı sil
                            session_file.unlink()
                            deleted += 1
                            logger.debug(f"Deleted old session: {session_file.name}")
                        else:
                            kept += 1
                    
                    except Exception as e:
                        errors += 1
                        logger.error(f"Error deleting session file {session_file.name}: {e}")
                
                logger.info(f"Session cleanup completed: {deleted} deleted, {kept} kept, {errors} errors")
                
                return {
                    "deleted": deleted,
                    "kept": kept,
                    "errors": errors,
                    "timestamp": datetime.now().isoformat()
                }
            
            except Exception as e:
                logger.error(f"Session cleanup error: {e}")
                return {"deleted": deleted, "kept": kept, "errors": errors + 1}


# =============================================================================
# SESSION CLEANUP SCHEDULER
# =============================================================================
_cleanup_scheduler: Optional[BackgroundScheduler] = None
_session_cleanup: Optional[SessionFileCleanup] = None


def init_cleanup_scheduler(
    app,
    session_dir: Optional[str] = None,
    cleanup_interval_hours: int = 6,
    max_session_age_hours: int = 24
):
    """
    Session cleanup scheduler'ını başlat.
    
    Args:
        app: Flask app instance
        session_dir: Session dosyaları dizini (varsayılan: instance/sessions)
        cleanup_interval_hours: Cleanup aralığı (saat)
        max_session_age_hours: Maksimum session yaşı (saat)
    """
    global _cleanup_scheduler, _session_cleanup
    
    # Scheduler zaten başlatılmış mı?
    if _cleanup_scheduler and _cleanup_scheduler.running:
        logger.debug("Cleanup scheduler already running")
        return
    
    # Session dizinini al
    if session_dir is None:
        session_dir = os.path.join(app.instance_path, "sessions")
    
    # Session cleanup instance'ı oluştur
    _session_cleanup = SessionFileCleanup(session_dir, max_session_age_hours)
    
    # Scheduler'ı başlat
    _cleanup_scheduler = BackgroundScheduler(daemon=True)
    
    # Cleanup job'ı ekle - her X saatte bir çalışır
    _cleanup_scheduler.add_job(
        func=_session_cleanup.cleanup_old_sessions,
        trigger='interval',
        hours=cleanup_interval_hours,
        id='session_cleanup',
        name='Session File Cleanup',
        replace_existing=True
    )
    
    # Başlangıçta bir kere çalıştır
    _cleanup_scheduler.add_job(
        func=_session_cleanup.cleanup_old_sessions,
        trigger='date',
        id='initial_session_cleanup',
        name='Initial Session Cleanup'
    )
    
    # Scheduler'ı başlat
    _cleanup_scheduler.start()
    
    logger.info(f"Session cleanup scheduler started (interval: {cleanup_interval_hours}h, max_age: {max_session_age_hours}h)")
    
    # Uygulama shutdown'ında scheduler'ı durdur
    atexit.register(shutdown_cleanup_scheduler)


def shutdown_cleanup_scheduler():
    """Cleanup scheduler'ını kapat."""
    global _cleanup_scheduler
    
    if _cleanup_scheduler and _cleanup_scheduler.running:
        logger.info("Shutting down cleanup scheduler...")
        _cleanup_scheduler.shutdown(wait=True)
        logger.info("Cleanup scheduler stopped")


def cleanup_session_files(session_dir: Optional[str] = None, max_age_hours: int = 24) -> dict:
    """
    Session dosyalarını manuel olarak temizle.
    
    Args:
        session_dir: Session dosyaları dizini
        max_age_hours: Maksimum dosya yaşı
        
    Returns:
        Cleanup istatistikleri
    """
    if session_dir is None:
        from flask import current_app
        session_dir = os.path.join(current_app.instance_path, "sessions")
    
    cleanup = SessionFileCleanup(session_dir, max_age_hours)
    return cleanup.cleanup_old_sessions()


# =============================================================================
# CONTEXT-AWARE RESOURCE MANAGEMENT
# =============================================================================
class ResourceManager:
    """
    Context-aware resource manager.
    
    Flask g object ile per-request resource lifecycle yönetimi.
    """
    
    @staticmethod
    def get_http_session():
        """
        Request'e özgü HTTP session'ı al.
        
        Her request için yeni bir session oluşturulur ve
        request sonunda otomatik olarak kapatılır.
        
        Returns:
            requests.Session objesi veya None
        """
        if hasattr(g, 'http_session'):
            return g.http_session
        
        # Session yoksa, uyarı log'la
        logger.warning("HTTP session not found in g context. Make sure @app.before_request creates it.")
        return None
    
    @staticmethod
    def cleanup_resources():
        """
        Request sonunda kaynakları temizle.
        
        Bu fonksiyon @app.teardown_request decorator'ı ile çağrılır.
        """
        # HTTP session'ı kapat
        if hasattr(g, 'http_session'):
            try:
                g.http_session.close()
                logger.debug("HTTP session closed")
            except Exception as e:
                logger.error(f"Error closing HTTP session: {e}")
        
        # Diğer kaynakları temizle
        if hasattr(g, 'db_session'):
            try:
                g.db_session.close()
                logger.debug("DB session closed")
            except Exception as e:
                logger.error(f"Error closing DB session: {e}")
        
        if hasattr(g, 'cache'):
            try:
                del g.cache
                logger.debug("Cache cleared from g")
            except Exception as e:
                logger.error(f"Error clearing cache: {e}")


# =============================================================================
# DATABASE CONNECTION POOLING
# =============================================================================
class DatabaseConnectionPool:
    """
    Database connection pool manager.
    
    SQLAlchemy ile connection pooling ayarlarını yönetir.
    """
    
    @staticmethod
    def configure_pool(app, pool_size: int = 10, max_overflow: int = 20):
        """
        Connection pool yapılandırmasını ayarla.
        
        Args:
            app: Flask app instance
            pool_size: Pool boyutu
            max_overflow: Maksimum overflow
        """
        # SQLAlchemy config
        app.config['SQLALCHEMY_POOL_SIZE'] = pool_size
        app.config['SQLALCHEMY_POOL_TIMEOUT'] = 30
        app.config['SQLALCHEMY_POOL_RECYCLE'] = 3600
        app.config['SQLALCHEMY_POOL_PRE_PING'] = True
        app.config['SQLALCHEMY_MAX_OVERFLOW'] = max_overflow
        
        logger.info(f"Database connection pool configured: size={pool_size}, max_overflow={max_overflow}")
    
    @staticmethod
    def get_pool_status(db) -> dict:
        """
        Connection pool durumunu döndür.
        
        Args:
            db: Flask-SQLAlchemy db objesi
            
        Returns:
            Pool status dict
        """
        try:
            engine = db.engine
            pool = engine.pool
            
            return {
                "pool_size": pool.size(),
                "checked_in_connections": pool.checkedin(),
                "checked_out_connections": pool.checkedout(),
                "overflow": pool.overflow(),
                "checked_in_overflow": pool.checkedin_overflow()
            }
        except Exception as e:
            logger.error(f"Error getting pool status: {e}")
            return {"error": str(e)}


# =============================================================================
# MEMORY PROFILING UTILITIES
# =============================================================================
def log_memory_usage(message: str = "Memory usage"):
    """
    Bellek kullanımını log'la.
    
    Args:
        message: Log mesajı
    """
    try:
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        logger.info(f"{message}: RSS={memory_info.rss / 1024 / 1024:.2f}MB, VMS={memory_info.vms / 1024 / 1024:.2f}MB")
    
    except ImportError:
        # psutil yüklü değilse, basit logging
        logger.debug(f"{message} (psutil not installed for detailed info)")


def check_memory_leak(threshold_mb: int = 500) -> bool:
    """
    Bellek leak kontrolü yap.
    
    Args:
        threshold_mb: Bellek threshold (MB)
        
    Returns:
        True if leak detected, False otherwise
    """
    try:
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        rss_mb = memory_info.rss / 1024 / 1024
        
        if rss_mb > threshold_mb:
            logger.warning(f"High memory usage detected: {rss_mb:.2f}MB (threshold: {threshold_mb}MB)")
            return True
        
        return False
    
    except ImportError:
        logger.debug("Memory leak check skipped (psutil not installed)")
        return False


# =============================================================================
# FLASK EXTENSION INTEGRATION
# =============================================================================
def init_resource_management(app):
    """
    Resource management'ı Flask uygulamasına entegre et.
    
    Args:
        app: Flask app instance
    """
    # Teardown handler'ı kaydet
    app.teardown_appcontext(ResourceManager.cleanup_resources)
    
    # Session cleanup scheduler'ını başlat (development modunda değilse)
    if not app.debug and not app.testing:
        init_cleanup_scheduler(app)
    
    logger.info("Resource management initialized")


if __name__ == "__main__":
    # Test
    print("Testing resource cleanup...")
    
    # Session cleanup test
    cleanup = SessionFileCleanup("./test_sessions", max_age_hours=1)
    stats = cleanup.cleanup_old_sessions()
    print(f"✅ Session cleanup test: {stats}")
    
    # Memory usage test
    log_memory_usage("Test memory")
    
    print("✅ Resource cleanup module working!")
