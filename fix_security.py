#!/usr/bin/env python3
"""
Güvenlik hardcoding fix script - HYPERBOLIC_API_KEY'i kaldırır
"""
import os

def fix_app_py():
    """app.py dosyasındaki hardcoded HYPERBOLIC_API_KEY'i kaldırır"""
    file_path = "D:/astro-ai-predictor/backend/flask_app/app.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Lines 71-74 arasını bul ve değiştir (index 70-73)
    new_lines = []
    skip_next = 0
    
    for i, line in enumerate(lines):
        if skip_next > 0:
            skip_next -= 1
            continue
        
        # HYPERBOLIC_API_KEY tanımını bul
        if 'HYPERBOLIC_API_KEY = os.getenv(' in line:
            # Bu satırı ve sonraki 3 satırı atla, yorumla değiştir
            new_lines.append("# HYPERBOLIC_API_KEY artık config.py'den geliyor\n")
            new_lines.append("# Kullanım: app.config['HYPERBOLIC_API_KEY']\n")
            # 2 satır daha atla (kapatma parantezi ve boşluk)
            skip_next = 3
        else:
            new_lines.append(line)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("✅ app.py HYPERBOLIC_API_KEY hardcoded değeri kaldırıldı")

def fix_references():
    """app.py'deki HYPERBOLIC_API_KEY referanslarını app.config['HYPERBOLIC_API_KEY'] ile değiştirir"""
    file_path = "D:/astro-ai-predictor/backend/flask_app/app.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Referansları değiştir (yorum satırlarındaki hariç)
    import re
    
    # Authorization: Bearer {HYPERBOLIC_API_KEY} -> Authorization: Bearer {app.config["HYPERBOLIC_API_KEY"]}
    content = re.sub(
        r'Authorization: f"Bearer \{HYPERBOLIC_API_KEY\}"',
        'Authorization: f"Bearer {app.config[\'HYPERBOLIC_API_KEY\']}"',
        content
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ HYPERBOLIC_API_KEY referansları app.config'e güncellendi")

if __name__ == "__main__":
    print("🔒 Güvenlik fix script'i başlatılıyor...")
    fix_app_py()
    fix_references()
    print("✅ Güvenlik düzeltmeleri tamamlandı!")
