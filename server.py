import json
import re
from datetime import date
from random import randrange
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api import VkApi, exceptions
from sql_orm import DatingUser, UserPhoto, IgnoreUser, SkippedUser, UserVk, State, Search


def get_age(birth_info):
    date_info = re.findall(r'(\d\d?).(\d\d?)?.?(\d{4})?', birth_info)[0]
    if date_info[2]:
        today = date.today()
        age = (int(today.year) - int(date_info[2]) - int(
            (today.month, today.day) < (int(date_info[1]), int(date_info[0]))))
    else:
        age = f"{date_info[0]}.{date_info[1]}"
    return age


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


class Server:

    def __init__(self, api_token, db_session, server_name: str = "Empty"):
        self.server_name = server_name
        self.vk = VkApi(token=api_token)
        self.long_poll = VkLongPoll(self.vk)
        self.vk_api = self.vk.get_api()
        self.session = db_session
        self.event = None
        self.users_info_dict = {}
        self.count = 0
        self.states = {}

    def write_msg(self, message):
        self.vk.method('messages.send', {'user_id': self.event.user_id,
                                         'message': message,
                                         'random_id': randrange(10 ** 7)})

    def write_msg_keyboard(self, message, keyboard):
        self.vk.method('messages.send', {'user_id': self.event.user_id,
                                         'message': message,
                                         'random_id': randrange(10 ** 7),
                                         'keyboard': json.dumps(keyboards[keyboard], ensure_ascii=False)})

    def looking_for_user_vk(self, user_id):
        result = self.session.query(UserVk).filter_by(user_id=user_id)
        if self.session.query(result.exists()).one()[0]:
            for user, state, search in self.session.query(UserVk, State, Search).filter_by(user_id=user_id).all():
                return user, state, search
        else:
            user_info = VkUser().get_user_info(user_id)
            user_firstname = user_info['first_name']
            user_lastname = user_info['last_name']
            try:
                user_age = user_info['bdate']
                user_age = get_age(user_age)
            except KeyError:
                user_age = 'нет данных'
            user_sex = user_info['sex']
            try:
                user_city = user_info['city'][0]['title']
            except KeyError:
                user_city = 'нет данных'
            # добавляем юзера в базу данных
            user = UserVk(user_id=user_id, user_firstname=user_firstname, user_lastname=user_lastname,
                          user_age=user_age, user_sex=user_sex, user_city=user_city)
            self.session.add(user)
            self.session.commit()
            state = State(user_id=user_id, state='Hello')
            self.session.add(state)
            self.session.commit()
            search = Search().add_search(user_id=user_id)
            self.session.add(state)
            self.session.commit()
            return user, state, search

    # def get_search_user_info(self, search_user_id):
    #     """
    #     Функция добавляет пользователя в таблицу
    #     :param search_user_id:  Id человека ведущего поиск
    #     :return:                Объекты пользователя и его состояния
    #     """
    #     if self.looking_for_user_vk(search_user_id):
    #         for user, state, search in self.session.query(UserVk, State, Search).filter_by(
    #                 user_id=search_user_id).all():
    #             return user, state, search
    #     else:
    #         user_info = VkUser().get_user_info(search_user_id)
    #         user_firstname = user_info['first_name']
    #         user_lastname = user_info['last_name']
    #         try:
    #             user_age = user_info['bdate']
    #             user_age = get_age(user_age)
    #         except KeyError:
    #             user_age = 'нет данных'
    #         user_sex = user_info['sex']
    #         try:
    #             user_city = user_info['city'][0]['title']
    #         except KeyError:
    #             user_city = 'нет данных'
    #         # добавляем юзера в базу данных
    #         user = UserVk(user_id=search_user_id, user_firstname=user_firstname, user_lastname=user_lastname,
    #                       user_age=user_age, user_sex=user_sex, user_city=user_city)
    #         self.session.add(user)
    #         self.session.commit()
    #         state = State(user_id=search_user_id, state='Hello')
    #         self.session.add(state)
    #         self.session.commit()
    #         search = Search().add_search(user_id=search_user_id)
    #         self.session.add(state)
    #         self.session.commit()
    #         return user, state, search

    def hello_state(self, objects):
        if self.event.text == "выход":
            setattr(objects[1], "state", "Hello")
            self.session.commit()
            return False
        setattr(objects[1], "state", "Initial")
        self.session.commit()
        self.write_msg_keyboard('Выберите действие:', 'greeting')

    def initial_state(self, objects):
        if self.event.text == "начать поиск":
            try:
                setattr(objects[1], "state", "City")
                self.session.commit()
                self.write_msg('Введите город')
            except ValueError:
                setattr(objects[1], "state", "Error_Initial")
                self.session.commit()
            except IndexError:
                setattr(objects[1], "state", "Error_Initial")
                self.session.commit()
        elif self.event.text == "показать/удалить людей из лайк списка":
            pass
        elif self.event.text == "показать/удалить людей из блэк списка":
            pass
        elif self.event.text == "выйти":
            return False
        else:
            self.write_msg_keyboard('Привет! Выбери действие', 'greeting')
            setattr(objects[1], "state", "Initial")
            self.session.commit()

    def city_state(self, objects):
        try:
            city_name = VkUser().get_city_name(VkUser().get_city_id(self.event.text))[0]['title']
            setattr(objects[2], "search_city", city_name)
            setattr(objects[1], "state", "Sex")
            self.session.commit()
            self.write_msg('Введите пол:\n1 - женщина\n2 - мужчина')
        except IndexError:
            setattr(objects[1], "state", "Error_City")
            self.session.commit()

    def sex_state(self, objects):
        try:
            sex_value = int(self.event.text)
            setattr(objects[2], "search_sex", sex_value)
            setattr(objects[1], "state", "Relation")
            self.session.commit()
            self.write_msg('Введите семейное положение\n1 — не женат/не замужем\n2 — есть друг/есть подруга\n'
                           '3 — помолвлен/помолвлена\n4 — женат/замужем\n5 — всё сложно\n6 — в активном поиске\n'
                           '7 — влюблён/влюблена\n8 — в гражданском браке\n0 — не указано\n')
        except ValueError:
            setattr(objects[1], "state", "Error_Sex")
            self.session.commit()

    def relation_state(self, objects):
        try:
            status = int(self.event.text)
            setattr(objects[2], "search_relation", status)
            setattr(objects[1], "state", "Range")
            self.write_msg('Введите диапозон поиска ОТ и ДО (через пробел или -)')
        except ValueError:
            setattr(objects[1], "state", "Error_Relation")
            self.session.commit()

    def range_state(self, objects):
        try:
            age_pattern = re.compile(r'(\d\d?)[ -]+(\d\d?)')
            age_from = int(age_pattern.sub(r"\1", self.event.text))
            age_to = int(age_pattern.sub(r"\2", self.event.text))
            if age_to - age_from > 0:
                setattr(objects[2], "search_from", age_from)
                setattr(objects[2], "search_to", age_to)
                setattr(objects[1], "state", "Decision")
                self.session.commit()
                print(f'state inside Range - {objects[1].state}')
                age_from = objects[2].search_from
                age_to = objects[2].search_to
                sex = objects[2].search_sex
                city_name = objects[2].search_city
                status = objects[2].search_relation
                self.users_info_dict = VkUser().search_dating_user(age_from, age_to, sex, city_name, status)
            else:
                setattr(objects[1], "state", "Error_Range")
                self.session.commit()
        except ValueError:
            setattr(objects[1], "state", "Error_Range")
            self.session.commit()

    def decision_state(self, objects):
        if self.event.text == "выход":
            setattr(objects[1], "state", "Hello")
            self.session.commit()
            return False
        else:
            person = self.users_info_dict[self.count]
            user_dating_id = person['id']
            # проверка наличия найденного Id в таблицах
            if not self.is_inside_ignore_dating_skipped(user_dating_id, self.event.user_id):
                first_name = person['first_name']
                last_name = person['last_name']
                link = VkUser().get_users_best_photos(user_dating_id)  # сделать другой вывод
                self.write_msg(f'{first_name} {last_name} - {link}\n')
                self.write_msg_keyboard('Выберите действие', 'decision')
                setattr(objects[1], "state", "Answer")
                self.session.commit()
            else:
                self.count += 1

    def is_inside_ignore_dating_skipped(self, user_vk_id, search_id):
        """
        Проверяет юзера на наличие его в таблицах лайков и игноров
        Если совпадение есть, то Юзер пропускается в выдаче
        :param user_vk_id:  Id пары
        :param search_id:   Id диапозона
        :return:            True или False
        """
        result1 = self.session.query(DatingUser).filter_by(dating_user_id=user_vk_id, search_id=search_id)
        if self.session.query(result1.exists()).one()[0]:
            return True
        else:
            result2 = self.session.query(IgnoreUser).filter_by(ignore_user_id=user_vk_id, search_id=search_id)
            if self.session.query(result2.exists()).one()[0]:
                return True
            else:
                result3 = self.session.query(SkippedUser).filter_by(skip_user_id=user_vk_id, search_id=search_id)
                return self.session.query(result3.exists()).one()[0]

    def answer_state(self, objects):
        if self.event.text == "лайк":
            setattr(objects[1], "state", "Decision")
            self.session.commit()
            person = self.users_info_dict[self.count]
            first_name = person['first_name']
            last_name = person['last_name']
            user_dating_id = person['id']
            print('дошли до Answer')
            try:
                age = person['bdate']
                age = get_age(age)
            except KeyError:
                age = 'нет данных'
            DatingUser().add_dating_user(user_dating_id, first_name, last_name, age, objects[2].search_id)
            UserPhoto().add_user_photo(VkUser().get_users_best_photos(user_dating_id), user_dating_id,
                                       objects[2].search_id)
            self.count += 1
        elif self.event.text == "крестик":
            setattr(objects[1], "state", "Decision")
            self.session.commit()
            person = self.users_info_dict[self.count]
            user_ignore_id = person['id']
            IgnoreUser().add_ignore_user(user_ignore_id, objects[2].search_id)
            self.count += 1
        elif self.event.text == "пропуск":
            setattr(objects[1], "state", "Decision")
            self.session.commit()
            person = self.users_info_dict[self.count]
            user_skip_id = person['id']
            SkippedUser().add_skipped_user(user_skip_id, objects[2].search_id)
            self.count += 1
        elif self.event.text == "выход":
            setattr(objects[1], "state", "Hello")
            self.session.commit()

    def get_user_first_name(self, user_id):
        """ Получаем имя пользователя"""
        return self.vk_api.users.get(user_id=user_id)[0]['first_name']

    def get_user_last_name(self, user_id):
        """ Получаем фамилию пользователя"""
        return self.vk_api.users.get(user_id=user_id)[0]['last_name']

    def get_user_city(self, user_id):
        """ Получаем город пользователя"""
        return self.vk_api.users.get(user_id=user_id, fields="city")[0]["city"]['title']

    def get_user_sex(self, user_id):
        """ Получаем пол пользователя"""
        return self.vk_api.users.get(user_id=user_id, fields="sex")[0]['sex']

    def get_user_birth_day(self, user_id):
        """ Получаем день рождения пользователя"""
        try:
            return self.vk_api.users.get(user_id=user_id, fields="bdate")[0]['bdate']
        except KeyError:
            return str('Нет данных')

    def use_state(self, state_name):
        self.states = {
            "Hello": self.hello_state,
            "Initial": self.initial_state,
            "City": self.city_state,
            "Sex": self.sex_state,
            "Relation": self.relation_state,
            "Range": self.range_state,
            "Decision": self.decision_state,
            "Answer": self.answer_state
        }
        return self.states[state_name]

    def start(self):
        for event in self.long_poll.listen():
            self.event = event
            if self.event.type != VkEventType.MESSAGE_NEW:
                continue
            if not self.event.to_me:
                continue
            objects = self.looking_for_user_vk(self.event.user_id)
            print(f'current state = {objects[1].state}')
            ans = self.use_state(objects[1].state)(objects)
            # при нажатии Выход ans возвращает False и выходим из программы
            if ans or ans is None:
                continue
            else:
                break


class VkUser:

    def __init__(self):
        self.token = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'
        self.vk_api = VkApi(token=self.token).get_api()
        self.photo_info_dict = {}
        self.users_info_dict = {}
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
        except exceptions.ApiError:
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
        self.users_info_dict = self.vk_api.users.search(offset=self.offset, count=1000, age_from=age_from,
                                                        age_to=age_to, sex=sex, city=self.get_city_id(city),
                                                        status=status, fields='bdate')
        self.offset += 1000
        return self.users_info_dict['items']


if __name__ == '__main__':
    pass
