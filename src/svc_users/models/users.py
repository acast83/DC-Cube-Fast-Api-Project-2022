"""Sqlalchemy Models"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    """SQlalchemy model class used for table users"""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, )
    username = Column(String(50), nullable=False)
    password = Column(String(50), nullable=False)
