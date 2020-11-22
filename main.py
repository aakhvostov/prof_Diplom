import re
from vk_module import VkUser
from indep_func import get_age, session, engine
from sql_orm import ORMFunctions, Base, UserVk, DatingUser, UserPhoto, IgnoreUser#, SkippedUser
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
        result = int(input(f"Запрос User_id {user_info['id']}, {user_info['last_name']} {user_info['first_name']} "
                           f"и диапозон поиска {search_range} уже есть в таблице\n"
                           f"Желаете продолжить поиск по этой комбинации?\n"
                           f"1 - Да / 2 - Нет\n"))
        if result == 1:
            return age_from, age_to, sex, city_id, status, user_info['id'], search_range
        elif result == 2:
            return False
        else:
            raise SystemExit('Всего хорошего!')
    # Если нет ПОЛНОГО совпадения по Id + Range - добавить в базу новую запись и вести поиск
    else:
        city_name = VkUser().get_city_name(city_id)
        UserVk().add_user_vk(user_info['id'], user_info['first_name'], user_info['last_name'], age,
                             search_range, user_info['sex'], city_name[0]['title'])
        return age_from, age_to, sex, city_id, status, user_info['id'], search_range


def decision_for_user(users_list, search_id, search_range):
    """
    Проходится по списку словарей и по одному ждем от пользователя решения куда добавить человека:
    в лайк лист
    в игнор лист
    пропустить человека - с добавлениев в Скип лист, чтобы они не выходили в дальнейшем поиске
    :param search_id: vk_id пользователя для которого ведется поиск
    :param search_range: диапозон поиска людей пользователя для которого ведется поиск
    :param users_list: список со словарями людей, полученных по результатам поиска
    :return: решение куда добавть человека
    """
    print(f'Всего найдено {len(users_list)} человек\nПриступим к просмотру ;)')
    for person in users_list:
        first_name = person['first_name']
        last_name = person['last_name']
        user_id = person['id']
        try:
            age = person['bdate']
            age = get_age(age)
        except KeyError:
            age = 'нет данных'
        # проверка наличия пары в таблицах
        if not orm.is_inside_ignore_dating_skipped(user_id, search_id, search_range):
            link = VkUser().get_users_best_photos(user_id)
            print(f'{first_name} {last_name} - {link}\n')
            decision = input('Нравится этот человек?\n'
                             '"1" - ДА - добавить в список понравившихся\n'
                             '"2" - НЕТ - пропустить и добавить в черный список\n'
                             '"3" - пропустить\n'
                             '"7" - выход\n')
            if re.match("[/+1yYдД]", decision):
                DatingUser().add_dating_user(user_id, first_name, last_name, age, search_id, search_range)
                UserPhoto().add_user_photo(VkUser().get_users_best_photos(user_id), user_id, search_id)
                continue
            elif re.match("[/-2nNнН]", decision):
                IgnoreUser().add_ignore_user(user_id, search_id, search_range)
                continue
            elif decision == str(3):
                # SkippedUser().add_skipped_user(user_id, search_id, search_range)
                continue
            elif decision == str(7):
                return False
            else:
                print('Ввели что-то не то')
                break
        else:
            continue
    return True


def get_range_input(user_id):
    """
    Выводит диапозон поиска согласно данным таблицы User_vk
    :param user_id:     Id человека ведущего поиск
    :return:            диапозон поиска
    """
    ranges = orm.show_id_and_range(user_id)
    if len(ranges) == 0:
        print('Ops, похоже Вы еще не производили поиск!\n')
        return None
    if len(ranges) == 1:
        return 0
    if len(ranges) > 1:
        range_input = int(input('Выберите диапозон:\n'))
        if range_input in ranges:
            return range_input
        return 'неверное значение'


def main():
    vk_func = VkUser()
    user_id = input('Добро пожаловать в сервис по подбору своей второй половинки\nВведите ваш User_id Вконтакте\n')
    user_id = new_user_id = vk_func.get_user_info(user_id)['id']
    while True:
        if user_id != new_user_id:
            user_id = new_user_id
            vk_func = VkUser()
        user_id = vk_func.get_user_info(user_id)['id']
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
            range_input = get_range_input(user_id)
            # проверка наличия уже происходивших поисков и продолжения их
            if range_input == 'неверное значение':
                print('Вы выбрали неверный диапозон')
                continue
            elif range_input is not None:
                vk_func_dict = orm.get_vk_users(user_id, range_input)
                vk_range_dict = vk_func_dict[0]
                vk_object_dict = vk_func_dict[1]
                # тут логика продолжения существующего поиска
                    # вывести объект из vk_object_dict с индексом range_input и записать кортеж в search_details
                    # search_details = # age_from, age_to, sex, city_id, status, user_info['id'], search_range
                    # continue

                search_details = get_started_data(user_id)
            else:
                search_details = get_started_data(user_id)
            if search_details:
                answer = decision_for_user(vk_func.search_dating_user(*search_details[:5]), *search_details[5:])
                if answer:
                    while True:
                        next_list = int(input(f'Ops! список закончился, желаете еще поискать половинку?\n'
                                              f'Введите\n1 - да\n2 - нет\n'))
                        if next_list == 1:
                            decision_for_user(vk_func.search_dating_user(*search_details[:5]), *search_details[5:])
                        elif next_list == 2:
                            break
                        else:
                            print('Ввели что-то не то')
        elif user_input == 2:
            range_input = get_range_input(user_id)
            dating_func_dict = orm.get_dating_users(user_id, range_input)
            dating_dict = dating_func_dict[0]
            if len(dating_dict) == 0:
                print('Ops! смотреть некого\n')
                continue
            for user_dat_id in dating_dict.values():
                print(f'https://vk.com/id{user_dat_id}')
            print()
        elif user_input == 3:
            range_input = get_range_input(user_id)
            dating_func_dict = orm.get_dating_users(user_id, range_input)
            dating_dict = dating_func_dict[0]
            if len(dating_dict) == 0:
                print('Ops! удалять некого\n')
                continue
            dating_objs = dating_func_dict[1]
            for key, url in enumerate(dating_dict.values()):
                print(f'{key} - https://vk.com/id{url}')
            ans = int(input('Кого хотите удалить?\nили введите 911 для отмены\n'))
            if ans >= 0:
                dating_objs[ans].remove_dating_user()
            else:
                print('Неверный ввод')
                pass
        elif user_input == 4:
            range_input = get_range_input(user_id)
            ignore_func_dict = orm.get_ignore_users(user_id, range_input)
            ignore_dict = ignore_func_dict[0]
            if len(ignore_dict) == 0:
                print('Ops! смотреть некого\n')
                continue
            for user_ign_id in ignore_dict.values():
                print(f'https://vk.com/id{user_ign_id}')
            print()
        elif user_input == 5:
            range_input = get_range_input(user_id)
            ignore_func_dict = orm.get_ignore_users(user_id, range_input)
            ignore_dict = ignore_func_dict[0]
            if len(ignore_dict) == 0:
                print('Ops! удалять некого\n')
                continue
            ignore_objs = ignore_func_dict[1]
            for key, url in enumerate(ignore_dict.values()):
                print(f'{key} - https://vk.com/id{url}')
            ans = int(input('Кого хотите удалить?\nили введите 911 для отмены\n'))
            if ans in ignore_dict:
                ignore_objs[ans].remove_ignore_user()
            else:
                print('Неверный ввод')
                pass
        elif user_input == 6:
            new_user_id = input('Введите новый id\n')
            new_user_id = vk_func.get_user_info(new_user_id)['id']
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
    # print(ORMFunctions(session).is_id_inside_user_vk(13924278))
    # print(ORMFunctions(session).id_and_range_inside_user_vk(1, '30-32'))
    # user_in_table = session.query(VkUser).filter
    # print(ignore_ids)
    # Что еще необхоимо сделать:
    # Удалить из списка человека
    # Реализовать тесты на базовую функциональность

    pass
