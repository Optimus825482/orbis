from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

cors = CORS()
migrate = Migrate()
db = SQLAlchemy()

# Login Manager'ı tanımla
login_manager = LoginManager()
login_manager.login_view = 'main.dashboard'  # Dashboard'a yönlendir
login_manager.login_message = 'Bu sayfaya erişmek için giriş yapmalısınız.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    """User modelini dinamik import et - circular import'u önlemek için."""
    try:
        # models modülü mevcut değilse, session-based authentication kullan
        # Veritabanı devre dışı bırakıldığı için User modeli yok
        from flask import session
        return None  # Session-based auth kullanılıyor
    except ImportError:
        return None
    except Exception:
        return None


def init_db(app):
    """Database ve extension'ları başlat."""
    cors.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
