import os
from dotenv import load_dotenv
from vk_bot_api import VkBotApi

if __name__ == '__main__':
    # Проверяем наличие файла .env и если он существует, то берём оттуда токен группы
    dotenv_path = os.path.join('.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    token = os.getenv('VK_GROUP_TOKEN')

    # создаём экземпляр класса VkBotApi и начинаем диалог с пользователем
    bot = VkBotApi(token)
    bot.dialog()
