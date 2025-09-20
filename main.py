from config import load_config
from bot import run_bot

def main():
    """Основная функция запуска"""
    try:
        config = load_config()
        run_bot(config['token'], config['token_weather'], config['catToken'])
    except Exception as e:
        print(f"Ошибка при запуске: {e}")

if __name__ == '__main__':
    main()