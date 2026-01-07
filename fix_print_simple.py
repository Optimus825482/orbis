#!/usr/bin/env python3
"""
ai_interpretations.py - Basit print -> logger dönüşümü
"""

def fix_print_statements():
    file_path = "D:/astro-ai-predictor/backend/flask_app/ai_interpretations.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    for i, line in enumerate(lines):
        # print() çağrılarını logger ile değiştir
        if 'print(f"Data: {data}")' in line:
            new_lines.append('        logging.debug(f"AI yorum isteği - Data: {data}")\n')
        elif 'print("prompt", prompt)' in line:
            new_lines.append('        logging.debug(f"Generated prompt: {prompt[:200]}...")\n')
        elif 'print(f"Uyarı:' in line:
            new_lines.append(line.replace('print(f"Uyarı:', 'logging.warning(f"'))
        elif 'print(f"Hyperbolic API Hatası:' in line:
            new_lines.append(line.replace('print(f"Hyperbolic API Hatası:', 'logging.error(f"Hyperbolic API Hatası:'))
        elif 'print(#' in line and 'm.name' in line:
            # Comment satırlarını koru
            new_lines.append(line)
        else:
            new_lines.append(line)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("✅ print() statement'ları logger ile değiştirildi")

if __name__ == "__main__":
    fix_print_statements()
