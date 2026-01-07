#!/usr/bin/env python3
"""
ai_interpretations.py dosyasındaki print statement'larını logger ile değiştirir
"""
import re

def fix_ai_interpretations():
    file_path = "D:/astro-ai-predictor/backend/flask_app/ai_interpretations.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Print statement'larını logger ile değiştir
    replacements = {
        r'print\(f"Data: \{data\}"\)': 'logging.debug(f"AI yorum isteği - Data: {data}")',
        r'print\("prompt", prompt\)': 'logging.debug(f"Generated prompt: {prompt[:200]}...")',
        'print(f"Uyarı:': 'logging.warning(f"',
        'print(f"Hyperbolic': 'logging.error(f"',
        'print(f"Transit': 'logging.debug(f"',
    }
    
    for pattern, replacement in replacements.items():
        content = re.sub(pattern, replacement, content)
    
    # Type hint düzeltmeleri
    # TypedDict import'u ekle (eğer yoksa)
    if 'from typing import' in content and 'TypedDict' not in content:
        content = content.replace(
            'from typing import',
            'from typing import TypedDict,'
        )
    
    # OpenAI type hint hatalarını düzelt
    # completion.choices[0].message.content -> completion.choices[0].message.content if exists
    content = re.sub(
        r'completion\.choices\[0\]\.message\.content\.strip\(\)',
        'completion.choices[0].message.content.strip() if completion.choices and completion.choices[0].message.content else ""',
        content
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ ai_interpretations.py düzeltmeleri tamamlandı")
    print("   - print() statement'ları logger.debug() ile değiştirildi")
    print("   - Type hint hataları düzeltildi")

if __name__ == "__main__":
    fix_ai_interpretations()
