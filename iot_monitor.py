import requests
import time
import os
from datetime import datetime
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

class IoTMonitor:
    def __init__(self):
        self.api_url = os.getenv('IOT_API_URL')
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        # Пороговые значения для определения пересыхания
        self.soil_moisture_threshold = 30  # ниже этого значения - пересыхание
        self.air_temp_threshold = 35       # выше этого значения - жарко
        self.soil_temp_threshold = 30      # выше этого значения - горячая почва
        
    def get_sensor_data(self):
        """Получение данных с датчиков через API"""
        try:
            response = requests.get(self.api_url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении данных: {e}")
            return None
    
    def send_telegram_message(self, message):
        """Отправка сообщения через Telegram бота"""
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {
            'chat_id': self.telegram_chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()
            print("Сообщение отправлено в Telegram")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при отправке сообщения: {e}")
            return False
    
    def analyze_soil_condition(self, sensor_data):
        """Анализ состояния почвы на основе данных датчиков"""
        # Предполагаем, что API возвращает данные в следующем формате
        # Нужно адаптировать под реальную структуру ответа API
        
        try:
            # Пример структуры данных (замените на реальные поля из API)
            soil_moisture = sensor_data.get('soil_moisture', 0)
            soil_temperature = sensor_data.get('soil_temperature', 0)
            air_temperature = sensor_data.get('air_temperature', 0)
            
            print(f"Влажность почвы: {soil_moisture}%")
            print(f"Температура почвы: {soil_temperature}°C")
            print(f"Температура воздуха: {air_temperature}°C")
            
            # Проверка условий пересыхания
            issues = []
            
            if soil_moisture < self.soil_moisture_threshold:
                issues.append(f"⚠️ Низкая влажность почвы: {soil_moisture}%")
            
            if air_temperature > self.air_temp_threshold:
                issues.append(f"🔥 Высокая температура воздуха: {air_temperature}°C")
            
            if soil_temperature > self.soil_temp_threshold:
                issues.append(f"🌡️ Высокая температура почвы: {soil_temperature}°C")
            
            return issues, {
                'soil_moisture': soil_moisture,
                'soil_temperature': soil_temperature,
                'air_temperature': air_temperature
            }
            
        except Exception as e:
            print(f"Ошибка при анализе данных: {e}")
            return [], {}
    
    def format_alert_message(self, issues, sensor_data):
        """Форматирование сообщения для отправки"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        message = f"🚨 <b>ОБНАРУЖЕНО ПЕРЕСЫХАНИЕ ПОЧВЫ</b> 🚨\n"
        message += f"⏰ Время: {timestamp}\n\n"
        
        message += "📊 <b>Текущие показания:</b>\n"
        message += f"💧 Влажность почвы: {sensor_data['soil_moisture']}%\n"
        message += f"🌡️ Температура почвы: {sensor_data['soil_temperature']}°C\n"
        message += f"🌤️ Температура воздуха: {sensor_data['air_temperature']}°C\n\n"
        
        message += "⚠️ <b>Обнаруженные проблемы:</b>\n"
        for issue in issues:
            message += f"• {issue}\n"
        
        return message
    
    def monitor_loop(self, check_interval=300):  # Проверка каждые 5 минут
        """Основной цикл мониторинга"""
        print("Запуск мониторинга датчиков...")
        
        while True:
            print(f"\n--- Проверка {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
            
            # Получение данных с датчиков
            sensor_data = self.get_sensor_data()
            
            if sensor_data:
                # Анализ состояния почвы
                issues, current_data = self.analyze_soil_condition(sensor_data)
                
                # Если обнаружены проблемы - отправляем сообщение
                if issues:
                    alert_message = self.format_alert_message(issues, current_data)
                    self.send_telegram_message(alert_message)
                else:
                    print("✅ Состояние почвы в норме")
            else:
                print("❌ Не удалось получить данные с датчиков")
            
            # Ожидание перед следующей проверкой
            print(f"Ожидание {check_interval} секунд до следующей проверки...")
            time.sleep(check_interval)

def main():
    # Создание экземпляра монитора
    monitor = IoTMonitor()
    
    # Проверка наличия необходимых переменных
    if not all([monitor.telegram_token, monitor.telegram_chat_id, monitor.api_url]):
        print("❌ Ошибка: Не все необходимые переменные окружения установлены")
        print("Проверьте файл .env и убедитесь, что установлены:")
        print("TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, IOT_API_URL")
        return
    
    # Запуск мониторинга
    try:
        monitor.monitor_loop()
    except KeyboardInterrupt:
        print("\nМониторинг остановлен пользователем")

if __name__ == "__main__":
    main()