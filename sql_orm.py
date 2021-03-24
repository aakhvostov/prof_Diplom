from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
DSN = 'postgresql://nelot:netology@localhost:5432/netology'
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
    state = Column(String(20))
    datings = relationship('DatingUser')
    ignores = relationship('IgnoreUser')

    def remove_user_vk(self):
        session.delete(self)
        session.commit()


class Search(Base):
    __tablename__ = 'search'

    search_city = Column(String(40))
    search_sex = Column(Integer)
    search_relation = Column(Integer)
    search_from = Column(Integer)
    search_to = Column(Integer)
    search_user = relationship("UserVk")
    user_id = Column(Integer, ForeignKey('user_vk.user_id'), primary_key=True)

    def add_search(self, user_id):
        self.user_id = user_id
        session.add(self)
        session.commit()

    def remove_search(self):
        session.delete(self)
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

    def remove_dating_user(self):
        """
        Удаляет человека из таблицы DatingUser
        """
        session.delete(self)
        session.commit()


class UserPhoto(Base):
    __tablename__ = 'user_photo'

    photo_id = Column(Integer, primary_key=True)
    photo_link = Column(String)
    photo_likes = Column(Integer)
    attachment_id = Column(Integer)
    dating_id = Column(Integer, ForeignKey('dating_user.dating_id'))

    def add_user_photo(self, likes_attechments_links, user_vk_id, search_user_id):
        for like, link in likes_attechments_links.items():
            self.photo_likes = like
            self.attachment_id = link[0]
            self.photo_link = link[1]
            self.dating_id = get_dating_id(user_vk_id, search_user_id)
            session.add(self)
            session.commit()


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
        return self.ignore_id

    def remove_ignore_user(self):
        """
        Удаляет запись из таблицы IgnoreUser
        """
        session.delete(self)
        session.commit()


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
        return self.skip_id

    def remove_skip_user(self):
        """
        Удаляет запись из таблицы SkippedUser
        """
        session.delete(self)
        session.commit()


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
        result2 = session.query(IgnoreUser).filter_by(ignore_user_id=user_vk_id, user_id=search_user_id)
        if session.query(result2.exists()).one()[0]:
            return True
        result3 = session.query(SkippedUser).filter_by(skip_user_id=user_vk_id, user_id=search_user_id)
        return session.query(result3.exists()).one()[0]

    @staticmethod
    def looking_for_user_vk(user_id):
        for user, search in session.query(UserVk, Search).filter_by(user_id=user_id).all():
            return user, search

    @staticmethod
    def add_objects(user_id, params):
        user = UserVk(user_id=user_id, user_firstname=params[0], user_lastname=params[1],
                      user_age=params[2], user_sex=params[3], user_city=params[4], state='Hello')
        search = Search(search_user=user)
        session.add_all([user, search])
        session.commit()
        return user, search

    def get_dating_list(self, vk_search_id):
        """Функция создает список всех понравившихся пользователей"""
        self.dating_list = session.query(UserVk).filter(UserVk.user_id == vk_search_id).one().datings

    def show_dating_user(self):
        """Функция выдает по одному понравившихся пользователей"""
        try:
            dat_name = f'{self.dating_list[self.dating_count].dating_firstname} ' \
                f'{self.dating_list[self.dating_count].dating_lastname}'
            dat_age = self.dating_list[self.dating_count].dating_age
            dat_id = self.dating_list[self.dating_count].dating_user_id
            dat_attach = self.dating_list[self.dating_count].photos[0].attachment_id
            return dat_name, dat_age, dat_id, dat_attach
        except IndexError:
            return False

    def get_ignore_list(self, vk_search_id):
        """Функция создает список всех игнорируемых пользователей"""
        self.ignore_list = session.query(UserVk).filter(UserVk.user_id == vk_search_id).one().ignores

    def show_ignore_user(self):
        """Функция выдает по одному игнорируемых пользователей"""
        try:
            return self.ignore_list[self.ignore_count].ignore_user_id
        except IndexError:
            return False


if __name__ == '__main__':
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    # ORMFunctions.looking_for_user_vk(13924278)
    # print(session.query(UserVk, Search).filter_by(user_id=13924278).first())
