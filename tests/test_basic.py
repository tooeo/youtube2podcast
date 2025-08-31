#!/usr/bin/env python3
"""
Basic tests for the application
"""

import pytest
import sys
import os

# Добавляем корневую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    """Тест импорта основных модулей"""
    try:
        from config import Source, SourceType, Subscription, Config, ConfigManager
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import config: {e}")

    try:
        import multi_downloader
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import multi_downloader: {e}")


def test_source_type_enum():
    """Тест enum SourceType"""
    from config import SourceType
    
    assert SourceType.CHANNEL.value == "channel"
    assert SourceType.PLAYLIST.value == "playlist"
    
    # Тест создания из строки
    assert SourceType("channel") == SourceType.CHANNEL
    assert SourceType("playlist") == SourceType.PLAYLIST


def test_source_creation():
    """Тест создания Source"""
    from config import Source, SourceType
    
    source = Source(
        name="test",
        url="https://www.youtube.com/@test",
        source_type=SourceType.CHANNEL,
        enabled=True,
        check_interval=10,
        max_videos=5,
        custom_title="Test",
        custom_description="Test Description",
        category="Test",
        author="test_author"
    )
    
    assert source.name == "test"
    assert source.url == "https://www.youtube.com/@test"
    assert source.source_type == SourceType.CHANNEL
    assert source.enabled is True


def test_subscription_creation():
    """Тест создания Subscription"""
    from config import Source, SourceType, Subscription
    
    source = Source(
        name="test_source",
        url="https://www.youtube.com/@test",
        source_type=SourceType.CHANNEL
    )
    
    subscription = Subscription(
        name="test_sub",
        title="Test Subscription",
        description="Test Description",
        enabled=True,
        category="Test",
        author="test_author",
        sources=[source]
    )
    
    assert subscription.name == "test_sub"
    assert subscription.title == "Test Subscription"
    assert len(subscription.sources) == 1
    assert subscription.sources[0].name == "test_source"


def test_config_manager_base_url():
    """Тест метода get_base_url"""
    from config import ConfigManager
    
    # Создаем временный ConfigManager
    config_manager = ConfigManager()
    
    # Тестируем получение базового URL
    base_url = config_manager.get_base_url()
    assert isinstance(base_url, str)
    assert len(base_url) > 0


if __name__ == "__main__":
    pytest.main([__file__])
