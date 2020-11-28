import re

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
    searches = relationship('Search',)
    datings = relationship('DatingUser')
    ignores = relationship('IgnoreUser')


class State(Base):
    __tablename__ = 'state'

    user_id = Column(Integer, ForeignKey('user_vk.user_id'), primary_key=True)
    state = Column(String)


class Search(Base):
    __tablename__ = 'search'

    search_city = Column(String(40))
    search_sex = Column(Integer)
    search_relation = Column(Integer)
    search_from = Column(Integer)
    search_to = Column(Integer)
    user_id = Column(Integer, ForeignKey('user_vk.user_id'), primary_key=True)

    def add_search(self, user_id):
        self.user_id = user_id
        session.add(self)
        session.commit()


class DatingUser(Base):
    __tablename__ = 'dating_user'

    dating_id = Column(Integer, primary_key=True)
    dating_user_id = Column(Integer)
    dating_firstname = Column(String(40))
    dating_lastname = Column(String(40))
    dating_age = Column(String(15))
    user_id = Column(Integer, ForeignKey('user_vk.user_id'))
    photos = relationship('UserPhoto', backref='user_photo')

    def add_dating_user(self, dating_user_id, dating_firstname, dating_lastname, dating_age, user_id):
        """
        Добавляет человека в таблицу dating_user
        """
        self.dating_user_id = dating_user_id
        self.dating_firstname = dating_firstname
        self.dating_lastname = dating_lastname
        self.dating_age = dating_age
        self.user_id = user_id
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
    attachment_id = Column(Integer)
    dating_id = Column(Integer, ForeignKey('dating_user.dating_id'))

    def add_user_photo(self, likes_attechments_links, user_vk_id, search_user_id):
        pattern = re.compile(r"(\d+)\@(.+)")
        for like, link in likes_attechments_links.items():
            self.photo_likes = like
            self.photo_link = pattern.sub(r"\2", link)
            self.attachment_id = pattern.sub(r"\1", link)
            self.dating_id = get_dating_id(user_vk_id, search_user_id)
            session.add(self)
            session.commit()
            print(f'фото {like} добавлено в список')


class IgnoreUser(Base):
    __tablename__ = 'ignore_user'

    ignore_id = Column(Integer, primary_key=True)
    ignore_user_id = Column(Integer)
    user_id = Column(Integer, ForeignKey('user_vk.user_id'))

    def add_ignore_user(self, ignore_user_id, search_user_id):
        """
        Добавляет человека в таблицу ignore_user
        """
        self.ignore_user_id = ignore_user_id
        self.user_id = search_user_id
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
    user_id = Column(Integer, ForeignKey('user_vk.user_id'))

    def add_skipped_user(self, skip_user_id, search_user_id):
        """
        Добавляет человека в таблицу ignore_user
        """
        self.skip_user_id = skip_user_id
        self.user_id = search_user_id
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


def get_dating_id(user_vk_id, search_user_id):
    """
    Функция ищет dating_id в таблице Dating_user и возвращает его для дальнейшего использования при добавлении
    фотографии по этой паре
    :param user_vk_id:      Id пары
    :param search_user_id:  Id ведущего поиск
    :return:                dating_id (primary key)
    """
    dating_id = session.query(DatingUser).filter_by(dating_user_id=user_vk_id,
                                                    user_id=search_user_id).all()
    return dating_id[0].dating_id


class ORMFunctions:
    def __init__(self):
        self.search_range_dict = {}
        self.dating_list = []
        self.ignore_list = []
        self.dating_count = 0
        self.ignore_count = 0

    @staticmethod
    def is_viewed(user_vk_id, search_user_id):
        """
        Проверяет юзера на наличие его в таблицах лайков, игноров и пропусков
        Если совпадение есть, то Юзер пропускается в выдаче
        :param user_vk_id:      Id пары
        :param search_user_id:  Id ведущего поиск
        :return:                True или False
        """
        result1 = session.query(DatingUser).filter_by(dating_user_id=user_vk_id, user_id=search_user_id)
        if session.query(result1.exists()).one()[0]:
            return True
        else:
            result2 = session.query(IgnoreUser).filter_by(ignore_user_id=user_vk_id, user_id=search_user_id)
            if session.query(result2.exists()).one()[0]:
                return True
            else:
                result3 = session.query(SkippedUser).filter_by(skip_user_id=user_vk_id, user_id=search_user_id)
                return session.query(result3.exists()).one()[0]

    @staticmethod
    def looking_for_user_vk(user_id):
        for user, state, search in session.query(UserVk, State, Search).filter_by(user_id=user_id).all():
            return user, state, search

    @staticmethod
    def add_objects(user_id, params):
        user = UserVk(user_id=user_id, user_firstname=params[0], user_lastname=params[1],
                      user_age=params[2], user_sex=params[3], user_city=params[4])
        session.add(user)
        session.commit()
        state = State(user_id=user_id, state='Hello')
        session.add(state)
        session.commit()
        search = Search().add_search(user_id=user_id)
        session.add(state)
        session.commit()
        return user, state, search

    def get_dating_list(self, vk_search_id):
        """Функция создает список всех понравившихся пользователей"""
        self.dating_list = session.query(UserVk).filter(UserVk.user_id == vk_search_id).one().datings

    def show_dating_user(self):
        """Функция выдает по одному понравившихся пользователей"""
        dat_name = f'{self.dating_list[self.dating_count].dating_firstname} ' \
                    f'{self.dating_list[self.dating_count].dating_lastname}'
        dat_age = self.dating_list[self.dating_count].dating_age
        dat_id = self.dating_list[self.dating_count].dating_user_id
        dat_attach = self.dating_list[self.dating_count].photos[0].attachment_id
        return dat_name, dat_age, dat_id, dat_attach

    def get_ignore_list(self, vk_search_id):
        """Функция создает список всех игнорируемых пользователей"""
        self.ignore_list = session.query(UserVk).filter(UserVk.user_id == vk_search_id).one().ignores

    def show_ignore_user(self):
        """Функция выдает по одному игнорируемых пользователей"""
        return self.ignore_list[self.ignore_count].ignore_user_id


if __name__ == '__main__':
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    # orm = ORMFunctions()
    # orm.get_dating_list(13924278)
    # print(orm.show_dating_user())
    pass
