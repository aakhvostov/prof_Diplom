#! /usr/bin/env python
# -*- coding: utf-8 -*-
from bot import group_token
from sql_orm import session
from server import Server

# elif state_object.state == 'Error_Initial':
#     pass
# elif state_object.state == 'Error_City':
#     pass
# elif state_object.state == 'Error_Sex':
#     pass
# elif state_object.state == 'Relation':
#     pass
# elif state_object.state == 'Error_Relation':
#     pass
# elif state_object.state == 'Error_Range':
#
#
#     elif user_input == 3:
#         range_input = get_range_input(user_id)
#         dating_func_dict = orm.get_dating_users(user_id, range_input)
#         dating_dict = dating_func_dict[0]
#         if len(dating_dict) == 0:
#             print('Ops! удалять некого\n')
#             continue
#         dating_objects = dating_func_dict[1]
#         for key, url in enumerate(dating_dict.values()):
#             print(f'{key} - https://vk.com/id{url}')
#         ans = int(input('Кого хотите удалить?\n или введите 911 для отмены\n'))
#         if ans == 911:
#             continue
#         elif ans >= 0:
#             dating_objects[ans].remove_dating_user()
#         else:
#             print('Неверный ввод')
#             pass
#     elif user_input == 5:
#         range_input = get_range_input(user_id)
#         ignore_func_dict = orm.get_ignore_users(user_id, range_input)
#         ignore_dict = ignore_func_dict[0]
#         if len(ignore_dict) == 0:
#             print('Ops! удалять некого\n')
#             continue
#         ignore_objects = ignore_func_dict[1]
#         for key, url in enumerate(ignore_dict.values()):
#             print(f'{key} - https://vk.com/id{url}')
#         ans = int(input('Кого хотите удалить?\n или введите 911 для отмены\n'))
#         if ans in ignore_dict:
#             ignore_objects[ans].remove_ignore_user()
#         else:
#             print('Неверный ввод')
#             pass
#
# def get_range_input(search_user_id):
#     """
#     Выводит диапозон поиска согласно данным таблицы User_vk
#     :param search_user_id:      Id человека ведущего поиск
#     :return:                    диапозон поиска
#     """
#     ranges = orm.show_id_and_range(search_user_id)
#     if len(ranges) == 0:
#         print('Ops, похоже Вы еще не производили поиск!\n')
#         return None
#     # if len(ranges) == 1:
#     #     return 0
#     if len(ranges) >= 1:
#         range_input = int(input('Выберите диапозон. Или введите 911 для нового поиска\n'))
#         if range_input in ranges:
#             return range_input
#         elif range_input == 911:
#             return None
#         else:
#             return 'неверное значение'


if __name__ == '__main__':
    Server(group_token, session).start()
    # server1.start()
    # main()
                        # Что еще необхоимо сделать:

    # Удалить из списка человека
    # Реализовать тесты на базовую функциональность
    # удалить тестировочные принты
    pass
