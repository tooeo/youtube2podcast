#!/usr/bin/env python3
"""
Tests for main.py
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
import sys

# Добавляем корневую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import (
    get_playlist_videos,
    print_video_links,
    get_file_hash,
    check_video_availability,
    clean_filename,
    download_latest_audio,
    create_or_update_rss
)


class TestMainFunctions:
    """Тесты для основных функций main.py"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def teardown_method(self):
        """Очистка после каждого теста"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)

    def test_get_file_hash(self):
        """Тест функции get_file_hash"""
        title = "Test Video Title"
        hash_result = get_file_hash(title)
        
        assert isinstance(hash_result, str)
        assert len(hash_result) == 32  # MD5 hash length
        assert hash_result.isalnum()  # Only alphanumeric characters

    def test_clean_filename(self):
        """Тест функции clean_filename"""
        # Тест с обычными символами
        assert clean_filename("normal_filename") == "normal_filename"
        
        # Тест с специальными символами
        assert clean_filename("file/with\\special:chars") == "file_with_special_chars"
        
        # Тест с множественными подчеркиваниями
        assert clean_filename("file__with___multiple___underscores") == "file_with_multiple_underscores"

    def test_get_playlist_videos_mock(self):
        """Тест get_playlist_videos с моком"""
        mock_videos = [
            {
                'title': 'Test Video 1',
                'id': 'test123',
                'duration': 3600,
                'uploader': 'test_user',
                'view_count': 1000
            },
            {
                'title': 'Test Video 2',
                'id': 'test456',
                'duration': 1800,
                'uploader': 'test_user',
                'view_count': 500
            }
        ]
        
        with patch('main.yt_dlp.YoutubeDL') as mock_ydl:
            mock_instance = MagicMock()
            mock_instance.extract_info.return_value = {
                'entries': mock_videos
            }
            mock_ydl.return_value.__enter__.return_value = mock_instance
            
            result = get_playlist_videos("https://www.youtube.com/playlist?list=test")
            
            assert len(result) == 2
            assert result[0]['title'] == 'Test Video 1'
            assert result[1]['title'] == 'Test Video 2'

    def test_check_video_availability_mock(self):
        """Тест check_video_availability с моком"""
        with patch('main.yt_dlp.YoutubeDL') as mock_ydl:
            mock_instance = MagicMock()
            mock_instance.extract_info.return_value = {'title': 'Test Video'}
            mock_ydl.return_value.__enter__.return_value = mock_instance
            
            result = check_video_availability("test123")
            assert result is True

    def test_check_video_availability_unavailable(self):
        """Тест check_video_availability для недоступного видео"""
        with patch('main.yt_dlp.YoutubeDL') as mock_ydl:
            mock_instance = MagicMock()
            mock_instance.extract_info.side_effect = Exception("Video unavailable")
            mock_ydl.return_value.__enter__.return_value = mock_instance
            
            result = check_video_availability("test123")
            assert result is False

    def test_create_or_update_rss(self):
        """Тест создания RSS файла"""
        videos = [
            {
                'title': 'Test Video',
                'id': 'test123',
                'duration': 3600,
                'uploader': 'test_user'
            }
        ]
        
        latest_video = videos[0]
        playlist_id = "test_playlist"
        
        # Создаем RSS файл
        create_or_update_rss(videos, playlist_id, latest_video)
        
        # Проверяем, что файл создан
        rss_file = f"data/{playlist_id}/podcast.rss"
        assert os.path.exists(rss_file)
        
        # Проверяем содержимое файла
        with open(rss_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert '<?xml version="1.0" encoding="utf-8"?>' in content
            assert '<rss version="2.0"' in content
            assert 'Test Video' in content

    def test_create_or_update_rss_empty_video(self):
        """Тест create_or_update_rss с пустым видео"""
        videos = []
        latest_video = {}
        playlist_id = "test_playlist"
        
        # Не должно вызывать ошибку
        create_or_update_rss(videos, playlist_id, latest_video)
        
        # Файл не должен быть создан
        rss_file = f"data/{playlist_id}/podcast.rss"
        assert not os.path.exists(rss_file)


if __name__ == "__main__":
    pytest.main([__file__])
