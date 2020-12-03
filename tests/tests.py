import pytest
from server import Server
from sql_orm import session
from sql_orm import ORMFunctions


orm = ORMFunctions()
token = "fe40651e2f644afbf32552f6fabc7d471bbab8a43fffd2b08d62d63e955977892f8f1a468018b8f2ee2f5"
server1 = Server(token, session)


class TestServerStates:

    # проблема с event.text - в init Server(), self.event = None
    @pytest.mark.parametrize("args, expected_result", [
        ("выйти", False),
        ("привет", True)
    ])
    @pytest.mark.usefixtures("create_objects")
    def test_hello_state(self, args, expected_result, create_objects):
        res = server1.hello_state(create_objects)
        assert res == expected_result


class TestOrmFunctions:

    @pytest.mark.parametrize("args, expected_result", [
        ((11, 1), True),
        ((44, 1), False),
        ((22, 1), True),
        ((33, 1), True)
    ])
    @pytest.mark.usefixtures("db_input")
    def test_is_viewed(self, args, expected_result):
        """Функция тестирует проверку наличия пользователя в списках Datings, Ignores, Skipped"""
        res = orm.is_viewed(*args)
        assert res == expected_result

    @pytest.mark.parametrize("user_id, args, expected_result", [
        (2, ['u_first_name', 'u_last_name', 20, 2, 'u_city'], tuple)
    ])
    @pytest.mark.usefixtures("clean_db")
    def test_add_objects(self, user_id, args, expected_result):
        """Функция проверяет тип возвращаемых данных"""
        res = orm.add_objects(user_id, args)
        assert isinstance(res, expected_result)
