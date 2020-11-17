from sqlalchemy import Column, Integer, String, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from indep_func import Base, engine, Session


class UserVk(Base):
    __tablename__ = 'user_vk'

    user_id = Column(Integer, primary_key=True)
    user_firstname = Column(String(40))
    user_lastname = Column(String(40))
    user_age = Column(String(15))
    search_range = Column(String(40))
    sex = Column(Integer)
    user_city = Column(String(40))
    dating_users = relationship('DatingUser', backref='user_vk')
    ignore_users = relationship('IgnoreUser', backref='user_vk')
    skipped_users = relationship('SkippedUser', backref='user_vk')


class DatingUser(Base):
    __tablename__ = 'dating_user'

    dating_id = Column(Integer, primary_key=True)
    dating_user_id = Column(Integer)
    user_firstname = Column(String(40))
    user_lastname = Column(String(40))
    user_age = Column(String(15))
    user_id = Column(Integer, ForeignKey('user_vk.user_id'))


class UserPhoto(Base):
    __tablename__ = 'user_photo'

    user_photo_id = Column(Integer, primary_key=True)
    photo_link = Column(String)
    photo_likes = Column(Integer)
    dating_id = Column(Integer, ForeignKey('dating_user.dating_id'))


class IgnoreUser(Base):
    __tablename__ = 'ignore_user'

    user_ignore_id = Column(Integer)
    user_id = Column(Integer, ForeignKey('user_vk.user_id'))

    __table_args__ = (PrimaryKeyConstraint(user_ignore_id, user_id),)


class SkippedUser(Base):
    __tablename__ = 'skipped_user'

    skipped_id = Column(Integer)
    user_id = Column(Integer, ForeignKey('user_vk.user_id'))

    __table_args__ = (PrimaryKeyConstraint(skipped_id, user_id),)


if __name__ == '__main__':
    # Base.metadata.create_all(engine)
    # session = Session()
    # ignore_ids = [ignore_user.user_ignore_id for ignore_user in
    #               session.query(UserVk).filter_by(user_id=206241).first().ignore_users]

    # vk1 = UserVk(user_id=99999999, user_firstname='qqqqq', user_lastname='wwwwwww', user_age='28', search_range='30-31', sex=1, user_city='1')
    # session.add_all([vk1])
    # session.commit()

    # dat1 = DatingUser(dating_user_id=1234, user_firstname='qqqq', user_lastname='wwwww', user_age='32', user_id=99999999)
    # session.add_all([dat1])
    # session.commit()

    # ign1 = IgnoreUser(user_ignore_id=99999999, user_id=99999999)
    # session.add_all([ign1])
    # session.commit()
    pass