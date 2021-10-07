import vk_api


class VkUserApi:
    def __init__(self, token):
        token = token
        self.vk = vk_api.VkApi(token=token)

    def get_city_by_name(self, city_name):
        user_response = self.vk.method('database.getCities', {'country_id': 1, 'q': city_name, 'count': 1})
        city_id = user_response['items'][0]['id']
        return city_id

    def get_users(self, city_type, city, sex, age_from, age_to, offset):
        user_response = self.vk.method('users.search', {'sort': 1, 'count': 1, f'{city_type}': city, 'sex': sex,
                                                        'status': 6, 'age_from': age_from, 'age_to': age_to,
                                                        'has_photo': 1, 'fields': 'screen_name', 'offset': offset})
        return user_response

    def get_photos(self, owner_id):
        user_response = self.vk.method('photos.get', {'owner_id': owner_id, 'album_id': 'profile',
                                                      'extended': 1, 'count': 1000})
        return user_response

    def get_photo(self, photo_id):
        user_response = self.vk.method('photos.getById', {'photos': photo_id, 'photo_sizes': 1})
        return user_response
