from typing import Tuple

import aiohttp
import time


class YandexGPTStoryteller:
    """
    Класс для создания нейроcказок с использованием модели YandexGPT.
    """
    SYSTEM_PROMPT: str = 'Твоя задача написать нейроcказку про завтрашний прогноз погоды в указанном городе, используя температуру и описание погоды, в указанном жанре'

    def __init__(self, api_key: str, folder_id: str):
        """
        Инициализация объекта YandexGPTStoryteller.
        """
        self._api_key = api_key
        self._folder_id = folder_id

    async def tell_story(self, city: str, genre: str, temp: str, description: str, length: str) -> Tuple[str, float]:
        """
        Генерирует нейроcказку о погоде в указанном городе.
        """
        prompt = {
            "modelUri": f"gpt://{self._folder_id}/yandexgpt-lite",
            "completionOptions": {
                "stream": False,
                "temperature": 0.1,
                "maxTokens": int(length) + 50
            },
            "messages": [
                {
                    "role": "system",
                    "text": self.SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "text": f"Напиши сказку используя следующую информацию:\n"
                            f"-Название города: {city}\n"
                            f"-Жанр сказки: {genre}\n"
                            f"-Прогноз на завтрашнюю погоду: температура {temp}, {description}\n"
                            f"-Длина сказки в символах: {length}"
                }
            ]
        }

        url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Api-Key {self._api_key}',
            'x-folder-id': self._folder_id,
        }

        start_time = time.time()

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, headers=headers, json=prompt) as response:
                    result = (await response.json())['result']['alternatives'][0]['message']['text']
            except aiohttp.ClientError as e:
                raise ValueError(f"Error during HTTP request: {e}")

        time_spent = time.time() - start_time
        return result, time_spent
