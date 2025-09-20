import random
from telegram import Update, KeyboardButton
from telegram.ext import ContextTypes
from telegram import ReplyKeyboardMarkup
from utils import get_user_info, get_ip_address, get_cat_photo, get_weather, create_main_menu

async def say_hi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    try:
        if not update or not update.message:
            return
            
        user_info = get_user_info(update)
        if not user_info[0]:
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
            await context.bot.send_message(chat_id=user_info[0], text=f'Ваш IP адрес: {ip_address}')
        elif text == 'Погода сегодня':
            await request_location(update, context)
        else:
            await context.bot.send_message(chat_id=user_info[0], text=f'{user_info[1]}, как твои дела?')
    except Exception as e:
        print(f"Ошибка в say_hi: {e}")

async def request_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запрос геолокации"""
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

async def send_cat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет фото кота"""
    try:
        user_info = get_user_info(update)
        if not user_info[0]:
            return
            
        catToken = context.bot_data.get('catToken')
        cat_url = await get_cat_photo(catToken)
        
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

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик геолокации"""
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
        token_weather = context.bot_data.get('token_weather')
        weather_report = await get_weather(latitude, longitude, token_weather)
        
        await update.message.reply_text(weather_report)

        main_menu = create_main_menu()
        await update.message.reply_text('Главное меню:', reply_markup=main_menu)
        
    except Exception as e:
        print(f"Ошибка в handle_location: {e}")

async def wake_up(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    try:
        user_info = get_user_info(update)
        if not user_info[0]:
            return
            
        button = create_main_menu()
        
        await context.bot.send_message(
            chat_id=user_info[0],
            text=f'Hello, {user_info[2]}, мы начинаем!',
            reply_markup=button
        )
    except Exception as e:
        print(f"Ошибка в wake_up: {e}")

async def miid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /miID"""
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

async def random_digit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /random_digit"""
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