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
    __table_args__ = (PrimaryKeyConstraint(user_id, search_range),)

    def add_user_vk(self, vk_id, firstname, lastname, age, search_range, sex, city):
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
        session.add(self)
        session.commit()
        return print(f'юзер {self.user_id} добавлен в user_vk список')


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
        return print(f'юзер {self.dating_user_id} добавлен в лайк список')


class UserPhoto(Base):
    __tablename__ = 'user_photo'

    user_photo_id = Column(Integer, primary_key=True)
    photo_link = Column(String)
    photo_likes = Column(Integer)
    dating_id = Column(Integer, ForeignKey('dating_user.dating_id'))

    def add_user_photo(self, links_likes, vk_id, dating_vk_id):
        for like, link in links_likes.items():
            self.photo_link = link
            self.photo_likes = like
            self.dating_id = ORMFunctions(session).select_photo(dating_vk_id, vk_id)
            session.add(self)
            session.commit()
            print(f'фото {like} добавлено в список')


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


class SkippedUser(Base):
    __tablename__ = 'skipped_user'

    skipped_id = Column(Integer)
    user_id = Column(Integer)
    user_id_range = Column(String(15))
    __table_args__ = (PrimaryKeyConstraint(skipped_id, user_id),
                      (ForeignKeyConstraint(('user_id', 'user_id_range'), [UserVk.user_id, UserVk.search_range])),)

    def add_skipped_user(self, skipped_id, vk_id, search_range):
        """
        Добавляет человека в таблицу ignore_user
        """
        self.skipped_id = skipped_id
        self.user_id = vk_id
        self.user_id_range = search_range
        session.add(self)
        session.commit()
        return print(f'юзер {self.skipped_id} добавлен в скип список')


class ORMFunctions:

    def __init__(self, session_elem):
        self.session = session_elem
        self.search_range_dict = {}

    def is_id_inside_user_vk(self, user_vk_id: int):  # не пользуется
        result = self.session.query(UserVk).filter_by(user_id=user_vk_id)
        return self.session.query(result.exists()).one()[0]

    def is_id_and_range_inside_user_vk(self, user_vk_id, age_range: str):
        result = self.session.query(UserVk).filter_by(user_id=user_vk_id, search_range=age_range)
        return self.session.query(result.exists()).one()[0]

    def show_id_and_range(self, user_vk_id):
        """
        Функция для вывода истории поиска юзера Id
        :param user_vk_id: Id юзера
        :return: словарь с диапозонами поиска
        """
        result = self.session.query(UserVk.search_range).filter_by(user_id=user_vk_id).all()
        for k, v in enumerate([ranges[0] for ranges in result]):
            self.search_range_dict[k] = v
        if len(self.search_range_dict) != 0:
            print(f'у Вас в таблице есть следующие диапозоны поиска {self.search_range_dict}')
        return self.search_range_dict

    def show_dating_users(self, user_vk_id, find_range):
        """
        Функция для поиска людей в Dating_user по паре Id+range
        :param user_vk_id: Id человека ведущего поиск
        :param find_range: диапозон поиска
        :return: список id людей из Dating_user
        """
        result = self.session.query(DatingUser).filter_by(user_id=user_vk_id,
                                                          user_id_range=self.search_range_dict[find_range]).all()
        dating_users = [dat_id.dating_user_id for dat_id in result]
        print(f'по Вашему запросу в таблице найдены id - {dating_users}')
        return dating_users

    def show_ignore_users(self, user_vk_id, find_range):
        """
        Функция для поиска людей в Dating_user по паре Id+range
        :param user_vk_id: Id человека ведущего поиск
        :param find_range: диапозон поиска
        :return: список id людей из Dating_user
        """
        result = self.session.query(IgnoreUser).filter_by(user_id=user_vk_id,
                                                          user_id_range=self.search_range_dict[find_range]).all()
        ignore_users = [ign_id.user_ignore_id for ign_id in result]
        print(f'по Вашему запросу в таблице найдены id - {ignore_users}')
        return ignore_users

    def select_photo(self, dating_user_id, user_id):
        dating_id = self.session.query(DatingUser).filter_by(dating_user_id=dating_user_id,
                                                             user_id=user_id).one().dating_id
        return dating_id

    def is_inside_ignore_dating_skipped(self, vk_id, vk_search_id, search_range):
        """
        Проверяет юзера на наличие его в таблицах лайков и игноров
        Если совпадение есть, то Юзер пропускается в выдаче
        :param vk_id: Юзер id, которого нашли
        :param vk_search_id: Юзер id, кто искал
        :param search_range: диапозон поиска
        :return: True или False
        """
        result = self.session.query(DatingUser).filter_by(dating_user_id=vk_id, user_id=vk_search_id,
                                                          user_id_range=search_range)
        entry = self.session.query(result.exists()).one()[0]
        if entry:
            return entry
        else:
            result = self.session.query(IgnoreUser).filter_by(user_ignore_id=vk_id, user_id=vk_search_id,
                                                              user_id_range=search_range)
            entry = self.session.query(result.exists()).one()[0]
            if entry:
                return entry
            else:
                result = self.session.query(SkippedUser).filter_by(skipped_id=vk_id, user_id=vk_search_id,
                                                                   user_id_range=search_range)
                entry = self.session.query(result.exists()).one()[0]
        return entry

    def find_dating_user_photo(self, user_vk_id, user_search_id, search_range):
        photo_user_data = {}
        dating_id = self.session.query(DatingUser).filter_by(dating_user_id=user_vk_id, user_id=user_search_id,
                                                             user_id_range=search_range).one()
        photos = self.session.query(UserPhoto).filter_by(dating_id=dating_id.dating_id).all()
        for user_photo in photos:
            link = user_photo.photo_link
            like = user_photo.photo_likes
            photo_user_data[like] = link
        return photo_user_data

    def remove_dating_user(self):
        pass


if __name__ == '__main__':
    new_used = ORMFunctions(session)
    # print(new_used.find_dating_user_photo(250183789, 13924278, '32-39'))
    # print(ORMFunctions(session).is_id_and_range_inside_user_vk(13924278, '38-40'))
    # new_used.show_id_and_range(13924278)
    # new_used.select_photo(143041215, 1582074)
    # print(new_used.is_inside_ignore_dating_skipped(45269508, 13924278, '30-31'))
    # print(new_used.show_dating_users(13924278, 1))
    # new_used.is_inside_ignore_dating_skipped(18349823)
    pass
