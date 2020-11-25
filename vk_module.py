from urllib.parse import urlencode
from requests import get
# from vk_api.longpoll import VkEventType
# from main import get_search_user_info
import vk_api
from vk_api.keyboard import VkKeyboard
from vk_api.longpoll import VkLongPoll
from vk_api import VkApi
from random import randrange
import json

# group_token = input('Token: ')
group_token = 'fe40651e2f644afbf32552f6fabc7d471bbab8a43fffd2b08d62d63e955977892f8f1a468018b8f2ee2f5'
vk = VkApi(token=group_token)
longpoll = VkLongPoll(vk)

decision_key = VkKeyboard(one_time=True)


# def get_token():
#     url = f"https://oauth.vk.com/access_token"
#     params = {
#         "client_id": 7585945,
#         "client_secret": "xVuQdxMEBJQkz937xpeY",
#         "grant_type": "client_credentials",
#         "scope": "friends",
#         "v": 5.126
#     }
#     url_requests = "?".join((url, urlencode(params)))
#     response = get(url_requests)
#     print(url_requests)
#     ACCESS_TOKEN = response.json()["access_token"]
#     print(ACCESS_TOKEN)
#     return ACCESS_TOKEN


class VkUser:

    def __init__(self):
        self.token = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'
        self.vk_api = vk_api.VkApi(token=self.token).get_api()
        self.photo_info_dict = {}
        self.tmp = {}
        self.offset = 0

    def get_user_info(self, user_id):
        """
        :param user_id: принимает User ID или Короткое название аккаунта VK
        :return: словарь со информацией о Юзере (Имя, Фамилия, Id, пол, день рождеждения, город(id, название)
        """
        user = self.vk_api.users.get(user_ids=user_id, fields='first_name, last_name, sex, relation, bdate')
        return user[0]

    def get_users_best_photos(self, user_id, count_photos=3):
        """
        Получаем словарь с ТОП фотографиями из профиля
        :param count_photos: количество фотографий с максимальными лайками
        :param user_id: принимает User ID или Короткое название аккаунта VK
        :return: словарь с ТОП 3мя фотографиями (ссылки (значения))
        из профиля аккаунта с их лайками (в качетстве имени (ключ))
        """
        try:
            photos_info = self.vk_api.photos.get(owner_id=self.get_user_info(user_id)['id'], album_id='profile',
                                                 extended=1, count=1000, photo_sizes=0)
            # создаем словарь со всеми лайками и ссылками на фото
            for elem in photos_info['items']:
                photo_url = elem['sizes'][-1]['url']
                photos_list_likes = elem['likes']['count']
                if photos_list_likes in self.photo_info_dict:
                    self.tmp[photos_list_likes - 1] = photo_url
                self.tmp[photos_list_likes] = photo_url
            # новый словарь с необходимым количеством максимальных лайков
            try:
                self.photo_info_dict = {k: v for k, v in self.tmp.items() if
                                        k > sorted(self.tmp.keys(), reverse=True)[count_photos]}
                return self.photo_info_dict
            except IndexError:
                if len(self.tmp) == 0:
                    return str(f'у юзера {user_id} нет фотографий в профиле')
                else:
                    return self.tmp
        except vk_api.exceptions.ApiError:
            return str(f'профиль юзера {user_id} приватный - фоток нет')

    def get_city_id(self, city):
        """
        Принимает название города или его id и выдает id города
        :param city: Название города, можно часть или id
        :return: id города
        """
        try:
            int(city)
            return city
        except ValueError:
            city_id = self.vk_api.database.getCities(country_id=1, q=city)
            return city_id['items'][0]['id']

    def get_city_name(self, city_id):
        city_name = self.vk_api.database.getCitiesById(city_ids=city_id)
        return city_name

    def search_dating_user(self, age_from, age_to, sex, city, status):
        """
        Получаем словарь с результатами поиска для дальнейшего просмотра людей
        :param age_from:    возраст, от.
        :param age_to:      возраст, до.
        :param sex:         пол                 (1 — женщина;
                                                 2 — мужчина)
        :param city:        город (id или название)
        :param status:      семейное положение (1 — не женат/не замужем;
                                                2 — есть друг/есть подруга;
                                                3 — помолвлен/помолвлена;
                                                4 — женат/замужем;
                                                5 — всё сложно;
                                                6 — в активном поиске;
                                                7 — влюблён/влюблена;
                                                8 — в гражданском браке;
                                                0 — не указано)
        :return:            список словарей подходящих Юзеров
        """
        users_info_dict = self.vk_api.users.search(offset=self.offset, count=1000, age_from=age_from, age_to=age_to,
                                                   sex=sex, city=self.get_city_id(city), status=status,
                                                   fields='bdate')
        self.offset += 1
        return users_info_dict['items']


def get_text_buttons(label, color, payload=""):
    return {
        "action": {
            "type": "text",
            "label": label,
            "payload": json.dumps(payload)
        },
        "color": color
    }


decision = {'inline': True,
            'buttons': [
                [
                    get_text_buttons('лайк', 'positive'),
                    get_text_buttons('крестик', 'secondary'),
                    get_text_buttons('пропуск', 'secondary')
                ],
                [get_text_buttons('выход', 'negative')]
            ]
            }

greeting = {'one_time': True,
            'buttons': [
                [get_text_buttons('начать поиск', 'primary')],
                [get_text_buttons('показать/удалить людей из лайк списка', 'positive')],
                [get_text_buttons('показать/удалить людей из блэк списка', 'secondary')],
                [get_text_buttons('выйти', 'negative')],
            ]
            }

keyboards = {
    'greeting': greeting,
    'decision': decision,
}


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id,
                                'message': message,
                                'random_id': randrange(10 ** 7)})


def write_msg_keyboard(user_id, message, keyboard):
    vk.method('messages.send', {'user_id': user_id,
                                'message': message,
                                'random_id': randrange(10 ** 7),
                                'keyboard': json.dumps(keyboards[keyboard], ensure_ascii=False)})


if __name__ == '__main__':
    pass
