"""Sqlalchemy Models"""

from sqlalchemy import Column, Integer, String, ForeignKey,Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class CountryModel(Base):
    """SQlalchemy model class used for table countries"""
    __tablename__ = "countries"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    # __table_args__ = (Index('idx_country_id_name', id),)


class CityModel(Base):
    """SQlalchemy model class used for table cities"""
    __tablename__ = "cities"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    lat = Column(Integer, nullable=False)
    lng = Column(Integer, nullable=False)
    population = Column(Integer, nullable=True)
    country_id = Column(Integer, ForeignKey('countries.id'))
    country = relationship('CountryModel', backref='cities')



class User(Base):
    """SQlalchemy model class used for table users"""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, )
    username = Column(String(50), nullable=False)
    password = Column(String(50), nullable=False)
