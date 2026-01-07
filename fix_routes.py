#!/usr/bin/env python3
"""
routes.py dosyasındaki sorunları düzelten script
"""
import re

def fix_routes_py():
    """routes.py dosyasını düzeltir"""
    file_path = "D:/astro-ai-predictor/backend/flask_app/routes.py"
    
    print("🔧 routes.py düzeltme işlemi başlatılıyor...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Duplicate import'ları temizle
    # İlk 26 satırın tekrarını bul ve kaldır
    lines = content.split('\n')
    
    # İlk import bloğunu bul
    first_import_end = -1
    for i, line in enumerate(lines):
        if i > 20 and line.strip() == 'SESSION_DIR = os.path.join(os.path.dirname(__file__)':
            first_import_end = i
            break
    
    if first_import_end > 0:
        # İlk bölümü al
        cleaned_lines = lines[:first_import_end + 5]
        
        # Duplicate import bloğunu atla (second occurrence)
        # "from os import name" ile başlayan ikinci bölümü bul ve atla
        skip_until = -1
        for i in range(first_import_end + 5, len(lines)):
            if lines[i].strip() == 'from os import name':
                # İkinci import bloğu başladı, bunu atla
                skip_until = i + 28  # Yaklaşık 28 satır atla
                break
        
        if skip_until > 0:
            # Temiz içeriği birleştir
            cleaned_lines.extend(lines[skip_until:])
            content = '\n'.join(cleaned_lines)
    
    # 2. Unreachable code'u temizle (settings fonksiyonunda)
    # Bu pattern'i bul ve unreachable return'u sil
    content = re.sub(
        r'(return render_template\("settings\.html", settings=current_settings\))\s+# Misafir veya.*?return render_template\("index\.html"\)',
        r'\1',
        content,
        flags=re.DOTALL
    )
    
    # 3. calculate_astro_data çağrılarında analysis_type parametresini ara ve ekle
    # Pattern: calculate_astro_data(...) - analysis_type eksikse ekle
    def add_analysis_type(match):
        call = match.group(0)
        # Eğer analysis_type zaten varsa dokunma
        if 'analysis_type' in call:
            return call
        # Son parantezden önce ekle
        return call.rstrip(')') + ', analysis_type="natal")'
    
    # Basit bir yaklaşım - sadece calculate_astro_data çağrılarını bul
    content = re.sub(
        r'calculate_astro_data\([^)]*\)(?!\s*,\s*analysis_type)',
        lambda m: m.group(0).replace(')', ', analysis_type="natal")') if m.group(0).count('(') == m.group(0).count(')') else m.group(0),
        content
    )
    
    # Düzeltmeyi kaydet
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ routes.py düzeltme tamamlandı!")
    print("   - Duplicate import'lar temizlendi")
    print("   - Unreachable code kaldırıldı")
    print("   - analysis_type parametreleri eklendi")

if __name__ == "__main__":
    fix_routes_py()
