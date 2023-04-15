from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from pathlib import Path
import os
from models import Base
DIR_PATH = str(Path().absolute())
engine = create_engine("sqlite:///" + DIR_PATH +
                       "/database.db", echo=False)

Session = sessionmaker(bind=engine)
session = Session()

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()

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