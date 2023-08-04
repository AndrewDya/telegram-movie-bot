import locale
import os
from dotenv import load_dotenv
import logging

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

locale.setlocale(locale.LC_ALL, '')

log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    filename=os.path.join(log_dir, 'info.log'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
