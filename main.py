from vk_module import VkUser
from DB import PostgresBase
from indep_func import get_birth_date


def make_tables():
    base = PostgresBase()
    base.create_table_user_vk()
    base.create_table_dating_user()
    base.create_table_user_photo()
    base.create_table_ignore_user()


def start_search():
    """
    :param age_from:    возраст, от.
    :param age_to:      возраст, до.
    :param sex:         пол                 (1 — женщина;
                                             2 — мужчина)
    :param city:        город (id или название)
    :param relation:    семейное положение (1 — не женат/не замужем;
                                            2 — есть друг/есть подруга;
                                            3 — помолвлен/помолвлена;
                                            4 — женат/замужем;
                                            5 — всё сложно;
                                            6 — в активном поиске;
                                            7 — влюблён/влюблена;
                                            8 — в гражданском браке;
                                            0 — не указано.
    :return: возвращает кортеж данных о пользователе совершившем поиск (id, возраст)
    и параметры поиска (возраст от и до, пол, город, семейное положение)
    """
    user_search_id = input('Введите user name или user id вконтакте\n')
    age_from = input('Введите возраст ОТ\n')
    age_to = input('Введите возраст ДО\n')
    sex = input('Введите пол 1 - ж, 2 - м\n')
    city = input('Введите город\n')
    relation = input('Введите семейное положение\n')
    user_info = VkUser().get_user_info(user_search_id)
    try:
        user_city = user_info['city']['title']
    except KeyError:
        user_city = 'Нет данных'
    try:
        birth_day = user_info['bdate']
        age = get_birth_date(birth_day)
    except KeyError:
        age = 'Нет данных'
    PostgresBase().add_user_vk(user_info['id'], user_info['first_name'], user_info['last_name'], age,
                   f'{age_from}-{age_to}', user_info['sex'], user_city)
    return user_info['id'], age_from, age_to, sex, city, relation


if __name__ == '__main__':
    # print(start_search.__doc__)
    # make_tables()
    a = start_search()
    # photos_count = int(input('Какое количество фотографий Вы хотите просмотреть?\n'))
    PostgresBase().decision_for_user(VkUser().search_dating_user(*a[1:]), a[0])
