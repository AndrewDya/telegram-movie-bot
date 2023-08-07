# Telegram-бот для информации о фильмах

Проект представляет собой Telegram-бот (написан на python telegram bot 20.4), который позволяет пользователям искать фильмы, актёров и сериалы по названию, просматривать информацию о них, а также добавлять фильмы в список избранного с использованием открытого API от The Movie Database (TMDb).

## Установка и настройка

1. Установите Python 3.9 или более новую версию, которую можно скачать с официального сайта Python:

https://www.python.org/downloads/

2. Клонируйте репозиторий проекта:

git clone https://github.com/AndrewDya/telegram-movie-bot


3. Установите зависимости, указанные в файле `requirements.txt`:

pip install -r requirements.txt


4. Получите API-ключ TMDb, зарегистрировавшись на их [сайте](https://www.themoviedb.org/):


5. Создайте бота в Telegram и получите TOKEN от @BotFather, это можно сделать перейдя по [ссылке](https://t.me/BotFather)


6. В папке проекта создайте файл `.env` и добавьте в него следующие строки (есть файл примера .env.template), заменив `<YOUR_API_KEY>` и `<YOUR_TOKEN>` на ваш собственный API-ключ TMDb и ваш собственный telegram TOKEN:

```python
API_KEY = "YOUR_API_KEY_HERE"
TOKEN = "YOUR_TOKEN_HERE"
```

## Как использовать

1. Запустите скрипт `main.py`:

python main.py


2. В Telegram найдите созданного бота и начните с ним диалог введя команду /start.

3. Доступные команды бота:

- `/help` - помощь по командам бота.
- `/popular` - список популярных фильмов.
- `/top_rated` - список фильмов с высоким рейтингом.
- `/upcoming` - список ожидаемых фильмов.
- `/search` - поиск фильма/актёра/сериала по названию.
- `/favorite` - список избранных фильмов.

### Популярные фильмы

Команда: /popular_command
Описание: Эта команда позволяет получить список популярных фильмов. Пользователь может выбрать количество фильмов для вывода (например, 1, 3, 5 или 10) и бот предоставит информацию о соответствующем числе популярных фильмов. После выбора количества фильмов, бот отобразит названия фильмов, их рейтинг, жанры, продолжительность и информацию об актерах.

### Топ рейтинга

Команда: /top_rated_command
Описание: Эта команда позволяет получить список фильмов с высоким рейтингом. Пользователь также может выбрать количество фильмов для вывода (1, 3, 5 или 10) и получит информацию о фильмах с наивысшим рейтингом. Бот предоставит информацию о названиях фильмов, их рейтинге, жанрах, продолжительности и актерах.

### Ожидаемые фильмы

Команда: /upcoming_command
Описание: Эта команда позволяет получить список ожидаемых фильмов. Пользователь может выбрать количество фильмов для вывода (1, 3, 5 или 10) и бот предоставит информацию о соответствующем числе ожидаемых фильмов. Бот отобразит названия фильмов, их рейтинг, жанры, продолжительность и информацию об актерах.

### Поиск фильма

Команда: /search_command
Описание: Эта команда позволяет пользователю искать фильмы/актёров/сериалы по названию. После ввода команды, бот запросит пользователя выбрать категорию, затем ввести поисковый запрос. После этого, он выполнит поиск, используя запросы к API и выведет результаты поиска. Если найдены соответствующие результаты, бот отобразит информацию о них, включая название, рейтинг, жанры, продолжительность и т.д..

### Избранное

Команда: /favorites_command
Описание: Эта команда позволяет просмотреть список фильмов, добавленных в список избранного. Если пользователь добавил фильмы в избранное с помощью команды "Добавить в избранное", то бот отобразит их в этом списке. Бот предоставит информацию о названиях фильмов, их рейтинге, продолжительности и другую дополнительную информацию. Каждая команда возвращает информацию о фильмах в виде списка, который включает название фильма, его рейтинг, жанры, продолжительность и информацию об актерах. При необходимости, можно просмотреть дополнительную информацию о фильме, включая его описание и трейлер, если они доступны. Кнопки в сообщениях позволяют легко навигировать по функциям бота, добавлять фильмы в избранное и просматривать дополнительную информацию.

## Дополнительная информация

- Проект разработан на языке Python и использует библиотеку python-telegram-bot для взаимодействия с Telegram API.
- Для получения информации о фильмах используется открытое API от The Movie Database (TMDb).
- Для работы с базой данных SQLite используется модуль sqlite3.
- Для выполнения HTTP-запросов используется модуль requests.
- Изображения фильмов загружаются и отправляются с использованием модуля io и методов Telegram API.
- Бот сохраняет информацию о фильмах, добавленных в избранное, в базе данных SQLite.
- Модуль Peewee обеспечивает работу с базой данных SQLite, позволяя сохранять информацию о фильмах, добавленных в избранное, с помощью объектно-реляционного отображения (ORM).
- Для более подробного мониторинга используется логирование с помощью библиотеки logging. Данные сохраняются в папке logs.

## Лицензия

[MIT License](https://opensource.org/licenses/MIT)


## Screenshots

![Screenshot](/images/Screen_1.jpg)
![Screenshot](/images/Screen_2.jpg)

## Контакты

Если у вас есть вопросы или предложения по улучшению MovieBot, свяжитесь со мной:

- Email: AndrewDya@gmail.com
- Telegram: [AndrewDya](https://t.me/AndrewDya)
