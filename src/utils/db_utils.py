import pathlib
from fastapi import Request
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from pathlib import Path
import os
from svc_users.models.users import Base
from utils.config_utils import get_service_name
from fastapi import HTTPException
from functools import partial

current_file_folder = os.path.dirname(os.path.realpath(__file__))

# Create a new function with the Session argument bound to the Session object
#
# def get_session_by_request(request):
#
#     base_url_port = request.base_url.port
#     service_name = get_service_name(base_url_port)
#     db_path = f'{current_file_folder}/../../dbs/{service_name}.db'
#     engine = create_engine("sqlite:///" + db_path)
#
#     Session = sessionmaker(bind=engine)
#     return Session

def get_session_by_request(request: Request):
    base_url_port = request.base_url.port
    service_name = get_service_name(base_url_port)
    db_path = f'{current_file_folder}/../../dbs/{service_name}.db'
    engine = create_engine("sqlite:///" + db_path)

    Session = sessionmaker(bind=engine)
    return Session()


def get_session_by_svc_name(service_name):
    db_path = f'{current_file_folder}/../../dbs/{service_name}.db'
    engine = create_engine("sqlite:///" + db_path)
    Session = sessionmaker(bind=engine)
    return Session()

def get_db(Session):
    db = Session()
    try:
        return db
    finally:
        db.close()


def create_db():
    """
    Function used to create a database
    """
    db_path = Path().resolve()
    if os.path.isfile(str(db_path)):
        print("Database already exists")
    else:
        Base.metadata.create_all(engine)
        print("Database successfully created")


if __name__ == '__main__':
    create_db()
