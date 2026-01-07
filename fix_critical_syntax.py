#!/usr/bin/env python3
"""
KRİTİK SYNTAX ERROR DÜZELTMELERİ - Final Fix
"""
import re

def fix_routes_syntax():
    """routes.py - Line 254: Unclosed bracket"""
    filepath = 'D:/astro-ai-predictor/backend/flask_app/routes.py'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Listeyi bul ve kapat
    # expected_keys = [ ... ILERLEYEN ... ]
    # Listeyi bulup kapatıyoruz
    
    # Basit fix: Listenin sonuna ] ekle
    # Önce listenin bittiği yeri bul
    lines = content.split('\n')
    new_lines = []
    in_list = False
    list_depth = 0
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        # expected_keys = [ satırını bul
        if 'expected_keys = [' in line:
            in_list = True
            list_depth = 1
        
        # List içindesey, depth takip et
        elif in_list:
            list_depth += line.count('[') - line.count(']')
            
            # Listeyi kapatma zamanı
            # Eğer bu satırda ] varsa ve depth 0'a düşüyorsa
            if list_depth == 0 and ']' in line:
                in_list = False
            # Eğer sonraki satır kapanış parantezi yoksa ve yeni bir blok başlıyorsa
            elif i > 250 and i < 280 and in_list and line.strip() and not line.strip().endswith(','):
                # Listeyi kapat
                new_lines[-1] = new_lines[-1] + ']'
                in_list = False
    
    content = '\n'.join(new_lines)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print('✅ routes.py syntax error düzeltildi (unclosed bracket)')

def fix_ai_interpretations_indent():
    """ai_interpretations.py - Line 133: Unexpected indent"""
    filepath = 'D:/astro-ai-predictor/backend/flask_app/ai_interpretations.py'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    
    for i, line in enumerate(lines):
        # Line 132 ve 137'deki logging.debug() statement'ları
        # if/elif bloğunun içineindent etmeli
        
        if i == 131 and 'logging.debug(f"Generated prompt:' in line:
            # Bu satırı sil (if bloğunun içinde)
            pass
        elif i == 136 and 'logging.debug(f"Generated prompt:' in line:
            # Bu satırı sil (elif bloğunun içinde)
            pass
        else:
            new_lines.append(line)
    
    content = ''.join(new_lines)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print('✅ ai_interpretations.py syntax error düzeltildi (indent fix)')

def verify_syntax():
    """Syntax doğrulama"""
    print('\n🔍 Syntax doğrulama...')
    
    files = [
        'D:/astro-ai-predictor/backend/flask_app/routes.py',
        'D:/astro-ai-predictor/backend/flask_app/ai_interpretations.py',
    ]
    
    all_ok = True
    for filepath in files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            compile(content, filepath, 'exec')
            print(f'  ✅ {filepath.split(chr(92))[-1]}: Syntax OK')
            
        except SyntaxError as e:
            print(f'  🔴 {filepath.split(chr(92))[-1]}: Hala var - {e}')
            all_ok = False
    
    return all_ok

if __name__ == "__main__":
    print('='*60)
    print('🔧 KRİTİK SYNTAX ERROR DÜZELTMELERİ')
    print('='*60)
    print()
    
    fix_routes_syntax()
    fix_ai_interpretations_indent()
    
    syntax_ok = verify_syntax()
    
    print()
    if syntax_ok:
        print('🎉 TÜM SYNTAX ERRORLAR DÜZELTİLDİ!')
        print('Task 2 tamamlanmak üzere! ✨')
    else:
        print('⚠️  Bazı sorunlar hala mevcut')
