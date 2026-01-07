#!/usr/bin/env python3
"""
routes.py - Critical syntax error fix
"""
import re

def fix_routes_syntax():
    filepath = 'D:/astro-ai-predictor/backend/flask_app/routes.py'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Yanlış syntax: transit_info=transit_info, analysis_type="natal")
    # Düzelt: transit_info=transit_info)
    content = re.sub(
        r'transit_info=transit_info,\s*analysis_type="natal"\)',
        r'transit_info=transit_info)',
        content
    )
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print('✅ routes.py syntax error düzeltildi')
        print('   analysis_type parametresi kaldırıldı')
        return True
    else:
        print('⚠️  Değişiklik gerekmiyor (zaten düzeltildi)')
        return False

if __name__ == "__main__":
    fix_routes_syntax()
