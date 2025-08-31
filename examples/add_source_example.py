#!/usr/bin/env python3
"""
Пример добавления нового источника в YouTube2Podcast
"""

import sys
import os

# Добавляем корневую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Source, SourceType, add_source, add_subscription, list_sources, list_subscriptions


def main():
    """Пример добавления нового источника"""
    print("🎯 Пример добавления нового источника")
    print("=" * 40)
    
    # Показываем текущие подписки
    print("📦 Текущие подписки:")
    subscriptions = list_subscriptions()
    for sub in subscriptions:
        print(f"  - {sub['name']} ({sub['title']})")
    
    # Показываем текущие источники
    print("\n📋 Текущие источники:")
    sources = list_sources()
    for source in sources:
        print(f"  - {source['name']} ({source['type']}) в подписке '{source['subscription']}'")
    
    print("\n➕ Добавляем новую подписку и источник...")
    
    # Добавляем новую подписку
    add_subscription(
        name="example_subscription",
        title="Example Subscription",
        description="Пример подписки для тестирования",
        category="Education",
        author="example_user"
    )
    
    # Добавляем новый источник в подписку
    add_source(
        name="example_channel",
        url="https://www.youtube.com/@example_channel",
        source_type=SourceType.CHANNEL,
        custom_title="Example Channel - Подкаст",
        custom_description="Пример подкаста с канала",
        check_interval=15,  # Проверка каждые 15 минут
        max_videos=3,       # Проверяем только 3 последних видео
        category="Education",
        author="example_user"
    )
    
    print("✅ Подписка и источник добавлены!")
    
    # Показываем обновленный список
    print("\n📦 Обновленный список подписок:")
    subscriptions = list_subscriptions()
    for sub in subscriptions:
        print(f"  - {sub['name']} ({sub['title']}) - {'✅ Активна' if sub['enabled'] else '❌ Отключена'}")
    
    print("\n📋 Обновленный список источников:")
    sources = list_sources()
    for source in sources:
        print(f"  - {source['name']} ({source['type']}) в подписке '{source['subscription']}' - {'✅ Активен' if source['enabled'] else '❌ Отключен'}")


if __name__ == "__main__":
    main()
