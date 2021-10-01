import vk_api


class VkGroupApi:
    def __init__(self, token):
        self.vk = vk_api.VkApi(token=token)

    def get_user_data(self, user_id):
        user_fields = ['bdate', 'sex', 'city']
        user_info = self.vk.method('users.get', {'user_ids': user_id, 'fields': 'bdate, sex, city'})

        fields_values = []
        for field in user_fields:
            try:
                fields_values.append(str(user_info[0][f'{field}']))
            except KeyError:
                fields_values.append('')
        return fields_values

    def get_username(self, user_id):
        user_info = self.vk.method('users.get', {'user_ids': user_id})
        return user_info[0]['first_name']

    def get_message_id(self):
        user_response = self.vk.method('messages.getConversations')
        user_input_data = user_response['items'][0]['conversation']['last_message_id']
        return user_input_data

    def get_message_by_id(self, message_id):
        user_response = self.vk.method('messages.getById', {'message_ids': message_id})
        user_input_data = user_response['items'][0]['text']
        return user_input_data

    def get_message(self):
        user_response = self.vk.method('messages.getConversations')
        user_input_data = user_response['items'][0]['last_message']['text']
        return user_input_data
