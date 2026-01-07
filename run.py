import sys
import os

# Geçerli dizini modül arama yoluna ekle
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# __init__.py'den create_app fonksiyonunu import et
from __init__ import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8088)
