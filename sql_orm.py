from sqlalchemy import Column, Integer, String, ForeignKey, PrimaryKeyConstraint, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from indep_func import Base, session


class UserVk(Base):
    __tablename__ = 'user_vk'

    user_id = Column(Integer)
    user_firstname = Column(String(40))
    user_lastname = Column(String(40))
    user_age = Column(String(15))
    search_range = Column(String(15))
    sex = Column(Integer)
    user_city = Column(String(40))
    status = Column(Integer)
    __table_args__ = (PrimaryKeyConstraint(user_id, search_range),)

    def add_user_vk(self, vk_id, firstname, lastname, age, search_range, sex, city, status):
        """
        Добавляет человека в базу таблицу user_vk
        """
        self.user_id = vk_id
        self.user_firstname = firstname
        self.user_lastname = lastname
        self.user_age = age
        self.search_range = search_range
        self.sex = sex
        self.user_city = city
        self.status = status
        session.add(self)
        session.commit()
        return print(f'юзер {self.user_id} добавлен в user_vk список')

    def remove_user_vk(self):
        """
        Удаляет человека из таблицы UserVK
        """
        session.delete(self)
        session.commit()
        print(f'юзер удален из user_vk')


class DatingUser(Base):
    __tablename__ = 'dating_user'

    dating_id = Column(Integer, primary_key=True)
    dating_user_id = Column(Integer)
    user_firstname = Column(String(40))
    user_lastname = Column(String(40))
    user_age = Column(String(15))
    user_id = Column(Integer)
    user_id_range = Column(String(15))
    photos = relationship('UserPhoto', backref='user_photo')
    __table_args__ = (ForeignKeyConstraint(('user_id', 'user_id_range'), [UserVk.user_id, UserVk.search_range]),)

    def add_dating_user(self, vk_id, firstname, lastname, age, user_id, search_range):
        """
        Добавляет человека в таблицу dating_user
        """
        self.dating_user_id = vk_id
        self.user_firstname = firstname
        self.user_lastname = lastname
        self.user_age = age
        self.user_id = user_id
        self.user_id_range = search_range
        session.add(self)
        session.commit()
        print(f'юзер {self.dating_user_id} добавлен в лайк список')

    def remove_dating_user(self):
        """
        Удаляет человека из таблицы DatingUser
        """
        session.delete(self)
        session.commit()
        print(f'юзер удален из dating_user')


class UserPhoto(Base):
    __tablename__ = 'user_photo'

    user_photo_id = Column(Integer, primary_key=True)
    photo_link = Column(String)
    photo_likes = Column(Integer)
    dating_id = Column(Integer, ForeignKey('dating_user.dating_id'))

    def add_user_photo(self, links_likes, user_vk_id, user_search_id):
        for like, link in links_likes.items():
            self.photo_link = link
            self.photo_likes = like
            self.dating_id = ORMFunctions(session).select_photo(user_vk_id, user_search_id)
            session.add(self)
            session.commit()
            print(f'фото {like} добавлено в список')

    def remove_user_photo(self):
        """
        Удаляет фото из таблицы UserPhoto
        """
        session.delete(self)
        session.commit()
        print(f'фотки удалены')


class IgnoreUser(Base):
    __tablename__ = 'ignore_user'

    user_ignore_id = Column(Integer)
    user_id = Column(Integer)
    user_id_range = Column(String(15))
    __table_args__ = (PrimaryKeyConstraint(user_ignore_id, user_id),
                      (ForeignKeyConstraint(('user_id', 'user_id_range'), [UserVk.user_id, UserVk.search_range])),)

    def add_ignore_user(self, ignore_id, vk_id, search_range):
        """
        Добавляет человека в таблицу ignore_user
        """
        self.user_ignore_id = ignore_id
        self.user_id = vk_id
        self.user_id_range = search_range
        session.add(self)
        session.commit()
        return print(f'юзер {self.user_ignore_id}  добавлен в игнор список')

    def remove_ignore_user(self):
        """
        Удаляет фото из таблицы IgnoreUser
        """
        session.delete(self)
        session.commit()
        print(f'юзер удален из ignore_user')


# class SkippedUser(Base):
#     __tablename__ = 'skipped_user'
#
#     skipped_id = Column(Integer)
#     user_id = Column(Integer)
#     user_id_range = Column(String(15))
#     __table_args__ = (PrimaryKeyConstraint(skipped_id, user_id),
#                       (ForeignKeyConstraint(('user_id', 'user_id_range'), [UserVk.user_id, UserVk.search_range])),)
#
#     def add_skipped_user(self, skipped_id, vk_id, search_range):
#         """
#         Добавляет человека в таблицу ignore_user
#         """
#         self.skipped_id = skipped_id
#         self.user_id = vk_id
#         self.user_id_range = search_range
#         session.add(self)
#         session.commit()
#         return print(f'юзер {self.skipped_id} добавлен в скип список')


class ORMFunctions:
    def __init__(self, session_elem):
        self.session = session_elem
        self.search_range_dict = {}

    def is_id_and_range_inside_user_vk(self, vk_search_id, search_range: str):
        """
        Функция проверяет наличия составного primary key (user_id + range) в таблице User_vk
        :param vk_search_id:    Id человека ведущего поиск
        :param search_range:    диапозон поиска
        :return:                True или False
        """
        result = self.session.query(UserVk).filter_by(user_id=vk_search_id, search_range=search_range)
        return self.session.query(result.exists()).one()[0]

    def show_id_and_range(self, vk_search_id):
        """
        Функция для вывода истории поиска Юзера
        :param vk_search_id:    Id человека ведущего поиск
        :return:                словарь с диапозонами поиска
        """
        result = self.session.query(UserVk.search_range).filter_by(user_id=vk_search_id).all()
        for k, v in enumerate([ranges[0] for ranges in result]):
            self.search_range_dict[k] = v
        # if len(self.search_range_dict) > 1:
        print(f'у Вас в таблице есть следующие диапозоны поиска {self.search_range_dict}')
        return self.search_range_dict

    def get_vk_users(self, vk_search_id, find_range):
        """
        Функция для поиска записи в User_vk по паре Id+range
        :param vk_search_id:    Id человека ведущего поиск
        :param find_range:      диапазон поиска
        :return:                объект юзера из таблицы User_vk
        """
        result = self.session.query(UserVk).filter_by(user_id=vk_search_id,
                                                      search_range=self.search_range_dict[find_range]).one()

        return result

    def get_dating_users(self, vk_search_id, find_range):
        """
        Функция для поиска людей в Dating_user по паре Id+range
        :param vk_search_id:    Id человека ведущего поиск
        :param find_range:      диапазон поиска
        :return:                словарь dat_id + user_dat_vk_id из таблицы Dating_user
                                и список самих объектов из таблицы Dating_user
        """
        dating_dict = {}  # скорее всего СДЕЛАТЬ SELF.DATING_DICT!!! и в остальных так же
        result = self.session.query(DatingUser).filter_by(user_id=vk_search_id,
                                                          user_id_range=self.search_range_dict[find_range]).all()
        for user_obj in result:
            dating_dict[user_obj.dating_id] = user_obj.dating_user_id
        return dating_dict, result

    def get_ignore_users(self, vk_search_id, find_range):  # заменить в  elif user_input == 4: elif user_input == 5:
        """
        Функция для поиска людей в Ignore_user по паре Id+range
        :param vk_search_id:    Id человека ведущего поиск
        :param find_range:      диапазон поиска
        :return:                словарь key + user_ignore_id из Ignore_user
                                и список самих объектов из таблицы Ignore_user
        """
        ignore_dict = {}
        result = self.session.query(IgnoreUser).filter_by(user_id=vk_search_id,
                                                          user_id_range=self.search_range_dict[find_range]).all()
        for key, user_obj in enumerate(result):
            ignore_dict[key] = user_obj.user_ignore_id
        return ignore_dict, result

    def select_photo(self, user_vk_id, user_search_id):
        """
        Функция ищет dating_id в таблице Dating_user и возвращает его для дальнейшего использования при добавлении
        фотографии по этой паре
        :param user_vk_id:      Id пары
        :param user_search_id:  диапазон поиска
        :return:                dating_id (primary key)
        """
        dating_id = self.session.query(DatingUser).filter_by(dating_user_id=user_vk_id,
                                                             user_id=user_search_id).one().dating_id
        return dating_id

    def is_inside_ignore_dating_skipped(self, user_vk_id, user_search_id, search_range):
        """
        Проверяет юзера на наличие его в таблицах лайков и игноров
        Если совпадение есть, то Юзер пропускается в выдаче
        :param user_vk_id: Id пары
        :param user_search_id: Id искателя
        :param search_range: диапозон поиска
        :return: True или False
        """
        result = self.session.query(DatingUser).filter_by(dating_user_id=user_vk_id, user_id=user_search_id,
                                                          user_id_range=search_range)
        entry = self.session.query(result.exists()).one()[0]
        if entry:
            return entry
        else:
            result = self.session.query(IgnoreUser).filter_by(user_ignore_id=user_vk_id, user_id=user_search_id,
                                                              user_id_range=search_range)
            entry = self.session.query(result.exists()).one()[0]
            if entry:
                return entry
            # else:
            #     result = self.session.query(SkippedUser).filter_by(skipped_id=user_vk_id, user_id=user_search_id,
            #                                                        user_id_range=search_range)
            #     entry = self.session.query(result.exists()).one()[0]
        return entry

    # def get_dating_search_range(self, dating_id):
    #     """
    #     Функция ищет в таблице Dating Users по Id диапозон поиска
    #     :param dating_id: Id записи в таблице Dating Users
    #     :return: диапозо поиска
    #     """
    #     search_range = self.session.query(DatingUser).filter(DatingUser.dating_id == dating_id).one()
    #     return search_range.user_id_range


if __name__ == '__main__':
    new_used = ORMFunctions(session)
    print(len(new_used.show_id_and_range(2)))
    # print(new_used.show_dating_users(13924278, '38-40')[0])
    # print()
    # print(new_used.show_dating_users(13924278, '38-40')[1])
    # print(new_used.find_dating_user_photo(250183789, 13924278, '32-39'))
    # print(ORMFunctions(session).is_id_and_range_inside_user_vk(13924278, '38-40'))
    # new_used.show_id_and_range(13924278)
    # new_used.select_photo(143041215, 1582074)
    # print(new_used.is_inside_ignore_dating_skipped(45269508, 13924278, '30-31'))
    # print(new_used.show_dating_users(13924278, 1))
    # new_used.is_inside_ignore_dating_skipped(18349823)
    pass
