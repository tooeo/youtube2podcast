#!/usr/bin/env python3
"""
Конфигурация для YouTube2Podcast
"""

import os
import yaml
from typing import List, Dict, Any, Union, Optional
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class SourceType(Enum):
    """Типы источников"""
    PLAYLIST = "playlist"
    CHANNEL = "channel"


@dataclass
class Source:
    """Конфигурация источника"""
    name: str
    url: str
    source_type: SourceType
    enabled: bool = True
    check_interval: int = 10  # минуты
    max_videos: int = 5  # количество последних видео для проверки
    custom_title: str = None  # кастомное название для RSS
    custom_description: str = None  # кастомное описание для RSS
    category: str = "News & Politics"  # категория для iTunes
    author: str = None  # автор


@dataclass
class Subscription:
    """Конфигурация подписки"""
    name: str
    title: str
    description: str
    enabled: bool = True
    category: str = "News & Politics"
    author: str = None
    sources: List[Source] = None


@dataclass
class Config:
    """Основная конфигурация"""
    global_settings: Dict[str, Any]
    subscriptions: List[Subscription]
    download_settings: Dict[str, Any]
    rss_settings: Dict[str, Any]
    logging_settings: Dict[str, Any]
    diagnostics_settings: Dict[str, Any]


class ConfigManager:
    """Менеджер конфигурации"""
    
    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = config_file
        self.config = None
        self._load_config()
    
    def _load_config(self) -> None:
        """Загрузить конфигурацию из YAML файла"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
            
            # Парсим подписки
            subscriptions = []
            for sub_name, sub_data in yaml_data.get('subscriptions', {}).items():
                # Парсим источники в подписке
                sources = []
                for source_name, source_data in sub_data.get('sources', {}).items():
                    source_type = SourceType(source_data.get('type', 'channel'))
                    
                    # Применяем глобальные настройки по умолчанию
                    global_settings = yaml_data.get('global', {})
                    check_interval = source_data.get('check_interval', global_settings.get('check_interval', 10))
                    max_videos = source_data.get('max_videos', global_settings.get('max_videos', 5))
                    
                    source = Source(
                        name=source_name,
                        url=source_data['url'],
                        source_type=source_type,
                        enabled=source_data.get('enabled', True),
                        check_interval=check_interval,
                        max_videos=max_videos,
                        custom_title=source_data.get('custom_title'),
                        custom_description=source_data.get('custom_description'),
                        category=source_data.get('category', sub_data.get('category', 'News & Politics')),
                        author=source_data.get('author', sub_data.get('author'))
                    )
                    sources.append(source)
                
                subscription = Subscription(
                    name=sub_name,
                    title=sub_data.get('title', sub_name.title()),
                    description=sub_data.get('description', ''),
                    enabled=sub_data.get('enabled', True),
                    category=sub_data.get('category', 'News & Politics'),
                    author=sub_data.get('author'),
                    sources=sources
                )
                subscriptions.append(subscription)
            
            self.config = Config(
                global_settings=yaml_data.get('global', {}),
                subscriptions=subscriptions,
                download_settings=yaml_data.get('download', {}),
                rss_settings=yaml_data.get('rss', {}),
                logging_settings=yaml_data.get('logging', {}),
                diagnostics_settings=yaml_data.get('diagnostics', {})
            )
            
        except FileNotFoundError:
            print(f"❌ Файл конфигурации {self.config_file} не найден")
            print("📝 Скопируйте config.yaml.dist в config.yaml и настройте под свои нужды:")
            print("   cp config.yaml.dist config.yaml")
            self._create_default_config()
        except yaml.YAMLError as e:
            print(f"❌ Ошибка парсинга YAML: {e}")
            self._create_default_config()
        except Exception as e:
            print(f"❌ Ошибка загрузки конфигурации: {e}")
            self._create_default_config()
    
    def _create_default_config(self) -> None:
        """Создать конфигурацию по умолчанию"""
        print("📝 Создание конфигурации по умолчанию...")
        
        default_sources = [
            Source(
                name="che_proishodit",
                url="https://www.youtube.com/playlist?list=PLceIIEa--FBIIrCD1GIp7ndizRDCwcJgf",
                source_type=SourceType.PLAYLIST,
                custom_title="Чё Происходит - Подкаст",
                custom_description="Еженедельный подкаст о том, что происходит в мире"
            ),
            Source(
                name="varlamov",
                url="https://www.youtube.com/@varlamov",
                source_type=SourceType.CHANNEL,
                custom_title="Varlamov - Подкаст",
                custom_description="Подкаст с канала Varlamov"
            )
        ]
        
        default_subscription = Subscription(
            name="news_politics",
            title="Новости и политика",
            description="Подкасты о новостях и политических событиях",
            sources=default_sources
        )
        
        self.config = Config(
            global_settings={'check_interval': 10, 'max_videos': 5, 'language': 'ru'},
            subscriptions=[default_subscription],
            download_settings={'format': 'bestaudio/best', 'audio_codec': 'mp3'},
            rss_settings={'version': '2.0'},
            logging_settings={'level': 'INFO'},
            diagnostics_settings={'enabled': True}
        )
    
    def save_config(self) -> None:
        """Сохранить конфигурацию в YAML файл"""
        try:
            yaml_data = {
                'global': self.config.global_settings,
                'subscriptions': {},
                'download': self.config.download_settings,
                'rss': self.config.rss_settings,
                'logging': self.config.logging_settings,
                'diagnostics': self.config.diagnostics_settings
            }
            
            # Сохраняем подписки
            for subscription in self.config.subscriptions:
                yaml_data['subscriptions'][subscription.name] = {
                    'enabled': subscription.enabled,
                    'title': subscription.title,
                    'description': subscription.description,
                    'category': subscription.category,
                    'author': subscription.author,
                    'sources': {}
                }
                
                # Сохраняем источники в подписке
                for source in subscription.sources:
                    yaml_data['subscriptions'][subscription.name]['sources'][source.name] = {
                        'enabled': source.enabled,
                        'type': source.source_type.value,
                        'url': source.url,
                        'custom_title': source.custom_title,
                        'custom_description': source.custom_description,
                        'check_interval': source.check_interval,
                        'max_videos': source.max_videos,
                        'category': source.category,
                        'author': source.author
                    }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(yaml_data, f, default_flow_style=False, allow_unicode=True, indent=2)
            
            print(f"✅ Конфигурация сохранена в {self.config_file}")
            
        except Exception as e:
            print(f"❌ Ошибка сохранения конфигурации: {e}")
    
    def get_enabled_subscriptions(self) -> List[Subscription]:
        """Получить список активных подписок"""
        return [sub for sub in self.config.subscriptions if sub.enabled]

    def get_subscription_by_name(self, name: str) -> Subscription:
        """Получить подписку по имени"""
        for subscription in self.config.subscriptions:
            if subscription.name == name:
                return subscription
        raise ValueError(f"Подписка '{name}' не найдена")

    def get_all_enabled_sources(self) -> List[Source]:
        """Получить список всех активных источников из всех активных подписок"""
        sources = []
        for subscription in self.get_enabled_subscriptions():
            sources.extend([source for source in subscription.sources if source.enabled])
        return sources

    def get_source_by_name(self, name: str) -> Source:
        """Получить источник по имени из всех подписок"""
        for subscription in self.config.subscriptions:
            for source in subscription.sources:
                if source.name == name:
                    return source
        raise ValueError(f"Источник '{name}' не найден")

    def add_subscription(self, subscription: Subscription) -> None:
        """Добавить новую подписку"""
        # Проверяем, что подписка с таким именем не существует
        for existing_sub in self.config.subscriptions:
            if existing_sub.name == subscription.name:
                raise ValueError(f"Подписка '{subscription.name}' уже существует")
        
        self.config.subscriptions.append(subscription)
        self.save_config()

    def remove_subscription(self, name: str) -> None:
        """Удалить подписку по имени"""
        self.config.subscriptions = [sub for sub in self.config.subscriptions if sub.name != name]
        self.save_config()

    def enable_subscription(self, name: str) -> None:
        """Включить подписку"""
        subscription = self.get_subscription_by_name(name)
        subscription.enabled = True
        self.save_config()

    def disable_subscription(self, name: str) -> None:
        """Отключить подписку"""
        subscription = self.get_subscription_by_name(name)
        subscription.enabled = False
        self.save_config()

    def list_subscriptions(self) -> List[Dict[str, Any]]:
        """Получить список всех подписок с их статусом"""
        result = []
        for subscription in self.config.subscriptions:
            enabled_sources = [source for source in subscription.sources if source.enabled]
            result.append({
                'name': subscription.name,
                'title': subscription.title,
                'description': subscription.description,
                'enabled': subscription.enabled,
                'category': subscription.category,
                'author': subscription.author,
                'sources_count': len(subscription.sources),
                'enabled_sources_count': len(enabled_sources)
            })
        return result

    def list_sources(self) -> List[Dict[str, Any]]:
        """Получить список всех источников с их статусом и подпиской"""
        result = []
        for subscription in self.config.subscriptions:
            for source in subscription.sources:
                result.append({
                    'name': source.name,
                    'subscription': subscription.name,
                    'url': source.url,
                    'type': source.source_type.value,
                    'enabled': source.enabled and subscription.enabled,
                    'check_interval': source.check_interval,
                    'max_videos': source.max_videos,
                    'custom_title': source.custom_title,
                    'custom_description': source.custom_description,
                    'category': source.category,
                    'author': source.author
                })
        return result
    
    def get_global_setting(self, key: str, default=None):
        """Получить глобальную настройку"""
        return self.config.global_settings.get(key, default)
    
    def get_download_setting(self, key: str, default=None):
        """Получить настройку загрузки"""
        return self.config.download_settings.get(key, default)
    
    def get_rss_setting(self, key: str, default=None):
        """Получить настройку RSS"""
        return self.config.rss_settings.get(key, default)
    
    def get_base_url(self) -> str:
        """Получить базовый URL для RSS ссылок"""
        return self.config.global_settings.get('base_url', 'http://localhost')


# Глобальный экземпляр менеджера конфигурации
config_manager = ConfigManager()


# Функции для обратной совместимости
def get_enabled_sources() -> List[Source]:
    """Получить список всех активных источников из всех активных подписок"""
    return config_manager.get_all_enabled_sources()


def get_source_by_name(name: str) -> Source:
    """Получить источник по имени"""
    return config_manager.get_source_by_name(name)


def add_source(name: str, url: str, source_type: SourceType, **kwargs) -> None:
    """Добавить новый источник в первую активную подписку"""
    source = Source(name=name, url=url, source_type=source_type, **kwargs)
    # Добавляем в первую активную подписку или создаем новую
    enabled_subs = config_manager.get_enabled_subscriptions()
    if enabled_subs:
        enabled_subs[0].sources.append(source)
        config_manager.save_config()
    else:
        # Создаем новую подписку по умолчанию
        subscription = Subscription(
            name="default",
            title="Default Subscription",
            description="Default subscription",
            sources=[source]
        )
        config_manager.add_subscription(subscription)


def remove_source(name: str) -> None:
    """Удалить источник по имени из всех подписок"""
    for subscription in config_manager.config.subscriptions:
        subscription.sources = [s for s in subscription.sources if s.name != name]
    config_manager.save_config()


def enable_source(name: str) -> None:
    """Включить источник"""
    source = config_manager.get_source_by_name(name)
    source.enabled = True
    config_manager.save_config()


def disable_source(name: str) -> None:
    """Отключить источник"""
    source = config_manager.get_source_by_name(name)
    source.enabled = False
    config_manager.save_config()


def list_sources() -> List[Dict[str, Any]]:
    """Получить список всех источников с их статусом"""
    return config_manager.list_sources()


# Новые функции для работы с подписками
def get_enabled_subscriptions() -> List[Subscription]:
    """Получить список активных подписок"""
    return config_manager.get_enabled_subscriptions()


def get_subscription_by_name(name: str) -> Subscription:
    """Получить подписку по имени"""
    return config_manager.get_subscription_by_name(name)


def add_subscription(name: str, title: str, description: str, **kwargs) -> None:
    """Добавить новую подписку"""
    subscription = Subscription(name=name, title=title, description=description, **kwargs)
    config_manager.add_subscription(subscription)


def remove_subscription(name: str) -> None:
    """Удалить подписку по имени"""
    config_manager.remove_subscription(name)


def enable_subscription(name: str) -> None:
    """Включить подписку"""
    config_manager.enable_subscription(name)


def disable_subscription(name: str) -> None:
    """Отключить подписку"""
    config_manager.disable_subscription(name)


def list_subscriptions() -> List[Dict[str, Any]]:
    """Получить список всех подписок с их статусом"""
    return config_manager.list_subscriptions()
