from vk_module import VkUser
from DB import PostgresBase
from indep_func import get_age, session
from sql_orm import UserVk, UserPhoto, DatingUser, SkippedUser, IgnoreUser, ORMFunctions


pg_base = PostgresBase()


def make_tables():
    pg_base.create_table_user_vk()
    pg_base.create_table_dating_user()
    pg_base.create_table_user_photo()
    pg_base.create_table_ignore_user()
    pg_base.create_table_skipped_user()


def get_start_data():
    """
    age_from:    возраст, от.
    age_to:      возраст, до.
    sex:         пол                 (1 — женщина;
                                             2 — мужчина)
    city:        город (id или название)
    status:    семейное положение (1 — не женат/не замужем;
                                            2 — есть друг/есть подруга;
                                            3 — помолвлен/помолвлена;
                                            4 — женат/замужем;
                                            5 — всё сложно;
                                            6 — в активном поиске;
                                            7 — влюблён/влюблена;
                                            8 — в гражданском браке;
                                            0 — не указано.
    :return: возвращает кортеж данных о пользователе совершившем поиск (id, возраст, диапозон поиска)
    и параметры поиска (возраст от и до, пол, город, семейное положение)
    """
    user_search_id = input('Введите user name или user id вконтакте\n')
    age_from = input('Введите возраст ОТ\n')
    age_to = input('Введите возраст ДО\n')
    sex = input('Введите пол 1 - ж, 2 - м\n')
    city = input('Введите город\n')
    status = input('Введите семейное положение\n1 — не женат/не замужем; 2 — есть друг/есть подруга; '
                     '3 — помолвлен/помолвлена; 4 — женат/замужем; 5 — всё сложно; 6 — в активном поиске; '
                     '7 — влюблён/влюблена; 8 — в гражданском браке; 0 — не указано\n')
    user_info = VkUser().get_user_info(user_search_id)
    search_range = f'{age_from}-{age_to}'
    city_id = VkUser().get_city_id(city)
    # Проверка исключение - если у Юзера VK в профиле нет данных о Городе или Дате рождения
    try:
        age = user_info['bdate']
        age = get_age(age)
    except KeyError:
        age = 'нет данных'
    # проверка наличия запроса User_id - Search_range в базе данных
    id_with_range = ORMFunctions(session).is_id_and_range_inside_user_vk(user_info['id'], search_range)
    # Если есть совпадение ПОЛНОЕ - по Id + Range - спросить:
    # продолжить поиск и добавлять людей по этому запросу или прервать работу
    if id_with_range:
        result = input(f"Запрос User_id {user_info['id']}, {user_info['last_name']} {user_info['first_name']} "
                       f"и диапозон поиска {search_range} уже есть в таблице\n"
                       f"Желаете продолжить поиск по этой комбинации?\n"
                       f"Yes/No\n")
        if result.lower() == 'yes':
            return age_from, age_to, sex, city_id, status, user_info['id'], search_range
        else:
            raise SystemExit('Всего хорошего!')
    # Если нет ПОЛНОГО совпадения по Id + Range - добавить в базу новую запись и вести поиск
    else:
        city_name = VkUser().get_city_name(city_id)
        pg_base.add_user_vk(user_info['id'], user_info['first_name'], user_info['last_name'], age,
                            search_range, user_info['sex'], city_name[0]['title'])
        return age_from, age_to, sex, city_id, status, user_info['id'], search_range


# def main():  # Тут будет вся логика общения с пользователем
#     print('Добро пожаловать в сервис по подбору своей второй половинки\n')
#     while True:
#         requests_dict = {
#             'i': start_search,
#             's': pg_base.decision_for_user(VkUser().search_dating_user(*search_details[:5]), *search_details[5:]),
#             'e': exit,
#         }
#         user_input = input('Выберите действие:\ni - ввод начальных данных\ns - начать поиск\ne - выход\n')
#         requests_dict[user_input]()
#     search_details = start_search()
#     pg_base.decision_for_user(VkUser().search_dating_user(*search_details[:5]), *search_details[5:])


if __name__ == '__main__':
    # main()
    # data = get_start_data()
    # print(data)
    pg_base.decision_for_user(VkUser().search_dating_user('32', '39', '1', 60, '6'), 13924278, '32-39')   # проверка отсутствия фоток в профиле

    # print(start_search.__doc__)
    # make_tables()         # создаем все таблицы
    # print(ORMFunctions(session).is_id_inside_user_vk(13924278))
    # print(ORMFunctions(session).id_and_range_inside_user_vk(1, '30-32'))
    # user_in_table = session.query(VkUser).filter
    # print(ignore_ids)
    #
    #
    # Что еще необхоимо сделать:

# Доделать проверку по Id + Range как primary key - Логика такая, что у одного и того же User_id в таблице User_vk  DONE
# может быть разный диапозон поиска, и как следствие разные люди будут выходить в результатах!
# Поэтому хочу сделать User_id + Range как primary key и добавлять и выводить данные по этим 2м полям

# Вывод всех понравившихся людей - это будет в 'sql_orm' блоке через UserVk.dating_users

# Удалить из лайк списка человека - скорее всего тоже в 'sql_orm' сделаю, хотя можно и в 'DB' через запрос SQL

# Реализовать тесты на базовую функциональность
    pass
