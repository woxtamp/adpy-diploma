import os
from dotenv import load_dotenv
from dialog import Dialog

if __name__ == '__main__':
    # Проверяем наличие файла .env и если он существует, то берём оттуда токен группы
    dotenv_path = os.path.join('.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    token = os.getenv('VK_GROUP_TOKEN')

    # создаём экземпляр класса VkBotApi и начинаем диалог с пользователем
    bot = Dialog(token)
    bot.dialog()
