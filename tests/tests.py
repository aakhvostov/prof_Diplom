import pytest
from server import Server, VkUser
from sql_orm import ORMFunctions
from dataclasses import dataclass


orm = ORMFunctions()
vk_user = VkUser()
token = "fe40651e2f644afbf32552f6fabc7d471bbab8a43fffd2b08d62d63e955977892f8f1a468018b8f2ee2f5"
server1 = Server(token)


@dataclass
class Event:
    text: str
    user_id = ""


class TestServerStates:

    @pytest.mark.parametrize("args, expected_result", [
        ("выйти", False),
        ("выход", False)
    ])
    @pytest.mark.usefixtures("create_objects")
    def test_hello_state(self, args, expected_result, create_objects):
        """Тест возможности полного заверешения бота"""

        server1.event = Event(args)
        res = server1.hello_state(create_objects)
        assert res == expected_result

    # @pytest.mark.parametrize("args, expected_result", [
    #     ("выйти", False),
    #     ("выход", False)
    # ])
    # def test_city_state_excepts(self, args, expected_result):
    #     """Тест проверяет правильность исключений"""
    #     server1.event = Event(args)
    #     pass


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


class TestVkApiFunctions:

    @pytest.mark.parametrize("args, expected_result", [
        ("Москва", 1),
        ("Санкт", 2),
        (1, 1),
        (2, 2)
    ])
    def test_get_city_id_check(self, args, expected_result):
        """Тест проверяет корректность выдачи city_id"""
        res = vk_user.get_city_id(args)
        assert res == expected_result

    def test_get_city_id_get_raise(self):
        """Тест на отлов raise ValueError"""
        with pytest.raises(ValueError):
            vk_user.get_city_id(("Санкт", "Петербург"))


class TestServerFunctions:

    @pytest.mark.usefixtures("db_input")
    def test_get_founded_user_info(self):
        """Проверка выдачи None при наличии человека в списках лайк/игнор/скип"""
        vk_user.search_dating_user(23, 30, 1, 1, 6)
        server1.get_founded_user_info()
        pass