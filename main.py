#! /usr/bin/env python
# -*- coding: utf-8 -*-
from sql_orm import session
from server import Server
from vk_api.longpoll import VkLongPoll
from vk_api import VkApi


group_token = input('Token: ')
vk = VkApi(token=group_token)
long_poll = VkLongPoll(vk)


if __name__ == '__main__':
    Server(group_token, session).start()
    pass
