import aiohttp
import asyncio
import random
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton

def get_user_info(update: Update):
    """Извлекает информацию о пользователе"""
    try:
        if not update or not update.effective_chat:
            return None, "Гость", "Гость", "", 0
            
        chat_id = update.effective_chat.id
        user = update.effective_user
        user_id = user.id if user else 0
        message = update.effective_message
        timestamp = int(message.date.timestamp()) if message else 0
        first_name = user.first_name or '' if user else ''
        last_name = user.last_name or '' if user else ''
        full_name = f'{first_name} {last_name}'.strip()
        username = user.username if user else 'anonymous'
        ava_str = f'{username}{timestamp}'.strip()
        ava_url = f'https://robohash.org/{ava_str}?set=set5'
        return chat_id, first_name, full_name, ava_url, user_id
    except Exception as e:
        print(f"Ошибка в get_user_info: {e}")
        return None, "Гость", "Гость", "", 0

async def get_ip_address() -> str:
    """Получает публичный IP адрес"""
    try:
        url = "https://api.ipify.org?format=json"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['ip']
                return "Ошибка при получении IP: сервер недоступен"
    except asyncio.TimeoutError:
        return "Таймаут запроса к серверу IP"
    except aiohttp.ClientError:
        return "Сетевая ошибка при получении IP"
    except Exception as e:
        print(f"Неизвестная ошибка в get_ip_address: {e}")
        return f"Ошибка при получении IP: {str(e)}"

async def get_cat_photo(api_key: str) -> str:
    """Получает фото кота от The Cat API"""
    if not api_key:
        return None
        
    try:
        url = "https://api.thecatapi.com/v1/images/search"
        
        headers = {'x-api-key': api_key}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=10) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                return data[0]['url']
    except asyncio.TimeoutError:
        print("Таймаут при получении фото кота")
        return None
    except aiohttp.ClientError as e:
        print(f"Сетевая ошибка при получении кота: {e}")
        return None
    except Exception as e:
        print(f"Ошибка в get_cat_photo: {e}")
        return None

async def get_weather(lat: float, lon: float, api_key: str) -> str:
    """Получает данные о погоде"""
    if not api_key:
        return "Токен погоды не настроен. Не могу получить данные о погоде."
        
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=ru"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                if resp.status != 200:
                    return 'Ошибка при получении данных о погоде. Сервер недоступен.'
                data = await resp.json()
                
        try: 
            city = data.get("name", "Неизвестное место")
            weather_desc = data['weather'][0]['description']
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            wind_speed = data['wind']['speed']

            if wind_speed < 5:
                wind_recom = "Погода хорошая, ветра почти нет"
            elif wind_speed < 10:
                wind_recom = "На улице ветрено, оденьтесь чуть теплее"
            elif wind_speed < 20:
                wind_recom = "Ветер очень сильный, будьте осторожны, выходя из дома"
            else:
                wind_recom = "На улице ураган, на улицу лучше не выходить"

            return (f'Сейчас в {city}: {weather_desc}\n'
                    f'Температура: {temp}°C (ощущается как {feels_like}°C)\n'
                    f'Ветер: {wind_speed} м/с\n'
                    f'{wind_recom}')
        except (KeyError, IndexError) as e:
            print(f"Ошибка парсинга погоды: {e}")
            return 'Ошибка при обработке данных о погоде. Неверный формат данных.'
            
    except aiohttp.ClientError:
        return 'Сетевая ошибка при подключении к серверу погоды.'
    except asyncio.TimeoutError:
        return 'Сервер погоды не ответил вовремя. Попробуйте позже.'
    except Exception as e:
        print(f"Неизвестная ошибка в get_weather: {e}")
        return 'Не удалось получить данные о погоде.'

def create_main_menu():
    """Создает главное меню"""
    return ReplyKeyboardMarkup([
        ['Погода сегодня', 'Сгенери аватар'],
        ['Мой ID', 'Мой IP'],
        ['Фото кота', '/random_digit']
    ], resize_keyboard=True)