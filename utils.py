import os
import asyncio
import aiofiles

from dotenv import load_dotenv
from helpers import YandexGPTStoryteller, GigaChatStoryteller


async def tell_stories(city: str, genre: str, temperature: str, description: str, story_length: str) -> tuple:
    """
    Генерирует истории с помощью моделей YandexGPT и GigaChat.
    """
    load_dotenv()
    YA_GPT_API_KEY = os.getenv('YA_GPT_API_KEY')
    YA_GPT_FOLDER_ID = os.getenv('YA_GPT_FOLDER_ID')
    GIGA_CHAT_AUTH_DATA = os.getenv('GIGA_CHAT_AUTH_DATA')

    yandexgpt_storyteller = YandexGPTStoryteller(api_key=YA_GPT_API_KEY, folder_id=YA_GPT_FOLDER_ID)
    gigachat_storyteller = GigaChatStoryteller(auth_data=GIGA_CHAT_AUTH_DATA)

    yandexgpt_result = await yandexgpt_storyteller.tell_story(city, genre, temperature, description, story_length)
    gigachat_result = await gigachat_storyteller.tell_story(city, genre, temperature, description, story_length)

    return yandexgpt_result, gigachat_result


async def save_to_file(base_dir: str, base_name: str, content: str) -> str:
    """
    Сохраняет содержимое в файл.
    """
    file_name = get_unique_filename(base_dir, base_name)
    async with aiofiles.open(file_name, 'w', encoding='utf-8') as file:
        await file.write(content)
    return file_name


async def main_with_saving(city: str, genre: str, temperature: str, description: str, story_length: str) -> None:
    """
    Главная функция для генерации и сохранения историй.
    """
    yandexgpt_result, gigachat_result = await tell_stories(city, genre, temperature, description, story_length)

    yandexgpt_story, yandexgpt_time_spent = yandexgpt_result
    gigachat_story, gigachat_time_spent = gigachat_result

    base_dir = 'results'
    os.makedirs(base_dir, exist_ok=True)

    yandexgpt_file, gigachat_file = await asyncio.gather(
        save_to_file(base_dir, 'yandexgpt_story', yandexgpt_story.replace('\n\n', '\n')),
        save_to_file(base_dir, 'gigachat_story', gigachat_story.replace('\n\n', '\n'))
    )

    print(f"\n{'=' * 40}")
    print(f"Модель: YandexGPT")
    print(f"Длительность запроса: {yandexgpt_time_spent:.2f} секунд")
    print(f"Файл: {yandexgpt_file}")
    print(f"{'=' * 40}")
    print(f"Модель: GigaChat")
    print(f"Длительность запроса: {gigachat_time_spent:.2f} секунд")
    print(f"Файл: {gigachat_file}")
    print(f"{'=' * 40}\n")


def get_unique_filename(base_dir: str, base_name: str) -> str:
    """
    Генерирует уникальное имя файла.
    """
    index = 0
    file_name = os.path.join(base_dir, f"{base_name}.txt")
    while os.path.exists(file_name):
        index += 1
        file_name = os.path.join(base_dir, f"{base_name}{index}.txt")
    return file_name
