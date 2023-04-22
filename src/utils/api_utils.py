from fastapi import status, HTTPException, Depends, Header, Request
from sqlalchemy.orm import Session
import jwt
import yaml
import pathlib
from functools import partial
from svc_users.models.users import User
from utils.db_utils import get_session_by_request, get_session_by_svc_name, get_db
from utils.logging_setup import get_logger
import os

current_file_folder = os.path.dirname(os.path.realpath(__file__))

JWT_SECRET = os.getenv("JWT_KEY")
ALGORITHM = os.getenv("ALGORITHM")


class Handler:
    def __init__(self, session, request, id_user, log):
        self.db = session
        self.request = request
        self.id_user = id_user
        self.log = log


def check_token(request):
    token = request.headers["Authorization"]
    session = get_session_by_svc_name(service_name="users")

    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        db_user = session.query(User).filter_by(
            username=decoded_token["username"], password=decoded_token["password"]).one_or_none()
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="USER_NOT_FOUND")
        session.close()

        return {"id_user": db_user.id, "token": token}

    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_auth_dependencies(request: Request):
    token_data = check_token(request=request)
    log = get_logger(request=request)
    session = get_session_by_request(request=request)
    handler = Handler(session=session, request=request, id_user=token_data["id_user"], log=log)
    try:
        yield handler
    finally:
        session.close()


def get_non_auth_dependencies(request: Request):
    log = get_logger(request=request)
    session = get_session_by_request(request=request)

    handler = Handler(session=session, request=request, id_user=None, log=log)

    try:
        yield handler
    finally:
        session.close()
