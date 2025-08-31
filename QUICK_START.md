# 🚀 Быстрый старт

## Docker (рекомендуется)

```bash
# 1. Создайте папку для данных
mkdir -p data

# 2. Настройте конфигурацию
cp config.yaml.dist config.yaml
# Отредактируйте config.yaml под свои нужды

# 3. Запустите контейнер
docker-compose up -d

# 3. Проверьте логи
docker-compose logs -f

# 4. Остановите (когда нужно)
docker-compose down
```

## Локальный запуск

```bash
# 1. Активируйте виртуальное окружение
source venv/bin/activate

# 2. Настройте конфигурацию
cp config.yaml.dist config.yaml
# Отредактируйте config.yaml под свои нужды

# 3. Управление источниками
python manage_sources.py list                    # Показать источники
python manage_sources.py add                     # Добавить источник

# 3. Запуск с автоматическим циклом
python multi_downloader.py --loop

# 4. Или однократный запуск
python multi_downloader.py
```

## 📁 Результат

Файлы будут сохранены в:
- `data/news_politics/[md5-hash].mp3` - аудио файлы
- `data/news_politics/[md5-hash].webp` - обложки
- `data/news_politics/podcast.rss` - RSS файл подписки

## ⏰ Расписание

- **Docker**: Автоматически каждые 10 минут
- **Локально**: Зависит от выбранного режима

## 🛑 Остановка

- **Docker**: `docker-compose down`
- **Локально**: `Ctrl+C`
