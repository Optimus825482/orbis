"""
Task 2: Import Hatalarını ve Ulaşılamayan Kodları Düzeltme - DOĞRULAMA SCRIPT'i
"""

import os
import sys
from pathlib import Path

# Flask app dizinini path'e ekle
sys.path.insert(0, str(Path(__file__).parent))

def check_file_syntax(filepath):
    """Dosyanın Python syntax kontrolünü yap."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            compile(f.read(), filepath, 'exec')
        return True, "✅ Syntax OK"
    except SyntaxError as e:
        return False, f"❌ Syntax Error: {e}"
    except Exception as e:
        return False, f"❌ Error: {e}"

def check_imports(filepath):
    """Dosyada sorunlu import'ları kontrol et."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # models.py import kontrolü
    if 'from models import' in content:
        issues.append("❌ models.py import'u mevcut (models.py dosyası yok)")
    
    # Kullanılmayan import kontrolü
    unused_imports = []
    if 'from collections.abc import' in content and 'Mapping' not in content:
        unused_imports.append("collections.abc")
    if 'import os.name' in content:
        unused_imports.append("os.name (geçersiz import)")
    
    if unused_imports:
        issues.append(f"⚠️ Kullanılmayan import'lar: {', '.join(unused_imports)}")
    
    return issues if issues else ["✅ Import'lar temiz"]

def check_unreachable_code(filepath):
    """Ulaşılamayan kodları kontrol et."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    issues = []
    
    # Basit kontrol: return, break, continue sonrası kod
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith(('return ', 'break', 'continue', 'raise ')):
            # Sonraki 3 satıra bak
            for j in range(i, min(i+3, len(lines))):
                next_line = lines[j].strip()
                if next_line and not next_line.startswith('#') and not next_line.startswith(('elif', 'else', 'finally', 'except')):
                    if i < len(lines):
                        issues.append(f"⚠️ Satır {i+1} sonrası muhtemelen ulaşılamaz kod: {next_line[:50]}")
                    break
    
    return issues if issues else ["✅ Ulaşılamayan kod yok"]

def main():
    print("=" * 80)
    print("TASK 2 DOĞRULAMA RAPORU")
    print("=" * 80)
    
    files_to_check = [
        'app.py',
        'routes.py',
        'extensions.py',
        'ai_interpretations.py',
        'config.py',
        'env_config.py',
    ]
    
    all_passed = True
    
    for filename in files_to_check:
        filepath = f"D:/astro-ai-predictor/backend/flask_app/{filename}"
        if not os.path.exists(filepath):
            print(f"\n❌ {filename}: DOSYA BULUNAMADI")
            all_passed = False
            continue
        
        print(f"\n📄 {filename}")
        print("-" * 60)
        
        # Syntax kontrolü
        syntax_ok, syntax_msg = check_file_syntax(filepath)
        print(f"  Syntax: {syntax_msg}")
        if not syntax_ok:
            all_passed = False
            continue
        
        # Import kontrolü
        import_issues = check_imports(filepath)
        for issue in import_issues:
            print(f"  Import: {issue}")
            if issue.startswith("❌"):
                all_passed = False
        
        # Ulaşılamayan kod kontrolü
        if filename in ['routes.py', 'app.py', 'ai_interpretations.py']:
            unreachable_issues = check_unreachable_code(filepath)
            for issue in unreachable_issues:
                print(f"  Code: {issue}")
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ TASK 2 TAMAMLANDI - Tüm kontroller başarılı!")
    else:
        print("❌ TASK 2 DEVAM EDİYOR - Bazı sorunlar çözülmeli")
    print("=" * 80)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
