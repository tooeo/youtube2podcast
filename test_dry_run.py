#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки dry-run режима
"""

import sys
import os

# Добавляем корневую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Source, SourceType, Subscription
from multi_downloader import dry_run_analysis


def test_dry_run_mode():
    """Тестируем dry-run режим"""
    
    print("🧪 Тестирование dry-run режима")
    print("=" * 60)
    
    # Создаем тестовый источник (канал)
    test_source = Source(
        name="test_channel",
        url="https://www.youtube.com/@varlamov",  # Замените на нужный канал
        source_type=SourceType.CHANNEL,
        enabled=True,
        check_interval=10,
        max_videos=3,  # Проверим несколько видео
        custom_title="Test Channel",
        custom_description="Test Description",
        category="Test",
        author="test_author"
    )
    
    # Создаем тестовую подписку
    test_subscription = Subscription(
        name="test_subscription",
        title="Test Subscription",
        description="Test Description",
        enabled=True,
        category="Test",
        author="test_author",
        sources=[test_source]
    )
    
    print(f"📋 Тестируем источник: {test_source.name}")
    print(f"📋 Подписка: {test_subscription.name}")
    print(f"🔗 URL: {test_source.url}")
    print(f"📊 Максимум видео: {test_source.max_videos}")
    print("=" * 60)
    
    # Запускаем dry-run анализ
    analysis_result = dry_run_analysis(test_source, test_subscription)
    
    if analysis_result:
        print(f"\n✅ Dry-run анализ завершен успешно")
        print(f"📊 Результаты:")
        print(f"   Всего найдено видео: {analysis_result.get('total_videos_found', 0)}")
        print(f"   Проверено видео: {analysis_result.get('videos_to_check', 0)}")
        print(f"   Доступных видео: {len(analysis_result.get('available_videos', []))}")
        print(f"   Недоступных видео: {len(analysis_result.get('unavailable_videos', []))}")
        
        if analysis_result.get('will_download'):
            print(f"   🎯 Будет загружено: {analysis_result['will_download']['title']}")
            print(f"   📁 Файл существует: {analysis_result.get('file_exists', False)}")
        else:
            print(f"   ❌ Нет доступных видео для загрузки")
    else:
        print(f"\n❌ Dry-run анализ не удался")


def test_dry_run_playlist():
    """Тестируем dry-run режим с плейлистом"""
    
    print("\n🧪 Тестирование dry-run режима с плейлистом")
    print("=" * 60)
    
    # Создаем тестовый источник (плейлист)
    test_source = Source(
        name="test_playlist",
        url="https://www.youtube.com/playlist?list=PLceIIEa--FBIIrCD1GIp7ndizRDCwcJgf",  # Замените на нужный плейлист
        source_type=SourceType.PLAYLIST,
        enabled=True,
        check_interval=10,
        max_videos=3,  # Проверим несколько видео
        custom_title="Test Playlist",
        custom_description="Test Description",
        category="Test",
        author="test_author"
    )
    
    # Создаем тестовую подписку
    test_subscription = Subscription(
        name="test_subscription",
        title="Test Subscription",
        description="Test Description",
        enabled=True,
        category="Test",
        author="test_author",
        sources=[test_source]
    )
    
    print(f"📋 Тестируем источник: {test_source.name}")
    print(f"📋 Подписка: {test_subscription.name}")
    print(f"🔗 URL: {test_source.url}")
    print(f"📊 Максимум видео: {test_source.max_videos}")
    print("=" * 60)
    
    # Запускаем dry-run анализ
    analysis_result = dry_run_analysis(test_source, test_subscription)
    
    if analysis_result:
        print(f"\n✅ Dry-run анализ плейлиста завершен успешно")
        print(f"📊 Результаты:")
        print(f"   Всего найдено видео: {analysis_result.get('total_videos_found', 0)}")
        print(f"   Проверено видео: {analysis_result.get('videos_to_check', 0)}")
        print(f"   Доступных видео: {len(analysis_result.get('available_videos', []))}")
        print(f"   Недоступных видео: {len(analysis_result.get('unavailable_videos', []))}")
        
        if analysis_result.get('will_download'):
            print(f"   🎯 Будет загружено: {analysis_result['will_download']['title']}")
            print(f"   📁 Файл существует: {analysis_result.get('file_exists', False)}")
        else:
            print(f"   ❌ Нет доступных видео для загрузки")
    else:
        print(f"\n❌ Dry-run анализ плейлиста не удался")


if __name__ == "__main__":
    test_dry_run_mode()
    test_dry_run_playlist()
