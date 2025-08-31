#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки извлечения видео из плейлистов
"""

import sys
import os

# Добавляем корневую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Source, SourceType
from multi_downloader import get_playlist_info_and_videos, get_latest_video_from_source, print_video_links


def test_playlist_extraction():
    """Тестируем извлечение видео из плейлиста"""
    
    # Создаем тестовый источник (плейлист)
    test_source = Source(
        name="test_playlist",
        url="https://www.youtube.com/playlist?list=PLceIIEa--FBIIrCD1GIp7ndizRDCwcJgf",  # Замените на нужный плейлист
        source_type=SourceType.PLAYLIST,
        enabled=True,
        check_interval=10,
        max_videos=5,  # Проверим несколько видео
        custom_title="Test Playlist",
        custom_description="Test Description",
        category="Test",
        author="test_author"
    )
    
    print("🧪 Тестирование извлечения видео из плейлиста")
    print("=" * 60)
    print(f"Плейлист: {test_source.url}")
    print(f"Максимум видео для проверки: {test_source.max_videos}")
    print("=" * 60)
    
    # Тест 1: Получаем информацию о плейлисте и его видео
    print("\n📡 Тест 1: Получение информации о плейлисте и его видео")
    import time
    start_time = time.time()
    playlist_data = get_playlist_info_and_videos(test_source)
    end_time = time.time()
    
    if not playlist_data:
        print("❌ Не удалось получить информацию о плейлисте")
        return
    
    print(f"✅ Успешно получена информация о плейлисте за {end_time - start_time:.2f} секунд")
    print("=" * 60)
    
    # Показываем информацию о плейлисте
    print("📋 Информация о плейлисте:")
    print(f"   Название: {playlist_data.get('title', 'Неизвестно')}")
    print(f"   Автор: {playlist_data.get('uploader', 'Неизвестно')}")
    print(f"   Всего видео: {playlist_data.get('video_count', 0)}")
    if playlist_data.get('last_updated'):
        print(f"   Последнее обновление: {playlist_data['last_updated']}")
    if playlist_data.get('created_date'):
        print(f"   Дата создания: {playlist_data['created_date']}")
    
    # Показываем видео из плейлиста
    videos = playlist_data.get('entries', [])
    if videos:
        print(f"\n📺 Видео в плейлисте (отсортированные по дате загрузки):")
        print_video_links(videos, test_source.name)
    
    # Тест 2: Получаем только последнее видео
    print("\n📡 Тест 2: Получение только последнего видео из плейлиста")
    start_time = time.time()
    latest_video = get_latest_video_from_source(test_source)
    end_time = time.time()
    
    if latest_video:
        print(f"✅ Успешно получено последнее видео за {end_time - start_time:.2f} секунд")
        print(f"📺 Название: {latest_video['title']}")
        if latest_video.get('upload_date'):
            upload_date = latest_video['upload_date']
            formatted_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
            print(f"📅 Дата загрузки: {formatted_date}")
        if latest_video.get('playlist_position'):
            print(f"📋 Позиция в плейлисте: {latest_video['playlist_position']}")
    else:
        print("❌ Не удалось получить последнее видео")
    
    # Проверяем сортировку
    print("\n🔍 Проверка сортировки:")
    if len(videos) >= 2:
        first_video = videos[0]
        second_video = videos[1]
        
        print(f"1. {first_video['title']}")
        if first_video.get('upload_date'):
            print(f"   Дата: {first_video['upload_date']}")
        if first_video.get('playlist_position'):
            print(f"   Позиция: {first_video['playlist_position']}")
        
        print(f"2. {second_video['title']}")
        if second_video.get('upload_date'):
            print(f"   Дата: {second_video['upload_date']}")
        if second_video.get('playlist_position'):
            print(f"   Позиция: {second_video['playlist_position']}")
        
        # Проверяем, что первое видео новее второго
        if (first_video.get('upload_date', '') > second_video.get('upload_date', '')):
            print("✅ Сортировка работает правильно (новые видео сначала)")
        else:
            print("❌ Сортировка может работать неправильно")
    else:
        print("⚠️ Недостаточно видео для проверки сортировки")


if __name__ == "__main__":
    test_playlist_extraction()
