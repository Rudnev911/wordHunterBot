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

# Извлекаем chat_id и разные параметры пользователя
def get_user_info(update: Update):
    chat_id = update.effective_chat.id
    user = update.effective_user
    user_id = user.id
    message = update.effective_message
    timestamp = int(message.date.timestamp())
    first_name = user.first_name or ''
    last_name = user.last_name or ''
    full_name = f'{first_name} {last_name}'.strip()
    ava_str = f'{user.username}{timestamp}'.strip()
    ava_url = f'https://robohash.org/{ava_str}?set=set5' # Заменил монстров на человечков
    return chat_id, first_name, full_name, ava_url, user_id

async def say_hi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_info = get_user_info(update)
    text = update.message.text
    
    if text == 'Сгенери аватар':
        await context.bot.send_photo(chat_id=user_info[0], photo=user_info[3])
    elif text == 'Мой ID':
        await context.bot.send_message(chat_id=user_info[0], text=f'Твой ID: {user_info[4]}')
    elif text == 'Фото кота':
        await send_cat(update, context)
    elif text == 'Мой IP': # Функция получения IP доработана
        ip_address = await get_ip_address()
        await context.bot.send_message(
            chat_id=user_info[0],
            text=f'Ваш IP адрес: {ip_address}'
        )
    elif text == 'Погода сегодня':
        await request_location(update, context)
    else:
        await context.bot.send_message(chat_id=user_info[0], text=f'{user_info[1]}, как твои дела?')

async def request_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_info = get_user_info(update)
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

#Get cat photo
async def get_cat_photo() -> str:
    url = "https://api.thecatapi.com/v1/images/search"
    
    headers = {
        'x-api-key': catToken  # Добавляем API ключ в заголовки
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            return data[0]['url']  # Возвращаем URL изображения кота

#send cat photo  
async def send_cat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_info = get_user_info(update)
    
    try:
        # Получаем URL фото кота
        cat_url = await get_cat_photo()
        
        if cat_url:
            # Отправляем фото кота
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
        await context.bot.send_message(
            chat_id=user_info[0],
            text=f"Произошла ошибка: {str(e)}"
        )

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    location = update.message.location
    latitude = location.latitude
    longitude = location.longitude
    context.user_data['location'] = (latitude, longitude)

    weather_report = await get_weather(latitude, longitude)
    await update.message.reply_text(weather_report)

    main_menu = ReplyKeyboardMarkup([
        ['Погода сегодня', 'Сгенери аватар'],
        ['Мой ID', 'Мой IP'],
        ['/random_digit']
    ], resize_keyboard=True)
    await update.message.reply_text('Главное меню:', reply_markup=main_menu)

async def get_weather(lat: float, lon: float) -> str:
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={token_weather}&units=metric&lang=ru"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return 'Ошибка при получении данных о погоде'
            data = await resp.json()

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

#keybord
async def wake_up(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_info = get_user_info(update)
    button = ReplyKeyboardMarkup([
        ['Погода сегодня', 'Сгенери аватар'],
        ['Мой ID', 'Мой IP'],
        ['Фото кота' ,'/random_digit']
    ], resize_keyboard=True)
    
    await context.bot.send_message(
        chat_id=user_info[0],
        text=f'Hello, {user_info[2]}, мы начинаем!',
        reply_markup=button
    )

async def miid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    user_id = user.id
    first_name = user.first_name or ''
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"Информация о вашем аккаунте:\n"
             f"• User ID: {user_id}\n"
             f"• Chat ID: {chat_id}\n"
             f"• Имя: {first_name}\n"
    )

#Get IP address - teper tochno
async def get_ip_address() -> str:
    url = "https://api.ipify.org?format=json"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['ip']
                return "Ошибка при получении IP"
        except asyncio.TimeoutError:
            return "Таймаут запроса"
        except Exception as e:
            return f"Ошибка: {str(e)}"


async def random_digit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_info = get_user_info(update)
    random_number = random.randint(1, 100)
    
    await context.bot.send_message(
        chat_id=user_info[0],
        text=f'🎲 Случайное число: {random_number}'
    )

application = ApplicationBuilder().token(token).build()
application.add_handler(CommandHandler('start', wake_up))
application.add_handler(CommandHandler('miID', miid_command))
application.add_handler(CommandHandler('random_digit', random_digit))
application.add_handler(MessageHandler(filters.TEXT, say_hi))
application.add_handler(MessageHandler(filters.LOCATION, handle_location))
application.run_polling()