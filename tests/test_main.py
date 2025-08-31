#!/usr/bin/env python3
"""
Tests for multi_downloader.py and config.py
"""

import pytest
import os
import tempfile
import shutil
import sys
import yaml
from unittest.mock import patch, MagicMock

# Добавляем корневую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Source, SourceType, Subscription, Config, ConfigManager


class TestConfigClasses:
    """Тесты для классов конфигурации"""

    def test_source_creation(self):
        """Тест создания объекта Source"""
        source = Source(
            name="test_source",
            url="https://www.youtube.com/@test",
            source_type=SourceType.CHANNEL,
            enabled=True,
            check_interval=10,
            max_videos=5,
            custom_title="Test Title",
            custom_description="Test Description",
            category="Test Category",
            author="test_author"
        )
        
        assert source.name == "test_source"
        assert source.url == "https://www.youtube.com/@test"
        assert source.source_type == SourceType.CHANNEL
        assert source.enabled is True
        assert source.check_interval == 10
        assert source.max_videos == 5
        assert source.custom_title == "Test Title"
        assert source.custom_description == "Test Description"
        assert source.category == "Test Category"
        assert source.author == "test_author"

    def test_subscription_creation(self):
        """Тест создания объекта Subscription"""
        source = Source(
            name="test_source",
            url="https://www.youtube.com/@test",
            source_type=SourceType.CHANNEL
        )
        
        subscription = Subscription(
            name="test_subscription",
            title="Test Subscription",
            description="Test Description",
            enabled=True,
            category="Test Category",
            author="test_author",
            sources=[source]
        )
        
        assert subscription.name == "test_subscription"
        assert subscription.title == "Test Subscription"
        assert subscription.description == "Test Description"
        assert subscription.enabled is True
        assert subscription.category == "Test Category"
        assert subscription.author == "test_author"
        assert len(subscription.sources) == 1
        assert subscription.sources[0].name == "test_source"

    def test_config_creation(self):
        """Тест создания объекта Config"""
        source = Source(
            name="test_source",
            url="https://www.youtube.com/@test",
            source_type=SourceType.CHANNEL
        )
        
        subscription = Subscription(
            name="test_subscription",
            title="Test Subscription",
            description="Test subscription description",
            sources=[source]
        )
        
        config = Config(
            global_settings={'check_interval': 10},
            subscriptions=[subscription],
            download_settings={'format': 'mp3'},
            rss_settings={'version': '2.0'},
            logging_settings={'level': 'INFO'},
            diagnostics_settings={'enabled': True}
        )
        
        assert config.global_settings['check_interval'] == 10
        assert len(config.subscriptions) == 1
        assert config.download_settings['format'] == 'mp3'
        assert config.rss_settings['version'] == '2.0'
        assert config.logging_settings['level'] == 'INFO'
        assert config.diagnostics_settings['enabled'] is True


class TestConfigManager:
    """Тесты для ConfigManager"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Создаем тестовый config.yaml
        test_config = {
            'global': {
                'check_interval': 10,
                'max_videos': 5,
                'language': 'ru',
                'timezone': 'Europe/Moscow',
                'base_url': 'http://test.domain.com'
            },
            'subscriptions': {
                'test_subscription': {
                    'enabled': True,
                    'title': 'Test Subscription',
                    'description': 'Test subscription description',
                    'category': 'Test',
                    'author': 'test_author',
                    'sources': {
                        'test_source': {
                            'enabled': True,
                            'type': 'channel',
                            'url': 'https://www.youtube.com/@test',
                            'custom_title': 'Test Source',
                            'custom_description': 'Test Description',
                            'category': 'Test',
                            'author': 'test_author'
                        }
                    }
                }
            },
            'download': {
                'format': 'bestaudio/best',
                'audio_codec': 'mp3'
            },
            'rss': {
                'version': '2.0'
            },
            'logging': {
                'level': 'INFO'
            },
            'diagnostics': {
                'enabled': True
            }
        }
        
        import yaml
        with open('config.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(test_config, f, default_flow_style=False, allow_unicode=True)
        
        # Проверяем, что файл создан
        assert os.path.exists('config.yaml'), "config.yaml должен быть создан в setup_method"

    def teardown_method(self):
        """Очистка после каждого теста"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)

    def test_config_manager_initialization(self):
        """Тест инициализации ConfigManager"""
        # config.yaml уже создан в setup_method
        config_manager = ConfigManager()
        
        assert config_manager.config_file == "config.yaml"
        assert hasattr(config_manager, 'config')
        assert isinstance(config_manager.config, Config)

    def test_get_enabled_subscriptions(self):
        """Тест получения активных подписок"""
        config_manager = ConfigManager()
        
        # Создаем тестовую конфигурацию
        source = Source(
            name="test_source",
            url="https://www.youtube.com/@test",
            source_type=SourceType.CHANNEL,
            enabled=True
        )
        
        subscription = Subscription(
            name="test_subscription",
            title="Test Subscription",
            description="Test subscription description",
            enabled=True,
            sources=[source]
        )
        
        # Заменяем подписки в конфигурации
        config_manager.config.subscriptions = [subscription]
        
        enabled_subscriptions = config_manager.get_enabled_subscriptions()
        assert len(enabled_subscriptions) == 1
        assert enabled_subscriptions[0].name == "test_subscription"

    def test_get_enabled_sources(self):
        """Тест получения активных источников"""
        config_manager = ConfigManager()
        
        # Создаем тестовую конфигурацию
        source1 = Source(
            name="test_source1",
            url="https://www.youtube.com/@test1",
            source_type=SourceType.CHANNEL,
            enabled=True
        )
        
        source2 = Source(
            name="test_source2",
            url="https://www.youtube.com/@test2",
            source_type=SourceType.CHANNEL,
            enabled=False
        )
        
        subscription = Subscription(
            name="test_subscription",
            title="Test Subscription",
            description="Test subscription description",
            enabled=True,
            sources=[source1, source2]
        )
        
        # Заменяем подписки в конфигурации
        config_manager.config.subscriptions = [subscription]
        
        enabled_sources = config_manager.get_all_enabled_sources()
        assert len(enabled_sources) == 1
        assert enabled_sources[0].name == "test_source1"


class TestSourceType:
    """Тесты для SourceType enum"""

    def test_source_type_values(self):
        """Тест значений SourceType"""
        assert SourceType.CHANNEL.value == "channel"
        assert SourceType.PLAYLIST.value == "playlist"

    def test_source_type_from_string(self):
        """Тест создания SourceType из строки"""
        assert SourceType("channel") == SourceType.CHANNEL
        assert SourceType("playlist") == SourceType.PLAYLIST


if __name__ == "__main__":
    pytest.main([__file__])
