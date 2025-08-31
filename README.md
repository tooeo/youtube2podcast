# YouTube to Podcast Converter

[![CI](https://github.com/tooeo/youtube2podcast/workflows/CI/badge.svg)](https://github.com/tooeo/youtube2podcast/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Программа для загрузки аудио из YouTube плейлистов и каналов с созданием RSS подкастов.

## 🌟 Особенности

- 📥 Загрузка аудио из YouTube плейлистов и каналов
- 🎵 Автоматическая конвертация в MP3 формат
- 📻 Генерация RSS подкастов с iTunes метаданными
- 🖼️ Загрузка обложек в формате WebP
- 🔄 Автоматический цикл выполнения каждые 10 минут
- 🐳 Docker контейнеризация для легкого развертывания
- 🔍 Диагностика сетевых проблем
- 🛡️ Проверка доступности видео перед загрузкой
- 🔐 MD5 хеширование имен файлов для уникальности
- 🎯 **Поддержка множественных источников** - работа с несколькими плейлистами и каналами одновременно
- ⚙️ **Гибкая конфигурация** - настройка для каждого источника отдельно
- 🛠️ **Утилита управления** - удобное добавление и настройка источников

## Установка и запуск

### Вариант 1: Docker (рекомендуется)

1. Убедитесь, что у вас установлен Docker и Docker Compose

2. Создайте папку для данных:
```bash
mkdir -p data
```

3. Запустите контейнер:
```bash
docker-compose up -d
```

4. Проверьте логи:
```bash
docker-compose logs -f
```

5. Остановите контейнер:
```bash
docker-compose down
```

**Примечание**: Программа будет автоматически запускаться каждые 10 минут внутри контейнера.

### Вариант 2: Локальная установка

1. Установите Python 3.7 или выше
2. Установите FFmpeg (необходим для конвертации аудио):
   - **macOS**: `brew install ffmpeg`
   - **Ubuntu/Debian**: `sudo apt install ffmpeg`
   - **Windows**: Скачайте с [официального сайта](https://ffmpeg.org/download.html)
3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Настройте конфигурацию:
```bash
cp config.yaml.dist config.yaml
# Отредактируйте config.yaml под свои нужды
```

5. Запустите программу:

**Однократный запуск:**
```bash
python multi_downloader.py
```

**Автоматический запуск каждые 10 минут:**
```bash
python multi_downloader.py --loop
```

**Управление источниками:**
```bash
# Показать все источники
python manage_sources.py list

# Добавить новый источник (интерактивно)
python manage_sources.py add

# Добавить источник программно
python manage_sources.py add-source "my_channel" "https://youtube.com/@channel" channel

# Включить/отключить источник
python manage_sources.py enable varlamov
python manage_sources.py disable varlamov

# Удалить источник
python manage_sources.py remove varlamov
```

**Однократный запуск:**
```bash
python multi_downloader.py
```

**Автоматический запуск каждые 10 минут:**
```bash
python multi_downloader.py --loop
```

**Управление источниками:**
```bash
# Показать все источники
python manage_sources.py list

# Добавить новый источник (интерактивно)
python manage_sources.py add

# Добавить источник программно
python manage_sources.py add-source "my_channel" "https://youtube.com/@channel" channel

# Управление подписками
python manage_sources.py list-subscriptions
python manage_sources.py add-subscription
python manage_sources.py enable-subscription news_politics
python manage_sources.py disable-subscription news_politics
python manage_sources.py remove-subscription news_politics

# Управление источниками
python manage_sources.py enable news24
python manage_sources.py disable news24
python manage_sources.py remove news24

# Тестирование конфигурации
python test_config.py
```

### 📋 Конфигурация подписок

Подписки и источники настраиваются в файле `config.yaml` (скопируйте из `config.yaml.dist`):

```yaml
subscriptions:
  # Подписка "Новости и политика"
  news_politics:
    enabled: true
    title: "Новости и политика"
    description: "Подкасты о новостях и политических событиях"
    category: "News & Politics"
    author: "news_anchor"
    sources:
      # Плейлист "Еженедельные новости"
      weekly_news:
        enabled: true
        type: "playlist"
        url: "https://www.youtube.com/playlist?list=PLexample123"
        custom_title: "Еженедельные новости - Подкаст"
        custom_description: "Еженедельный обзор главных событий"
        category: "News & Politics"
        author: "news_anchor"

      # Канал Новости24
      news24:
        enabled: false  # Отключен по умолчанию
        type: "channel"
        url: "https://www.youtube.com/@news24"
        custom_title: "Новости24 - Подкаст"
          custom_description: "Ежедневные новости и аналитика"
      category: "News & Politics"
      author: "news24"
```

Программа автоматически обработает все активные источники из конфигурации.

## Вывод

Программа выведет:
- Подробную информацию о каждой подписке и её источниках
- Информацию о каждом видео (название, автор, длительность, количество просмотров)
- Ссылки на каждое видео в удобном формате
- Загрузит аудио из последних видео в папки подписок (например, `data/news_politics/`)
- Создаст/обновит RSS файлы для каждой подписки для использования в приложениях подкастов

## Возможности

- **Иерархическая структура подписок** - группировка источников по темам
- Извлечение метаданных без скачивания видео
- Обработка ошибок для отдельных видео в плейлистах и каналах
- Удобный формат вывода с нумерацией
- Информация о длительности и количестве просмотров
- Автоматическая загрузка аудио из последних видео источников
- Конвертация в MP3 формат с качеством 192kbps
- Загрузка обложки видео
- Создание RSS файлов для каждой подписки с поддержкой iTunes метаданных
- **Docker контейнеризация** для простого развертывания
- **Автоматический запуск каждые 10 минут** через cron или встроенный цикл
- **MD5 хеширование имен файлов** для уникальности и совместимости
- **Проверка существования файлов** для избежания повторных загрузок
- **Проверка доступности видео** - автоматически находит первое доступное видео из последних 5

## Структура файлов

```
youtube2podcast/
├── multi_downloader.py     # Основная программа для множественных источников
├── config.py              # Менеджер конфигурации
├── config.yaml.dist       # Шаблон конфигурации
├── manage_sources.py      # Утилита управления источниками
├── test_config.py         # Тестирование конфигурации
├── requirements.txt       # Python зависимости
├── README.md             # Документация
├── TROUBLESHOOTING.md    # Решение проблем
├── QUICK_START.md        # Быстрый старт
├── Dockerfile            # Docker образ
├── docker-compose.yml    # Docker Compose конфигурация
├── .dockerignore         # Исключения для Docker
├── run.sh                # Скрипт запуска программы
├── start.sh              # Скрипт запуска контейнера
├── crontab               # Cron расписание
├── test-docker.sh        # Скрипт тестирования Docker
├── examples/             # Примеры использования
│   └── add_source_example.py
├── data/                 # Загруженные файлы (монтируется в Docker)
│   ├── news_politics/    # Подписка "Новости и политика"
│   │   ├── [md5-hash].mp3
│   │   ├── [md5-hash].webp
│   │   └── podcast.rss
│   ├── education/        # Подписка "Образование"
│   │   ├── [md5-hash].mp3
│   │   └── podcast.rss
│   ├── entertainment/    # Подписка "Развлечения"
│   │   ├── [md5-hash].mp3
│   │   └── podcast.rss
│   └── technology/       # Подписка "Технологии"
│       ├── [md5-hash].mp3
│       └── podcast.rss
└── logs/                 # Логи (опционально)
```

## Требования

- Python 3.8+
- yt-dlp библиотека
- ffmpeg-python библиотека
- FFmpeg (установленный в системе)

## 📚 Документация

- [Быстрый старт](QUICK_START.md) - Краткое руководство по запуску
- [Решение проблем](TROUBLESHOOTING.md) - Часто встречающиеся проблемы и их решения
- [Участие в проекте](CONTRIBUTING.md) - Как внести свой вклад

## 🤝 Участие в проекте

Мы приветствуем вклад от сообщества! Пожалуйста, ознакомьтесь с [руководством по участию](CONTRIBUTING.md) перед отправкой pull request.

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл [LICENSE](LICENSE) для подробностей.

## ⭐ Поддержка проекта

Если проект оказался полезным, поставьте звездочку на GitHub! Это мотивирует нас продолжать разработку.

## 🔗 Ссылки

- [Репозиторий на GitHub](https://github.com/tooeo/youtube2podcast)
- [Issues](https://github.com/tooeo/youtube2podcast/issues)
- [Pull Requests](https://github.com/tooeo/youtube2podcast/pulls)
