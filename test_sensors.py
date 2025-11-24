import requests
import json
from iot_monitor import IoTMonitor

def test_api_connection():
    """Тестирование подключения к API"""
    monitor = IoTMonitor()
    
    print("Тестирование подключения к API...")
    data = monitor.get_sensor_data()
    
    if data:
        print("✅ Подключение успешно!")
        print("Структура полученных данных:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # Анализ данных
        issues, sensor_data = monitor.analyze_soil_condition(data)
        print("\nРезультаты анализа:")
        if issues:
            for issue in issues:
                print(issue)
        else:
            print("✅ Проблем не обнаружено")
    else:
        print("❌ Ошибка подключения к API")

def test_telegram_bot():
    """Тестирование Telegram бота"""
    monitor = IoTMonitor()
    
    test_message = "🤖 <b>Тестовое сообщение</b>\nБот работает корректно!"
    
    print("Тестирование Telegram бота...")
    if monitor.send_telegram_message(test_message):
        print("✅ Сообщение отправлено успешно!")
    else:
        print("❌ Ошибка отправки сообщения")

if __name__ == "__main__":
    print("Выберите тест:")
    print("1 - Тест API")
    print("2 - Тест Telegram бота")
    print("3 - Оба теста")
    
    choice = input("Введите номер: ")
    
    if choice == "1":
        test_api_connection()
    elif choice == "2":
        test_telegram_bot()
    elif choice == "3":
        test_api_connection()
        test_telegram_bot()
    else:
        print("Неверный выбор")