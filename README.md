![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
# 🌱 Минимальная система мониторинга теплицы

Простая система для мониторинга температуры и влажности в теплице с уведомлениями в Telegram.

## 🚀 Быстрый старт

1. **Установите зависимости:**
```bash
pip install -r requirements.txt
Настройте config.py:

Замените TELEGRAM_TOKEN на токен вашего бота

Замените TELEGRAM_CHAT_ID на ваш ID

Проверьте DEVICE_ID (обычно 10)

Запустите:

bash
python greenhouse_monitor.py
✨ Функции
📊 Мониторинг 3 датчиков: температура воздуха, почвы, влажность

🚨 Автоматические уведомления в Telegram при проблемах

⏱️ Гибкие интервалы проверки

📝 Логирование в консоль

🔧 Настройка порогов
В config.py можно настроить:

CRITICAL_HUMIDITY - критический уровень влажности

MIN_TEMP_DIFF - минимальная разница температур для определения наличия воды

⚠️ Важно
Программа использует тестовые данные (2025 год)

Для реального использования нужен доступ к реальным датчикам

Telegram бот должен быть создан заранее (@BotFather)

📞 Поддержка
При проблемах проверьте:

Правильность токена и chat_id

Доступность API датчиков

Подключение к интернету

🎯 КАК ЗАПУСТИТЬ:
bash
# 1. Создайте папку проекта
mkdir greenhouse_project
cd greenhouse_project

# 2. Создайте 3 файла выше
# 3. Установите зависимости
pip install requests

# 4. Настройте config.py (вставьте свои данные)
# 5. Запустите
python greenhouse_monitor.py

## 📁 Структура проекта
greenhouse_monitor/
├── greenhouse_monitor.py # Основной скрипт
├── config.py # Настройки
├── requirements.txt # Зависимости
└── README.md # Эта инструкция