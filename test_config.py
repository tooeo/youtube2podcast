#!/usr/bin/env python3
"""
Тестовый скрипт для проверки конфигурации
"""

from config import config_manager, list_sources, list_subscriptions, get_enabled_sources, get_enabled_subscriptions


def main():
    """Тестируем конфигурацию"""
    print("🧪 Тестирование конфигурации")
    print("=" * 40)
    
    # Показываем все подписки
    print("📦 Все подписки:")
    subscriptions = list_subscriptions()
    for sub in subscriptions:
        status = "✅ Активна" if sub['enabled'] else "❌ Отключена"
        print(f"  - {sub['name']} ({sub['title']}) - {status}")
        print(f"    Источников: {sub['enabled_sources_count']}/{sub['sources_count']}")
    
    # Показываем только активные подписки
    print("\n✅ Активные подписки:")
    enabled_subscriptions = get_enabled_subscriptions()
    for sub in enabled_subscriptions:
        print(f"  - {sub.name} ({sub.title})")
    
    # Показываем все источники
    print("\n📋 Все источники:")
    sources = list_sources()
    for source in sources:
        status = "✅ Активен" if source['enabled'] else "❌ Отключен"
        print(f"  - {source['name']} ({source['type']}) в подписке '{source['subscription']}' - {status}")
    
    # Показываем только активные источники
    print("\n✅ Активные источники:")
    enabled_sources = get_enabled_sources()
    for source in enabled_sources:
        print(f"  - {source.name} ({source.source_type.value})")
    
    # Показываем настройки
    print("\n⚙️ Глобальные настройки:")
    global_settings = config_manager.config.global_settings
    for key, value in global_settings.items():
        print(f"  - {key}: {value}")
    
    print("\n✅ Конфигурация загружена успешно!")


if __name__ == "__main__":
    main()
