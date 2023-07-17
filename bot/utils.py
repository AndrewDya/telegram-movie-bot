import os
import locale
import logging
import httpx
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('API_KEY')
TOKEN = os.getenv('TOKEN')
language = 'ru-RU'

locale.setlocale(locale.LC_ALL, '')
logging.basicConfig(
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
	level=logging.INFO
)


# Вспомогательная функция для отправки HTTP-запроса
async def send_http_request(url):
	async with httpx.AsyncClient() as client:
		response = await client.get(url)
		if response.status_code == 200:
			return response.json()
		return None


# Вспомогательная функция для загрузки фотографии и получения ее содержимого
async def load_photo_content(url):
	async with httpx.AsyncClient() as client:
		response = await client.get(url)
		if response.status_code == 200:
			return response.content
		return None
