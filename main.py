#! /usr/bin/env python
# -*- coding: utf-8 -*-

import re
from vk_module import VkUser, longpoll, write_msg, write_msg_greeting
from indep_func import get_age, session, engine
from sql_orm import ORMFunctions, Base, UserVk, DatingUser, UserPhoto, IgnoreUser, SkippedUser, Search
from vk_api.longpoll import VkEventType


orm = ORMFunctions(session)


def get_search_user_info(search_user_id):
    """
    Функция добавляет пользователя в таблицу
    :param search_user_id: Id человека ведущего поиск
    :return:
    """
    user_info = VkUser().get_user_info(search_user_id)
    user_id = user_info['id']
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
    if not orm.looking_for_user_vk(user_id):
        UserVk().add_user_vk(user_id, user_firstname, user_lastname, user_age, user_sex, user_city)


def get_started_data(search_user_id):
    """
    Функция принимает ввводные данные для поиска людей
    :param search_user_id:  Id человека ведущего поиск
    :return:                Возвращает кортеж данных для поиска
    """
    age_from = input('Введите возраст ОТ\n')
    age_to = input('Введите возраст ДО\n')
    sex = input('Введите пол (1 - ж, 2 - м)\n')
    city = input('Введите город (id или Название)\n')
    status = input('Введите семейное положение\n1 — не женат/не замужем; 2 — есть друг/есть подруга; '
                   '3 — помолвлен/помолвлена; 4 — женат/замужем; 5 — всё сложно; 6 — в активном поиске; '
                   '7 — влюблён/влюблена; 8 — в гражданском браке; 0 — не указано\n')
    search_range = f'{age_from}-{age_to}'
    city_name = VkUser().get_city_id(city)
    search_id = Search().add_search(search_range, sex, city_name, status, search_user_id)
    return age_from, age_to, sex, city_name, status, search_id


def decision_for_user(users_list, search_id):
    """
    Проходится по списку словарей и по одному ждем от пользователя решения куда добавить человека:
    в лайк лист
    в игнор лист
    пропустить человека - с добавление в Скип лист, чтобы они не выходили в дальнейшем поиске
    :param users_list: список со словарями людей, полученных по результатам поиска
    :param search_id: Id записи в таблице Search
    :return: решение куда добавть человека
    """
    print(f'Всего найдено {len(users_list)} человек\nПриступим к просмотру ;)')
    print(f'search_id - {search_id}')
    for person in users_list:
        first_name = person['first_name']
        last_name = person['last_name']
        user_id = person['id']
        try:
            age = person['bdate']
            age = get_age(age)
        except KeyError:
            age = 'нет данных'
        # проверка наличия найденного Id в таблицах
        if not orm.is_inside_ignore_dating_skipped(user_id, search_id):
            link = VkUser().get_users_best_photos(user_id)
            print(f'{first_name} {last_name} - {link}\n')
            decision = input('Нравится этот человек?\n'
                             '"1" - ДА - добавить в список понравившихся\n'
                             '"2" - НЕТ - пропустить и добавить в черный список\n'
                             '"3" - пропустить с добавлением в список Skipped_user\n'
                             '"7" - выход\n')
            if re.match(r"[/+1yYдД]", decision):
                DatingUser().add_dating_user(user_id, first_name, last_name, age, search_id)
                UserPhoto().add_user_photo(VkUser().get_users_best_photos(user_id), user_id, search_id)
                continue
            elif re.match(r"[/-2nNнН]", decision):
                IgnoreUser().add_ignore_user(user_id, search_id)
                continue
            elif re.match(r"[/3пПsSpP]", decision):
                SkippedUser().add_skipped_user(user_id, search_id)
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
    # if len(ranges) == 1:
    #     return 0
    if len(ranges) >= 1:
        range_input = int(input('Выберите диапозон. Или введите 911 для нового поиска\n'))
        if range_input in ranges:
            return range_input
        elif range_input == 911:
            return None
        else:
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
            # range_input = get_range_input(user_id)
            # # проверка наличия уже происходивших поисков и продолжения их
            # if range_input == 'неверное значение':
            #     print('Вы выбрали неверный диапозон')
            #     continue
            # elif range_input is None:
            #     get_search_user_info(user_id)
            #     search_details = get_started_data()
            # elif range_input is not None:
            #     vk_object_dict = orm.get_vk_users(user_id, range_input)
            #     age_pattern = re.compile(r'(\d\d?)-(\d\d?\d?)')
            #     sex = vk_object_dict.sex
            #     city = vk_func.get_city_id(vk_object_dict.user_city)
            #     search_range = vk_object_dict.search_range
            #     age_from = age_pattern.sub(r"\1", search_range)
            #     age_to = age_pattern.sub(r"\2", search_range)
            #     status = vk_object_dict.status
            #     search_details = (age_from, age_to, sex, city, status, user_id, search_range)
            # else:
            get_search_user_info(user_id)
            search_details = get_started_data(user_id)
            if search_details:
                answer = decision_for_user(vk_func.search_dating_user(*search_details[:5]), search_details[5])
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
            dating_objects = dating_func_dict[1]
            for key, url in enumerate(dating_dict.values()):
                print(f'{key} - https://vk.com/id{url}')
            ans = int(input('Кого хотите удалить?\nили введите 911 для отмены\n'))
            if ans == 911:
                continue
            elif ans >= 0:
                dating_objects[ans].remove_dating_user()
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
            ignore_objects = ignore_func_dict[1]
            for key, url in enumerate(ignore_dict.values()):
                print(f'{key} - https://vk.com/id{url}')
            ans = int(input('Кого хотите удалить?\nили введите 911 для отмены\n'))
            if ans in ignore_dict:
                ignore_objects[ans].remove_ignore_user()
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
    for event in longpoll.listen():
        user_id = event.user_id
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text
                if request == "привет":
                    write_msg_greeting(event.user_id, 'Привет! Выбери действие')
                elif "блэк" in request:
                    write_msg(event.user_id, "Идем в черный список")
                elif "лайк" in request:
                    write_msg(event.user_id, "Идем в лайк список")
                elif request == "пока":
                    write_msg(event.user_id, "Пока((")
                elif request == "выйти":
                    break
                else:
                    write_msg_greeting(event.user_id, 'Что будем делать дальше?')
    # main()
    # проверка отсутствия фоток в профиле
    # print(ORMFunctions(session).is_id_inside_user_vk(13924278))
    # print(ORMFunctions(session).id_and_range_inside_user_vk(1, '30-32'))
    # user_in_table = session.query(VkUser).filter
    # print(ignore_ids)
    # Что еще необхоимо сделать:
    # Удалить из списка человека
    # Реализовать тесты на базовую функциональность

    pass
