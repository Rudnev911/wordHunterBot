from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters
from handlers import say_hi, handle_location, wake_up, miid_command, random_digit

def setup_handlers(application):
    """Настройка обработчиков бота"""
    application.add_handler(CommandHandler('start', wake_up))
    application.add_handler(CommandHandler('miID', miid_command))
    application.add_handler(CommandHandler('random_digit', random_digit))
    application.add_handler(MessageHandler(filters.TEXT, say_hi))
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))

def run_bot(token, token_weather, catToken):
    """Запуск бота"""
    try:
        application = ApplicationBuilder().token(token).build()
        
        # Сохраняем конфигурацию в данных бота
        application.bot_data['token_weather'] = token_weather
        application.bot_data['catToken'] = catToken
        
        # Настраиваем обработчики
        setup_handlers(application)
        
        print("Бот запускается...")
        application.run_polling()
        
    except Exception as e:
        print(f"Критическая ошибка при запуске бота: {e}")