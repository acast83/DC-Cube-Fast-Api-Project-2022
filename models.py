"""Sqlalchemy Models"""

from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey,Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()
DIR_PATH = str(Path().absolute())
engine = create_engine("sqlite:///" + DIR_PATH +
                       "/database.db", echo=False)

Session = sessionmaker(bind=engine)
session = Session()


class CountryModel(Base):
    """SQlalchemy model class used for table countries"""
    __tablename__ = "countries"
    id = Column(Integer, primary_key=True)
    country_name = Column(String(50), nullable=False)
    __table_args__ = (Index('idx_country_id_name', id),)


class CityModel(Base):
    """SQlalchemy model class used for table cities"""
    __tablename__ = "cities"
    id = Column(Integer, primary_key=True)
    city_ascii_name = Column(String(50), nullable=False)
    lat = Column(Integer, nullable=False)
    lng = Column(Integer, nullable=False)
    population = Column(Integer, nullable=True)
    country_id = Column(Integer, ForeignKey('countries.id'))
    country = relationship('CountryModel', backref='cities')



class UserModel(Base):
    """SQlalchemy model class used for table users"""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, )
    username = Column(String(50), nullable=False)
    hashed_password = Column(String(50), nullable=False)
