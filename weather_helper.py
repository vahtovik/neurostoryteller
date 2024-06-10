from typing import Union, Tuple, Dict
from datetime import datetime, timedelta

import requests


class WeatherHelper:
    """
    Класс для получения прогноза погоды с использованием API OpenWeatherMap.
    """

    _location_cache: Dict[str, Tuple[float, float]] = {}

    def __init__(self, api_key: str):
        """
        Инициализация объекта WeatherHelper с API-ключом для OpenWeatherMap.
        """
        self._api_key = api_key

    def get_location_coordinates(self, location: str) -> Tuple[float, float]:
        """
        Получает координаты (широта и долгота) для заданного местоположения.
        :return: Кортеж (широта, долгота).
        """
        if location in WeatherHelper._location_cache:
            return WeatherHelper._location_cache[location]

        base_url = 'http://api.openweathermap.org/geo/1.0/direct'
        params = {
            'q': location,
            'appid': self._api_key,
        }

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            if data:
                lat, lon = data[0]['lat'], data[0]['lon']
                WeatherHelper._location_cache[location] = (lat, lon)
                return lat, lon
            else:
                raise ValueError('Location not found.')
        except requests.RequestException as e:
            raise ValueError(f"Error fetching location coordinates for {location}: {e}")

    def get_weather_info(self, location: str) -> Dict[str, Union[float, str]]:
        """
        Получает прогноз погоды на следующий день для заданного местоположения.
        :return: Словарь с данными о погоде.
        """
        lat, lon = self.get_location_coordinates(location)
        base_url = "http://api.openweathermap.org/data/2.5/forecast"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self._api_key,
            'units': 'metric',
            'lang': 'ru',
        }

        try:
            response = requests.get(base_url, params=params)
            data = response.json()
            # Проходим временным отрезкам прогнозов
            for forecast in data['list']:
                # Если дошли до прогноза на завтрашний день
                if forecast['dt_txt'].split()[0] == (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'):
                    try:
                        weather_info = {
                            'температура': forecast['main']['temp'],
                            'описание': forecast['weather'][0]['description'],
                            'влажность': forecast['main']['humidity'],
                            'давление': forecast['main']['pressure'],
                            'скорость ветра': forecast['wind']['speed']
                        }
                        return weather_info
                    except KeyError:
                        raise ValueError('Unexpected response format')
            raise ValueError('Weather data not found for tomorrow')
        except requests.RequestException as e:
            raise ValueError(f"Error fetching weather data for {location}: {e}")
