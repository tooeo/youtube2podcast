# Contributing to YouTube2Podcast

Спасибо за интерес к проекту! Мы приветствуем вклад от сообщества.

## Как внести свой вклад

### Сообщение об ошибках

1. Проверьте, что ошибка еще не была зарегистрирована в [Issues](https://github.com/tooeo/youtube2podcast/issues)
2. Создайте новое issue с подробным описанием:
   - Описание проблемы
   - Шаги для воспроизведения
   - Ожидаемое поведение
   - Фактическое поведение
   - Версия Python, yt-dlp, операционная система

### Предложение улучшений

1. Создайте issue с описанием предлагаемого улучшения
2. Обсудите предложение с сообществом
3. После одобрения создайте pull request

### Создание Pull Request

1. Форкните репозиторий
2. Создайте ветку для ваших изменений: `git checkout -b feature/your-feature-name`
3. Внесите изменения и закоммитьте их: `git commit -m 'Add some feature'`
4. Отправьте изменения: `git push origin feature/your-feature-name`
5. Создайте Pull Request

## Стандарты кода

- Используйте Python 3.8+
- Следуйте PEP 8 для стиля кода
- Добавляйте docstrings для всех функций
- Пишите тесты для новых функций
- Обновляйте документацию при необходимости

## Установка для разработки

```bash
# Клонируйте репозиторий
git clone https://github.com/tooeo/youtube2podcast.git
cd youtube2podcast

# Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate

# Установите зависимости
pip install -r requirements.txt

# Установите FFmpeg (если еще не установлен)
# Ubuntu/Debian: sudo apt-get install ffmpeg
# macOS: brew install ffmpeg
# Windows: скачайте с официального сайта
```

## Тестирование

```bash
# Запустите тесты
python -m pytest tests/

# Проверьте стиль кода
flake8 .
black --check .
```

## Структура проекта

```
youtube2podcast/
├── main.py              # Основная программа для плейлистов
├── main_loop.py         # Версия с автоматическим циклом
├── channel_downloader.py # Программа для работы с каналами
├── requirements.txt     # Зависимости Python
├── Dockerfile          # Docker образ
├── docker-compose.yml  # Docker Compose конфигурация
├── README.md           # Основная документация
├── TROUBLESHOOTING.md  # Решение проблем
├── QUICK_START.md      # Быстрый старт
└── data/               # Папка для загруженных файлов (исключена из git)
```

## Лицензия

Проект распространяется под лицензией MIT. Внося изменения, вы соглашаетесь с условиями лицензии.
