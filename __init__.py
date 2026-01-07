import os
import sys
import logging # logging modülünü ekle

# Modül yolu sorununu çözmek için ana dizini sys.path'e ekleyelim
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import config
from extensions import db, cors, migrate

def create_app(test_config=None):
    # Flask uygulamasını oluştur ve yapılandır
    app = Flask(__name__, instance_relative_config=True)
    
    # Config sınıfını doğrudan yükle
    app.config.from_object(config.Config)
    
    if test_config is not None:
        # test yapılıyorsa, test_config'den yapılandırma yükle
        app.config.from_mapping(test_config)
    
    # instance klasörünün var olduğundan emin ol
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    

    
    # Blueprintleri kaydet
    import routes
    app.register_blueprint(routes.bp)
    
    # Filtre ve temizleyicileri ekle
    import utils
    app.jinja_env.filters["date"] = utils.format_date
    app.jinja_env.filters["time"] = utils.format_time
    app.jinja_env.filters["safe_round"] = utils.safe_round
    
    # Veritabanı ekle
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    
    # Tailwind CSS dosyasını ekle (eğer varsa)
    @app.context_processor
    def inject_tailwind_css():
        tailwind_exists = False
        if app.static_folder: # app.static_folder'ın None olup olmadığını kontrol et
            try:
                with open(os.path.join(app.static_folder, 'css/tailwind.css')) as f:
                    tailwind_exists = True
            except FileNotFoundError:
                tailwind_exists = False
            except Exception as e:
                app.logger.error(f"Tailwind CSS dosyası kontrol edilirken hata oluştu: {e}")
        else:
            app.logger.warning("app.static_folder bulunamadı, tailwind.css kontrolü atlanıyor.")
        
        return dict(tailwind_exists=tailwind_exists)
    
    return app
