import pytest
from sql_orm import UserVk, DatingUser, IgnoreUser, SkippedUser, session, engine, Base, Search
from server import Server


# def server_dict_input():
#     server1



@pytest.fixture(scope="class")
def create_objects():
    """Фикстура по заполнению базы данных пользователями"""
    user = UserVk(user_id=1, user_firstname='first_name', user_lastname='last_name', user_age=20, user_sex=1,
                  user_city='city', state='Hello')
    session.add(user)
    session.commit()
    search = Search(user_id=1)
    session.add(search)
    session.commit()
    yield user, search
    search.remove_search()
    user.remove_user_vk()


@pytest.fixture(scope="class")
def db_input():
    """Фикстура по заполнению базы данных пользователями"""
    user = UserVk(user_id=1, user_firstname='first_name', user_lastname='last_name',
                  user_age=20, user_sex=1, user_city='city')
    session.add(user)
    session.commit()
    dating = DatingUser(dating_user_id=11, dating_firstname='d_first_name', dating_lastname='d_last_name',
                        dating_age=20, user_id=1)
    ignore = IgnoreUser(ignore_user_id=22, user_id=1)
    skip = SkippedUser(skip_user_id=33, user_id=1)
    session.add_all([dating, ignore, skip])
    session.commit()
    yield
    dating.remove_dating_user()
    ignore.remove_ignore_user()
    skip.remove_skip_user()
    user.remove_user_vk()


@pytest.fixture(scope="class")
def clean_db():
    """Функция очищает базы данных"""
    yield
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
