import json
import re
from random import randrange
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api import VkApi, exceptions
from sql_orm import DatingUser, UserPhoto, IgnoreUser, SkippedUser, ORMFunctions
from bot import keyboards, get_age


class VkUser:

    def __init__(self):
        self.token = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'
        self.vk_api = VkApi(token=self.token).get_api()
        self.photo_info_dict = {}
        self.users_info_dict = {}
        self.offset = 0

    def get_user_info(self, user_id):
        """
        :param user_id: принимает User ID или Короткое название аккаунта VK
        :return: словарь со информацией о Юзере (Имя, Фамилия, Id, пол, день рождеждения, город(id, название)
        """
        user = self.vk_api.users.get(user_ids=user_id, fields='first_name, last_name, sex, relation, bdate')
        return user[0]

    def get_user_data(self, user_id):
        user_info = self.get_user_info(user_id)
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
        return user_firstname, user_lastname, user_age, user_sex, user_city

    def get_users_best_photos(self, user_id, count_photos=3):
        """
        Получаем словарь с ТОП фотографиями из профиля
        :param count_photos: количество фотографий с максимальными лайками
        :param user_id: принимает User ID или Короткое название аккаунта VK
        :return: словарь с ТОП 3мя фотографиями (ссылки (значения))
        из профиля аккаунта с их лайками (в качетстве имени (ключ))
        """
        tmp = {}
        try:
            photos_info = self.vk_api.photos.get(owner_id=self.get_user_info(user_id)['id'], album_id='profile',
                                                 extended=1, count=1000, photo_sizes=0)
            # создаем словарь со всеми лайками и ссылками на фото
            for elem in photos_info['items']:
                attachment_id = elem['id']
                photo_url = elem['sizes'][-1]['url']
                photos_likes = elem['likes']['count']
                tmp[photos_likes] = (attachment_id, photo_url)
            # новый словарь с необходимым количеством максимальных лайков
            try:
                self.photo_info_dict = {k: v for k, v in tmp.items() if
                                        k > sorted(tmp.keys(), reverse=True)[count_photos]}
                return self.photo_info_dict
            except IndexError:
                if len(tmp) == 0:
                    self.photo_info_dict[0] = 'нет фотографий в профиле'
                    return self.photo_info_dict
                else:
                    self.photo_info_dict = tmp
                    return self.photo_info_dict
        except exceptions.ApiError:
            self.photo_info_dict[0] = 'приватный профиль - фоток нет'
            return self.photo_info_dict

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


orm = ORMFunctions()
vk_server = VkUser()


class Server:

    def __init__(self, api_token, server_name: str = "Empty"):
        self.server_name = server_name
        self.vk = VkApi(token=api_token)
        self.long_poll = VkLongPoll(self.vk)
        self.vk_api = self.vk.get_api()
        self.event = None
        self.current_user_id = None
        # словарь подобранных людей
        self.users_info_dict = {}
        # счетчик просмотра подобранных людей
        self.count = 0
        # текущее состояние пользователя
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

    def write_msg_attachment(self, message, attachment, keyboard):
        self.vk.method('messages.send', {'user_id': self.event.user_id,
                                         'message': message,
                                         'random_id': randrange(10 ** 7),
                                         'keyboard': json.dumps(keyboards[keyboard], ensure_ascii=False),
                                         'attachment': attachment})

    def hello_state(self, objects):
        if self.event.text == "выход" or self.event.text == "выйти":
            return False
        objects[0].state = "Initial"
        self.write_msg_keyboard('Выберите действие:', 'greeting')

    def initial_state(self, objects):
        if self.event.text == "начать поиск":
            objects[0].state = "City"
            self.write_msg('Введите город')
        elif self.event.text == "показать/удалить людей":
            orm.get_dating_list(self.event.user_id)
            orm.get_ignore_list(self.event.user_id)
            self.write_msg_keyboard('Привет! Выбери действие', 'like_ignore')
        elif self.event.text == "лайк":
            orm.dating_count = 0
            objects[0].state = "Like"
            self.write_msg_keyboard(f'У вас найдено - {len(orm.dating_list)} человек. Приступим?', 'filter_msg')
        elif self.event.text == "игнор":
            orm.ignore_count = 0
            objects[0].state = "Ignore"
            self.write_msg_keyboard(f'У вас найдено - {len(orm.ignore_list)} человек. Приступим?', 'filter_msg')
        elif self.event.text == "выйти":
            self.write_msg_keyboard('Выбери действие', 'greeting')
        else:
            self.write_msg_keyboard('Выбери действие', 'greeting')

    def like_state(self, objects):
        if self.event.text == "следующий":
            orm.dating_count += 1
            if orm.show_dating_user():
                dat_name, dat_age, dat_id, dat_attach = orm.show_dating_user()
                self.write_msg_attachment(f'{dat_name}\nВозраст - {dat_age}\nhttps://vk.com/id{dat_id}',
                                          f'photo{dat_id}_{dat_attach}', 'show_users')
            else:
                objects[0].state = "Initial"
                self.write_msg_keyboard('Список закончился. Выберите действие', 'greeting')

        elif self.event.text == "удалить":
            orm.dating_list[orm.dating_count].remove_dating_user()
            orm.dating_count += 1
            if orm.show_dating_user():
                dat_name, dat_age, dat_id, dat_attach = orm.show_dating_user()
                self.write_msg_attachment(f'{dat_name}\nВозраст - {dat_age}\nhttps://vk.com/id{dat_id}',
                                          f'photo{dat_id}_{dat_attach}', 'show_users')
            else:
                objects[0].state = "Initial"
                self.write_msg_keyboard('Список закончился. Выберите действие', 'greeting')
        elif self.event.text == "выйти":
            self.write_msg_keyboard('Выбери действие', 'greeting')
            objects[0].state = "Initial"
        else:
            if orm.show_dating_user():
                dat_name, dat_age, dat_id, dat_attach = orm.show_dating_user()
                self.write_msg_attachment(f'{dat_name}\nВозраст - {dat_age}\nhttps://vk.com/id{dat_id}',
                                          f'photo{dat_id}_{dat_attach}', 'show_users')
            else:
                objects[0].state = "Initial"
                self.write_msg_keyboard('Лайк список пуст. Выберите действие', 'greeting')

    def ignore_state(self, objects):
        if self.event.text == "следующий":
            orm.ignore_count += 1
            if orm.show_ignore_user():
                self.write_msg_keyboard(f'https://vk.com/id{orm.show_ignore_user()}', 'show_users')
            else:
                objects[0].state = "Initial"
                self.write_msg_keyboard('Список закончился. Выберите действие', 'greeting')
        elif self.event.text == "удалить":
            orm.ignore_list[orm.ignore_count].remove_ignore_user()
            orm.ignore_count += 1
            if orm.show_ignore_user():
                self.write_msg_keyboard(f'https://vk.com/id{orm.show_ignore_user()}', 'show_users')
            else:
                objects[0].state = "Initial"
                self.write_msg_keyboard('Список закончился. Выберите действие', 'greeting')
        elif self.event.text == "выйти":
            self.write_msg_keyboard('Выбери действие', 'greeting')
            objects[0].state = "Initial"
        else:
            if orm.show_ignore_user():
                self.write_msg_keyboard(f'https://vk.com/id{orm.show_ignore_user()}', 'show_users')
            else:
                objects[0].state = "Initial"
                self.write_msg_keyboard('Игнор список пуст. Выберите действие', 'greeting')

    def city_state(self, objects):
        if re.findall(r'[а-яА-яёЁ0-9]+', self.event.text):
            try:
                city_name = VkUser().get_city_name(VkUser().get_city_id(self.event.text))[0]['title']
                objects[0].state = "Sex"
                objects[1].search_city = city_name
                self.write_msg('Введите пол:\n1 - женщина\n2 - мужчина')
            except IndexError:
                self.write_msg('Вы ввели неверную информацию\nВведите город повторно')
        else:
            self.write_msg('Вы ввели неверную информацию\nВведите город повторно')

    def sex_state(self, objects):
        if self.event.text == '1' or self.event.text == '2':
            try:
                sex_value = int(self.event.text)
                objects[0].state = "Relation"
                objects[1].search_sex = sex_value
                self.write_msg('Введите семейное положение\n1 — не женат/не замужем\n2 — есть друг/есть подруга\n'
                               '3 — помолвлен/помолвлена\n4 — женат/замужем\n5 — всё сложно\n6 — в активном поиске\n'
                               '7 — влюблён/влюблена\n8 — в гражданском браке\n0 — не указано\n')
            except ValueError:
                self.write_msg('Вы ввели неверную информацию\nВведите пол повторно\n1 - женщина\n2 - мужчина')
        else:
            self.write_msg('Вы ввели неверную информацию\nВведите пол повторно\n1 - женщина\n2 - мужчина')

    def relation_state(self, objects):
        if re.findall(r'[0-8]', self.event.text):
            try:
                status = int(self.event.text)
                objects[0].state = "Range"
                objects[1].search_relation = status
                self.write_msg('Введите диапозон поиска ОТ и ДО (через пробел или -)')
            except ValueError:
                self.write_msg('Вы ввели неверную информацию\nВведите статус повторно\n1 — не женат/не замужем\n'
                               '2 — есть друг/есть подруга\n3 — помолвлен/помолвлена\n4 — женат/замужем\n5 — всё '
                               'сложно\n6 — в активном поиске\n7 — влюблён/влюблена\n8 — в гражданском браке\n'
                               '0 — не указано\n')
        else:
            self.write_msg('Вы ввели неверную информацию\nВведите статус повторно\n1 — не женат/не замужем\n'
                           '2 — есть друг/есть подруга\n3 — помолвлен/помолвлена\n4 — женат/замужем\n5 — всё '
                           'сложно\n6 — в активном поиске\n7 — влюблён/влюблена\n8 — в гражданском браке\n'
                           '0 — не указано\n')

    def range_state(self, objects):
        try:
            age_pattern = re.compile(r'(\d\d?)[ -]+(\d\d?)')
            age_from = int(age_pattern.sub(r"\1", self.event.text))
            age_to = int(age_pattern.sub(r"\2", self.event.text))
            if age_to - age_from < 0:
                self.write_msg('Вы ввели неверную информацию\nВведите диапозон поиска ОТ и ДО (через пробел или -)')
                return
            objects[0].state = "Decision"
            objects[1].search_from = age_from
            objects[1].search_to = age_to
            age_from = objects[1].search_from
            age_to = objects[1].search_to
            sex = objects[1].search_sex
            city_name = objects[1].search_city
            status = objects[1].search_relation
            vk_server.search_dating_user(age_from, age_to, sex, city_name, status)
            user_founded_id, first_name, last_name, age, attachment_list = self.get_founded_user_info()
            while user_founded_id is None:
                user_founded_id, first_name, last_name, age, attachment_list = self.get_founded_user_info()
            if len(attachment_list) >= 1:
                self.write_msg_attachment(f'{first_name} {last_name}', attachment_list, 'decision')
            else:
                self.write_msg(f'{first_name} {last_name} - {attachment_list}\n')
                self.write_msg_keyboard('Выберите действие', 'decision')
        except ValueError:
            self.write_msg('Вы ввели неверную информацию\nВведите диапозон поиска ОТ и ДО (через пробел или -)')

    def get_founded_user_info(self):
        person = vk_server.users_info_dict['items'][self.count]
        user_dating_id = person['id']
        # проверка наличия найденного Id в таблицах
        if orm.is_viewed(user_dating_id, self.event.user_id):
            self.count += 1
            return None, None, None, None, None
        first_name = person['first_name']
        last_name = person['last_name']
        attachment_list = []
        try:
            age = person['bdate']
            age = get_age(age)
        except KeyError:
            age = 'нет данных'
        link_dict = VkUser().get_users_best_photos(user_dating_id)
        try:
            for photo_links in link_dict.values():
                attachment = photo_links[0]
                attachment_list.append(f'photo{user_dating_id}_{attachment}')
            attachment_string = ",".join(attachment_list)
            return user_dating_id, first_name, last_name, age, attachment_string
        except AttributeError:
            link_dict = 'нет фотографий'
            return user_dating_id, first_name, last_name, age, link_dict

    def decision_state(self, objects):
        user_founded_id, first_name, last_name, age, attachment_list = self.get_founded_user_info()
        if self.event.text == "выход":
            objects[0].state = "Initial"
            self.write_msg_keyboard('Выберите действие:', 'greeting')
            return
        elif self.event.text == "лайк":
            DatingUser().add_dating_user(user_founded_id, first_name, last_name, age, self.event.user_id)
            UserPhoto().add_user_photo(VkUser().get_users_best_photos(user_founded_id), user_founded_id,
                                       self.event.user_id)
            self.count += 1
            user_founded_id, first_name, last_name, age, attachment_list = self.get_founded_user_info()
            if len(attachment_list) >= 1:
                self.write_msg_attachment(f'{first_name} {last_name}', attachment_list, 'decision')
            else:
                self.write_msg(f'{first_name} {last_name} - {attachment_list}\n')
                self.write_msg_keyboard('Выберите действие', 'decision')
        elif self.event.text == "крестик":
            IgnoreUser().add_ignore_user(user_founded_id, self.event.user_id)
            self.count += 1
            user_founded_id, first_name, last_name, age, attachment_list = self.get_founded_user_info()
            if len(attachment_list) >= 1:
                self.write_msg_attachment(f'{first_name} {last_name}', attachment_list, 'decision')
            else:
                self.write_msg(f'{first_name} {last_name} - {attachment_list}\n')
                self.write_msg_keyboard('Выберите действие', 'decision')
        elif self.event.text == "пропуск":
            SkippedUser().add_skipped_user(user_founded_id, self.event.user_id)
            self.count += 1
            user_founded_id, first_name, last_name, age, attachment_list = self.get_founded_user_info()
            if len(attachment_list) >= 1:
                self.write_msg_attachment(f'{first_name} {last_name}', attachment_list, 'decision')
            else:
                self.write_msg(f'{first_name} {last_name} - {attachment_list}\n')
                self.write_msg_keyboard('Выберите действие', 'decision')
        else:
            return

    def use_state(self, state_name):
        self.states = {
            "Hello": self.hello_state,
            "Initial": self.initial_state,
            "City": self.city_state,
            "Sex": self.sex_state,
            "Relation": self.relation_state,
            "Range": self.range_state,
            "Decision": self.decision_state,
            "Like": self.like_state,
            "Ignore": self.ignore_state
        }
        return self.states[state_name]

    def start(self, ):
        for event in self.long_poll.listen():
            self.event = event
            if self.event.type != VkEventType.MESSAGE_NEW:
                continue
            if not self.event.to_me:
                continue
            if self.event.user_id != self.current_user_id:
                self.current_user_id = self.event.user_id
            else:
                pass
            if orm.looking_for_user_vk(self.event.user_id) is None:
                objects = orm.add_objects(self.event.user_id, VkUser().get_user_data(self.event.user_id))
            else:
                objects = orm.looking_for_user_vk(self.event.user_id)
            if self.event.text == '/start':
                objects[0].state = "Initial"
                self.write_msg_keyboard('Выберите действие:', 'greeting')
            elif self.event.text == '/test':
                pass
            else:
                ans = self.use_state(objects[0].state)(objects)
                # при нажатии Выход ans возвращает False и выходим из программы
                if ans or ans is None:
                    continue
                else:
                    break


if __name__ == '__main__':
    pass
