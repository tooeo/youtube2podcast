# Docker Documentation

## Обзор

YouTube2Podcast предоставляет полную Docker поддержку для легкого развертывания и управления.

## Образы Docker

### Основной образ

```bash
# Сборка локально
docker build -t youtube2podcast .

# Запуск
docker run -d \
  --name youtube2podcast \
  -v $(pwd)/data:/app/data \
  youtube2podcast
```

### Docker Compose (рекомендуется)

```yaml
version: '3.8'
services:
  youtube2podcast:
    build: .
    container_name: youtube2podcast
    volumes:
      - ./data:/app/data
    environment:
      - TZ=Europe/Moscow
    restart: unless-stopped
```

## Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `TZ` | Часовой пояс | `UTC` |
| `LOG_LEVEL` | Уровень логирования | `INFO` |
| `CHECK_INTERVAL` | Интервал проверки (минуты) | `10` |

## Тома (Volumes)

### Обязательные

- `./data:/app/data` - Папка для загруженных файлов

### Опциональные

- `./logs:/app/logs` - Папка для логов
- `./config:/app/config` - Папка для конфигурации

## Сетевые порты

По умолчанию контейнер не открывает порты, так как не предоставляет веб-интерфейс.

## Мониторинг

### Логи

```bash
# Просмотр логов
docker-compose logs -f

# Просмотр логов конкретного контейнера
docker logs youtube2podcast
```

### Статус

```bash
# Проверка статуса
docker-compose ps

# Статистика ресурсов
docker stats youtube2podcast
```

## Обновление

```bash
# Остановка контейнера
docker-compose down

# Пересборка образа
docker-compose build --no-cache

# Запуск с новым образом
docker-compose up -d
```

## Резервное копирование

```bash
# Создание бэкапа данных
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# Восстановление из бэкапа
tar -xzf backup-20241219.tar.gz
```

## Troubleshooting

### Контейнер не запускается

```bash
# Проверка логов
docker-compose logs

# Проверка конфигурации
docker-compose config
```

### Проблемы с правами доступа

```bash
# Изменение владельца папки data
sudo chown -R 1000:1000 data/

# Или запуск с правами root (не рекомендуется)
docker run --user root youtube2podcast
```

### Проблемы с сетью

```bash
# Проверка сетевых настроек
docker network ls
docker network inspect youtube2podcast_default
```

## Production развертывание

### Рекомендуемая конфигурация

```yaml
version: '3.8'
services:
  youtube2podcast:
    build: .
    container_name: youtube2podcast
    volumes:
      - /opt/youtube2podcast/data:/app/data
      - /opt/youtube2podcast/logs:/app/logs
    environment:
      - TZ=Europe/Moscow
      - LOG_LEVEL=INFO
      - CHECK_INTERVAL=10
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Мониторинг

```bash
# Создание скрипта мониторинга
cat > /usr/local/bin/youtube2podcast-monitor.sh << 'EOF'
#!/bin/bash
if ! docker ps | grep -q youtube2podcast; then
    echo "YouTube2Podcast container is down, restarting..."
    docker-compose -f /opt/youtube2podcast/docker-compose.yml up -d
fi
EOF

chmod +x /usr/local/bin/youtube2podcast-monitor.sh

# Добавление в cron
echo "*/5 * * * * /usr/local/bin/youtube2podcast-monitor.sh" | sudo crontab -
```

## Безопасность

### Рекомендации

1. **Не запускайте с правами root**
2. **Используйте read-only файловую систему где возможно**
3. **Ограничьте ресурсы контейнера**
4. **Регулярно обновляйте базовый образ**

### Пример безопасной конфигурации

```yaml
version: '3.8'
services:
  youtube2podcast:
    build: .
    container_name: youtube2podcast
    volumes:
      - ./data:/app/data:rw
      - ./logs:/app/logs:rw
    environment:
      - TZ=Europe/Moscow
    restart: unless-stopped
    read_only: true
    tmpfs:
      - /tmp
      - /var/tmp
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    mem_limit: 512m
    cpu_quota: 50000
    user: "1000:1000"
```
