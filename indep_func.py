import re
from datetime import date


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
