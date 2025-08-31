#!/usr/bin/env python3
"""
Simple import tests
"""

import sys
import os

# Добавляем корневую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_import_config():
    """Тест импорта config.py"""
    try:
        from config import Source, SourceType, Subscription, Config, ConfigManager
        assert True
    except ImportError as e:
        assert False, f"Failed to import config: {e}"

def test_import_multi_downloader():
    """Тест импорта multi_downloader.py"""
    try:
        import multi_downloader
        assert True
    except ImportError as e:
        assert False, f"Failed to import multi_downloader: {e}"

def test_import_manage_sources():
    """Тест импорта manage_sources.py"""
    try:
        import manage_sources
        assert True
    except ImportError as e:
        assert False, f"Failed to import manage_sources: {e}"

def test_import_test_config():
    """Тест импорта test_config.py"""
    try:
        import test_config
        assert True
    except ImportError as e:
        assert False, f"Failed to import test_config: {e}"

if __name__ == "__main__":
    # Запускаем все тесты
    test_import_config()
    test_import_multi_downloader()
    test_import_manage_sources()
    test_import_test_config()
    print("✅ All import tests passed!")
