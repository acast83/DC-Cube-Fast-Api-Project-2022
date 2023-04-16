from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from pathlib import Path
import os
from src.svc_geoloc.models.geoloc import Base

current_file_folder = os.path.dirname(os.path.realpath(__file__))
db_path = f'{current_file_folder}/../../../dbs/geoloc.db'
engine = create_engine("sqlite:///" + db_path)

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
    db_path = Path().resolve()
    if os.path.isfile(db_path):
        print("Database already exists")
    else:
        Base.metadata.create_all(engine)
        print("Database successfully created")


if __name__ == '__main__':
    create_db()
