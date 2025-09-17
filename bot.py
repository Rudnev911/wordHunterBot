from telegram import Update, KeyboardButton
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from telegram.ext import CommandHandler
from telegram import ReplyKeyboardMarkup
import os
import aiohttp
from dotenv import load_dotenv
import random
import asyncio

load_dotenv()
token = os.getenv('TOKEN')
token_weather = os.getenv('TOKEN_WEATHER')
catToken = os.getenv('catToken')

# Проверка наличия токенов
if not token:
    raise ValueError("Токен бота (TOKEN) не найден в переменных окружения")
if not token_weather:
    print("Предупреждение: Токен погоды (TOKEN_WEATHER) не найден")
if not catToken:
    print("Предупреждение: Токен котиков (catToken) не найден")

# Извлекаем chat_id и разные параметры пользователя
def get_user_info(update: Update):
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
        ava_url = f'https://robohash.org/{ava_str}?set=set5' # поменял монстров на человечков
        return chat_id, first_name, full_name, ava_url, user_id
    except Exception as e:
        print(f"Ошибка в get_user_info: {e}")
        return None, "Гость", "Гость", "", 0

async def say_hi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update or not update.message:
            return
            
        user_info = get_user_info(update)
        if not user_info[0]:  # Проверяем chat_id
            return
            
        text = update.message.text
        
        if text == 'Сгенери аватар':
            await context.bot.send_photo(chat_id=user_info[0], photo=user_info[3])
        elif text == 'Мой ID':
            await context.bot.send_message(chat_id=user_info[0], text=f'Твой ID: {user_info[4]}')
        elif text == 'Фото кота':
            await send_cat(update, context)
        elif text == 'Мой IP':
            ip_address = await get_ip_address()
            await context.bot.send_message(
                chat_id=user_info[0],
                text=f'Ваш IP адрес: {ip_address}'
            )
        elif text == 'Погода сегодня':
            await request_location(update, context)
        else:
            await context.bot.send_message(chat_id=user_info[0], text=f'{user_info[1]}, как твои дела?')
    except Exception as e:
        print(f"Ошибка в say_hi: {e}")
        try:
            if update and update.effective_chat:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Произошла ошибка при обработке сообщения"
                )
        except:
            pass

async def request_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_info = get_user_info(update)
        if not user_info[0]:
            return
            
        location_keyboard = ReplyKeyboardMarkup(
            [[KeyboardButton('Отправить координаты 📍', request_location=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await context.bot.send_message(
            chat_id=user_info[0],
            text='Пожалуйста, поделитесь своей геолокацией:',
            reply_markup=location_keyboard
        )
    except Exception as e:
        print(f"Ошибка в request_location: {e}")

async def get_cat_photo() -> str:
    if not catToken:
        return None
        
    try:
        url = "https://api.thecatapi.com/v1/images/search"
        
        headers = {
            'x-api-key': catToken
        }
        
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

async def send_cat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_info = get_user_info(update)
        if not user_info[0]:
            return
            
        cat_url = await get_cat_photo()
        
        if cat_url:
            await context.bot.send_photo(
                chat_id=user_info[0],
                photo=cat_url,
                caption="Вот ваш котик! 🐱"
            )
        else:
            await context.bot.send_message(
                chat_id=user_info[0],
                text="Не удалось получить фото кота 😿"
            )
    except Exception as e:
        print(f"Ошибка в send_cat: {e}")
        try:
            if update and update.effective_chat:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Произошла ошибка при отправке котика"
                )
        except:
            pass

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update or not update.message:
            return
            
        if update.message.location is None:
            latitude, longitude = 55.7558, 37.6173
            await update.message.reply_text("Используются координаты Москвы по умолчанию!")
        else:
            location = update.message.location
            latitude, longitude = location.latitude, location.longitude
        
        context.user_data['location'] = (latitude, longitude)
        weather_report = await get_weather(latitude, longitude)
        
        await update.message.reply_text(weather_report)

        main_menu = ReplyKeyboardMarkup([
            ['Погода сегодня', 'Сгенери аватар'],
            ['Мой ID', 'Мой IP'],
            ['Фото кота', '/random_digit']
        ], resize_keyboard=True)
        await update.message.reply_text('Главное меню:', reply_markup=main_menu)
        
    except Exception as e:
        print(f"Ошибка в handle_location: {e}")
        try:
            await update.message.reply_text("Произошла ошибка при обработке локации")
            
            main_menu = ReplyKeyboardMarkup([
                ['Погода сегодня', 'Сгенери аватар'],
                ['Мой ID', 'Мой IP'],
                ['Фото кота', '/random_digit']
            ], resize_keyboard=True)
            await update.message.reply_text('Главное меню:', reply_markup=main_menu)
        except:
            pass

async def get_weather(lat: float, lon: float) -> str:
    if not token_weather:
        return "Токен погоды не настроен. Не могу получить данные о погоде."
        
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={token_weather}&units=metric&lang=ru"

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

async def wake_up(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_info = get_user_info(update)
        if not user_info[0]:
            return
            
        button = ReplyKeyboardMarkup([
            ['Погода сегодня', 'Сгенери аватар'],
            ['Мой ID', 'Мой IP'],
            ['Фото кота', '/random_digit']
        ], resize_keyboard=True)
        
        await context.bot.send_message(
            chat_id=user_info[0],
            text=f'Hello, {user_info[2]}, мы начинаем!',
            reply_markup=button
        )
    except Exception as e:
        print(f"Ошибка в wake_up: {e}")

async def miid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update or not update.effective_chat:
            return
            
        chat_id = update.effective_chat.id
        user = update.effective_user
        user_id = user.id if user else 0
        first_name = user.first_name or '' if user else ''
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Информация о вашем аккаунте:\n"
                 f"• User ID: {user_id}\n"
                 f"• Chat ID: {chat_id}\n"
                 f"• Имя: {first_name}\n"
        )
    except Exception as e:
        print(f"Ошибка в miid_command: {e}")

async def get_ip_address() -> str:
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

async def random_digit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_info = get_user_info(update)
        if not user_info[0]:
            return
            
        random_number = random.randint(1, 100)
        
        await context.bot.send_message(
            chat_id=user_info[0],
            text=f'🎲 Случайное число: {random_number}'
        )
    except Exception as e:
        print(f"Ошибка в random_digit: {e}")

def main():
    try:
        if not token:
            print("Ошибка: Токен бота не найден!")
            return
            
        application = ApplicationBuilder().token(token).build()
        application.add_handler(CommandHandler('start', wake_up))
        application.add_handler(CommandHandler('miID', miid_command))
        application.add_handler(CommandHandler('random_digit', random_digit))
        application.add_handler(MessageHandler(filters.TEXT, say_hi))
        application.add_handler(MessageHandler(filters.LOCATION, handle_location))
        
        print("Бот запускается...")
        application.run_polling()
        
    except Exception as e:
        print(f"Критическая ошибка при запуске бота: {e}")

if __name__ == '__main__':
    main()