from vk_module import VkUser
from DB import PostgresBase
from indep_func import get_birth_date


def make_tables():
    base = PostgresBase()
    base.create_table_user_vk()
    base.create_table_dating_user()
    base.create_table_user_photo()
    base.create_table_ignore_user()
    base.create_table_skipped_user()


def main():         # Тут будет вся логика общения с пользователем
    print('Добро пожаловать в сервис по подбору своей второй половинки\nВыберите действие:\n')
    print('Чтобы начать поиск')


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
    relation = input('Введите семейное положение\n1 — не женат/не замужем; 2 — есть друг/есть подруга; '
                     '3 — помолвлен/помолвлена; 4 — женат/замужем; 5 — всё сложно; 6 — в активном поиске; '
                     '7 — влюблён/влюблена; 8 — в гражданском браке; 0 — не указано\n')
    user_info = VkUser().get_user_info(user_search_id)
    search_range = f'{age_from}-{age_to}'
    # Проверка исключение - если у Юзера VK в профиле нет данных о Городе или Дате рождения
    try:
        user_city = user_info['city']['title']
    except KeyError:
        user_city = 'Нет данных'
    try:
        birth_day = user_info['bdate']
        age = get_birth_date(birth_day)
    except KeyError:
        age = 'Нет данных'
    # проверка наличия запроса User_id - Search_range в базе данных
    # Если нет совпадения Id + Range - добавить в таблицу и вести поиск
    if not PostgresBase().is_inside_user_vk(user_info['id'], search_range):
        PostgresBase().add_user_vk(user_info['id'], user_info['first_name'], user_info['last_name'], age,
                       search_range, user_info['sex'], user_city)
        return user_info['id'], age_from, age_to, sex, city, relation
    # Если есть совпадение Id + Range
    # Продолжить поиск или выйти
    else:
        result = input(f"Запрос User_id {user_info['id']}, {user_info['last_name']} {user_info['first_name']} "
              f"и диапозон поиска {search_range} уже есть в таблице\nЖелаете продолжить поиск по этой комбинации?\n"
              f"Yes/No\n")
        if result == 'Yes':
            return user_info['id'], age_from, age_to, sex, city, relation
        else:
            raise SystemExit('Всего хорошего!')


if __name__ == '__main__':
    # print(start_search.__doc__)
    # make_tables()         # создаем все таблицы
    a = start_search()
    PostgresBase().decision_for_user(VkUser().search_dating_user(*a[1:]), a[0])


            # Что еще необхоимо сделать:

# Доделать проверку по Id + Range как primary key - Логика такая, что у одного и того же User_id в таблице User_vk
# может быть разный диапозон поиска, и как следствие разные люди будут выходить в результатах!
# Поэтому хочу сделать User_id + Range как primary key и добавлять и выводить данные по этим 2м полям

# Вывод всех понравившихся людей - это будет в 'sql_orm' блоке через UserVk.dating_users

# Удалить из лайк списка человека - скорее всего тоже в 'sql_orm' сделаю, хотя можно и в 'DB' через запрос SQL

# Реализовать тесты на базовую функциональность
