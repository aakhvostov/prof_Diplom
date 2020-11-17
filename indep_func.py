from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import re
from datetime import date


Base = declarative_base()
DSN = 'postgres://nelot:netology@localhost:5432/netology'
engine = create_engine(DSN)
Session = sessionmaker(bind=engine)
session = Session()

def get_birth_date(bdate):
    try:
        a = bdate[2]
        date_info = re.findall(r'(\d\d?).(\d\d?)?.?(\d{4})?', bdate)[0]
        if date_info[2]:
            age = calculate_age(date_info[0], date_info[1], date_info[2])
        else:
            age = bdate
    except KeyError:
        age = 'no data'
    return age


def calculate_age(day, month, year):
    """
    вычисляет возраст человека
    :param year: год
    :param month: месяц
    :param day: день
    :return: вызраста в годах
    """
    today = date.today()
    year = (int(today.year) - int(year) - int((today.month, today.day) < (int(month), int(day))))
    return year


if __name__ == '__main__':
    print(f'Сердечко - \U0001F497')
    print(f'Галочка - \U00002705')
    print(f'Крестик - \U0000274C')
    print(f'Пропуск - \U0000267B')
    print(f'Exit - \U000024BA\U000024CD\U000024BE\U000024C9')
    pass
