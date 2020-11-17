from sqlalchemy import Column, Integer, String, ForeignKey, PrimaryKeyConstraint, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from indep_func import Base, session, engine


class UserVk(Base):
    __tablename__ = 'user_vk'

    user_id = Column(Integer)
    user_firstname = Column(String(40))
    user_lastname = Column(String(40))
    user_age = Column(String(15))
    search_range = Column(String(15))
    sex = Column(Integer)
    user_city = Column(String(40))
    dating_users = relationship('DatingUser', backref='user_vk')
    ignore_users = relationship('IgnoreUser', backref='user_vk')
    skipped_users = relationship('SkippedUser', backref='user_vk')
    __table_args__ = (PrimaryKeyConstraint(user_id, search_range),)


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


class UserPhoto(Base):
    __tablename__ = 'user_photo'

    user_photo_id = Column(Integer, primary_key=True)
    photo_link = Column(String)
    photo_likes = Column(Integer)
    dating_id = Column(Integer, ForeignKey('dating_user.dating_id'))


class IgnoreUser(Base):
    __tablename__ = 'ignore_user'

    user_ignore_id = Column(Integer)
    user_id = Column(Integer)
    user_id_range = Column(String(15))
    __table_args__ = (PrimaryKeyConstraint(user_ignore_id, user_id),
                      (ForeignKeyConstraint(('user_id', 'user_id_range'), [UserVk.user_id, UserVk.search_range])),)


class SkippedUser(Base):
    __tablename__ = 'skipped_user'

    skipped_id = Column(Integer)
    user_id = Column(Integer)
    user_id_range = Column(String(15))
    __table_args__ = (PrimaryKeyConstraint(skipped_id, user_id),
                      (ForeignKeyConstraint(('user_id', 'user_id_range'), [UserVk.user_id, UserVk.search_range])),)


class OrmFunctions:

    def __init__(self, session_elem):
        self.session = session_elem

    def is_id_inside_user_vk(self, user_vk_id: int):        # не пользуется
        result = self.session.query(UserVk).filter(UserVk.user_id == user_vk_id)
        return self.session.query(result.exists()).one()[0]

    def is_id_and_range_inside_user_vk(self, user_vk_id, age_range: str):
        result = self.session.query(UserVk).filter(UserVk.user_id == user_vk_id).filter(
            UserVk.search_range == age_range)
        return self.session.query(result.exists()).one()[0]

    def is_inside_ignore_dating_skipped(self, vk_search_id):
        result = self.session.query(UserVk).join(DatingUser).join(IgnoreUser).join(SkippedUser).filter(
            UserVk.user_id == vk_search_id)
        print(result)
        print()
        print(self.session.query(result.exists()).one()[0])
        # return self.session.query(result.exists()).one()[0]


if __name__ == '__main__':
    # Base.metadata.create_all(engine)
    # OrmFunctions(session).is_inside_ignore_dating_skipped(5015179)

    # ignore_ids = [ignore_user.user_ignore_id for ignore_user in session.query(
    #     UserVk).filter_by(user_id=206241).first().ignore_users]

    # vk1 = UserVk(user_id=99999999, user_firstname='Андрей', user_lastname='Хвостов',
    #              user_age='28', search_range='30-31', sex=1, user_city='1')
    # session.add_all([vk1])
    # session.commit()

    # dat1 = DatingUser(dating_user_id=1234, user_firstname='Андрей', user_lastname='Хвостов',
    #                   user_age='32', user_id=99999999)
    # session.add_all([dat1])
    # session.commit()

    # ign1 = IgnoreUser(user_ignore_id=99999999, user_id=99999999)
    # session.add_all([ign1])
    # session.commit()
    pass
