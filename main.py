#! /usr/bin/env python
# -*- coding: utf-8 -*-
from bot import group_token
from sql_orm import session
from server import Server, ORMFunctions, VkUser
orm = ORMFunctions()
vkuser = VkUser()


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


if __name__ == '__main__':
    Server(group_token, session).start(orm, vkuser)
    # server1.start()
    # main()
                        # Что еще необхоимо сделать:

    # Удалить из списка человека
    # Реализовать тесты на базовую функциональность
    # удалить тестировочные принты
    pass
