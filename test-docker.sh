#!/bin/bash

echo "🧪 Тестирование Docker контейнера подкаст-загрузчика"
echo "=================================================="

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker и попробуйте снова."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Установите Docker Compose и попробуйте снова."
    exit 1
fi

echo "✅ Docker и Docker Compose найдены"

# Создаем папки если их нет
mkdir -p data logs

echo "📁 Папки data/ и logs/ созданы"

echo "🔨 Сборка Docker образа..."
docker-compose build

if [ $? -eq 0 ]; then
    echo "✅ Образ успешно собран"
else
    echo "❌ Ошибка при сборке образа"
    exit 1
fi

echo "🚀 Запуск контейнера в фоновом режиме..."
docker-compose up -d

if [ $? -eq 0 ]; then
    echo "✅ Контейнер запущен"
    echo ""
    echo "📋 Полезные команды:"
    echo "  Просмотр логов: docker-compose logs -f"
    echo "  Остановка: docker-compose down"
    echo "  Перезапуск: docker-compose restart"
    echo ""
    echo "📁 Файлы будут сохраняться в папку data/"
    echo "📝 Логи будут записываться в папку logs/"
else
    echo "❌ Ошибка при запуске контейнера"
    exit 1
fi
