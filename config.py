import locale
import os
from dotenv import load_dotenv
import logging

# Проверяем наличие файла .env и загружаем переменные окружения
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    raise FileNotFoundError("Файл .env не найден. Убедитесь, что он существует "
                            "и содержит необходимые переменные окружения.")

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("Переменная окружения API_KEY не определена. Убедитесь, "
                     "что она присутствует в файле .env.")

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("Переменная окружения TOKEN не определена. Убедитесь, "
                     "что она присутствует в файле .env.")

language = 'ru-RU'

# Устанавливаем настройки вывода даты и времени, а также логирование
locale.setlocale(locale.LC_ALL, '')
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
