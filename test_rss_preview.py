#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки RSS с превью
"""

import sys
import os
import xml.etree.ElementTree as ET

# Добавляем корневую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Source, SourceType, Subscription
from multi_downloader import create_or_update_rss, get_file_hash


def test_rss_with_preview():
    """Тестируем создание RSS с превью"""
    
    print("🧪 Тестирование RSS с превью")
    print("=" * 60)
    
    # Создаем тестовый источник
    test_source = Source(
        name="test_source",
        url="https://www.youtube.com/@varlamov",
        source_type=SourceType.CHANNEL,
        enabled=True,
        check_interval=10,
        max_videos=3,
        custom_title="Test Source",
        custom_description="Test Description",
        category="Test",
        author="test_author"
    )
    
    # Создаем тестовую подписку
    test_subscription = Subscription(
        name="test_subscription",
        title="Test Subscription",
        description="Test subscription for RSS preview testing",
        enabled=True,
        category="Test",
        author="test_author",
        sources=[test_source]
    )
    
    # Создаем тестовые видео
    test_videos = [
        {
            'title': 'Test Video 1 - Introduction',
            'id': 'test123',
            'uploader': 'Test Channel',
            'duration': 1800,  # 30 минут
            'upload_date': '20241201'
        },
        {
            'title': 'Test Video 2 - Main Content',
            'id': 'test456',
            'uploader': 'Test Channel',
            'duration': 2400,  # 40 минут
            'upload_date': '20241202'
        }
    ]
    
    # Создаем тестовые файлы
    subscription_dir = f"data/{test_subscription.name}"
    os.makedirs(subscription_dir, exist_ok=True)
    
    # Создаем тестовые MP3 файлы
    for video in test_videos:
        file_hash = get_file_hash(video['title'])
        mp3_path = f"{subscription_dir}/{file_hash}.mp3"
        webp_path = f"{subscription_dir}/{file_hash}.webp"
        
        # Создаем пустые файлы для тестирования
        with open(mp3_path, 'w') as f:
            f.write("test mp3 content")
        
        with open(webp_path, 'w') as f:
            f.write("test webp content")
        
        print(f"📁 Создан тестовый файл: {mp3_path}")
        print(f"🖼️ Создан тестовый превью: {webp_path}")
    
    # Тестируем создание RSS
    print(f"\n📋 Создание RSS для подписки: {test_subscription.name}")
    create_or_update_rss(test_videos, test_source, test_subscription, test_videos[0])
    
    # Проверяем созданный RSS файл
    rss_file = f"{subscription_dir}/podcast.rss"
    if os.path.exists(rss_file):
        print(f"✅ RSS файл создан: {rss_file}")
        
        # Парсим и проверяем RSS
        tree = ET.parse(rss_file)
        root = tree.getroot()
        
        # Регистрируем namespace для iTunes
        ET.register_namespace('itunes', 'http://www.itunes.com/dtds/podcast-1.0.dtd')
        
        # Проверяем превью канала
        channel = root.find('channel')
        if channel is not None:
            itunes_image = channel.find('{http://www.itunes.com/dtds/podcast-1.0.dtd}image')
            if itunes_image is not None:
                print(f"🖼️ Превью канала: {itunes_image.get('href')}")
            else:
                print("❌ Превью канала не найдено")
        
        # Проверяем превью эпизодов
        items = root.findall('channel/item')
        print(f"📊 Найдено {len(items)} эпизодов в RSS")
        
        for i, item in enumerate(items, 1):
            title = item.find('title')
            itunes_image = item.find('{http://www.itunes.com/dtds/podcast-1.0.dtd}image')
            
            print(f"  {i}. {title.text if title is not None else 'Без названия'}")
            if itunes_image is not None:
                print(f"     🖼️ Превью: {itunes_image.get('href')}")
            else:
                print(f"     ❌ Превью не найдено")
        
        # Проверяем URL аудио файлов
        print(f"\n🔗 Проверка URL аудио файлов:")
        for item in items:
            enclosure = item.find('enclosure')
            if enclosure is not None:
                print(f"  📻 {enclosure.get('url')}")
        
    else:
        print(f"❌ RSS файл не создан: {rss_file}")


def validate_rss_structure():
    """Проверяем структуру RSS файла"""
    
    print("\n🔍 Проверка структуры RSS файла")
    print("=" * 60)
    
    subscription_dir = "data/test_subscription"
    rss_file = f"{subscription_dir}/podcast.rss"
    
    if not os.path.exists(rss_file):
        print(f"❌ RSS файл не найден: {rss_file}")
        return
    
    try:
        # Регистрируем namespace для iTunes
        ET.register_namespace('itunes', 'http://www.itunes.com/dtds/podcast-1.0.dtd')
        
        tree = ET.parse(rss_file)
        root = tree.getroot()
        
        # Проверяем обязательные элементы
        required_elements = [
            'channel/title',
            'channel/description',
            'channel/language',
            'channel/item'
        ]
        
        print("✅ Обязательные элементы RSS:")
        for element_path in required_elements:
            element = root.find(element_path)
            if element is not None:
                print(f"  ✅ {element_path}: {element.text[:50]}...")
            else:
                print(f"  ❌ {element_path}: не найден")
        
        # Проверяем iTunes элементы
        itunes_elements = [
            'channel/{http://www.itunes.com/dtds/podcast-1.0.dtd}author',
            'channel/{http://www.itunes.com/dtds/podcast-1.0.dtd}summary',
            'channel/{http://www.itunes.com/dtds/podcast-1.0.dtd}category',
            'channel/{http://www.itunes.com/dtds/podcast-1.0.dtd}image',
            'channel/{http://www.itunes.com/dtds/podcast-1.0.dtd}explicit',
            'channel/{http://www.itunes.com/dtds/podcast-1.0.dtd}type'
        ]
        
        print("\n✅ iTunes элементы:")
        for element_path in itunes_elements:
            element = root.find(element_path)
            if element is not None:
                print(f"  ✅ {element_path.split('}')[-1]}: {element.text}")
            else:
                print(f"  ❌ {element_path.split('}')[-1]}: не найден")
        
        # Проверяем элементы эпизодов
        items = root.findall('channel/item')
        if items:
            first_item = items[0]
            item_elements = [
                'title',
                'description',
                'enclosure',
                '{http://www.itunes.com/dtds/podcast-1.0.dtd}duration',
                '{http://www.itunes.com/dtds/podcast-1.0.dtd}author',
                '{http://www.itunes.com/dtds/podcast-1.0.dtd}summary',
                '{http://www.itunes.com/dtds/podcast-1.0.dtd}category',
                '{http://www.itunes.com/dtds/podcast-1.0.dtd}image'
            ]
            
            print(f"\n✅ Элементы эпизода:")
            for element_path in item_elements:
                element = first_item.find(element_path)
                if element is not None:
                    if element_path == 'enclosure':
                        print(f"  ✅ {element_path}: {element.get('url')}")
                    else:
                        print(f"  ✅ {element_path}: {element.text[:50]}...")
                else:
                    print(f"  ❌ {element_path}: не найден")
        
    except ET.ParseError as e:
        print(f"❌ Ошибка парсинга RSS: {e}")


if __name__ == "__main__":
    test_rss_with_preview()
    validate_rss_structure()
