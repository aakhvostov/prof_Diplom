from vk_module import VkUser
from indep_func import get_birth_date
from indep_func import engine


class PostgresBase:

    def __init__(self):
        self.connection = engine.connect()
        self.user_output_id = ""

    def create_table_user_vk(self):
        self.connection.execute("""CREATE TABLE if not exists User_vk (
                            User_id integer primary key,
                            User_firstname varchar(40) not NULL,
                            User_lastname varchar(40) not NULL,
                            User_age varchar(15) not NULL,
                            Search_range varchar(10) not NULL,
                            Sex integer not NULL,
                            User_city varchar(40));""")

    def add_user_vk(self, vk_id, firstname, lastname, age, range_search, sex, city):
        """
        Добавляет человека в базу таблицу user_vk
        """
        self.connection.execute("INSERT INTO user_vk (user_id, user_firstname, user_lastname, user_age, "
                                "search_range, sex, user_city) VALUES (%s, %s, %s, %s, %s, %s, %s);",
                                (vk_id, firstname, lastname, age, range_search, sex, city))
        print(f'юзер {vk_id}, {firstname} добавлен в user список')

    def create_table_dating_user(self):
        self.connection.execute("""CREATE TABLE if not exists Dating_user (
                            Dating_id serial primary key,
                            Dating_user_id integer not NULL,
                            User_firstname varchar(40) not NULL,
                            User_lastname varchar(40) not NULL,
                            User_age varchar(15) not NULL,
                            User_id integer references User_vk(User_id));""")

    def add_dating_user_vk(self, vk_id, firstname, lastname, age, user_id):
        """
        Добавляет человека в таблицу dating_user
        """
        self.connection.execute("INSERT INTO dating_user (dating_user_id, user_firstname, user_lastname, user_age, "
                                "user_id) VALUES (%s, %s, %s, %s, %s);",
                                (vk_id, firstname, lastname, age, user_id))
        print(f'юзер {vk_id}, {firstname} добавлен в лайк список')

    def create_table_ignore_user(self):
        self.connection.execute("CREATE TABLE if not exists Ignore_user (User_ignore_id integer not NULL, "
                                "User_id integer not NULL references User_vk(User_id), "
                                "constraint iu primary key (User_ignore_id, User_id));")

    def add_ignore_user(self, ignore_id, vk_id):
        """
        Добавляет человека в таблицу ignore_user
        """
        self.connection.execute("INSERT INTO Ignore_user (User_ignore_id, User_id) VALUES (%s, %s);",
                                (ignore_id, vk_id))
        print(f'юзер {vk_id} добавлен в игнор список')

    def create_table_user_photo(self):
        self.connection.execute("""CREATE TABLE if not exists User_photo (
                            User_photo_id serial primary key,
                            Photo_link text not NULL,
                            Photo_likes integer not NULL,
                            Dating_id integer references Dating_user(Dating_id));""")

    def add_user_photo(self, links_likes, vk_id, dating_vk_id):
        dating_id = self.connection.execute("SELECT dating_id FROM dating_user WHERE "
                                            "dating_user_id = %s and user_id = %s;", (dating_vk_id, vk_id)).fetchone()
        for like, link in links_likes.items():
            self.connection.execute("INSERT INTO User_photo (Photo_link, Photo_likes, Dating_id) "
                                    "VALUES (%s, %s, %s);", (link, like, dating_id[0]))
            print(f'фото {like} добавлено в список')

    def create_table_skipped_user(self):
        self.connection.execute("CREATE TABLE if not exists Skipped_user ("
                                "Skipped_id integer not NULL, "
                                "User_id integer not NULL references User_vk(User_id), "
                                "constraint su primary key (Skipped_id, User_id));")

    def add_skipped_user(self, skipped_id, vk_id):
        """
        Добавляет человека в таблицу ignore_user
        """
        self.connection.execute("INSERT INTO Skipped_user (Skipped_id, User_id) VALUES (%s, %s);",
                                (skipped_id, vk_id))
        print(f'юзер {vk_id} добавлен в список для пропусков')

    def drop_tables(self, tables_name):
        for table in tables_name.split(","):
            try:
                self.connection.execute(f"DROP TABLE {table} CASCADE;")
                print(f'таблица {table} удалена')
            except NameError:
                print(f'Таблицы "{tables_name}" не найдено')
            except AttributeError:
                print('Необходимо передать название таблицы')
            except:
                print('Не верные данные или таблиц больше нет')

    def is_inside_ignore_dating_skipped(self, vk_id, vk_search_id):
        """
        Проверяет юзера на наличие его в таблицах лайков и игноров
        Если совпадение есть, то Юзер пропускается в выдаче
        :param vk_dating_id: Юзер id, которого нашли
        :param vk_search_id: Юзер id, кто искал
        :return: True или False
        """
        Flag = False
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
        for skiped in skipped_list:
            if vk_id == skiped[0] and vk_search_id == skiped[1]:
                print(f'найдено совпадение {vk_id} в Skipped_user')
                Flag = True
        return Flag

    def is_inside_user_vk(self, vk_search_id, vk_search_range):
        """
        Проверяет юзера на наличие его в таблицах лайков и игноров
        Если совпадение есть, то Юзер пропускается в выдаче
        :param vk_dating_id: Юзер id, которого нашли
        :param vk_search_id: Юзер id, кто искал
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

    def decision_for_user(self, users_dict, search_id, photos_count=3):
        """
        Проходится по списку словарей и по одному ждем от пользователя решения куда добавить человека:
        в лайк лист
        в игнор лист
        пропустить человека - с добавлениев в Скип лист, чтобы они не выходили в дальнейшем поиске
        :param photos_count: количество фотографий для превью
        :param search_id: vk_id пользователя для которого ведется поиск
        :param users_dict: словарь со списком людей, полученных по результатам поиска
        :return: решение куда добавть человека
        """
        print(f'Всего найдено {len(users_dict)} человек\nПриступим к просмотру ;)')
        for person in users_dict:
            first_name = person['first_name']
            last_name = person['last_name']
            user_id = person['id']
            age = get_birth_date(person['bdate'])
            if not self.is_inside_ignore_dating_skipped(user_id, search_id):
                link = VkUser().get_users_best_photos(user_id, photos_count)
                print(f'{first_name} {last_name} - {link}\n')
                decision = input('Нравится этот человек?\nyes - добавить в список понравившихся\n'
                                 'no - пропустить\nignore - добавить в черный список\nq - выход\n')
                if decision.lower() == 'yes':
                    self.add_dating_user_vk(user_id, first_name, last_name, age, search_id)
                    self.add_user_photo(VkUser().get_users_best_photos(user_id), search_id, user_id)
                    continue
                elif decision.lower() == 'no':
                    self.add_skipped_user(user_id, search_id)
                    continue
                elif decision.lower() == 'ignore':
                    self.add_ignore_user(user_id, search_id)
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
    # PostgresBase().add_user_photo({1: "qwe", 2: "rte", 3: "gdfg"}, 13924278, 39377403)
    # PostgresBase().drop_tables('user_vk,ignore_user,dating_user,user_photo,skipped_user')
    # print(PostgresBase().output_users(2, 159555338))
    # print(PostgresBase().is_inside_user_vk(13924278, '30-31'))
    pass

