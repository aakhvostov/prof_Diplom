from vk_api.longpoll import VkLongPoll
from vk_api import VkApi
from random import randrange
import json
from server import VkUser


# group_token = input('Token: ')
group_token = 'fe40651e2f644afbf32552f6fabc7d471bbab8a43fffd2b08d62d63e955977892f8f1a468018b8f2ee2f5'
vk = VkApi(token=group_token)
long_poll = VkLongPoll(vk)
current_user_vk = VkUser()


def get_text_buttons(label, color, payload=""):
    return {
        "action": {
            "type": "text",
            "label": label,
            "payload": json.dumps(payload)
        },
        "color": color
    }


decision = {'inline': True,
            'buttons': [
                [
                    get_text_buttons('лайк', 'positive'),
                    get_text_buttons('крестик', 'secondary'),
                    get_text_buttons('пропуск', 'secondary')
                ],
                [get_text_buttons('выход', 'negative')]
            ]
            }

greeting = {'one_time': True,
            'buttons': [
                [get_text_buttons('начать поиск', 'primary')],
                [get_text_buttons('показать/удалить людей из лайк списка', 'positive')],
                [get_text_buttons('показать/удалить людей из блэк списка', 'secondary')],
                [get_text_buttons('выйти', 'negative')],
            ]
            }

keyboards = {
    'greeting': greeting,
    'decision': decision,
}


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id,
                                'message': message,
                                'random_id': randrange(10 ** 7)})


def write_msg_keyboard(user_id, message, keyboard):
    vk.method('messages.send', {'user_id': user_id,
                                'message': message,
                                'random_id': randrange(10 ** 7),
                                'keyboard': json.dumps(keyboards[keyboard], ensure_ascii=False)})


# def hello_state(event, objects, session):
#     setattr(objects[1], "state", "Initial")
#     session.commit()
#     write_msg_keyboard(event.user_id, 'Выберите действие:', 'greeting')
#
#
# def initial_state(event, objects, session):
#     if event.text == "начать поиск":
#         try:
#             setattr(objects[1], "state", "City")
#             session.commit()
#             write_msg(event.user_id, 'Введите город')
#             return True
#         except ValueError:
#             setattr(objects[1], "state", "Error_Initial")
#             session.commit()
#             return True
#         except IndexError:
#             setattr(objects[1], "state", "Error_Initial")
#             session.commit()
#             return True
#     elif event.text == "показать/удалить людей из лайк списка":
#         return True
#     elif event.text == "показать/удалить людей из блэк списка":
#         return True
#     elif event.text == "выйти":
#         return False
#     else:
#         write_msg_keyboard(event.user_id, 'Привет! Выбери действие', 'greeting')
#         setattr(objects[1], "state", "Initial")
#         session.commit()
#         return True
#
#
# def city_state(event, objects, session):
#     try:
#         city_name = current_user_vk.get_city_name(current_user_vk.get_city_id(event.text))[0]['title']
#         setattr(objects[2], "search_city", city_name)
#         setattr(objects[1], "state", "Sex")
#         session.commit()
#         write_msg(event.user_id, 'Введите пол:\n1 - женщина\n2 - мужчина')
#         return True
#     except IndexError:
#         setattr(objects[1], "state", "Error_City")
#         session.commit()
#         return True
#
#
# def sex_state(event, objects, session):
#     try:
#         sex_value = int(event.text)
#         setattr(objects[2], "search_sex", sex_value)
#         setattr(objects[1], "state", "Relation")
#         session.commit()
#         write_msg(event.user_id,
#                   'Введите семейное положение\n1 — не женат/не замужем\n2 — есть друг/есть подруга\n'
#                   '3 — помолвлен/помолвлена\n4 — женат/замужем\n5 — всё сложно\n6 — в активном поиске\n'
#                   '7 — влюблён/влюблена\n8 — в гражданском браке\n0 — не указано\n')
#         return True
#     except ValueError:
#         setattr(objects[1], "state", "Error_Sex")
#         session.commit()
#         return True
#
#
# def relation_state(event, objects, session):
#     try:
#         status = int(event.text)
#         setattr(objects[2], "search_relation", status)
#         setattr(objects[1], "state", "Range")
#         write_msg(event.user_id, 'Введите диапозон поиска ОТ и ДО (через пробел или -)')
#         return True
#     except ValueError:
#         setattr(objects[1], "state", "Error_Relation")
#         session.commit()
#         return True
#
#
# def range_func_state(event, objects, session):
#     try:
#         age_pattern = re.compile(r'(\d\d?)[ -]+(\d\d?)')
#         age_from = int(age_pattern.sub(r"\1", event.text))
#         age_to = int(age_pattern.sub(r"\2", event.text))
#         if age_to - age_from > 0:
#             setattr(objects[2], "search_from", age_from)
#             setattr(objects[2], "search_to", age_to)
#             setattr(objects[1], "state", "Decision")
#             session.commit()
#             print(f'state inside Range - {objects[1].state}')
#             age_from = objects[2].search_from
#             age_to = objects[2].search_to
#             sex = objects[2].search_sex
#             city_name = objects[2].search_city
#             status = objects[2].search_relation
#             users_info_dict = current_user_vk.search_dating_user(age_from, age_to, sex, city_name, status)
#             return users_info_dict
#         else:
#             setattr(objects[1], "state", "Error_Range")
#             session.commit()
#             return True
#     except ValueError:
#         setattr(objects[1], "state", "Error_Range")
#         session.commit()
#         return True
#
#
# def decision_state(event, objects, session):
#     person = users_info_dict[count]
#     user_dating_id = person['id']
#     # проверка наличия найденного Id в таблицах
#     if not is_inside_ignore_dating_skipped(user_dating_id, event.user_id):
#         first_name = person['first_name']
#         last_name = person['last_name']
#         link = VkUser().get_users_best_photos(user_dating_id)  # сделать другой вывод
#         write_msg(event.user_id, f'{first_name} {last_name} - {link}\n')
#         write_msg_keyboard(event.user_id, 'Выберите действие', 'decision')
#         setattr(objects[1], "state", "Answer")
#         session.commit()
#         return True
#     else:
#         count += 1
#         return True
#
#
# def answer_state(event, objects, session):
#     if event.text == "лайк":
#         setattr(objects[1], "state", "Decision")
#         session.commit()
#         print('догли до Answer')
#         # try:
#         #     age = person['bdate']
#         #     age = get_age(age)
#         # except KeyError:
#         #     age = 'нет данных'
#         count += 1
#         print(f'Мы в Лайк меню Answer идем в Decision')
#     elif event.text == "крестик":
#         setattr(objects[1], "state", "Decision")
#         session.commit()
#     elif event.text == "пропуск":
#         setattr(objects[1], "state", "Decision")
#         session.commit()
#     elif event.text == "выход":
#         setattr(objects[1], "state", "Hello")
#         session.commit()
#
#
# states = {
#     "Hello": hello_state,
#     "Initial": initial_state,
#     "City": city_state,
#     "Sex": sex_state,
#     "Relation": relation_state,
#     "Range": range_func_state,
#     "Decision": decision_state,
#     "Answer": answer_state
# }

if __name__ == '__main__':
    pass
