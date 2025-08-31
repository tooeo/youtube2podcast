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
from typing import List, Dict, Any

from config import Source, SourceType, Subscription, get_enabled_sources, get_enabled_subscriptions, get_source_by_name, config_manager


running = True

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
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Пытаемся извлечь информацию о видео
            result = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            return result is not None
    except Exception as e:
        # Если есть ошибка, видео недоступно
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


def get_videos_from_source(source: Source) -> List[Dict[str, Any]]:
    """
    Извлекает информацию о видео из источника (плейлист или канал)
    
    Args:
        source: Конфигурация источника
        
    Returns:
        Список словарей с информацией о видео
    """
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,  # Извлекаем только метаданные, без скачивания
        'ignoreerrors': True,  # Пропускаем ошибки для отдельных видео
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Извлекаем информацию об источнике
            source_info = ydl.extract_info(source.url, download=False)
            
            if not source_info or 'entries' not in source_info:
                print(f"❌ Не удалось получить информацию об источнике: {source.name}")
                return []
            
            videos = []
            for entry in source_info['entries']:
                if entry:  # Проверяем, что запись не пустая
                    video_info = {
                        'title': entry.get('title', 'Без названия'),
                        'url': entry.get('url', ''),
                        'id': entry.get('id', ''),
                        'duration': entry.get('duration', 0),
                        'uploader': entry.get('uploader', 'Неизвестно'),
                        'view_count': entry.get('view_count', 0)
                    }
                    videos.append(video_info)
            
            print(f"✅ Найдено {len(videos)} видео в источнике: {source.name}")
            return videos
            
    except Exception as e:
        print(f"❌ Ошибка при извлечении информации из источника {source.name}: {e}")
        return []


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
        print("-" * 80)


def download_latest_audio(videos: List[Dict[str, Any]], source: Source, subscription: Subscription) -> Dict[str, Any]:
    """
    Загружает аудио из последнего доступного видео
    
    Args:
        videos: Список всех видео из источника
        source: Конфигурация источника
        subscription: Конфигурация подписки
        
    Returns:
        Словарь с информацией о загруженном видео или пустой словарь
    """
    if not videos:
        print(f"❌ Нет видео для загрузки в источнике: {source.name}")
        return {}
    
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
            ydl.download([video_url])
            print(f"Аудио успешно загружено в папку: {subscription_dir}")
            return latest_video
            
    except Exception as e:
        print(f"❌ Ошибка при загрузке аудио из источника '{source.name}': {e}")
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
    
    itunes_image = ET.SubElement(channel, "itunes:image")
    itunes_image.set("href", f"data/{subscription.name}/{get_file_hash(latest_video['title'])}.webp")
    
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
        mp3_path = f"data/{subscription.name}/{get_file_hash(video['title'])}.mp3"
        enclosure.set("url", mp3_path)
        enclosure.set("type", "audio/mpeg")
        if os.path.exists(mp3_path):
            enclosure.set("length", str(os.path.getsize(mp3_path)))
        else:
            enclosure.set("length", "0")
        
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
        # Получаем информацию о видео
        videos = get_videos_from_source(source)
        
        if not videos:
            print(f"❌ Не удалось получить видео из источника: {source.name}")
            return False
        
        # Выводим информацию о видео
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


def main_loop():
    """
    Основной цикл программы с автоматическим запуском
    """
    global running
    
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🎙️  YouTube2Podcast Multi-Source загрузчик запущен")
    print("⏰ Программа будет обрабатывать все источники каждые 10 минут")
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


def main():
    """
    Основная функция для однократного запуска
    """
    # Запускаем диагностику сетевых проблем
    diagnose_network_issues()
    
    print("🎙️  YouTube2Podcast Multi-Source - Однократный запуск")
    print("=" * 50)
    
    # Получаем активные подписки
    enabled_subscriptions = get_enabled_subscriptions()
    
    if not enabled_subscriptions:
        print("❌ Нет активных подписок для обработки")
        return
    
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
    
    print(f"\n📊 Общая обработка завершена. Успешно: {total_success_count}/{total_sources_count} источников")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--loop":
        main_loop()
    else:
        main()
