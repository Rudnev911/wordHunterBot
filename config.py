import os
from dotenv import load_dotenv

def load_config():
    """Загрузка конфигурации из переменных окружения"""
    load_dotenv()
    
    config = {
        'token': os.getenv('TOKEN'),
        'token_weather': os.getenv('TOKEN_WEATHER'),
        'catToken': os.getenv('catToken')
    }
    
    # Проверка обязательных токенов
    if not config['token']:
        raise ValueError("Токен бота (TOKEN) не найден в переменных окружения")
    
    # Предупреждения для опциональных токенов
    if not config['token_weather']:
        print("Предупреждение: Токен погоды (TOKEN_WEATHER) не найден")
    if not config['catToken']:
        print("Предупреждение: Токен котиков (catToken) не найден")
    
    return config