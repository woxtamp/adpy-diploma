import os
import time
import re
import vk_api
from random import randrange
from dotenv import load_dotenv
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_group_api import VkGroupApi
from vk_user_api import VkUserApi
from datetime import datetime
import db_worker as vk_db_user


class VkBotApi:
    def __init__(self, token):
        self.vk = vk_api.VkApi(token=token)
        self.longpoll = VkLongPoll(self.vk)
        self.group = VkGroupApi(token)
        self.user = VkUserApi(token)
        self.vk_db_user = vk_db_user

    def write_msg(self, user_id, message, keyboard=None, attachment=None):
        post = {'user_id': user_id, 'message': message, 'attachment': attachment, 'random_id': randrange(10 ** 7)}

        if keyboard is not None:
            post['keyboard'] = keyboard.get_keyboard()
        else:
            post['keyboard'] = VkKeyboard().get_empty_keyboard()

        self.vk.method('messages.send', post)

    def dialog(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    request = event.text.lower()

                    keyboard_main = VkKeyboard()
                    buttons_main = ['vkinder']
                    button_main_colors = [VkKeyboardColor.SECONDARY]
                    for btn, btn_color in zip(buttons_main, button_main_colors):
                        keyboard_main.add_button(btn, btn_color)

                    keyboard_sex = VkKeyboard()
                    buttons_sex = ['женский', 'мужской']
                    button_sex_colors = [VkKeyboardColor.SECONDARY, VkKeyboardColor.SECONDARY]
                    for btn, btn_color in zip(buttons_sex, button_sex_colors):
                        keyboard_sex.add_button(btn, btn_color)

                    users_offset = 0

                    while True:
                        if request == 'vkinder':
                            users_offset += 1
                            values_dict = {}
                            photos_dict = {}
                            photos_dict_sorted = {}

                            opened_user_id = 0
                            opened_user_name = ''

                            fields_values = self.group.get_user_data(event.user_id)
                            values_dict['vk_id'] = event.user_id

                            if not self.vk_db_user.check_exist_vk_token(values_dict['vk_id']) and int(
                                    datetime.now().timestamp()) < int(self.vk_db_user.get_token_lifetime_from_db(
                                    values_dict['vk_id'])):
                                self.user.__init__(self.vk_db_user.get_user_token_from_db(values_dict['vk_id']))

                            else:
                                dotenv_path = os.path.join('.env')
                                if os.path.exists(dotenv_path):
                                    load_dotenv(dotenv_path)
                                get_user_token_url = os.getenv('USER_TOKEN_URL')
                                self.write_msg(event.user_id, 'Привет! Я бот для поиска твоей идеальной второй '
                                                              f'половинки\n{self.group.get_username(event.user_id)}, '
                                                              'для моей работы нужно перейти по ссылке:\n'
                                                              f'{get_user_token_url}\n'
                                                              'Затем нужно разрешить доступ к аккаунту и отправить '
                                                              'мне ссылку из браузера в течение 30 секунд')
                                last_message = self.group.get_message_id()

                                time.sleep(30)

                                try:
                                    self.group.get_message_by_id(last_message + 1)
                                    user_token_url = self.group.get_message()
                                    pattern = r'(access_token=)(\w*)(&expires_in)'
                                    try:
                                        token_lifetime = int(datetime.now().timestamp()) + 86370
                                        user_token = (re.search(pattern, user_token_url, re.M | re.I)).group(2)
                                        self.vk_db_user.add_vk_user_token_to_db(values_dict['vk_id'], user_token,
                                                                                token_lifetime)
                                        self.user.__init__(self.vk_db_user.get_user_token_from_db(values_dict['vk_id']))
                                        break

                                    except AttributeError:
                                        self.write_msg(event.user_id, f'{self.group.get_username(event.user_id)}, к '
                                                                      'сожалению ты отправил неправильную ссылку.\n'
                                                                      'Пожалуйста, попробуй заново', keyboard_main)
                                        break

                                except IndexError:
                                    self.write_msg(event.user_id, 'Сожалею, но ты не успел :(\nНачни заново.',
                                                   keyboard_main)
                                    break

                            if fields_values[0] == '':
                                self.write_msg(event.user_id, f'{self.group.get_username(event.user_id)}, в течение 30 '
                                                              'секунд укажи свой возраст цифрами и немного подожди.')
                                last_message_id = self.group.get_message_id()
                                time.sleep(30)
                                try:
                                    self.group.get_message_by_id(last_message_id + 1)
                                    age = self.group.get_message()
                                    if not age.isdigit():
                                        self.write_msg(event.user_id, 'Сожалею, но ты ввёл не число :(\n'
                                                                      'Начни заново.', keyboard_main)
                                        break
                                    elif age < 18:
                                        self.write_msg(event.user_id, 'Ты ещё слишком молод для того, чтобы искать '
                                                                      'себе пару.\nВозвращайся когда повзрослеешь :(')
                                        break
                                    else:
                                        values_dict['age'] = int(self.group.get_message())
                                except IndexError:
                                    self.write_msg(event.user_id, 'Сожалею, но ты не успел :(\nНачни заново.',
                                                   keyboard_main)
                                    break
                            else:
                                year_now = datetime.now().year
                                year_birthday = int(fields_values[0][-4:])
                                age = year_now - year_birthday
                                if age < 18:
                                    self.write_msg(event.user_id, 'Ты ещё слишком молод для того, чтобы искать '
                                                                  'себе пару.\nВозвращайся когда повзрослеешь :(')
                                    break
                                else:
                                    values_dict['age'] = age

                            if fields_values[1] == '':
                                self.write_msg(event.user_id, f'{self.group.get_username(event.user_id)}, в течение '
                                                              '30 секунд кнопкой выбери свой пол и немного '
                                                              'подожди', keyboard_sex)
                                last_message_id = self.group.get_message_id()
                                time.sleep(30)
                                try:
                                    self.group.get_message_by_id(last_message_id + 1)
                                    sex = self.group.get_message().lower()
                                    if sex == 'женский':
                                        values_dict['sex'] = 1
                                    elif sex == 'мужской':
                                        values_dict['sex'] = 2
                                    else:
                                        self.write_msg(event.user_id, 'Я же сказал, выбери кнопкой, а не пиши сам!\n'
                                                                      'Теперь придётся начать заново :(', keyboard_main)
                                        break
                                except IndexError:
                                    self.write_msg(event.user_id, 'Сожалею, но ты не успел :(\nНачни заново.',
                                                   keyboard_main)
                                    break
                            else:
                                values_dict['sex'] = int((eval(fields_values[1])))

                            if fields_values[2] == '':
                                self.write_msg(event.user_id, f'{self.group.get_username(event.user_id)}, в течение 30 '
                                                              'секунд отправь название своего российского города на '
                                                              'русском языке и немного подожди.')
                                last_message_id = self.group.get_message_id()
                                time.sleep(30)
                                try:
                                    self.group.get_message_by_id(last_message_id + 1)
                                    city_name = self.group.get_message().lower().capitalize()
                                    try:
                                        values_dict['city_name'] = city_name
                                        values_dict['city_id'] = None

                                    except KeyError:
                                        self.write_msg(event.user_id, 'Сожалею, но такого города нет :(\nПопробуй '
                                                                      'указать его в своём профиле VK и напиши мне ещё '
                                                                      'раз', keyboard_main)

                                except IndexError:
                                    self.write_msg(event.user_id, 'Сожалею, но ты не успел :(\nНачни заново.',
                                                   keyboard_main)
                                    break
                            else:
                                values_dict['city_name'] = str((eval(fields_values[2])['title']))
                                values_dict['city_id'] = int((eval(fields_values[2])['id']))

                            self.write_msg(event.user_id, 'Пожалуйста, подожди! Подбираем тебе пару!\n'
                                                          'К сожалению, меня писал не очень опытный программист, '
                                                          'поэтому ожидание может быть долгим :(')

                            self.vk_db_user.add_user_to_db(values_dict['vk_id'], values_dict['age'],
                                                           values_dict['sex'], values_dict['city_name'],
                                                           values_dict['city_id'])
                            sex_search = 0
                            if values_dict['sex'] == 1:
                                sex_search = 2
                            elif values_dict['sex'] == 2:
                                sex_search = 1

                            self.vk_db_user.add_search_params_to_db(values_dict['vk_id'], values_dict['age'] - 2,
                                                                    values_dict['age'] + 2, sex_search,
                                                                    values_dict['city_name'],
                                                                    values_dict['city_id'])

                            if self.vk_db_user.check_exist_city_id(values_dict['vk_id']):
                                city_type = 'hometown'
                                city = values_dict['city_name']
                            else:
                                city_type = 'city'
                                city = values_dict['city_id']

                            vk_user = self.user.get_users(city_type, city, sex_search, values_dict['age'] - 2,
                                                          values_dict['age'] + 2, users_offset)

                            if not vk_user["items"]:
                                users_offset += 1
                                break

                            for item in vk_user["items"]:
                                is_closed_next = True
                                is_closed_next_repeat = False
                                opened_user_screen_name = ''

                                if item["is_closed"]:
                                    while is_closed_next:
                                        users_offset += 1
                                        vk_user_next = self.user.get_users(city_type, city, sex_search,
                                                                           values_dict['age'] - 2, values_dict['age']
                                                                           + 2, users_offset)
                                        for item_next in vk_user_next["items"]:
                                            if not self.vk_db_user.check_exist_find_user(values_dict['vk_id'],
                                                                                         item_next['id']):
                                                is_closed_next = True
                                            else:
                                                if item_next['is_closed']:
                                                    break
                                                else:
                                                    opened_user_id = item_next['id']
                                                    opened_user_screen_name = item_next['screen_name']
                                                    opened_user_name = item_next['first_name']
                                                    is_closed_next = False

                                    self.write_msg(event.user_id, f'Эй, {self.group.get_username(event.user_id)}, '
                                                                  f'смотри, неплохой кандидат на роль твоей '
                                                                  f'второй половинки - {opened_user_name}:\n'
                                                                  f'https://vk.com/{opened_user_screen_name}',
                                                   keyboard_main)
                                    self.vk_db_user.add_find_user_to_db(values_dict['vk_id'],
                                                                        opened_user_id)

                                else:
                                    while not is_closed_next_repeat:
                                        vk_user_next = self.user.get_users(city_type, city, sex_search,
                                                                           values_dict['age'] - 2, values_dict['age']
                                                                           + 2, users_offset)
                                        users_offset += 1
                                        for item_next in vk_user_next["items"]:
                                            if not self.vk_db_user.check_exist_find_user(values_dict['vk_id'],
                                                                                         item_next['id']):
                                                is_closed_next_repeat = False
                                            else:
                                                if item_next['is_closed']:
                                                    break
                                                else:
                                                    opened_user_id = item_next['id']
                                                    opened_user_screen_name = item_next['screen_name']
                                                    opened_user_name = item_next['first_name']
                                                    is_closed_next_repeat = True
                                    else:
                                        self.write_msg(event.user_id, f'Эй, {self.group.get_username(event.user_id)}, '
                                                                      'смотри, неплохой кандидат на роль твоей '
                                                                      f'второй половинки - {opened_user_name}:\n'
                                                                      f'https://vk.com/{opened_user_screen_name}',
                                                       keyboard_main)
                                        self.vk_db_user.add_find_user_to_db(values_dict['vk_id'],
                                                                            opened_user_id)
                            vk_photos = self.user.get_photos(opened_user_id)

                            for item in vk_photos['items']:
                                photos_dict[item['id']] = item['likes']['count'] + item['comments']['count']
                                photos_dict_sorted = dict(sorted(photos_dict.items(), key=lambda x: x[1])[-3:])

                            photo_ids = list(photos_dict_sorted.keys())

                            for item in photo_ids:
                                self.write_msg(event.user_id, '', keyboard_main, f'photo{opened_user_id}_{item}')

                            self.write_msg(event.user_id, 'Для продолжения поиска нажми кнопку "vkinder" ещё раз',
                                           keyboard_main)

                            break

                        elif request == 'привет' or request == 'хай':
                            self.write_msg(event.user_id, f'Привет, {self.group.get_username(event.user_id)}!',
                                           keyboard_main)
                            break
                        elif request == 'пока':
                            self.write_msg(event.user_id, f'До скорых встреч, {self.group.get_username(event.user_id)}',
                                           keyboard_main)
                            break
                        else:
                            self.write_msg(event.user_id, 'Пожалуйста, нажми на кнопку "vkinder".', keyboard_main)
                            break
