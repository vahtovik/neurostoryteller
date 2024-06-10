from weather_helper import WeatherHelper
from utils import main_with_saving
from dotenv import load_dotenv

import os
import asyncio

if __name__ == '__main__':
    load_dotenv()
    WEATHER_HELPER_API_KEY = os.getenv('WEATHER_HELPER_API_KEY')

    weather_helper = WeatherHelper(WEATHER_HELPER_API_KEY)

    weather_info = dict()
    while not weather_info:
        city = input('Введите название города: ').capitalize()
        try:
            weather_info = weather_helper.get_weather_info(city)
        except ValueError:
            print('Введите корректное название города')

    temperature = weather_info.get('температура')
    description = weather_info.get('описание')

    genres = ('драма', 'комедия', 'мюзикл', 'детектив', 'боевик', 'ужасы')
    genre = input('Выберите жанр - драма, комедия, мюзикл, детектив, боевик, ужасы: ').lower()
    while genre not in genres:
        print('Выберите жанр из списка')
        genre = input('Выберите жанр - драма, комедия, мюзикл, детектив, боевик, ужасы: ')

    story_length = input('Введите длину сказки в символах: ')
    while not story_length.isdigit():
        print('Введите корректное значение')
        story_length = input('Введите длину сказки в символах: ')

    asyncio.run(main_with_saving(city, genre, temperature, description, story_length))
