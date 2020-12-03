import re
import json
from datetime import date


def get_age(birth_info):
    date_info = re.findall(r'(\d\d?).(\d\d?)?.?(\d{4})?', birth_info)[0]
    if date_info[2]:
        today = date.today()
        age = (int(today.year) - int(date_info[2]) - int(
            (today.month, today.day) < (int(date_info[1]), int(date_info[0]))))
    else:
        age = f"нет данных"
    return age


def get_text_buttons(label, color, payload=""):
    return {
        "action": {
            "type": "text",
            "label": label,
            "payload": json.dumps(payload)
        },
        "color": color
    }


filter_msg = {'inline': True,
              'buttons': [
                  [
                      get_text_buttons('просмотр', 'positive'),
                      # get_text_buttons('нет', 'secondary')
                  ],
                  [get_text_buttons('выйти', 'negative')]
              ]
              }

like_ignore = {'inline': True,
               'buttons': [
                   [
                       get_text_buttons('лайк', 'positive'),
                       get_text_buttons('игнор', 'secondary')
                   ],
                   [get_text_buttons('выйти', 'negative')]
               ]
               }

show_users = {'inline': True,
              'buttons': [
                  [
                      get_text_buttons('следующий', 'positive'),
                      get_text_buttons('удалить', 'secondary')
                  ],
                  [get_text_buttons('выйти', 'negative')]
              ]
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
                [get_text_buttons('показать/удалить людей', 'secondary')],
                # [get_text_buttons('выйти', 'negative')],
            ]
            }

keyboards = {
    'greeting': greeting,
    'decision': decision,
    'show_users': show_users,
    'like_ignore': like_ignore,
    'filter_msg': filter_msg
}


if __name__ == '__main__':
    pass
