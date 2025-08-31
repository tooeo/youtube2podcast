#!/usr/bin/env python3
"""
Универсальная программа для загрузки аудио с множественных YouTube источников
"""

import yt_dlp
import sys
import os
import xml.etree.ElementTree as ET
from datetime import datetime
import re
import requests
import socket
import hashlib
import time
import signal
import argparse
from typing import List, Dict, Any

from config import Source, SourceType, Subscription, get_enabled_sources, get_enabled_subscriptions, get_source_by_name, config_manager


running = True
dry_run = False  # Глобальная переменная для dry-run режима


def parse_arguments():
    """
    Парсит аргументы командной строки
    """
    parser = argparse.ArgumentParser(
        description='YouTube2Podcast - Загрузка аудио с YouTube источников',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python multi_downloader.py                    # Обычный запуск
  python multi_downloader.py --dry-run          # Dry-run режим
  python multi_downloader.py --loop             # Запуск в цикле
  python multi_downloader.py --dry-run --loop   # Dry-run в цикле
        """
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Показать что будет загружено без фактической загрузки'
    )
    
    parser.add_argument(
        '--loop',
        action='store_true',
        help='Запустить в бесконечном цикле с интервалом 10 минут'
    )
    
    parser.add_argument(
        '--subscription',
        type=str,
        help='Обработать только указанную подписку'
    )
    
    parser.add_argument(
        '--source',
        type=str,
        help='Обработать только указанный источник'
    )
    
    return parser.parse_args()

def signal_handler(signum, frame):
    global running
    print(f"\nПолучен сигнал {signum}. Завершение работы...")
    running = False


def get_file_hash(title: str) -> str:
    """
    Создает MD5 хеш из названия видео для использования в имени файла
    """
    return hashlib.md5(title.encode('utf-8')).hexdigest()


def check_video_availability(video_id: str) -> bool:
    """
    Проверяет доступность видео по ID
    
    Args:
        video_id: ID видео на YouTube
        
    Returns:
        True если видео доступно, False если нет
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'extract_flat': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Пытаемся извлечь информацию о видео
            result = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            if result and result.get('title'):
                return True
            return False
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        if "Video unavailable" in error_msg:
            print(f"   ❌ Видео недоступно (ID: {video_id})")
        elif "Private video" in error_msg:
            print(f"   ❌ Приватное видео (ID: {video_id})")
        elif "This video is not available" in error_msg:
            print(f"   ❌ Видео недоступно в регионе (ID: {video_id})")
        else:
            print(f"   ❌ Ошибка доступа: {error_msg}")
        return False
    except Exception as e:
        print(f"   ❌ Неожиданная ошибка при проверке видео {video_id}: {e}")
        return False


def diagnose_network_issues():
    """
    Диагностирует проблемы с сетью и доступом к YouTube
    """
    print("🔍 Диагностика сетевых проблем...")
    
    # Проверка DNS
    try:
        ip = socket.gethostbyname("www.youtube.com")
        print(f"✅ DNS YouTube: {ip}")
    except Exception as e:
        print(f"❌ DNS YouTube: {e}")
    
    # Проверка HTTP соединения
    try:
        response = requests.get("https://www.youtube.com", timeout=10)
        print(f"✅ HTTP YouTube: {response.status_code}")
    except Exception as e:
        print(f"❌ HTTP YouTube: {e}")
    
    # Проверка yt-dlp версии
    try:
        import yt_dlp
        print(f"✅ yt-dlp версия: {yt_dlp.version.__version__}")
    except Exception as e:
        print(f"❌ yt-dlp версия: {e}")
    
    # Проверка доступности тестового видео
    test_video_id = "dQw4w9WgXcQ"  # Rick Roll
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            video_url = f"https://www.youtube.com/watch?v={test_video_id}"
            info = ydl.extract_info(video_url, download=False)
            print(f"✅ Тестовое видео доступно: {info.get('title', 'Unknown')}")
    except Exception as e:
        print(f"❌ Тестовое видео недоступно: {e}")
    
    print("=" * 50)


def clean_filename(filename: str) -> str:
    """
    Очищает имя файла от недопустимых символов для URL
    """
    # Заменяем недопустимые символы на подчеркивания
    cleaned = re.sub(r'[^\w\-_.]', '_', filename)
    # Убираем множественные подчеркивания
    cleaned = re.sub(r'_+', '_', cleaned)
    return cleaned


def diagnose_video_issue(video_id: str, video_title: str = ""):
    """
    Диагностирует проблемы с конкретным видео
    
    Args:
        video_id: ID видео на YouTube
        video_title: Название видео (опционально)
    """
    print(f"🔍 Диагностика видео: {video_title or video_id}")
    print(f"   ID: {video_id}")
    print(f"   URL: https://www.youtube.com/watch?v={video_id}")
    
    # Проверяем доступность через разные методы
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Пробуем извлечь полную информацию
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            if info:
                print(f"   ✅ Видео доступно")
                print(f"   📺 Название: {info.get('title', 'Неизвестно')}")
                print(f"   👤 Автор: {info.get('uploader', 'Неизвестно')}")
                print(f"   ⏱️ Длительность: {info.get('duration', 0)} сек")
                print(f"   👀 Просмотры: {info.get('view_count', 'Неизвестно')}")
                return True
            else:
                print(f"   ❌ Видео недоступно")
                return False
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        print(f"   ❌ Ошибка yt-dlp: {error_msg}")
        
        if "Video unavailable" in error_msg:
            print(f"   💡 Возможные причины:")
            print(f"      - Видео удалено автором")
            print(f"      - Видео приватное")
            print(f"      - Видео ограничено по возрасту")
            print(f"      - Видео заблокировано в вашем регионе")
        elif "Private video" in error_msg:
            print(f"   💡 Видео приватное - требуется авторизация")
        elif "This video is not available" in error_msg:
            print(f"   💡 Видео недоступно в вашем регионе")
        elif "Sign in to confirm your age" in error_msg:
            print(f"   💡 Требуется подтверждение возраста")
        
        return False
    except Exception as e:
        print(f"   ❌ Неожиданная ошибка: {e}")
        return False


def get_playlist_info_and_videos(source: Source) -> Dict[str, Any]:
    """
    Получает информацию о плейлисте и его последних видео
    
    Args:
        source: Конфигурация источника (плейлист)
        
    Returns:
        Словарь с информацией о плейлисте и его видео
    """
    ydl_opts = {
        'quiet': True,
        'extract_flat': False,  # Получаем полную информацию включая даты
        'ignoreerrors': True,  # Пропускаем ошибки для отдельных видео
        'extract_info': True,  # Извлекаем полную информацию
        'playlist_items': f'1-{source.max_videos}',  # Получаем только первые N видео
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Извлекаем информацию о плейлисте
            playlist_info = ydl.extract_info(source.url, download=False)
            
            if not playlist_info:
                print(f"❌ Не удалось получить информацию о плейлисте: {source.name}")
                return {}
            
            # Информация о плейлисте
            playlist_data = {
                'title': playlist_info.get('title', 'Без названия'),
                'description': playlist_info.get('description', ''),
                'uploader': playlist_info.get('uploader', 'Неизвестно'),
                'video_count': playlist_info.get('playlist_count', 0),
                'last_updated': playlist_info.get('modified_date', ''),
                'created_date': playlist_info.get('upload_date', ''),
                'entries': []
            }
            
            print(f"📋 Плейлист: {playlist_data['title']}")
            print(f"👤 Автор: {playlist_data['uploader']}")
            print(f"📊 Всего видео: {playlist_data['video_count']}")
            if playlist_data.get('last_updated'):
                print(f"🔄 Последнее обновление: {playlist_data['last_updated']}")
            
            # Обрабатываем видео в плейлисте
            if 'entries' in playlist_info and playlist_info['entries']:
                videos = []
                for entry in playlist_info['entries']:
                    if entry:  # Проверяем, что запись не пустая
                        # Получаем полную информацию о видео
                        try:
                            video_url = f"https://www.youtube.com/watch?v={entry.get('id', '')}"
                            video_info = ydl.extract_info(video_url, download=False)
                            
                            if video_info:
                                video_data = {
                                    'title': video_info.get('title', 'Без названия'),
                                    'url': video_info.get('webpage_url', ''),
                                    'id': video_info.get('id', ''),
                                    'duration': video_info.get('duration', 0),
                                    'uploader': video_info.get('uploader', 'Неизвестно'),
                                    'view_count': video_info.get('view_count', 0),
                                    'upload_date': video_info.get('upload_date', ''),
                                    'timestamp': video_info.get('timestamp', 0),
                                    'playlist_position': entry.get('playlist_index', 0)
                                }
                                videos.append(video_data)
                        except Exception as video_error:
                            # Если не удалось получить полную информацию, используем базовую
                            video_data = {
                                'title': entry.get('title', 'Без названия'),
                                'url': entry.get('url', ''),
                                'id': entry.get('id', ''),
                                'duration': entry.get('duration', 0),
                                'uploader': entry.get('uploader', 'Неизвестно'),
                                'view_count': entry.get('view_count', 0),
                                'upload_date': entry.get('upload_date', ''),
                                'timestamp': entry.get('timestamp', 0),
                                'playlist_position': entry.get('playlist_index', 0)
                            }
                            videos.append(video_data)
                
                # Сортируем видео по дате загрузки (новые сначала)
                videos.sort(key=lambda x: x.get('timestamp', 0) or x.get('upload_date', ''), reverse=True)
                playlist_data['entries'] = videos
                
                print(f"✅ Найдено {len(videos)} последних видео в плейлисте")
                if videos:
                    print(f"📅 Последнее видео: {videos[0]['title']}")
                    if videos[0].get('upload_date'):
                        upload_date = videos[0]['upload_date']
                        formatted_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
                        print(f"📅 Дата загрузки: {formatted_date}")
            
            return playlist_data
            
    except Exception as e:
        print(f"❌ Ошибка при извлечении информации о плейлисте {source.name}: {e}")
        return {}


def get_videos_from_source(source: Source) -> List[Dict[str, Any]]:
    """
    Извлекает информацию о последних видео из источника (плейлист или канал)
    
    Args:
        source: Конфигурация источника
        
    Returns:
        Список словарей с информацией о последних видео, отсортированный по дате загрузки
    """
    # Для плейлистов используем специальную функцию
    if source.source_type == SourceType.PLAYLIST:
        playlist_data = get_playlist_info_and_videos(source)
        return playlist_data.get('entries', [])
    
    # Для каналов используем стандартную логику
    ydl_opts = {
        'quiet': True,
        'extract_flat': False,  # Получаем полную информацию включая даты
        'ignoreerrors': True,  # Пропускаем ошибки для отдельных видео
        'extract_info': True,  # Извлекаем полную информацию
        'playlist_items': f'1-{source.max_videos}',  # Получаем только первые N видео
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Извлекаем информацию об источнике (только последние видео)
            source_info = ydl.extract_info(source.url, download=False)
            
            if not source_info or 'entries' not in source_info:
                print(f"❌ Не удалось получить информацию об источнике: {source.name}")
                return []
            
            videos = []
            for entry in source_info['entries']:
                if entry:  # Проверяем, что запись не пустая
                    # Получаем полную информацию о видео
                    try:
                        video_url = f"https://www.youtube.com/watch?v={entry.get('id', '')}"
                        video_info = ydl.extract_info(video_url, download=False)
                        
                        if video_info:
                            video_data = {
                                'title': video_info.get('title', 'Без названия'),
                                'url': video_info.get('webpage_url', ''),
                                'id': video_info.get('id', ''),
                                'duration': video_info.get('duration', 0),
                                'uploader': video_info.get('uploader', 'Неизвестно'),
                                'view_count': video_info.get('view_count', 0),
                                'upload_date': video_info.get('upload_date', ''),
                                'timestamp': video_info.get('timestamp', 0)
                            }
                            videos.append(video_data)
                    except Exception as video_error:
                        # Если не удалось получить полную информацию, используем базовую
                        video_data = {
                            'title': entry.get('title', 'Без названия'),
                            'url': entry.get('url', ''),
                            'id': entry.get('id', ''),
                            'duration': entry.get('duration', 0),
                            'uploader': entry.get('uploader', 'Неизвестно'),
                            'view_count': entry.get('view_count', 0),
                            'upload_date': entry.get('upload_date', ''),
                            'timestamp': entry.get('timestamp', 0)
                        }
                        videos.append(video_data)
            
            # Сортируем видео по дате загрузки (новые сначала)
            videos.sort(key=lambda x: x.get('timestamp', 0) or x.get('upload_date', ''), reverse=True)
            
            print(f"✅ Найдено {len(videos)} последних видео в источнике: {source.name}")
            if videos:
                print(f"📅 Последнее видео: {videos[0]['title']}")
                if videos[0].get('upload_date'):
                    upload_date = videos[0]['upload_date']
                    formatted_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
                    print(f"📅 Дата загрузки: {formatted_date}")
            
            return videos
            
    except Exception as e:
        print(f"❌ Ошибка при извлечении информации из источника {source.name}: {e}")
        return []


def get_latest_video_from_source(source: Source) -> Dict[str, Any]:
    """
    Извлекает информацию только о самом последнем видео из источника
    
    Args:
        source: Конфигурация источника
        
    Returns:
        Словарь с информацией о последнем видео или пустой словарь
    """
    # Для плейлистов получаем информацию о плейлисте и берем первое видео
    if source.source_type == SourceType.PLAYLIST:
        playlist_data = get_playlist_info_and_videos(source)
        videos = playlist_data.get('entries', [])
        if videos:
            latest_video = videos[0]  # Первое видео уже отсортировано по дате
            print(f"✅ Найдено последнее видео в плейлисте: {source.name}")
            print(f"📺 Название: {latest_video['title']}")
            if latest_video.get('upload_date'):
                upload_date = latest_video['upload_date']
                formatted_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
                print(f"📅 Дата загрузки: {formatted_date}")
            return latest_video
        else:
            print(f"❌ Не удалось получить последнее видео из плейлиста: {source.name}")
            return {}
    
    # Для каналов используем стандартную логику
    ydl_opts = {
        'quiet': True,
        'extract_flat': False,  # Получаем полную информацию включая даты
        'ignoreerrors': True,  # Пропускаем ошибки для отдельных видео
        'extract_info': True,  # Извлекаем полную информацию
        'playlist_items': '1',  # Получаем только первое видео
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Извлекаем информацию об источнике (только последнее видео)
            source_info = ydl.extract_info(source.url, download=False)
            
            if not source_info or 'entries' not in source_info or not source_info['entries']:
                print(f"❌ Не удалось получить информацию об источнике: {source.name}")
                return {}
            
            # Берем первое видео (самое последнее)
            entry = source_info['entries'][0]
            if not entry:
                print(f"❌ Не удалось получить последнее видео из источника: {source.name}")
                return {}
            
            # Получаем полную информацию о видео
            try:
                video_url = f"https://www.youtube.com/watch?v={entry.get('id', '')}"
                video_info = ydl.extract_info(video_url, download=False)
                
                if video_info:
                    video_data = {
                        'title': video_info.get('title', 'Без названия'),
                        'url': video_info.get('webpage_url', ''),
                        'id': video_info.get('id', ''),
                        'duration': video_info.get('duration', 0),
                        'uploader': video_info.get('uploader', 'Неизвестно'),
                        'view_count': video_info.get('view_count', 0),
                        'upload_date': video_info.get('upload_date', ''),
                        'timestamp': video_info.get('timestamp', 0)
                    }
                    
                    print(f"✅ Найдено последнее видео в источнике: {source.name}")
                    print(f"📺 Название: {video_data['title']}")
                    if video_data.get('upload_date'):
                        upload_date = video_data['upload_date']
                        formatted_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
                        print(f"📅 Дата загрузки: {formatted_date}")
                    
                    return video_data
                else:
                    print(f"❌ Не удалось получить информацию о последнем видео: {source.name}")
                    return {}
                    
            except Exception as video_error:
                print(f"❌ Ошибка при получении информации о последнем видео: {video_error}")
                return {}
            
    except Exception as e:
        print(f"❌ Ошибка при извлечении информации из источника {source.name}: {e}")
        return {}


def print_video_links(videos: List[Dict[str, Any]], source_name: str) -> None:
    """
    Выводит ссылки на видео в удобном формате
    
    Args:
        videos: Список словарей с информацией о видео
        source_name: Название источника
    """
    if not videos:
        print(f"Видео не найдены в источнике: {source_name}")
        return
    
    print(f"\nНайдено {len(videos)} видео в источнике '{source_name}':\n")
    print("=" * 80)
    
    for i, video in enumerate(videos, 1):
        print(f"{i:2d}. {video['title']}")
        print(f"    Ссылка: https://www.youtube.com/watch?v={video['id']}")
        print(f"    Автор: {video['uploader']}")
        if video['duration']:
            minutes = video['duration'] // 60
            seconds = video['duration'] % 60
            print(f"    Длительность: {minutes}:{seconds:02d}")
        if video['view_count']:
            print(f"    Просмотров: {video['view_count']:,}")
        else:
            print(f"    Просмотров: Недоступно")
        if video.get('upload_date'):
            upload_date = video['upload_date']
            formatted_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
            print(f"    📅 Дата загрузки: {formatted_date}")
        if video.get('playlist_position'):
            print(f"    📋 Позиция в плейлисте: {video['playlist_position']}")
        print("-" * 80)


def download_latest_audio(videos: List[Dict[str, Any]], source: Source, subscription: Subscription) -> Dict[str, Any]:
    """
    Загружает аудио из последнего доступного видео
    
    Args:
        videos: Список всех видео из источника (может быть пустым, если используется get_latest_video_from_source)
        source: Конфигурация источника
        subscription: Конфигурация подписки
        
    Returns:
        Словарь с информацией о загруженном видео или пустой словарь
    """
    # Проверяем переменную окружения для предотвращения загрузки в тестах
    if os.environ.get('SKIP_DOWNLOAD', 'false').lower() in ('true', '1', 'yes'):
        print(f"🚫 Загрузка пропущена (SKIP_DOWNLOAD=true) для источника: {source.name}")
        return {}
    # Если videos пустой, получаем только последнее видео
    if not videos:
        print(f"📡 Получаем только последнее видео из источника: {source.name}")
        latest_video = get_latest_video_from_source(source)
        if not latest_video:
            print(f"❌ Не удалось получить последнее видео из источника: {source.name}")
            return {}
    else:
        # Ищем первое доступное видео среди последних N
        latest_video = None
        max_check = min(source.max_videos, len(videos))
        
        for i, video in enumerate(videos[:max_check]):
            print(f"Проверяю доступность видео {i+1}: {video['title']}")
            
            # Проверяем доступность видео
            if check_video_availability(video['id']):
                latest_video = video
                print(f"✅ Видео доступно: {video['title']}")
                break
            else:
                print(f"❌ Видео недоступно: {video['title']}")
                # Если это последнее видео и оно недоступно, запускаем подробную диагностику
                if i == max_check - 1:
                    print(f"\n🔍 Запускаем подробную диагностику последнего видео...")
                    diagnose_video_issue(video['id'], video['title'])
        
        if not latest_video:
            print(f"❌ Не найдено доступных видео для загрузки в источнике: {source.name}")
            return {}
    
    # Создаем папку для подписки
    subscription_dir = f"data/{subscription.name}"
    os.makedirs(subscription_dir, exist_ok=True)
    
    # Проверяем, существует ли уже аудио файл по MD5 хешу
    file_hash = get_file_hash(latest_video['title'])
    mp3_filename = f"{file_hash}.mp3"
    mp3_path = os.path.join(subscription_dir, mp3_filename)
    
    if os.path.exists(mp3_path):
        print(f"\nАудио файл уже существует: {mp3_filename}")
        print(f"Пропускаю загрузку для видео: {latest_video['title']}")
        return latest_video
    
    print(f"\nЗагрузка аудио из последнего видео источника '{source.name}' (подписка '{subscription.name}'):")
    print(f"Название: {latest_video['title']}")
    print(f"ID: {latest_video['id']}")
    
    # Настройки для загрузки только аудио
    download_settings = config_manager.get_download_setting('format', 'bestaudio/best')
    audio_codec = config_manager.get_download_setting('audio_codec', 'mp3')
    audio_quality = config_manager.get_download_setting('audio_quality', '192')
    thumbnail_format = config_manager.get_download_setting('thumbnail_format', 'webp')
    write_subtitles = config_manager.get_download_setting('write_subtitles', False)
    write_automatic_subtitles = config_manager.get_download_setting('write_automatic_subtitles', False)
    
    ydl_opts = {
        'format': download_settings,
        'outtmpl': f'{subscription_dir}/{file_hash}.%(ext)s',  # Шаблон имени файла с MD5 хешем
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',  # Извлекаем аудио
                'preferredcodec': audio_codec,  # Конвертируем в MP3
                'preferredquality': audio_quality,  # Качество
            },
            {
                'key': 'FFmpegThumbnailsConvertor',
                'format': thumbnail_format,
            }
        ],
        'writethumbnail': True,  # Загружаем обложку
        'writesubtitles': write_subtitles,  # Загружаем субтитры
        'writeautomaticsub': write_automatic_subtitles,
        'ignoreerrors': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            video_url = f"https://www.youtube.com/watch?v={latest_video['id']}"
            print(f"Начинаю загрузку: {video_url}")
            
            # Сначала проверяем доступность видео перед загрузкой
            try:
                info = ydl.extract_info(video_url, download=False)
                if not info:
                    print(f"❌ Видео недоступно для загрузки: {latest_video['title']}")
                    return {}
                print(f"✅ Видео доступно для загрузки: {info.get('title', latest_video['title'])}")
            except Exception as extract_error:
                print(f"❌ Ошибка при проверке доступности видео: {extract_error}")
                print(f"Пробуем следующее видео...")
                return {}
            
            # Загружаем видео
            ydl.download([video_url])
            print(f"✅ Аудио успешно загружено в папку: {subscription_dir}")
            return latest_video
            
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        if "Video unavailable" in error_msg:
            print(f"❌ Видео недоступно: {latest_video['title']}")
            print(f"   ID: {latest_video['id']}")
            print(f"   Возможные причины: видео удалено, приватное, ограничено по возрасту или региону")
        elif "Private video" in error_msg:
            print(f"❌ Приватное видео: {latest_video['title']}")
        elif "This video is not available" in error_msg:
            print(f"❌ Видео недоступно в вашем регионе: {latest_video['title']}")
        else:
            print(f"❌ Ошибка загрузки: {error_msg}")
        return {}
    except Exception as e:
        print(f"❌ Неожиданная ошибка при загрузке аудио из источника '{source.name}': {e}")
        return {}


def create_or_update_rss(videos: List[Dict[str, Any]], source: Source, subscription: Subscription, latest_video: Dict[str, Any]) -> None:
    """
    Создает или обновляет RSS файл для подкастов
    
    Args:
        videos: Список всех видео из источника
        source: Конфигурация источника
        subscription: Конфигурация подписки
        latest_video: Информация о последнем загруженном видео
    """
    # Проверяем, что latest_video не пустой
    if not latest_video or latest_video == {}:
        print(f"❌ Нет информации о видео для создания RSS в источнике: {source.name}")
        return
        
    rss_file = f"data/{subscription.name}/podcast.rss"
    subscription_dir = f"data/{subscription.name}"
    
    # Создаем папку если её нет
    os.makedirs(subscription_dir, exist_ok=True)
    
    # Получаем настройки RSS из конфигурации
    rss_version = config_manager.get_rss_setting('version', '2.0')
    namespaces = config_manager.get_rss_setting('namespaces', {})
    default_language = config_manager.get_rss_setting('default_language', 'ru')
    
    # Создаем корневой элемент RSS
    rss = ET.Element("rss", version=rss_version)
    for ns_name, ns_url in namespaces.items():
        rss.set(f"xmlns:{ns_name}", ns_url)
    
    # Создаем канал
    channel = ET.SubElement(rss, "channel")
    
    # Метаданные канала
    title = ET.SubElement(channel, "title")
    title.text = subscription.title or f"{subscription.name.title()} - Подкаст"
    
    description = ET.SubElement(channel, "description")
    description.text = subscription.description or f"Подкаст из подписки {subscription.name}"
    
    language = ET.SubElement(channel, "language")
    language.text = "ru"
    
    # iTunes метаданные
    itunes_author = ET.SubElement(channel, "itunes:author")
    itunes_author.text = subscription.author or subscription.name
    
    itunes_summary = ET.SubElement(channel, "itunes:summary")
    itunes_summary.text = subscription.description or f"Подкаст из подписки {subscription.name}"
    
    itunes_category = ET.SubElement(channel, "itunes:category", text=subscription.category)
    
    # Дополнительные метаданные канала
    itunes_explicit = ET.SubElement(channel, "itunes:explicit")
    itunes_explicit.text = "false"
    
    itunes_type = ET.SubElement(channel, "itunes:type")
    itunes_type.text = "episodic"
    
    # Получаем базовый URL для RSS ссылок
    base_url = config_manager.get_base_url()
    
    # Добавляем превью канала (используем превью последнего видео)
    itunes_image = ET.SubElement(channel, "itunes:image")
    thumbnail_filename = f"{get_file_hash(latest_video['title'])}.webp"
    thumbnail_url = f"{base_url}/{subscription.name}/{thumbnail_filename}"
    itunes_image.set("href", thumbnail_url)
    
    # Находим все загруженные аудио файлы в папке подписки
    downloaded_videos = []
    if os.path.exists(subscription_dir):
        for file in os.listdir(subscription_dir):
            if file.endswith('.mp3'):
                # Извлекаем хеш из имени файла
                file_hash = file.replace('.mp3', '')
                
                # Ищем соответствующее видео в списке
                for video in videos:
                    if get_file_hash(video['title']) == file_hash:
                        downloaded_videos.append(video)
                        break
    
    # Добавляем элементы для каждого загруженного видео
    for video in downloaded_videos:
        item = ET.SubElement(channel, "item")
        
        # Заголовок
        item_title = ET.SubElement(item, "title")
        item_title.text = video['title']
        
        # Описание
        item_description = ET.SubElement(item, "description")
        item_description.text = f"Эпизод из подписки {subscription.name}: {video['title']}"
        
        # Дата публикации
        pub_date = ET.SubElement(item, "pubDate")
        pub_date.text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
        
        # GUID
        guid = ET.SubElement(item, "guid")
        guid.text = f"https://www.youtube.com/watch?v={video['id']}"
        
        # Ссылка на аудио файл
        enclosure = ET.SubElement(item, "enclosure")
        mp3_filename = f"{get_file_hash(video['title'])}.mp3"
        mp3_url = f"{base_url}/data/{subscription.name}/{mp3_filename}"
        enclosure.set("url", mp3_url)
        enclosure.set("type", "audio/mpeg")
        mp3_path = f"data/{subscription.name}/{mp3_filename}"
        if os.path.exists(mp3_path):
            enclosure.set("length", str(os.path.getsize(mp3_path)))
        else:
            enclosure.set("length", "0")
        
        # Превью для эпизода
        thumbnail_filename = f"{get_file_hash(video['title'])}.webp"
        thumbnail_path = f"data/{subscription.name}/{thumbnail_filename}"
        if os.path.exists(thumbnail_path):
            itunes_item_image = ET.SubElement(item, "itunes:image")
            thumbnail_url = f"{base_url}/data/{subscription.name}/{thumbnail_filename}"
            itunes_item_image.set("href", thumbnail_url)
        
        # Длительность для iTunes
        if video['duration']:
            itunes_duration = ET.SubElement(item, "itunes:duration")
            hours = video['duration'] // 3600
            minutes = (video['duration'] % 3600) // 60
            seconds = video['duration'] % 60
            if hours > 0:
                duration_str = f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                duration_str = f"{minutes}:{seconds:02d}"
            itunes_duration.text = duration_str
        
        # Автор для iTunes
        itunes_item_author = ET.SubElement(item, "itunes:author")
        itunes_item_author.text = video['uploader']
        
        # Дополнительные iTunes теги
        itunes_item_summary = ET.SubElement(item, "itunes:summary")
        itunes_item_summary.text = f"Эпизод из подписки {subscription.name}: {video['title']}"
        
        # Категория эпизода
        itunes_item_category = ET.SubElement(item, "itunes:category")
        itunes_item_category.text = subscription.category
    
    # Записываем RSS файл
    tree = ET.ElementTree(rss)
    ET.indent(tree, space="  ")
    tree.write(rss_file, encoding='utf-8', xml_declaration=True)
    
    print(f"RSS файл обновлен: {rss_file}")
    print(f"Добавлено {len(downloaded_videos)} загруженных эпизодов в RSS")


def process_source(source: Source, subscription: Subscription) -> bool:
    """
    Обрабатывает один источник в рамках подписки
    
    Args:
        source: Конфигурация источника
        subscription: Конфигурация подписки
        
    Returns:
        True если обработка прошла успешно, False если нет
    """
    print(f"\n🔄 Обработка источника: {source.name} (подписка: {subscription.name})")
    print(f"📋 Тип: {source.source_type.value}")
    print(f"🔗 URL: {source.url}")
    print("-" * 50)
    
    try:
        # Проверяем переменную окружения для предотвращения загрузки в тестах
        if os.environ.get('SKIP_DOWNLOAD', 'false').lower() in ('true', '1', 'yes'):
            print(f"🚫 Обработка пропущена (SKIP_DOWNLOAD=true) для источника: {source.name}")
            return True
        
        # Если включен dry-run режим, выполняем анализ
        if dry_run:
            analysis_result = dry_run_analysis(source, subscription)
            return analysis_result.get('will_download') is not None
        
        # Получаем информацию о видео
        videos = get_videos_from_source(source)
        
        if not videos:
            print(f"❌ Не удалось получить видео из источника: {source.name}")
            return False
        
        # Выводим информацию о видео (если есть)
        if videos:
            print_video_links(videos, source.name)
        
        # Загружаем аудио из последнего видео
        latest_video = download_latest_audio(videos, source, subscription)
        
        # Создаем/обновляем RSS файл
        if latest_video and latest_video != {}:
            create_or_update_rss(videos, source, subscription, latest_video)
            return True
        else:
            print(f"❌ Не удалось загрузить видео для RSS из источника: {source.name}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при обработке источника '{source.name}': {e}")
        return False


def dry_run_analysis(source: Source, subscription: Subscription) -> Dict[str, Any]:
    """
    Анализирует что будет загружено без фактической загрузки (dry-run режим)
    
    Args:
        source: Конфигурация источника
        subscription: Конфигурация подписки
        
    Returns:
        Словарь с информацией о том, что будет загружено
    """
    print(f"\n🔍 DRY-RUN: Анализ источника '{source.name}' в подписке '{subscription.name}'")
    print("=" * 80)
    
    # Получаем видео из источника
    if source.source_type == SourceType.PLAYLIST:
        playlist_data = get_playlist_info_and_videos(source)
        videos = playlist_data.get('entries', [])
        
        if playlist_data:
            print(f"📋 Плейлист: {playlist_data.get('title', 'Неизвестно')}")
            print(f"👤 Автор: {playlist_data.get('uploader', 'Неизвестно')}")
            print(f"📊 Всего видео: {playlist_data.get('video_count', 0)}")
            if playlist_data.get('last_updated'):
                print(f"🔄 Последнее обновление: {playlist_data['last_updated']}")
    else:
        videos = get_videos_from_source(source)
    
    if not videos:
        print("❌ DRY-RUN: Нет видео для анализа")
        return {}
    
    # Анализируем последние видео
    print(f"\n📺 DRY-RUN: Анализ последних {min(source.max_videos, len(videos))} видео:")
    print("-" * 80)
    
    analysis_result = {
        'source_name': source.name,
        'subscription_name': subscription.name,
        'total_videos_found': len(videos),
        'videos_to_check': min(source.max_videos, len(videos)),
        'available_videos': [],
        'unavailable_videos': [],
        'will_download': None
    }
    
    # Проверяем доступность видео
    for i, video in enumerate(videos[:source.max_videos]):
        print(f"\n{i+1}. {video['title']}")
        print(f"   ID: {video['id']}")
        print(f"   URL: https://www.youtube.com/watch?v={video['id']}")
        print(f"   Автор: {video['uploader']}")
        
        if video.get('upload_date'):
            upload_date = video['upload_date']
            formatted_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
            print(f"   📅 Дата загрузки: {formatted_date}")
        
        if video.get('playlist_position'):
            print(f"   📋 Позиция в плейлисте: {video['playlist_position']}")
        
        # Проверяем доступность
        is_available = check_video_availability(video['id'])
        
        if is_available:
            print(f"   ✅ Доступно")
            analysis_result['available_videos'].append(video)
        else:
            print(f"   ❌ Недоступно")
            analysis_result['unavailable_videos'].append(video)
    
    # Определяем какое видео будет загружено
    if analysis_result['available_videos']:
        will_download = analysis_result['available_videos'][0]  # Первое доступное
        analysis_result['will_download'] = will_download
        
        print(f"\n🎯 DRY-RUN: Будет загружено видео:")
        print(f"   Название: {will_download['title']}")
        print(f"   ID: {will_download['id']}")
        print(f"   URL: https://www.youtube.com/watch?v={will_download['id']}")
        
        # Проверяем, существует ли уже файл
        file_hash = get_file_hash(will_download['title'])
        mp3_filename = f"{file_hash}.mp3"
        subscription_dir = f"data/{subscription.name}"
        mp3_path = os.path.join(subscription_dir, mp3_filename)
        
        if os.path.exists(mp3_path):
            print(f"   ⚠️  Файл уже существует: {mp3_filename}")
            print(f"   📁 Путь: {mp3_path}")
            analysis_result['file_exists'] = True
        else:
            print(f"   📁 Файл будет создан: {mp3_filename}")
            print(f"   📁 Путь: {mp3_path}")
            analysis_result['file_exists'] = False
        
        # Показываем настройки загрузки
        download_settings = config_manager.get_download_setting('format', 'bestaudio/best')
        audio_codec = config_manager.get_download_setting('audio_codec', 'mp3')
        audio_quality = config_manager.get_download_setting('audio_quality', '192')
        
        print(f"\n⚙️  DRY-RUN: Настройки загрузки:")
        print(f"   Формат: {download_settings}")
        print(f"   Кодек: {audio_codec}")
        print(f"   Качество: {audio_quality}")
        
    else:
        print(f"\n❌ DRY-RUN: Нет доступных видео для загрузки")
        analysis_result['will_download'] = None
    
    # Статистика
    print(f"\n📊 DRY-RUN: Статистика:")
    print(f"   Всего найдено видео: {analysis_result['total_videos_found']}")
    print(f"   Проверено видео: {analysis_result['videos_to_check']}")
    print(f"   Доступных видео: {len(analysis_result['available_videos'])}")
    print(f"   Недоступных видео: {len(analysis_result['unavailable_videos'])}")
    
    return analysis_result


def main_loop(subscription_filter: str = None, source_filter: str = None):
    """
    Основной цикл программы с автоматическим запуском
    
    Args:
        subscription_filter: Фильтр по названию подписки (опционально)
        source_filter: Фильтр по названию источника (опционально)
    """
    global running
    
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    mode_text = "DRY-RUN" if dry_run else "Обычный"
    print(f"🎙️  YouTube2Podcast Multi-Source загрузчик запущен ({mode_text} режим)")
    print("⏰ Программа будет обрабатывать все источники каждые 10 минут")
    if subscription_filter:
        print(f"📋 Фильтр подписки: {subscription_filter}")
    if source_filter:
        print(f"📋 Фильтр источника: {source_filter}")
    print("🛑 Для остановки нажмите Ctrl+C")
    print("=" * 50)
    
    # Запускаем диагностику сетевых проблем
    diagnose_network_issues()
    
    while running:
        try:
            print(f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Запуск итерации")
            
            # Получаем активные подписки
            enabled_subscriptions = get_enabled_subscriptions()
            
            if not enabled_subscriptions:
                print("❌ Нет активных подписок для обработки")
                break
            
            print(f"📋 Найдено {len(enabled_subscriptions)} активных подписок")
            
            # Обрабатываем каждую подписку
            total_success_count = 0
            total_sources_count = 0
            
            for subscription in enabled_subscriptions:
                print(f"\n📦 Обработка подписки: {subscription.title}")
                print(f"📝 Описание: {subscription.description}")
                print(f"📊 Источников в подписке: {len(subscription.sources)}")
                print("-" * 50)
                
                # Обрабатываем источники в подписке
                subscription_success_count = 0
                enabled_sources = [source for source in subscription.sources if source.enabled]
                
                for source in enabled_sources:
                    if process_source(source, subscription):
                        subscription_success_count += 1
                    total_sources_count += 1
                    print()  # Пустая строка между источниками
                
                total_success_count += subscription_success_count
                print(f"✅ Подписка '{subscription.title}' завершена. Успешно: {subscription_success_count}/{len(enabled_sources)} источников")
            
            print(f"✅ Итерация завершена в {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"📊 Успешно обработано: {total_success_count}/{total_sources_count} источников")
            
            if running:
                print("⏳ Ожидание 10 минут до следующего запуска...")
                # Ждем 10 минут (600 секунд)
                for i in range(600):
                    if not running:
                        break
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            print("\n🛑 Получен сигнал прерывания")
            running = False
        except Exception as e:
            print(f"❌ Ошибка в основной программе: {e}")
            if running:
                print("⏳ Ожидание 10 минут перед повторной попыткой...")
                time.sleep(600)
    
    print("👋 Программа завершена")


def main(subscription_filter: str = None, source_filter: str = None):
    """
    Основная функция для однократного запуска
    
    Args:
        subscription_filter: Фильтр по названию подписки (опционально)
        source_filter: Фильтр по названию источника (опционально)
    """
    # Запускаем диагностику сетевых проблем
    diagnose_network_issues()
    
    mode_text = "DRY-RUN" if dry_run else "Обычный"
    print(f"🎙️  YouTube2Podcast Multi-Source - Однократный запуск ({mode_text} режим)")
    print("=" * 50)
    
    # Получаем активные подписки
    enabled_subscriptions = get_enabled_subscriptions()
    
    if not enabled_subscriptions:
        print("❌ Нет активных подписок для обработки")
        return
    
    # Фильтруем подписки если указан фильтр
    if subscription_filter:
        enabled_subscriptions = [sub for sub in enabled_subscriptions if sub.name == subscription_filter]
        if not enabled_subscriptions:
            print(f"❌ Подписка '{subscription_filter}' не найдена или неактивна")
            return
        print(f"📋 Фильтр подписки: {subscription_filter}")
    
    print(f"📋 Найдено {len(enabled_subscriptions)} активных подписок")
    
    # Обрабатываем каждую подписку
    total_success_count = 0
    total_sources_count = 0
    
    for subscription in enabled_subscriptions:
        print(f"\n📦 Обработка подписки: {subscription.title}")
        print(f"📝 Описание: {subscription.description}")
        print(f"📊 Источников в подписке: {len(subscription.sources)}")
        print("-" * 50)
        
        # Обрабатываем источники в подписке
        subscription_success_count = 0
        enabled_sources = [source for source in subscription.sources if source.enabled]
        
        # Фильтруем источники если указан фильтр
        if source_filter:
            enabled_sources = [source for source in enabled_sources if source.name == source_filter]
            if not enabled_sources:
                print(f"❌ Источник '{source_filter}' не найден или неактивен в подписке '{subscription.name}'")
                continue
            print(f"📋 Фильтр источника: {source_filter}")
        
        for source in enabled_sources:
            if process_source(source, subscription):
                subscription_success_count += 1
            total_sources_count += 1
            print()  # Пустая строка между источниками
        
        total_success_count += subscription_success_count
        print(f"✅ Подписка '{subscription.title}' завершена. Успешно: {subscription_success_count}/{len(enabled_sources)} источников")
    
    print(f"\n📊 Общая обработка завершена. Успешно: {total_success_count}/{total_sources_count} источников")


def init_application():
    """
    Инициализирует приложение с аргументами командной строки
    """
    global dry_run
    
    # Парсим аргументы командной строки
    args = parse_arguments()
    
    # Устанавливаем глобальные переменные
    dry_run = args.dry_run
    
    # Запускаем в зависимости от аргументов
    if args.loop:
        main_loop(args.subscription, args.source)
    else:
        main(args.subscription, args.source)


if __name__ == "__main__":
    init_application()
