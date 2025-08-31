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
from multi_downloader import get_videos_from_source, print_video_links


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
    
    # Извлекаем видео
    videos = get_videos_from_source(test_source)
    
    if not videos:
        print("❌ Не удалось извлечь видео из канала")
        return
    
    print(f"\n✅ Успешно извлечено {len(videos)} видео")
    print("=" * 60)
    
    # Показываем первые 10 видео с датами
    print("📋 Первые 10 видео (отсортированные по дате загрузки):")
    print_video_links(videos[:10], test_source.name)
    
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
