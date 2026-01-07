"""
Frontend Asset Optimization Script
===================================

Bu script, frontend asset'lerini optimize eder:
- JavaScript dosyalarını minify eder
- CSS dosyalarını minify eder
- Image lazy loading attribute'larını ekler
- Critical CSS inline alır

Kullanım:
    python frontend_optimize.py --minify-js --minify-css --add-lazy-loading
"""

import os
import sys
import json
import re
import subprocess
from pathlib import Path
from typing import List, Tuple
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# =============================================================================
# JAVASCRIPT MINIFICATION
# =============================================================================
def minify_javascript(input_file: str, output_file: str = None) -> bool:
    """
    JavaScript dosyasını minify eder.
    
    Args:
        input_file: Girdi dosyası
        output_file: Çıktı dosyası (varsayılan: input_file.min.js)
        
    Returns:
        True if successful, False otherwise
    """
    if output_file is None:
        output_file = input_file.replace(".js", ".min.js")
    
    try:
        # Dosyayı oku
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basit minification (comments ve boşlukları kaldır)
        # Single-line comments
        content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
        
        # Multi-line comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # Boş satırları kaldır
        content = re.sub(r'\n\s*\n', '\n', content)
        
        # Gereksiz boşlukları kaldır
        content = re.sub(r'\s+', ' ', content)
        
        # Write minified content
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        
        # Dosya boyutlarını karşılaştır
        original_size = os.path.getsize(input_file)
        minified_size = os.path.getsize(output_file)
        reduction = (1 - minified_size / original_size) * 100
        
        logger.info(f"✅ JS Minified: {input_file} -> {output_file} ({reduction:.1f}% reduction)")
        return True
    
    except Exception as e:
        logger.error(f"❌ JS Minification failed for {input_file}: {e}")
        return False


# =============================================================================
# CSS MINIFICATION
# =============================================================================
def minify_css(input_file: str, output_file: str = None) -> bool:
    """
    CSS dosyasını minify eder.
    
    Args:
        input_file: Girdi dosyası
        output_file: Çıktı dosyası (varsayılan: input_file.min.css)
        
    Returns:
        True if successful, False otherwise
    """
    if output_file is None:
        output_file = input_file.replace(".css", ".min.css")
    
    try:
        # Dosyayı oku
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Comments kaldır
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # Boşlukları kaldır
        content = re.sub(r'\s+', ' ', content)
        
        # Gereksiz boşlukları temizle
        content = re.sub(r'\s*([{}:;,])\s*', r'\1', content)
        
        # Write minified content
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        
        # Dosya boyutlarını karşılaştır
        original_size = os.path.getsize(input_file)
        minified_size = os.path.getsize(output_file)
        reduction = (1 - minified_size / original_size) * 100
        
        logger.info(f"✅ CSS Minified: {input_file} -> {output_file} ({reduction:.1f}% reduction)")
        return True
    
    except Exception as e:
        logger.error(f"❌ CSS Minification failed for {input_file}: {e}")
        return False


# =============================================================================
# LAZY LOADING ATTRIBUTE EKLEME
# =============================================================================
def add_lazy_loading_to_template(template_file: str) -> bool:
    """
    HTML template'ine lazy loading attribute'larını ekler.
    
    Args:
        template_file: Template dosyası
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Dosyayı oku
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # img tag'lerine loading="lazy" ekle
        # img tag'lerini bul
        img_pattern = r'<img(?![^>]*loading=)([^>]*)>'
        
        def add_loading_attr(match):
            img_tag = match.group(0)
            attrs = match.group(1)
            
            # Eğer src varsa ve loading attribute yoksa ekle
            if 'src=' in attrs:
                return f'<img{attrs} loading="lazy">'
            return img_tag
        
        # Replace
        new_content = re.sub(img_pattern, add_loading_attr, content)
        
        # Değişiklik varsa yaz
        if new_content != content:
            # Backup al
            backup_file = template_file + '.backup'
            shutil.copy2(template_file, backup_file)
            
            # Write updated content
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            logger.info(f"✅ Added lazy loading to: {template_file} (backup: {backup_file})")
            return True
        else:
            logger.debug(f"No changes needed for: {template_file}")
            return True
    
    except Exception as e:
        logger.error(f"❌ Failed to add lazy loading to {template_file}: {e}")
        return False


# =============================================================================
# SCRIPT VE STYLE DEFER/ASYNC EKLEME
# =============================================================================
def add_async_defer_to_template(template_file: str) -> bool:
    """
    HTML template'indeki script ve style tag'lerine async/defer attribute'larını ekler.
    
    Args:
        template_file: Template dosyası
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Dosyayı oku
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # External script'lere defer ekle (body'de olanlar hariç)
        content = re.sub(
            r'<script(?![^>]*(?:defer|async))([^>]*)src=["\']http',
            r'<script defer\1src="http',
            content
        )
        
        # CSS'i head'de tut ama async olarak yükle (critical CSS extraction için placeholder)
        # Bu, daha gelişmiş bir optimizasyon - şimdilik basit implementasyon
        
        # Değişiklik varsa yaz
        if content != original_content:
            # Backup al
            import shutil
            backup_file = template_file + '.backup'
            shutil.copy2(template_file, backup_file)
            
            # Write updated content
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"✅ Added async/defer to: {template_file} (backup: {backup_file})")
            return True
        else:
            logger.debug(f"No changes needed for: {template_file}")
            return True
    
    except Exception as e:
        logger.error(f"❌ Failed to add async/defer to {template_file}: {e}")
        return False


# =============================================================================
# PACKAGE.JSON GÜNCELLEME
# =============================================================================
def update_package_json():
    """
    package.json'a minification script'leri ekler.
    """
    package_json_path = "package.json"
    
    if not os.path.exists(package_json_path):
        logger.warning(f"package.json not found: {package_json_path}")
        return False
    
    try:
        # Dosyayı oku
        with open(package_json_path, 'r', encoding='utf-8') as f:
            package_data = json.load(f)
        
        # Scripts ekle
        if "scripts" not in package_data:
            package_data["scripts"] = {}
        
        package_data["scripts"].update({
            "minify:js": "python frontend_optimize.py --minify-js",
            "minify:css": "python frontend_optimize.py --minify-css",
            "minify:all": "python frontend_optimize.py --minify-js --minify-css",
            "optimize": "python frontend_optimize.py --minify-js --minify-css --add-lazy-loading"
        })
        
        # Write updated package.json
        with open(package_json_path, 'w', encoding='utf-8') as f:
            json.dump(package_data, f, indent=2)
        
        logger.info("✅ Updated package.json with minification scripts")
        return True
    
    except Exception as e:
        logger.error(f"❌ Failed to update package.json: {e}")
        return False


# =============================================================================
# BATCH OPTIMIZATION
# =============================================================================
def optimize_all_assets(
    minify_js: bool = True,
    minify_css: bool = True,
    add_lazy_loading: bool = True,
    add_async_defer: bool = True
) -> dict:
    """
    Tüm frontend asset'lerini optimize eder.
    
    Args:
        minify_js: JS minification yap
        minify_css: CSS minification yap
        add_lazy_loading: Lazy loading attribute'larını ekle
        add_async_defer: Async/defer attribute'larını ekle
        
    Returns:
        Optimizasyon istatistikleri
    """
    stats = {
        "js_minified": 0,
        "css_minified": 0,
        "lazy_loading_added": 0,
        "async_defer_added": 0,
        "errors": []
    }
    
    # JS dosyalarını bul
    if minify_js:
        static_dir = Path("static/js")
        if static_dir.exists():
            for js_file in static_dir.glob("*.js"):
                if not js_file.name.endswith(".min.js"):
                    if minify_javascript(str(js_file)):
                        stats["js_minified"] += 1
    
    # CSS dosyalarını bul
    if minify_css:
        static_dir = Path("static/css")
        if static_dir.exists():
            for css_file in static_dir.glob("*.css"):
                if not css_file.name.endswith(".min.css"):
                    if minify_css(str(css_file)):
                        stats["css_minified"] += 1
    
    # Template'lere lazy loading ekle
    if add_lazy_loading:
        templates_dir = Path("templates")
        if templates_dir.exists():
            for template_file in templates_dir.glob("*.html"):
                if add_lazy_loading_to_template(str(template_file)):
                    stats["lazy_loading_added"] += 1
    
    # Template'lere async/defer ekle
    if add_async_defer:
        templates_dir = Path("templates")
        if templates_dir.exists():
            for template_file in templates_dir.glob("*.html"):
                if add_async_defer_to_template(str(template_file)):
                    stats["async_defer_added"] += 1
    
    return stats


# =============================================================================
# MAIN
# =============================================================================
def main():
    """Ana fonksiyon - CLI argument parser."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Frontend Asset Optimization")
    parser.add_argument("--minify-js", action="store_true", help="Minify JavaScript files")
    parser.add_argument("--minify-css", action="store_true", help="Minify CSS files")
    parser.add_argument("--add-lazy-loading", action="store_true", help="Add lazy loading to images")
    parser.add_argument("--add-async-defer", action="store_true", help="Add async/defer to scripts")
    parser.add_argument("--all", action="store_true", help="Run all optimizations")
    parser.add_argument("--update-package-json", action="store_true", help="Update package.json scripts")
    
    args = parser.parse_args()
    
    # Hiçbir argüman verilmezse, yardım göster
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    # --all verilirse tümünü yap
    if args.all:
        args.minify_js = True
        args.minify_css = True
        args.add_lazy_loading = True
        args.add_async_defer = True
    
    # package.json güncelle
    if args.update_package_json:
        update_package_json()
    
    # Optimizasyonları çalıştır
    stats = optimize_all_assets(
        minify_js=args.minify_js,
        minify_css=args.minify_css,
        add_lazy_loading=args.add_lazy_loading,
        add_async_defer=args.add_async_defer
    )
    
    # Sonuçları yazdır
    print("\n" + "=" * 60)
    print("FRONTEND OPTIMIZATION RESULTS")
    print("=" * 60)
    print(f"✅ JavaScript files minified: {stats['js_minified']}")
    print(f"✅ CSS files minified: {stats['css_minified']}")
    print(f"✅ Lazy loading added: {stats['lazy_loading_added']} templates")
    print(f"✅ Async/defer added: {stats['async_defer_added']} templates")
    
    if stats['errors']:
        print(f"\n❌ Errors: {len(stats['errors'])}")
        for error in stats['errors']:
            print(f"   - {error}")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
