"""Sqlalchemy Models"""

from sqlalchemy import Column, Integer, String, ForeignKey, Index
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class DbCountryModel(Base):
    """SQlalchemy model class used for table countries"""
    __tablename__ = "geoloc_countries"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    # __table_args__ = (Index('idx_country_id_name', id),)


class DbCity(Base):
    """SQlalchemy model class used for table cities"""
    __tablename__ = "geoloc_cities"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    lat = Column(Integer, nullable=False)
    lng = Column(Integer, nullable=False)
    population = Column(Integer, nullable=True)
    country_id = Column(Integer, ForeignKey('geoloc_countries.id'))
    country = relationship('DbCountryModel', backref='cities')
