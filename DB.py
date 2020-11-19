from sqlalchemy import exc
from vk_module import VkUser
from indep_func import get_age
from indep_func import engine
from sql_orm import DatingUser, IgnoreUser, SkippedUser, UserPhoto


class PostgresBase:

    def __init__(self):
        self.connection = engine.connect()
        self.user_output_id = ""

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

    def output_users(self, output_table, search_user):          # не используется пока что
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
        return [person[0] for person in users_list]             #

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
                decision = int(input('Нравится этот человек?\n'
                                     '- "1" - добавить в список понравившихся\n'
                                     '- "2" - пропустить и добавить в список пропусков\n'
                                     '- "3" - добавить в черный список\n'
                                     '- "911" - выход\n'))
                if decision == 1:
                    DatingUser().add_dating_user(user_id, first_name, last_name, age, search_id, search_range)
                    UserPhoto().add_user_photo(VkUser().get_users_best_photos(user_id), search_id, user_id)
                    continue
                elif decision == 2:
                    SkippedUser().add_skipped_user(user_id, search_id, search_range)
                    continue
                elif decision == 3:
                    IgnoreUser().add_ignore_user(user_id, search_id, search_range)
                    continue
                elif decision == 911:
                    print('До свидания!')
                    break
                else:
                    print('Ввели что-то не то')
                    break
            else:
                continue


if __name__ == '__main__':
    # PostgresBase().add_user_photo({1: "qwe", 2: "rte", 3: ""}, 13924278, 39377403)
    PostgresBase().drop_tables('user_vk,ignore_user,dating_user,user_photo,skipped_user')
    # print(PostgresBase().output_users(2, 159555338))
    # print(PostgresBase().is_inside_user_vk(13924278, '30-31'))
    # PostgresBase().drop_tables('wer')
    pass
