import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()
DSN = 'postgres://nelot:netology@localhost:5432/netology'
engine = sq.create_engine(DSN, echo=True)
Session = sessionmaker(bind=engine)


class UserVk(Base):
    __tablename__ = 'user_vk'

    user_id = sq.Column(sq.Integer, primary_key=True)
    user_firstname = sq.Column(sq.String(40))
    user_lastname = sq.Column(sq.String(40))
    user_age = sq.Column(sq.String(15))
    search_range = sq.Column(sq.String(40))
    sex = sq.Column(sq.Integer)
    user_city = sq.Column(sq.String(40))
    dating_users = relationship('DatingUser', backhef='user_vk')


class DatingUser(Base):
    __tablename__ = 'dating_user'

    dating_id = sq.Column(sq.Integer, primary_key=True)
    dating_user_id = sq.Column(sq.Integer)
    user_firstname = sq.Column(sq.String(40))
    user_lastname = sq.Column(sq.String(40))
    user_age = sq.Column(sq.String(15))
    user_id = sq.Column(sq.Integer, sq.ForeignKey('user_vk.user_id'))


class UserPhoto(Base):
    __tablename__ = 'user_photo'

    user_photo_id = sq.Column(sq.Integer, primary_key=True)
    photo_link = sq.Column(sq.String)
    photo_likes = sq.Column(sq.Integer)
    dating_id = sq.Column(sq.Integer, sq.ForeignKey('dating_user.dating_id'))


class IgnoreUser(Base):
    __tablename__ = 'ignore_user'

    user_ignore_id = sq.Column(sq.Integer)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('user_vk.user_id'))

    __table_args__ = (sq.PrimaryKeyConstraint(user_id, user_ignore_id),)


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    session = Session()
    # vk1 = UserVk(user_id=99999999, user_firstname='qqqqq', user_lastname='wwwwwww', user_age='28', search_range='30-31', sex=1, user_city='1')
    # session.add_all([vk1])
    # session.commit()
    # dat1 = DatingUser(dating_user_id=1234, user_firstname='qqqq', user_lastname='wwwww', user_age='32', user_id=99999999)
    # session.add_all([dat1])
    # session.commit()
    # ign1 = IgnoreUser(user_ignore_id=99999999, user_id=99999999)
    # session.add_all([ign1])
    # session.commit()
    vks = session.query(UserVk).filter_by(user_id=99999999)
    print(vks[0].user_age)
