from typing import Union, Tuple

import aiohttp
import time
import uuid


class GigaChatStoryteller:
    """
    Класс для создания нейроcказок с использованием модели GigaChat.
    """
    SYSTEM_PROMPT: str = 'Твоя задача написать нейроcказку про завтрашний прогноз погоды в указанном городе, используя температуру и описание погоды, в указанном жанре'
    access_token: Union[str, None] = None

    def __init__(self, auth_data: str):
        """
        Инициализация объекта GigaChatStoryteller.
        """
        self._auth_data = auth_data

    async def issue_token(self) -> None:
        """
        Запрос на получение токена доступа к сервису GigaChat.
        """
        url = 'https://ngw.devices.sberbank.ru:9443/api/v2/oauth'

        payload = 'scope=GIGACHAT_API_PERS'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'RqUID': str(uuid.uuid4()),
            'Authorization': f'Basic {self._auth_data}'
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, headers=headers, data=payload, verify_ssl=False) as response:
                    self.access_token = (await response.json()).get('access_token')
            except aiohttp.ClientError as e:
                raise ValueError(f"Error while issuing token: {e}")

    async def tell_story(self, city: str, genre: str, temp: str, description: str, length: str) -> Tuple[str, float]:
        """
        Генерирует нейроcказку о погоде в указанном городе.
        """
        url = 'https://gigachat.devices.sberbank.ru/api/v1/chat/completions'

        payload = {
            "model": "GigaChat",
            "messages": [
                {
                    'role': 'system',
                    'content': self.SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": f"Напиши сказку используя следующую информацию:\n"
                               f"-Название города: {city}\n"
                               f"-Жанр сказки: {genre}\n"
                               f"-Прогноз на завтрашнюю погоду: температура {temp}, {description}\n"
                               f"-Длина сказки в символах: {length} символов"
                }
            ],
            "temperature": 1,
            "top_p": 0.1,
            "n": 1,
            "stream": False,
            "max_tokens": int(length) + 50,
            "repetition_penalty": 1
        }

        if self.access_token is None:
            await self.issue_token()

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }

        start_time = time.time()

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, headers=headers, json=payload, verify_ssl=False) as response:
                    result = (await response.json())['choices'][0]['message']['content']
            except aiohttp.ClientError as e:
                raise ValueError(f"Error during HTTP request: {e}")

        time_spent = time.time() - start_time
        return result, time_spent
