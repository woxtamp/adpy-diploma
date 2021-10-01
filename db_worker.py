import os
import sqlalchemy as sq
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

dotenv_path = os.path.join('.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
dsn = os.getenv('DSN')

engine = create_engine(dsn)
session = Session(bind=engine)

Base = declarative_base()


class VkUserDb(Base):
    __tablename__ = 'vk_user'

    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer)
    age = sq.Column(sq.Integer)
    sex = sq.Column(sq.Integer)
    city_name = sq.Column(sq.String)
    city_id = sq.Column(sq.Integer)


class VkSearchParams(Base):
    __tablename__ = 'vk_search_params'

    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer)
    age_from = sq.Column(sq.Integer)
    age_to = sq.Column(sq.Integer)
    sex = sq.Column(sq.Integer)
    city_name = sq.Column(sq.String)
    city_id = sq.Column(sq.Integer)


class VkFindUser(Base):
    __tablename__ = 'vk_find_user'

    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer)
    vk_search_id = sq.Column(sq.Integer)

def add_user_to_db(vk_id, age, sex, city_name, city_id):
    if session.query(VkUserDb).filter_by(vk_id=vk_id).first() is not None:
        session.query(VkUserDb).filter_by(vk_id=vk_id).update(
            {'age': age, 'sex': sex, 'city_name': city_name, 'city_id': city_id}
        )
        session.commit()
    else:
        vk_user = VkUserDb(vk_id=vk_id, age=age, sex=sex, city_name=city_name, city_id=city_id)
        session.add(vk_user)
        session.commit()
        session.close()


def check_exist_city_id(vk_id):
    if session.query(VkSearchParams).filter_by(vk_id=vk_id, city_id=None).first() is None:
        return True
    else:
        return False


def add_search_params_to_db(vk_id, age_from, age_to, sex, city_name, city_id):
    if session.query(VkSearchParams).filter_by(vk_id=vk_id).first() is not None:
        session.query(VkSearchParams).filter_by(vk_id=vk_id).update(
            {'age_from': age_from, 'age_to': age_to, 'sex': sex, 'city_name': city_name, 'city_id': city_id}
        )
        session.commit()
    else:
        vk_search_params = VkSearchParams(vk_id=vk_id, age_from=age_from, age_to=age_to, sex=sex,
                                          city_name=city_name, city_id=city_id)
        session.add(vk_search_params)
        session.commit()
        session.close()


def add_find_user_to_db(vk_id, vk_search_id):
    if session.query(VkFindUser).filter_by(vk_id=vk_id, vk_search_id=vk_search_id).first() is not None:
        pass
    else:
        vk_search_params = VkFindUser(vk_id=vk_id, vk_search_id=vk_search_id)
        session.add(vk_search_params)
        session.commit()
        session.close()


def check_exist_find_user(vk_id, vk_search_id):
    if session.query(VkFindUser).filter_by(vk_id=vk_id, vk_search_id=vk_search_id).first() is None:
        return True
    else:
        return False
