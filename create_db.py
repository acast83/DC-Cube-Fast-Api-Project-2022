"""
Python module used for purpose of creating a database and database tables
based on Sqlalchemy model from models.py
"""
import os.path
from models import Base, engine


def create_db():
    """
    Function used to create a database
    """
    if os.path.isfile('database.db'):
        print("Database already exists")
    else:
        Base.metadata.create_all(engine)
        print("Database successfully created")


if __name__ == '__main__':
    create_db()
