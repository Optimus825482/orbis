#!/usr/bin/env python3
"""
TOPSAL BATCH REFACTOR SCRIPT
Tüm kritik sorunları tek seferde düzeltir
"""
import re
import os
from pathlib import Path

BASE_PATH = Path('D:/astro-ai-predictor/backend/flask_app')

def fix_app_py():
    """app.py - Hardcoded JWT token ve analysis_type düzeltmeleri"""
    filepath = BASE_PATH / 'app.py'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. Hardcoded HYPERBOLIC_API_KEY JWT token'ını kaldır
    jwt_pattern = r'HYPERBOLIC_API_KEY = os\.getenv\(\s*"HYPERBOLIC_API_KEY",\s*"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9[^"]*",\s*\)'
    content = re.sub(jwt_pattern, 'HYPERBOLIC_API_KEY = Config.HYPERBOLIC_API_KEY', content)
    
    # 2. print() statement'ları temizle
    content = re.sub(r'print\(([^)]+)\)', r'logging.debug(\1)', content)
    
    # 3. Config import'u kontrol et
    if 'from config import Config' not in content:
        # Import kısmına Config ekle
        content = content.replace(
            'from dotenv import load_dotenv',
            'from config import Config\nfrom dotenv import load_dotenv'
        )
    
    # Değişiklik varsa kaydet
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print('✅ app.py düzeltildi')
        return True
    else:
        print('⏭️  app.py zaten temiz')
        return False

def fix_routes_py():
    """routes.py - Syntax error ve print statement düzeltmeleri"""
    filepath = BASE_PATH / 'routes.py'
    
    if not filepath.exists():
        print('❌ routes.py bulunamadı')
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    fixes = []
    
    # 1. Syntax error: , analysis_type="natal") yanlış yerde
    # Bu pattern'i düzelt: transit_info=transit_info, , analysis_type="natal")
    content = re.sub(
        r',\s*,\s*analysis_type="natal"\)',
        ', analysis_type="natal")',
        content
    )
    if content != original_content:
        fixes.append('Syntax error düzeltildi')
    
    # 2. print() statement'ları logger ile değiştir
    new_content = re.sub(r'print\(([^)]+)\)', r'logging.debug(\1)', content)
    if new_content != content:
        fixes.append('print() → logging.debug()')
        content = new_content
    
    # Değişiklik varsa kaydet
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'✅ routes.py düzeltildi: {", ".join(fixes)}')
        return True
    else:
        print('⏭️  routes.py zaten temiz')
        return False

def fix_ai_interpretations_py():
    """ai_interpretations.py - Kalan print statement'ları ve type hint'ler"""
    filepath = BASE_PATH / 'ai_interpretations.py'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    fixes = []
    
    # 1. Kalan print() statement'ları
    lines = content.split('\n')
    new_lines = []
    
    for i, line in enumerate(lines):
        # print(m.name) - model isimleri (bunları koru veya yorum satırı yap)
        if 'print(m.name)' in line and '#' not in line:
            new_lines.append('    # ' + line.strip())  # Yorum satırı yap
            fixes.append('Model name print yorumlandı')
        # Diğer print() statement'ları
        elif 'print(' in line and 'logging' not in line:
            # Basit print → logging dönüşümü
            new_line = re.sub(r'print\(', 'logging.debug(', line, count=1)
            new_lines.append(new_line)
            fixes.append('print() → logging.debug()')
        else:
            new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    # 2. TypedDict import'u ekle
    if 'from typing import' in content and 'TypedDict' not in content:
        content = content.replace(
            'from typing import',
            'from typing import TypedDict,'
        )
        fixes.append('TypedDict import eklendi')
    
    # Değişiklik varsa kaydet
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'✅ ai_interpretations.py düzeltildi: {", ".join(fixes)}')
        return True
    else:
        print('⏭️  ai_interpretations.py zaten temiz')
        return False

def fix_astro_calculations_py():
    """astro_calculations.py - Print statement'ları temizle"""
    filepath = BASE_PATH / 'astro_calculations.py'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. print() statement'larını logger ile değiştir
    # Debug print'leri
    content = re.sub(
        r'print\(f"[^"]*\{[^}]+\}[^"]*"\)',
        lambda m: f'logging.debug({m.group(0)[6:]})',
        content
    )
    
    # 2. Logger import'u kontrol et
    if 'import logging' not in content:
        content = 'import logging\n\n' + content
    
    # Değişiklik varsa kaydet
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print('✅ astro_calculations.py düzeltildi')
        return True
    else:
        print('⏭️  astro_calculations.py zaten temiz')
        return False

def run_batch_refactor():
    """Tüm batch refactor işlemlerini çalıştır"""
    print('='*60)
    print('🚀 TOPSAL BATCH REFACTOR BAŞLATILIYOR...')
    print('='*60)
    print()
    
    results = {
        'app.py': fix_app_py(),
        'routes.py': fix_routes_py(),
        'ai_interpretations.py': fix_ai_interpretations_py(),
        'astro_calculations.py': fix_astro_calculations_py(),
    }
    
    print()
    print('='*60)
    print('📊 BATCH REFACTOR ÖZETİ')
    print('='*60)
    
    fixed_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    for filename, fixed in results.items():
        status = '✅ DÜZELTİLDİ' if fixed else '⏭️  TEMİZ'
        print(f'{filename}: {status}')
    
    print()
    print(f'Toplam: {fixed_count}/{total_count} dosya düzeltildi')
    
    if fixed_count > 0:
        print()
        print('🎉 BATCH REFACTOR TAMAMLANDI!')
    else:
        print()
        print('✨ Tüm dosyalar zaten temiz!')

if __name__ == "__main__":
    run_batch_refactor()
