FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    ffmpeg \
    cron \
    wget \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование основного кода
COPY multi_downloader.py .
COPY config.py .
COPY manage_sources.py .

# Создание директории для данных
RUN mkdir -p data

# Создание скрипта для запуска
COPY run.sh .
RUN chmod +x run.sh

# Создание cron файла
COPY crontab /etc/cron.d/app-cron
RUN chmod 0644 /etc/cron.d/app-cron

# Создание скрипта запуска контейнера
COPY start.sh .
RUN chmod +x start.sh

# Создание точки входа
ENTRYPOINT ["./start.sh"]
