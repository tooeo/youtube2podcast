#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки извлечения видео из канала
"""

import sys
import os

# Добавляем корневую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Source, SourceType
from multi_downloader import get_videos_from_source, get_latest_video_from_source, print_video_links


def test_channel_extraction():
    """Тестируем извлечение видео из канала"""
    
    # Создаем тестовый источник (замените на реальный канал)
    test_source = Source(
        name="test_channel",
        url="https://www.youtube.com/@varlamov",  # Замените на нужный канал
        source_type=SourceType.CHANNEL,
        enabled=True,
        check_interval=10,
        max_videos=10,  # Проверим больше видео
        custom_title="Test Channel",
        custom_description="Test Description",
        category="Test",
        author="test_author"
    )
    
    print("🧪 Тестирование извлечения видео из канала")
    print("=" * 60)
    print(f"Канал: {test_source.url}")
    print(f"Максимум видео для проверки: {test_source.max_videos}")
    print("=" * 60)
    
    # Тест 1: Извлекаем несколько последних видео
    print("\n📡 Тест 1: Извлечение нескольких последних видео")
    import time
    start_time = time.time()
    videos = get_videos_from_source(test_source)
    end_time = time.time()
    
    if not videos:
        print("❌ Не удалось извлечь видео из канала")
        return
    
    print(f"✅ Успешно извлечено {len(videos)} видео за {end_time - start_time:.2f} секунд")
    print("=" * 60)
    
    # Показываем первые 10 видео с датами
    print("📋 Первые 10 видео (отсортированные по дате загрузки):")
    print_video_links(videos[:10], test_source.name)
    
    # Тест 2: Извлекаем только последнее видео
    print("\n📡 Тест 2: Извлечение только последнего видео")
    start_time = time.time()
    latest_video = get_latest_video_from_source(test_source)
    end_time = time.time()
    
    if latest_video:
        print(f"✅ Успешно извлечено последнее видео за {end_time - start_time:.2f} секунд")
        print(f"📺 Название: {latest_video['title']}")
        if latest_video.get('upload_date'):
            upload_date = latest_video['upload_date']
            formatted_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
            print(f"📅 Дата загрузки: {formatted_date}")
    else:
        print("❌ Не удалось извлечь последнее видео")
    
    # Проверяем сортировку
    print("\n🔍 Проверка сортировки:")
    if len(videos) >= 2:
        first_video = videos[0]
        second_video = videos[1]
        
        print(f"1. {first_video['title']}")
        if first_video.get('upload_date'):
            print(f"   Дата: {first_video['upload_date']}")
        
        print(f"2. {second_video['title']}")
        if second_video.get('upload_date'):
            print(f"   Дата: {second_video['upload_date']}")
        
        # Проверяем, что первое видео новее второго
        if (first_video.get('upload_date', '') > second_video.get('upload_date', '')):
            print("✅ Сортировка работает правильно (новые видео сначала)")
        else:
            print("❌ Сортировка может работать неправильно")
    else:
        print("⚠️ Недостаточно видео для проверки сортировки")


if __name__ == "__main__":
    test_channel_extraction()
