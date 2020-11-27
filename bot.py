from vk_api.longpoll import VkLongPoll
from vk_api import VkApi
from random import randrange
import json
from server import VkUser


group_token = input('Token: ')
# group_token = ''
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


if __name__ == '__main__':
    pass
