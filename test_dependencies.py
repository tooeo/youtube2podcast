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
        return False
    
    # Тестируем ffmpeg-python
    try:
        import ffmpeg
        print("✅ ffmpeg-python")
    except ImportError as e:
        print(f"❌ ffmpeg-python: {e}")
        return False
    
    # Тестируем PyYAML
    try:
        import yaml
        print("✅ PyYAML")
    except ImportError as e:
        print(f"❌ PyYAML: {e}")
        return False
    
    # Тестируем requests
    try:
        import requests
        print("✅ requests: {}".format(requests.__version__))
    except ImportError as e:
        print("❌ requests: {}".format(e))
        return False
    
    # Тестируем наши модули
    try:
        from config import Source, SourceType, Subscription, Config, ConfigManager
        print("✅ config.py")
    except ImportError as e:
        print(f"❌ config.py: {e}")
        return False
    
    try:
        import multi_downloader
        print("✅ multi_downloader.py")
    except ImportError as e:
        print(f"❌ multi_downloader.py: {e}")
        return False
    
    try:
        import manage_sources
        print("✅ manage_sources.py")
    except ImportError as e:
        print(f"❌ manage_sources.py: {e}")
        return False
    
    print("✅ Все зависимости работают!")
    return True


if __name__ == "__main__":
    success = test_imports()
    if not success:
        print("❌ Некоторые зависимости не работают!")
        exit(1)
    else:
        print("🎉 Все тесты прошли успешно!")
