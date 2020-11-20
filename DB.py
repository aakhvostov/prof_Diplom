from sqlalchemy import exc
from indep_func import engine


class PostgresBase:

    def __init__(self):
        self.connection = engine.connect()
        self.user_output_id = ""

    def drop_tables(self, tables_name):
        for table in tables_name.split(","):
            try:
                self.connection.execute(f"DROP TABLE {table} CASCADE;")
                print(f'таблица {table} удалена')
            except NameError:
                print(f'Таблицы "{tables_name}" не найдено')
            except AttributeError:
                print('Необходимо передать название таблицы')
            except exc.ProgrammingError:
                print('Не верные данные или таблиц больше нет')


if __name__ == '__main__':
    # PostgresBase().drop_tables('user_vk,ignore_user,dating_user,user_photo,skipped_user')
    pass
