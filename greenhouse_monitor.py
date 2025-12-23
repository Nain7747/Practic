#!/usr/bin/env python3
"""
Минимальная система мониторинга теплицы
Проверяет датчики и отправляет уведомления в Telegram
"""

import requests
import time
import logging
from datetime import datetime, timedelta
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, API_AUTHORIZATION, DEVICE_ID

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleGreenhouseMonitor:
    """Простой мониторинг теплицы"""
    
    def __init__(self):
        self.headers = {"Authorization": API_AUTHORIZATION}
        self.device_id = DEVICE_ID
        
        # Датчики: ID -> название
        self.sensors = {
            18: "🌡️ Воздух",
            19: "💧 Влажность почвы", 
            38: "🌱 Температура почвы"
        }
        
        logger.info(f"Запуск мониторинга для устройства {self.device_id}")
    
    def get_sensor_value(self, sensor_id):
        """Получить последнее значение датчика"""
        try:
            # Берем данные за последний час
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=1)
            
            params = {
                "start": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "end": end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "page": 1,
                "range": 3
            }
            
            url = f"https://api.iot.robolatoriya.com/device/{self.device_id}/getSensorData/{sensor_id}"
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data and 'dataset' in data and 'items' in data['dataset']:
                    items = data['dataset']['items']
                    if items:
                        return float(items[0].get('value', 0))
            return None
            
        except Exception as e:
            logger.error(f"Ошибка датчика {sensor_id}: {e}")
            return None
    
    def analyze_conditions(self, air_temp, soil_temp, humidity):
        """Проанализировать условия в теплице"""
        alerts = []
        
        # Проверка влажности
        if humidity is not None:
            if humidity < 30:
                alerts.append(f"🚨 КРИТИЧЕСКИ СУХО: {humidity:.1f}%")
            elif humidity < 40:
                alerts.append(f"⚠️ Низкая влажность: {humidity:.1f}%")
        
        # Проверка разницы температур
        if air_temp is not None and soil_temp is not None:
            temp_diff = air_temp - soil_temp
            if temp_diff < 2.0:
                alerts.append(f"💧 Возможно нет воды: разница {temp_diff:.1f}°C")
        
        return alerts
    
    def send_telegram_alert(self, sensor_values, alerts):
        """Отправить уведомление в Telegram"""
        if not alerts or not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
            return False
        
        try:
            message = f"🏠 Теплица #{self.device_id}\n"
            message += f"🕐 {datetime.now().strftime('%d.%m %H:%M')}\n\n"
            
            # Текущие показания
            message += "📊 Текущие данные:\n"
            for sensor_id, name in self.sensors.items():
                if sensor_id in sensor_values and sensor_values[sensor_id] is not None:
                    value = sensor_values[sensor_id]
                    message += f"{name}: {value:.1f}{'°C' if sensor_id != 19 else '%'}\n"
            
            # Предупреждения
            if alerts:
                message += "\n🚨 Проблемы:\n"
                for alert in alerts:
                    message += f"• {alert}\n"
            
            message += "\n🔧 Проверьте теплицу!"
            
            # Отправка
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            response = requests.post(url, data={
                'chat_id': TELEGRAM_CHAT_ID,
                'text': message
            }, timeout=10)
            
            if response.status_code == 200:
                logger.info("✅ Уведомление отправлено")
                return True
            else:
                logger.error(f"❌ Ошибка Telegram: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка отправки: {e}")
            return False
    
    def run_check(self):
        """Выполнить одну проверку"""
        logger.info("=" * 50)
        logger.info(f"🔍 Проверка {datetime.now().strftime('%H:%M:%S')}")
        
        sensor_values = {}
        
        # Собираем данные со всех датчиков
        for sensor_id, name in self.sensors.items():
            value = self.get_sensor_value(sensor_id)
            sensor_values[sensor_id] = value
            
            if value is not None:
                logger.info(f"{name}: {value:.1f}{'°C' if sensor_id != 19 else '%'}")
            else:
                logger.warning(f"{name}: нет данных")
        
        # Анализируем
        air_temp = sensor_values.get(18)
        soil_temp = sensor_values.get(38)
        humidity = sensor_values.get(19)
        
        alerts = self.analyze_conditions(air_temp, soil_temp, humidity)
        
        # Отправляем уведомление если есть проблемы
        if alerts:
            self.send_telegram_alert(sensor_values, alerts)
        else:
            logger.info("✅ Все показатели в норме")
        
        return len(alerts) > 0
    
    def run(self, interval_minutes=10):
        """Основной цикл работы"""
        logger.info(f"🚀 Старт мониторинга (интервал: {interval_minutes} мин)")
        logger.info("Нажмите Ctrl+C для остановки\n")
        
        try:
            while True:
                has_problems = self.run_check()
                
                # Если были проблемы, следующую проверку делаем раньше
                wait_time = 300 if has_problems else interval_minutes * 60  # 5 мин или N мин
                
                logger.info(f"⏳ Следующая проверка через {wait_time//60} минут...\n")
                time.sleep(wait_time)
                
        except KeyboardInterrupt:
            logger.info("\n🛑 Мониторинг остановлен")
        except Exception as e:
            logger.error(f"💥 Критическая ошибка: {e}")

def main():
    """Точка входа"""
    print("\n" + "="*60)
    print("🌱 СИСТЕМА МОНИТОРИНГА ТЕПЛИЦЫ")
    print("="*60)
    
    monitor = SimpleGreenhouseMonitor()
    
    try:
        monitor.run(interval_minutes=10)  # Проверка каждые 10 минут
    except Exception as e:
        logger.error(f"Ошибка запуска: {e}")

if __name__ == "__main__":
    main()