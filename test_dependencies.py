#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест зависимостей
"""

def test_imports():
    """Тестируем импорт всех зависимостей"""
    
    print("🧪 Тестирование зависимостей...")
    
    # Тестируем yt-dlp
    try:
        import yt_dlp
        print("✅ yt-dlp: {}".format(yt_dlp.version.__version__))
    except ImportError as e:
        print("❌ yt-dlp: {}".format(e))
        assert False, f"yt-dlp import failed: {e}"
    
    # Тестируем ffmpeg-python
    try:
        import ffmpeg
        print("✅ ffmpeg-python")
    except ImportError as e:
        print(f"❌ ffmpeg-python: {e}")
        assert False, f"ffmpeg-python import failed: {e}"
    
    # Тестируем PyYAML
    try:
        import yaml
        print("✅ PyYAML")
    except ImportError as e:
        print(f"❌ PyYAML: {e}")
        assert False, f"PyYAML import failed: {e}"
    
    # Тестируем requests
    try:
        import requests
        print("✅ requests: {}".format(requests.__version__))
    except ImportError as e:
        print("❌ requests: {}".format(e))
        assert False, f"requests import failed: {e}"
    
    # Тестируем наши модули
    try:
        from config import Source, SourceType, Subscription, Config, ConfigManager
        print("✅ config.py")
    except ImportError as e:
        print(f"❌ config.py: {e}")
        assert False, f"config.py import failed: {e}"
    
    try:
        import multi_downloader
        print("✅ multi_downloader.py")
    except ImportError as e:
        print(f"❌ multi_downloader.py: {e}")
        assert False, f"multi_downloader.py import failed: {e}"
    
    try:
        import manage_sources
        print("✅ manage_sources.py")
    except ImportError as e:
        print(f"❌ manage_sources.py: {e}")
        assert False, f"manage_sources.py import failed: {e}"
    
    print("✅ Все зависимости работают!")


if __name__ == "__main__":
    try:
        test_imports()
        print("🎉 Все тесты прошли успешно!")
    except AssertionError as e:
        print(f"❌ Некоторые зависимости не работают: {e}")
        exit(1)
