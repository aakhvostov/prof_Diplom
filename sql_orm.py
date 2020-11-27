from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
DSN = 'postgres://nelot:netology@localhost:5432/netology'
engine = create_engine(DSN)
Session = sessionmaker(bind=engine)
session = Session()


class UserVk(Base):
    __tablename__ = 'user_vk'

    user_id = Column(Integer, primary_key=True)
    user_firstname = Column(String(40))
    user_lastname = Column(String(40))
    user_age = Column(String(15))
    user_sex = Column(Integer)
    user_city = Column(String(40))
    searches = relationship('Search', backref='users_id')

    def add_user_vk(self, user_id, firstname, lastname, age, sex, city):
        """
        Добавляет человека в базу таблицу user_vk
        """
        self.user_id = user_id
        self.user_firstname = firstname
        self.user_lastname = lastname
        self.user_age = age
        self.user_sex = sex
        self.user_city = city
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


class State(Base):
    __tablename__ = 'state'

    user_id = Column(Integer, ForeignKey('user_vk.user_id'), primary_key=True)
    state = Column(String)


class Search(Base):
    __tablename__ = 'search'

    search_id = Column(Integer, primary_key=True)
    search_city = Column(String(40))
    search_sex = Column(Integer)
    search_relation = Column(Integer)
    search_from = Column(Integer)
    search_to = Column(Integer)

    user_id = Column(Integer, ForeignKey('user_vk.user_id'))

    def add_search(self, user_id):
        """
        Добавляет человека в базу таблицу user_vk
        """
        self.user_id = user_id
        session.add(self)
        session.commit()
        return self.search_id


class DatingUser(Base):
    __tablename__ = 'dating_user'

    dating_id = Column(Integer, primary_key=True)
    dating_user_id = Column(Integer)
    dating_firstname = Column(String(40))
    dating_lastname = Column(String(40))
    dating_age = Column(String(15))
    search_id = Column(Integer, ForeignKey('search.search_id'))
    photos = relationship('UserPhoto', backref='user_photo')

    def add_dating_user(self, dating_user_id, dating_firstname, dating_lastname, dating_age, search_id):
        """
        Добавляет человека в таблицу dating_user
        """
        self.dating_user_id = dating_user_id
        self.dating_firstname = dating_firstname
        self.dating_lastname = dating_lastname
        self.dating_age = dating_age
        self.search_id = search_id
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

    photo_id = Column(Integer, primary_key=True)
    photo_link = Column(String)
    photo_likes = Column(Integer)
    dating_id = Column(Integer, ForeignKey('dating_user.dating_id'))

    def add_user_photo(self, links_likes, user_vk_id, search_id):
        for like, link in links_likes.items():
            self.photo_link = link
            self.photo_likes = like
            self.dating_id = get_dating_id(user_vk_id, search_id)
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

    ignore_id = Column(Integer, primary_key=True)
    ignore_user_id = Column(Integer)
    search_id = Column(Integer, ForeignKey('search.search_id'))

    def add_ignore_user(self, ignore_user_id, search_id):
        """
        Добавляет человека в таблицу ignore_user
        """
        self.ignore_user_id = ignore_user_id
        self.search_id = search_id
        session.add(self)
        session.commit()
        print(f'юзер {self.ignore_user_id}  добавлен в игнор список')
        return self.ignore_id

    def remove_ignore_user(self):
        """
        Удаляет запись из таблицы IgnoreUser
        """
        session.delete(self)
        session.commit()
        print(f'юзер удален из ignore_user')


class SkippedUser(Base):
    __tablename__ = 'skipped_user'

    skip_id = Column(Integer, primary_key=True)
    skip_user_id = Column(Integer)
    search_id = Column(Integer, ForeignKey('search.search_id'))

    def add_skipped_user(self, skip_user_id, search_id):
        """
        Добавляет человека в таблицу ignore_user
        """
        self.skip_user_id = skip_user_id
        self.search_id = search_id
        session.add(self)
        session.commit()
        print(f'юзер {self.skip_id} добавлен в скип список')
        return self.skip_id

    def remove_skip_user(self):
        """
        Удаляет запись из таблицы SkippedUser
        """
        session.delete(self)
        session.commit()
        print(f'юзер удален из skipped_user')


def get_dating_id(user_vk_id, search_id):
    """
    Функция ищет dating_id в таблице Dating_user и возвращает его для дальнейшего использования при добавлении
    фотографии по этой паре
    :param user_vk_id:      Id пары
    :param search_id:       Id диапазона поиска
    :return:                dating_id (primary key)
    """
    dating_id = session.query(DatingUser).filter_by(dating_user_id=user_vk_id,
                                                    search_id=search_id).all()
    return dating_id[0].dating_id


class ORMFunctions:
    def __init__(self):
        self.search_range_dict = {}

    def show_id_and_range(self, vk_search_id):
        """
        Функция для вывода истории поиска Юзера
        :param vk_search_id:    Id человека ведущего поиск
        :return:                словарь с диапозонами поиска
        """
        result = session.query(UserVk.search_range).filter_by(user_id=vk_search_id).all()
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
        result = session.query(UserVk).filter_by(user_id=vk_search_id,
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
        result = session.query(DatingUser).filter_by(user_id=vk_search_id,
                                                     user_id_range=self.search_range_dict[find_range]).all()
        for user_obj in result:
            dating_dict[user_obj.dating_id] = user_obj.dating_user_id
        return dating_dict, result

    def get_ignore_users(self, vk_search_id, find_range):
        """
        Функция для поиска людей в Ignore_user по паре Id+range
        :param vk_search_id:    Id человека ведущего поиск
        :param find_range:      диапазон поиска
        :return:                словарь key + user_ignore_id из Ignore_user
                                и список самих объектов из таблицы Ignore_user
        """
        ignore_dict = {}
        result = session.query(IgnoreUser).filter_by(user_id=vk_search_id,
                                                     user_id_range=self.search_range_dict[find_range]).all()
        for key, user_obj in enumerate(result):
            ignore_dict[key] = user_obj.user_ignore_id
        return ignore_dict, result


# def is_id_and_range_inside_user_vk(vk_search_id, search_range: str):
#     """
#     Функция проверяет наличия составного primary key (user_id + range) в таблице User_vk
#     :param vk_search_id:    Id человека ведущего поиск
#     :param search_range:    диапозон поиска
#     :return:                True или False
#     """
#     result = session.query(UserVk).filter_by(user_id=vk_search_id, search_range=search_range)
#     return session.query(result.exists()).one()[0]
#
#
# def get_dating_search_range(dating_id):
#     """
#     Функция ищет в таблице Dating Users по Id диапозон поиска
#     :param dating_id: Id записи в таблице Dating Users
#     :return: диапазон поиска
#     """
#     search_range = session.query(DatingUser).filter(DatingUser.dating_id == dating_id).one()
#     return search_range.user_id_range


if __name__ == '__main__':
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    pass
