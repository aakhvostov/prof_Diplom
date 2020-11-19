from sqlalchemy import exc
from vk_module import VkUser
from indep_func import get_age
from indep_func import engine


class PostgresBase:

    def __init__(self):
        self.connection = engine.connect()
        self.user_output_id = ""

    def create_table_user_vk(self):
        self.connection.execute("""CREATE TABLE if not exists User_vk (
                                    User_id integer,
                                    User_firstname varchar(40),
                                    User_lastname varchar(40),
                                    User_age varchar(15),
                                    Search_range varchar(15),
                                    Sex integer,
                                    User_city varchar(40),
                                    constraint id_ran primary key (User_id, Search_range));""")

    def create_table_dating_user(self):
        self.connection.execute("""CREATE TABLE if not exists Dating_user (
                                    Dating_id serial primary key,
                                    Dating_user_id integer,
                                    User_firstname varchar(40),
                                    User_lastname varchar(40),
                                    User_age varchar(15),
                                    User_id integer,
                                    User_id_range varchar(15),
                                    constraint u_vk_dat foreign key (User_id, User_id_range) 
                                        references User_vk(User_id, Search_range)
                                    );""")

    def create_table_user_photo(self):
        self.connection.execute("""CREATE TABLE if not exists User_photo (
                                    User_photo_id serial primary key,
                                    Photo_link text,
                                    Photo_likes integer,
                                    Dating_id integer references Dating_user(Dating_id));""")

    def create_table_ignore_user(self):
        self.connection.execute("""CREATE TABLE if not exists Ignore_user (
                                    User_ignore_id integer, 
                                    User_id integer, 
                                    User_id_range varchar(15), 
                                    constraint ing_vk primary key (User_ignore_id, User_id), 
                                    constraint u_vk_ign foreign key (User_id, User_id_range) 
                                        references User_vk(User_id, Search_range)
                                    );""")

    def create_table_skipped_user(self):
        self.connection.execute("""CREATE TABLE if not exists Skipped_user (
                                    Skipped_id integer, 
                                    User_id integer, 
                                    User_id_range varchar(15),                                     
                                    constraint skip_u_vk primary key (Skipped_id, User_id),
                                    constraint u_vk_skip foreign key (User_id, User_id_range) 
                                        references User_vk(User_id, Search_range)
                                    );""")

    def drop_tables(self, tables_name):
        for table in tables_name.split(","):
            try:
                self.connection.execute(f"DROP TABLE {table} CASCADE;")
                print(f'таблица {table} удалена')
            except NameError:
                print(f'Таблицы "{tables_name}" не найдено')
            except AttributeError:
                print('Необходимо передать название таблицы')
            except exc.ProgrammingError:
                print('Не верные данные или таблиц больше нет')

    def add_user_vk(self, vk_id, firstname, lastname, age, range_search, sex, city):
        """
        Добавляет человека в базу таблицу user_vk
        """
        self.connection.execute("INSERT INTO user_vk (user_id, user_firstname, user_lastname, user_age, "
                                "search_range, sex, user_city) VALUES (%s, %s, %s, %s, %s, %s, %s);",
                                (vk_id, firstname, lastname, age, range_search, sex, city))
        print(f'юзер {vk_id}, {firstname} добавлен в user список')

    def add_dating_user_vk(self, vk_id, firstname, lastname, age, user_id, search_range):
        """
        Добавляет человека в таблицу dating_user
        """
        self.connection.execute("INSERT INTO dating_user (dating_user_id, user_firstname, user_lastname, user_age, "
                                "user_id, User_id_range) VALUES (%s, %s, %s, %s, %s, %s);",
                                (vk_id, firstname, lastname, age, user_id, search_range))
        print(f'юзер {vk_id}, {firstname} добавлен в лайк список')

    def add_user_photo(self, links_likes, vk_id, dating_vk_id):
        dating_id = self.connection.execute("SELECT dating_id FROM dating_user WHERE "
                                            "dating_user_id = %s and user_id = %s;", (dating_vk_id, vk_id)).fetchone()
        for like, link in links_likes.items():
            self.connection.execute("INSERT INTO User_photo (Photo_link, Photo_likes, Dating_id) "
                                    "VALUES (%s, %s, %s);", (link, like, dating_id[0]))
            print(f'фото {like} добавлено в список')

    def add_ignore_user(self, ignore_id, vk_id, search_range):
        """
        Добавляет человека в таблицу ignore_user
        """
        self.connection.execute("INSERT INTO Ignore_user (User_ignore_id, User_id, User_id_range) VALUES (%s, %s, %s);",
                                (ignore_id, vk_id, search_range))
        print(f'юзер {ignore_id} добавлен в игнор список')

    def add_skipped_user(self, skipped_id, vk_id, search_range):
        """
        Добавляет человека в таблицу ignore_user
        """
        self.connection.execute("INSERT INTO Skipped_user (Skipped_id, User_id, User_id_range) VALUES (%s, %s, %s);",
                                (skipped_id, vk_id, search_range))
        print(f'юзер {skipped_id} добавлен в список для пропусков')

    def is_inside_ignore_dating_skipped(self, vk_id, vk_search_id):
        """
        Проверяет юзера на наличие его в таблицах лайков и игноров
        Если совпадение есть, то Юзер пропускается в выдаче
        :param vk_id: Юзер id, которого нашли
        :param vk_search_id: Юзер id, кто искал
        :return: True или False
        """
        Flag: bool = False
        dating_list = self.connection.execute("SELECT dating_user_id, user_id FROM dating_user").fetchall()
        ignore_list = self.connection.execute("SELECT user_ignore_id, user_id FROM ignore_user").fetchall()
        skipped_list = self.connection.execute("SELECT skipped_id, user_id FROM skipped_user").fetchall()
        for dating in dating_list:
            if vk_id == dating[0] and vk_search_id == dating[1]:
                print(f'найдено совпадение {vk_id} в Dating_user')
                Flag = True
        for ignore in ignore_list:
            if vk_id == ignore[0] and vk_search_id == ignore[1]:
                print(f'найдено совпадение {vk_id} в Ignore_user')
                Flag = True
        for skipped in skipped_list:
            if vk_id == skipped[0] and vk_search_id == skipped[1]:
                print(f'найдено совпадение {vk_id} в Skipped_user')
                Flag = True
        return Flag

    def is_id_range_inside_user_vk(self, vk_search_id, vk_search_range):
        """
        Проверяет юзера на наличие его в таблицах лайков и игноров
        Если совпадение есть, то Юзер пропускается в выдаче
        :param vk_search_id: Юзер id, кто искал
        :param vk_search_range: Диапозон поиска для Юзер id
        :return: True или False
        """
        vk_id = self.connection.execute("SELECT user_id, search_range FROM user_vk").fetchone()
        if vk_search_id == vk_id[0] and vk_search_range == vk_id[1]:
            return True
        return False

    def output_users(self, output_table, search_user):
        """
        Выводит всех пользователей добавленных в лайк или игнор список
        среди данных юзера ведущего поиск
        :param search_user:     Id юзера ведущего поиск
        :param output_table:    1 - dating_user
                                2 - ignore_user
        :return: список id юзеров
        """
        if output_table == 'dating_user' or output_table == 1:
            self.user_output_id = 'Dating_user_id'
            output_table = 'dating_user'
        elif output_table == 'ignore_user' or output_table == 2:
            self.user_output_id = 'User_ignore_id'
            output_table = 'ignore_user'
        users_list = self.connection.execute("SELECT %s FROM %s WHERE user_id = %s;",
                                             (self.user_output_id, output_table, search_user)).fetchall()
        return [person[0] for person in users_list]

    def decision_for_user(self, users_dict, search_id, search_range):
        """
        Проходится по списку словарей и по одному ждем от пользователя решения куда добавить человека:
        в лайк лист
        в игнор лист
        пропустить человека - с добавлениев в Скип лист, чтобы они не выходили в дальнейшем поиске
        :param search_id: vk_id пользователя для которого ведется поиск
        :param search_range: диапозон поиска людей пользователя для которого ведется поиск
        :param users_dict: словарь со списком людей, полученных по результатам поиска
        :return: решение куда добавть человека
        """
        print(f'Всего найдено {len(users_dict)} человек\nПриступим к просмотру ;)')
        for person in users_dict:
            first_name = person['first_name']
            last_name = person['last_name']
            user_id = person['id']
            try:
                age = person['bdate']
                age = get_age(age)
            except KeyError:
                age = 'нет данных'
            if not self.is_inside_ignore_dating_skipped(user_id, search_id):
                link = VkUser().get_users_best_photos(user_id)
                print(f'{first_name} {last_name} - {link}\n')
                decision = input('Нравится этот человек?\n\U0001F497 - "yes" - добавить в список понравившихся\n'
                                 '\U0000267B - "no" - пропустить\n\U0000274C - "ignore" - добавить в черный список\n'
                                 '\U000024BA\U000024CD\U000024BE\U000024C9 - "q" - выход\n')
                if decision.lower() == 'yes':
                    self.add_dating_user_vk(user_id, first_name, last_name, age, search_id, search_range)
                    self.add_user_photo(VkUser().get_users_best_photos(user_id), search_id, user_id)
                    continue
                elif decision.lower() == 'no':
                    self.add_skipped_user(user_id, search_id, search_range)
                    continue
                elif decision.lower() == 'ignore':
                    self.add_ignore_user(user_id, search_id, search_range)
                    continue
                elif decision.lower() == 'q':
                    print('До свидания!')
                    break
                else:
                    print('Ввели что-то не то')
                    break
            else:
                continue


if __name__ == '__main__':
    # PostgresBase().add_user_photo({1: "qwe", 2: "rte", 3: ""}, 13924278, 39377403)
    # PostgresBase().drop_tables('user_vk,ignore_user,dating_user,user_photo,skipped_user')
    # print(PostgresBase().output_users(2, 159555338))
    # print(PostgresBase().is_inside_user_vk(13924278, '30-31'))
    # PostgresBase().drop_tables('wer')
    pass
