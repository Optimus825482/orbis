"""
Integration Test Suite
=======================

Bu modül, tüm refactor işlemlerinin entegrasyon testlerini içerir.
Her task'ın doğru çalıştığını doğrular.

Kullanım:
    python integration_test.py --all
    python integration_test.py --task 1
"""

import os
import sys
import subprocess
from pathlib import Path
import logging
from typing import List, Dict, Any
import json

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# =============================================================================
# TEST RESULTS
# =============================================================================
class TestResults:
    """Test sonuçlarını tutan class."""
    
    def __init__(self):
        self.results = {}
        self.total_tests = 0
        self.passed = 0
        self.failed = 0
    
    def add_result(self, task_name: str, test_name: str, passed: bool, message: str = ""):
        """Test sonucu ekle."""
        if task_name not in self.results:
            self.results[task_name] = []
        
        self.results[task_name].append({
            "test": test_name,
            "passed": passed,
            "message": message
        })
        
        self.total_tests += 1
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def print_summary(self):
        """Özeti yazdır."""
        print("\n" + "=" * 80)
        print("INTEGRATION TEST RESULTS")
        print("=" * 80)
        
        for task_name, tests in self.results.items():
            print(f"\n📋 {task_name}")
            print("-" * 60)
            
            task_passed = sum(1 for t in tests if t["passed"])
            task_total = len(tests)
            
            for test in tests:
                status = "✅" if test["passed"] else "❌"
                msg = f" - {test['message']}" if test["message"] else ""
                print(f"  {status} {test['test']}{msg}")
            
            print(f"\n  Subtotal: {task_passed}/{task_total} passed")
        
        print("\n" + "=" * 80)
        print(f"TOTAL: {self.passed}/{self.total_tests} tests passed ({self.passed/self.total_tests*100:.1f}%)")
        print("=" * 80)
        
        return self.failed == 0


# =============================================================================
# TASK 1: SECURITY TESTS
# =============================================================================
def test_task1_security(results: TestResults):
    """Task 1: Güvenlik testleri."""
    
    # Test 1: env_config.py var mı?
    if os.path.exists("env_config.py"):
        results.add_result("Task 1: Security", "env_config.py exists", True)
    else:
        results.add_result("Task 1: Security", "env_config.py exists", False, "File not found")
    
    # Test 2: config.py'de hardcoded secret var mı?
    with open("config.py", 'r', encoding='utf-8') as f:
        config_content = f.read()
    
    has_hardcoded_secret = "SECRET_KEY" in config_content and "=" in config_content
    if has_hardcoded_secret:
        # Environment variable'dan okuyor mu kontrol et
        if "get_env_required" in config_content or "os.getenv" in config_content:
            results.add_result("Task 1: Security", "Config uses env vars", True)
        else:
            results.add_result("Task 1: Security", "Config uses env vars", False, "Still using hardcoded values")
    else:
        results.add_result("Task 1: Security", "Config uses env vars", True)
    
    # Test 3: app.py'de hardcoded JWT var mı?
    with open("app.py", 'r', encoding='utf-8') as f:
        app_content = f.read()
    
    # Eski JWT token'ın hala orada olup olmadığını kontrol et
    suspicious_patterns = ["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"]
    has_hardcoded_jwt = any(pattern in app_content for pattern in suspicious_patterns)
    
    if not has_hardcoded_jwt:
        results.add_result("Task 1: Security", "No hardcoded JWT in app.py", True)
    else:
        # Comment içinde mi kontrol et
        lines_with_jwt = [line for line in app_content.split('\n') if suspicious_patterns[0] in line]
        if all('#' in line for line in lines_with_jwt):
            results.add_result("Task 1: Security", "No hardcoded JWT in app.py", True, "JWT only in comments")
        else:
            results.add_result("Task 1: Security", "No hardcoded JWT in app.py", False, "JWT still in code")
    
    # Test 4: .env.example var mı?
    if os.path.exists("env.example"):
        results.add_result("Task 1: Security", "env.example exists", True)
    else:
        results.add_result("Task 1: Security", "env.example exists", False, "File not found")


# =============================================================================
# TASK 2: IMPORT ERROR TESTS
# =============================================================================
def test_task2_imports(results: TestResults):
    """Task 2: Import error testleri."""
    
    # Test 1: routes.py syntax check
    try:
        compile(open("routes.py").read(), "routes.py", "exec")
        results.add_result("Task 2: Imports", "routes.py syntax OK", True)
    except SyntaxError as e:
        results.add_result("Task 2: Imports", "routes.py syntax OK", False, str(e))
    
    # Test 2: extensions.py'de models import'u var mı?
    with open("extensions.py", 'r', encoding='utf-8') as f:
        extensions_content = f.read()
    
    has_models_import = "from models import" in extensions_content
    if not has_models_import:
        results.add_result("Task 2: Imports", "No models.py import in extensions.py", True)
    else:
        results.add_result("Task 2: Imports", "No models.py import in extensions.py", False, "Still importing models")
    
    # Test 3: utils.py var mı?
    if os.path.exists("utils.py"):
        results.add_result("Task 2: Imports", "utils.py exists", True)
    else:
        results.add_result("Task 2: Imports", "utils.py exists", False, "File not found")


# =============================================================================
# TASK 3-4: REDIS & ASYNC TESTS
# =============================================================================
def test_task3_4_redis_async(results: TestResults):
    """Task 3-4: Redis ve Async testleri."""
    
    # Test 1: config.py'de Redis config var mı?
    with open("config.py", 'r', encoding='utf-8') as f:
        config_content = f.read()
    
    has_redis_config = "REDIS_HOST" in config_content and "SESSION_TYPE" in config_content
    results.add_result("Task 3: Redis", "Redis config in config.py", has_redis_config)
    
    # Test 2: ai_interpretations_async.py var mı?
    if os.path.exists("ai_interpretations_async.py"):
        results.add_result("Task 4: Async", "ai_interpretations_async.py exists", True)
    else:
        results.add_result("Task 4: Async", "ai_interpretations_async.py exists", False, "File not found")
    
    # Test 3: routes.py'de async wrapper var mı?
    with open("routes.py", 'r', encoding='utf-8') as f:
        routes_content = f.read()
    
    has_async_wrapper = "generate_interpretation_sync_wrapper" in routes_content
    results.add_result("Task 4: Async", "Async wrapper in routes.py", has_async_wrapper)


# =============================================================================
# TASK 5-6: UTILS & REFACTOR TESTS
# =============================================================================
def test_task5_6_utils_refactor(results: TestResults):
    """Task 5-6: Utils ve Refactor testleri."""
    
    # Test 1: utils.py'de parse_time_flexible var mı?
    with open("utils.py", 'r', encoding='utf-8') as f:
        utils_content = f.read()
    
    has_parse_time = "def parse_time_flexible" in utils_content
    results.add_result("Task 5: Utils", "parse_time_flexible in utils.py", has_parse_time)
    
    # Test 2: astro_calculations_refactored.py var mı?
    if os.path.exists("astro_calculations_refactored.py"):
        results.add_result("Task 6: Refactor", "astro_calculations_refactored.py exists", True)
    else:
        results.add_result("Task 6: Refactor", "astro_calculations_refactored.py exists", False, "File not found")
    
    # Test 3: AstroCalculator class'ı var mı?
    if os.path.exists("astro_calculations_refactored.py"):
        with open("astro_calculations_refactored.py", 'r', encoding='utf-8') as f:
            refactor_content = f.read()
        
        has_calculator_class = "class AstroCalculator" in refactor_content
        results.add_result("Task 6: Refactor", "AstroCalculator class exists", has_calculator_class)


# =============================================================================
# TASK 7-8: CACHE & EXCEPTIONS TESTS
# =============================================================================
def test_task7_8_cache_exceptions(results: TestResults):
    """Task 7-8: Cache ve Exceptions testleri."""
    
    # Test 1: cache_config.py var mı?
    if os.path.exists("cache_config.py"):
        results.add_result("Task 7: Cache", "cache_config.py exists", True)
    else:
        results.add_result("Task 7: Cache", "cache_config.py exists", False, "File not found")
    
    # Test 2: exceptions.py var mı?
    if os.path.exists("exceptions.py"):
        results.add_result("Task 8: Exceptions", "exceptions.py exists", True)
    else:
        results.add_result("Task 8: Exceptions", "exceptions.py exists", False, "File not found")
    
    # Test 3: AstroError base class var mı?
    if os.path.exists("exceptions.py"):
        with open("exceptions.py", 'r', encoding='utf-8') as f:
            exceptions_content = f.read()
        
        has_base_error = "class AstroError" in exceptions_content
        results.add_result("Task 8: Exceptions", "AstroError base class exists", has_base_error)


# =============================================================================
# TASK 9-10: RESOURCE CLEANUP & FRONTEND TESTS
# =============================================================================
def test_task9_10_resource_frontend(results: TestResults):
    """Task 9-10: Resource cleanup ve Frontend testleri."""
    
    # Test 1: resource_cleanup.py var mı?
    if os.path.exists("resource_cleanup.py"):
        results.add_result("Task 9: Resource", "resource_cleanup.py exists", True)
    else:
        results.add_result("Task 9: Resource", "resource_cleanup.py exists", False, "File not found")
    
    # Test 2: frontend_optimize.py var mı?
    if os.path.exists("frontend_optimize.py"):
        results.add_result("Task 10: Frontend", "frontend_optimize.py exists", True)
    else:
        results.add_result("Task 10: Frontend", "frontend_optimize.py exists", False, "File not found")
    
    # Test 3: .htaccess var mı?
    if os.path.exists("static/.htaccess"):
        results.add_result("Task 10: Frontend", "static/.htaccess exists", True)
    else:
        results.add_result("Task 10: Frontend", "static/.htaccess exists", False, "File not found")


# =============================================================================
# TASK 11: INTEGRATION TESTS
# =============================================================================
def test_task11_integration(results: TestResults):
    """Task 11: Entegrasyon testleri."""
    
    # Test 1: Tüm ana dosyaların syntax kontrolü
    critical_files = [
        "app.py",
        "routes.py",
        "config.py",
        "extensions.py",
        "utils.py",
        "cache_config.py",
        "exceptions.py",
        "resource_cleanup.py"
    ]
    
    all_syntax_ok = True
    failed_files = []
    
    for filename in critical_files:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                compile(f.read(), filename, "exec")
        except (SyntaxError, FileNotFoundError) as e:
            all_syntax_ok = False
            failed_files.append(f"{filename}: {str(e)}")
    
    if all_syntax_ok:
        results.add_result("Task 11: Integration", "All critical files syntax OK", True)
    else:
        results.add_result("Task 11: Integration", "All critical files syntax OK", False, f"Failed: {failed_files}")
    
    # Test 2: requirements.txt güncel mi?
    try:
        with open("requirements.txt", 'r', encoding='utf-8') as f:
            requirements = f.read()
        
        has_redis = "redis" in requirements
        has_aiohttp = "aiohttp" in requirements
        has_flask_cache = "Flask-Caching" in requirements
        
        if has_redis and has_aiohttp and has_flask_cache:
            results.add_result("Task 11: Integration", "requirements.txt updated", True)
        else:
            missing = []
            if not has_redis:
                missing.append("redis")
            if not has_aiohttp:
                missing.append("aiohttp")
            if not has_flask_cache:
                missing.append("Flask-Caching")
            
            results.add_result("Task 11: Integration", "requirements.txt updated", False, f"Missing: {missing}")
    
    except FileNotFoundError:
        results.add_result("Task 11: Integration", "requirements.txt updated", False, "File not found")
    
    # Test 3: Ana dosyaların import check
    try:
        # Python path'e ekle
        sys.path.insert(0, str(Path.cwd()))
        
        # Import test
        import config
        import env_config
        import utils
        import exceptions
        
        results.add_result("Task 11: Integration", "Core modules importable", True)
    
    except ImportError as e:
        results.add_result("Task 11: Integration", "Core modules importable", False, str(e))


# =============================================================================
# SECURITY SCAN
# =============================================================================
def run_security_scan(results: TestResults):
    """Basit güvenlik taraması."""
    
    # Hardcoded secret taraması
    suspicious_patterns = [
        "api_key",
        "secret_key",
        "password",
        "token"
    ]
    
    files_to_scan = ["app.py", "config.py", "routes.py"]
    issues_found = []
    
    for filename in files_to_scan:
        if not os.path.exists(filename):
            continue
        
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Comment satırlarını atla
            if line.strip().startswith('#'):
                continue
            
            # Şüpheli pattern ara
            for pattern in suspicious_patterns:
                if pattern in line.lower() and '=' in line:
                    # Environment variable'dan okuyorsa sorun değil
                    if 'os.getenv' in line or 'get_env' in line:
                        continue
                    
                    issues_found.append(f"{filename}:{i} - {line.strip()[:50]}")
    
    if not issues_found:
        results.add_result("Security Scan", "No hardcoded secrets found", True)
    else:
        results.add_result("Security Scan", "No hardcoded secrets found", False, f"Issues: {len(issues_found)}")


# =============================================================================
# PERFORMANCE BENCHMARK
# =============================================================================
def run_performance_benchmark(results: TestResults):
    """Basit performans benchmark'ı."""
    
    import time
    
    # AstroCalculator başlatma süresi
    try:
        start = time.time()
        from astro_calculations_refactored import AstroCalculator
        calc = AstroCalculator()
        init_time = time.time() - start
        
        if init_time < 1.0:  # 1 saniyenin altında olmalı
            results.add_result("Performance", "AstroCalculator init time", True, f"{init_time*1000:.1f}ms")
        else:
            results.add_result("Performance", "AstroCalculator init time", False, f"{init_time*1000:.1f}ms (too slow)")
    
    except Exception as e:
        results.add_result("Performance", "AstroCalculator init time", False, str(e))


# =============================================================================
# MAIN
# =============================================================================
def main():
    """Ana fonksiyon."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Integration Test Suite")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--task", type=int, help="Run specific task tests (1-11)")
    parser.add_argument("--security", action="store_true", help="Run security scan")
    parser.add_argument("--performance", action="store_true", help="Run performance benchmark")
    
    args = parser.parse_args()
    
    results = TestResults()
    
    if args.all or args.task == 1:
        test_task1_security(results)
    
    if args.all or args.task == 2:
        test_task2_imports(results)
    
    if args.all or args.task in [3, 4]:
        test_task3_4_redis_async(results)
    
    if args.all or args.task in [5, 6]:
        test_task5_6_utils_refactor(results)
    
    if args.all or args.task in [7, 8]:
        test_task7_8_cache_exceptions(results)
    
    if args.all or args.task in [9, 10]:
        test_task9_10_resource_frontend(results)
    
    if args.all or args.task == 11:
        test_task11_integration(results)
    
    if args.security:
        run_security_scan(results)
    
    if args.performance:
        run_performance_benchmark(results)
    
    # Sonuçları yazdır
    success = results.print_summary()
    
    # JSON rapor oluştur
    report = {
        "timestamp": str(Path.cwd()),
        "total_tests": results.total_tests,
        "passed": results.passed,
        "failed": results.failed,
        "success_rate": f"{results.passed/results.total_tests*100:.1f}%",
        "results": results.results
    }
    
    with open("test_report.json", 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("\n📄 Test report saved to: test_report.json")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
