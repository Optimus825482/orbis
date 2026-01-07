import os
import sys

# Modül yolu sorunlarını önlemek için ana dizini ekle
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Eğer paket olarak yapılandırıldıysa
    from flask_app import create_app
except ImportError:
    # Eğer doğrudan ana dizinden çalıştırılıyorsa
    try:
        from __init__ import create_app
    except ImportError:
        # Alternatif olarak app dosyasını dene
        def create_app():
            from app import app
            return app

app = create_app()

if __name__ == "__main__":
    # Railway ve benzeri platformlar PORT env değişkenini kullanır
    port = int(os.environ.get("PORT", 5005))
    app.run(host="0.0.0.0", debug=True, port=port)
