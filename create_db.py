from __init__ import create_app
from extensions import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def recreate_db():
    """Veritabanını yeniden oluştur"""
    app = create_app()
    
    with app.app_context():
        logger.info("Veritabanı tabloları siliniyor...")
        db.drop_all()
        
        logger.info("Veritabanı tabloları yeniden oluşturuluyor...")
        db.create_all()
        
        logger.info("Veritabanı başarıyla yeniden oluşturuldu!")

if __name__ == '__main__':
    recreate_db()