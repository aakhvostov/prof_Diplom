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


def get_age(birth_info):
    date_info = re.findall(r'(\d\d?).(\d\d?)?.?(\d{4})?', birth_info)[0]
    if date_info[2]:
        today = date.today()
        age = (int(today.year) - int(date_info[2]) - int(
            (today.month, today.day) < (int(date_info[1]), int(date_info[0]))))
    else:
        age = f"{date_info[0]}.{date_info[1]}"
    return age


if __name__ == '__main__':
    pass
