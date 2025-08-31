#!/usr/bin/env python3
"""
Утилита для управления источниками YouTube2Podcast
"""

import sys
import argparse
from config import (
    Source, SourceType, Subscription, get_enabled_sources, get_enabled_subscriptions, get_source_by_name,
    add_source, remove_source, enable_source, disable_source, list_sources,
    add_subscription, remove_subscription, enable_subscription, disable_subscription, list_subscriptions
)


def print_sources(sources):
    """Выводит список источников в табличном формате"""
    if not sources:
        print("❌ Нет источников")
        return
    
    print(f"\n📋 Найдено {len(sources)} источников:")
    print("=" * 120)
    print(f"{'Имя':<20} {'Подписка':<15} {'Тип':<10} {'Статус':<8} {'Интервал':<8} {'Макс.видео':<10} {'URL'}")
    print("-" * 120)
    
    for source in sources:
        status = "✅ Активен" if source['enabled'] else "❌ Отключен"
        subscription = source.get('subscription', 'N/A')
        print(f"{source['name']:<20} {subscription:<15} {source['type']:<10} {status:<8} {source['check_interval']:<8} {source['max_videos']:<10} {source['url']}")
    
    print("=" * 120)


def print_subscriptions(subscriptions):
    """Выводит список подписок в табличном формате"""
    if not subscriptions:
        print("❌ Нет подписок")
        return
    
    print(f"\n📦 Найдено {len(subscriptions)} подписок:")
    print("=" * 100)
    print(f"{'Имя':<20} {'Название':<25} {'Статус':<8} {'Категория':<15} {'Источников':<12}")
    print("-" * 100)
    
    for sub in subscriptions:
        status = "✅ Активна" if sub['enabled'] else "❌ Отключена"
        sources_info = f"{sub['enabled_sources_count']}/{sub['sources_count']}"
        print(f"{sub['name']:<20} {sub['title']:<25} {status:<8} {sub['category']:<15} {sources_info:<12}")
    
    print("=" * 100)


def add_source_interactive():
    """Интерактивное добавление источника"""
    print("\n➕ Добавление нового источника")
    print("-" * 30)
    
    # Получаем данные от пользователя
    name = input("Введите имя источника: ").strip()
    if not name:
        print("❌ Имя источника не может быть пустым")
        return
    
    url = input("Введите URL (плейлист или канал): ").strip()
    if not url:
        print("❌ URL не может быть пустым")
        return
    
    # Определяем тип источника
    if "playlist" in url:
        source_type = SourceType.PLAYLIST
    elif "@" in url or "channel" in url:
        source_type = SourceType.CHANNEL
    else:
        print("❌ Не удалось определить тип источника. Укажите явно:")
        print("1. Плейлист")
        print("2. Канал")
        choice = input("Выберите тип (1 или 2): ").strip()
        source_type = SourceType.PLAYLIST if choice == "1" else SourceType.CHANNEL
    
    # Дополнительные параметры
    custom_title = input("Кастомное название для RSS (необязательно): ").strip() or None
    custom_description = input("Кастомное описание для RSS (необязательно): ").strip() or None
    
    check_interval = input("Интервал проверки в минутах (по умолчанию 10): ").strip()
    check_interval = int(check_interval) if check_interval.isdigit() else 10
    
    max_videos = input("Количество последних видео для проверки (по умолчанию 5): ").strip()
    max_videos = int(max_videos) if max_videos.isdigit() else 5
    
    # Добавляем источник
    try:
        add_source(
            name=name,
            url=url,
            source_type=source_type,
            custom_title=custom_title,
            custom_description=custom_description,
            check_interval=check_interval,
            max_videos=max_videos
        )
        print(f"✅ Источник '{name}' успешно добавлен")
    except Exception as e:
        print(f"❌ Ошибка при добавлении источника: {e}")


def add_subscription_interactive():
    """Интерактивное добавление подписки"""
    print("\n📦 Добавление новой подписки")
    print("-" * 30)
    
    # Получаем данные от пользователя
    name = input("Введите имя подписки: ").strip()
    if not name:
        print("❌ Имя подписки не может быть пустым")
        return
    
    title = input("Введите название подписки: ").strip()
    if not title:
        title = name.title()
    
    description = input("Введите описание подписки: ").strip()
    if not description:
        description = f"Подкаст из подписки {name}"
    
    category = input("Введите категорию (по умолчанию 'News & Politics'): ").strip()
    if not category:
        category = "News & Politics"
    
    author = input("Введите автора (необязательно): ").strip() or None
    
    # Добавляем подписку
    try:
        add_subscription(
            name=name,
            title=title,
            description=description,
            category=category,
            author=author
        )
        print(f"✅ Подписка '{name}' успешно добавлена")
    except Exception as e:
        print(f"❌ Ошибка при добавлении подписки: {e}")


def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(
        description="Утилита для управления подписками и источниками YouTube2Podcast",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python manage_sources.py list                    # Показать все источники
  python manage_sources.py list-subscriptions      # Показать все подписки
  python manage_sources.py add                     # Интерактивное добавление источника
  python manage_sources.py add-subscription        # Интерактивное добавление подписки
  python manage_sources.py enable varlamov         # Включить источник
  python manage_sources.py disable varlamov       # Отключить источник
  python manage_sources.py remove varlamov        # Удалить источник
  python manage_sources.py enable-subscription news_politics  # Включить подписку
  python manage_sources.py disable-subscription news_politics  # Отключить подписку
  python manage_sources.py remove-subscription news_politics  # Удалить подписку
  python manage_sources.py add-source "test" "https://youtube.com/..." playlist  # Добавить программно
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Доступные команды')
    
    # Команда list
    list_parser = subparsers.add_parser('list', help='Показать все источники')
    
    # Команда list-subscriptions
    list_subscriptions_parser = subparsers.add_parser('list-subscriptions', help='Показать все подписки')
    
    # Команда add (интерактивная)
    add_parser = subparsers.add_parser('add', help='Интерактивное добавление источника')
    
    # Команда add-subscription (интерактивная)
    add_subscription_parser = subparsers.add_parser('add-subscription', help='Интерактивное добавление подписки')
    
    # Команда add-source (программная)
    add_source_parser = subparsers.add_parser('add-source', help='Программное добавление источника')
    add_source_parser.add_argument('name', help='Имя источника')
    add_source_parser.add_argument('url', help='URL источника')
    add_source_parser.add_argument('type', choices=['playlist', 'channel'], help='Тип источника')
    add_source_parser.add_argument('--title', help='Кастомное название для RSS')
    add_source_parser.add_argument('--description', help='Кастомное описание для RSS')
    add_source_parser.add_argument('--interval', type=int, default=10, help='Интервал проверки в минутах')
    add_source_parser.add_argument('--max-videos', type=int, default=5, help='Количество последних видео для проверки')
    
    # Команда enable
    enable_parser = subparsers.add_parser('enable', help='Включить источник')
    enable_parser.add_argument('name', help='Имя источника')
    
    # Команда disable
    disable_parser = subparsers.add_parser('disable', help='Отключить источник')
    disable_parser.add_argument('name', help='Имя источника')
    
    # Команда remove
    remove_parser = subparsers.add_parser('remove', help='Удалить источник')
    remove_parser.add_argument('name', help='Имя источника')
    
    # Команда enable-subscription
    enable_subscription_parser = subparsers.add_parser('enable-subscription', help='Включить подписку')
    enable_subscription_parser.add_argument('name', help='Имя подписки')
    
    # Команда disable-subscription
    disable_subscription_parser = subparsers.add_parser('disable-subscription', help='Отключить подписку')
    disable_subscription_parser.add_argument('name', help='Имя подписки')
    
    # Команда remove-subscription
    remove_subscription_parser = subparsers.add_parser('remove-subscription', help='Удалить подписку')
    remove_subscription_parser.add_argument('name', help='Имя подписки')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'list':
            sources = list_sources()
            print_sources(sources)
            
        elif args.command == 'list-subscriptions':
            subscriptions = list_subscriptions()
            print_subscriptions(subscriptions)
            
        elif args.command == 'add':
            add_source_interactive()
            
        elif args.command == 'add-subscription':
            add_subscription_interactive()
            
        elif args.command == 'add-source':
            source_type = SourceType.PLAYLIST if args.type == 'playlist' else SourceType.CHANNEL
            add_source(
                name=args.name,
                url=args.url,
                source_type=source_type,
                custom_title=args.title,
                custom_description=args.description,
                check_interval=args.interval,
                max_videos=args.max_videos
            )
            print(f"✅ Источник '{args.name}' успешно добавлен")
            
        elif args.command == 'enable':
            enable_source(args.name)
            print(f"✅ Источник '{args.name}' включен")
            
        elif args.command == 'disable':
            disable_source(args.name)
            print(f"✅ Источник '{args.name}' отключен")
            
        elif args.command == 'remove':
            remove_source(args.name)
            print(f"✅ Источник '{args.name}' удален")
            
        elif args.command == 'enable-subscription':
            enable_subscription(args.name)
            print(f"✅ Подписка '{args.name}' включена")
            
        elif args.command == 'disable-subscription':
            disable_subscription(args.name)
            print(f"✅ Подписка '{args.name}' отключена")
            
        elif args.command == 'remove-subscription':
            remove_subscription(args.name)
            print(f"✅ Подписка '{args.name}' удалена")
            
    except ValueError as e:
        print(f"❌ Ошибка: {e}")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")


if __name__ == "__main__":
    main()
