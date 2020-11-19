from vk_module import VkUser
from DB import PostgresBase
from indep_func import get_age, session, engine
from sql_orm import UserVk, UserPhoto, DatingUser, SkippedUser, IgnoreUser, ORMFunctions, Base

pg_base = PostgresBase()
orm = ORMFunctions(session)


def get_started_data(user_vk_id):
    """
    :param user_vk_id: Id пользователя, ведущего поиск
    :return: возвращает кортеж данных о пользователе совершившем поиск (id, возраст, диапозон поиска)
    и параметры поиска (возраст от и до, пол, город, семейное положение)
    """
    user_search_id = user_vk_id
    age_from = input('Введите возраст ОТ\n')
    age_to = input('Введите возраст ДО\n')
    sex = input('Введите пол (1 - ж, 2 - м)\n')
    city = input('Введите город (id или Название)\n')
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
    id_with_range = orm.is_id_and_range_inside_user_vk(user_info['id'], search_range)
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
        UserVk().add_user_vk(user_info['id'], user_info['first_name'], user_info['last_name'], age,
                             search_range, user_info['sex'], city_name[0]['title'])
        return age_from, age_to, sex, city_id, status, user_info['id'], search_range


def main():
    user_id = input('Добро пожаловать в сервис по подбору своей второй половинки\nВведите ваш User_id Вконтакте\n')
    while True:
        user_id = VkUser().get_user_info(user_id)['id']
        user_input = int(input('Что вы хотели бы сделать?\n'
                               '1 - начать новый поиск\n'
                               '2 - показать понравившихся людей\n'
                               '3 - удалить из списка понравившихся людей человека\n'
                               '4 - посмотреть черный спискок\n'
                               '5 - удалить из черного списка человека\n'
                               '6 - сменить Vk Id\n'
                               '7 - выйти\n'
                               '911 - удалить все базы данных и создать заново\n'))
        if user_input == 1:
            search_details = get_started_data(user_id)
            pg_base.decision_for_user(VkUser().search_dating_user(*search_details[:5]), *search_details[5:])
        elif user_input == 2:
            orm.show_id_and_range(user_id)
            range_input = int(input('Выберите диапозон поиска\n'))
            users_dating_id = orm.show_dating_users(user_id, range_input)
            for user in users_dating_id:
                print(f'https://vk.com/id{user}')
                print()
        elif user_input == 3:
            pass
        elif user_input == 4:
            pass
        elif user_input == 5:
            pass
        elif user_input == 6:
            user_id = input('Введите новый id\n')
        elif user_input == 7:
            break
        elif user_input == 911:
            Base.metadata.drop_all(engine)
            Base.metadata.create_all(engine)
        else:
            break


if __name__ == '__main__':
    main()

    # проверка отсутствия фоток в профиле
    # pg_base.decision_for_user(VkUser().search_dating_user('32', '39', '1', 60, '6'), 13924278, '32-39')

    # print(ORMFunctions(session).is_id_inside_user_vk(13924278))
    # print(ORMFunctions(session).id_and_range_inside_user_vk(1, '30-32'))
    # user_in_table = session.query(VkUser).filter
    # print(ignore_ids)
    #
    # Что еще необхоимо сделать:

    # Доделать проверку по Id + Range как primary key - У одного и того же User_id в таблице User_vk  DONE
    # может быть разный диапозон поиска, и как следствие разные люди будут выходить в результатах!
    # Поэтому хочу сделать User_id + Range как primary key и добавлять и выводить данные по этим 2м полям

    # Вывод всех понравившихся людей - это будет в 'sql_orm' блоке через UserVk.dating_users

    # Удалить из лайк списка человека - скорее всего тоже в 'sql_orm' сделаю, хотя можно и в 'DB' через запрос SQL

    # Реализовать тесты на базовую функциональность
    pass
