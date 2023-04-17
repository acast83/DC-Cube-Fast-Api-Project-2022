from fastapi import status, HTTPException, Depends, Header,Request
from sqlalchemy.orm import Session
import jwt
import yaml
import pathlib
from functools import partial
from svc_users.models.users import User
from utils.db_utils import get_session_by_request,get_session_by_svc_name,get_db
from utils.logging_setup import get_logger
import os

current_file_folder = os.path.dirname(os.path.realpath(__file__))

JWT_SECRET = os.getenv("JWT_KEY")
ALGORITHM = os.getenv("ALGORITHM")


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





# def get_token_dependency(token: str = Header(..., name="Authorization", alias="Authorization")):
#     if not token:
#         raise HTTPException(status_code=401, detail="Invalid token format")
#     return token

# async def get_request(request: Request):
#     return request

def get_database_dependency(db: Session = Depends(get_db)):
    return db

def get_auth_dependencies(request: Request,
                          # db: Session = Depends(lambda req: get_db(Session=get_session_by_request(req)))
                          ):
    token_data = check_token(request=request)
    log = get_logger(request=request)

    handler = type("Handler", (), {#"db": db,
                                   "id_user": token_data["id_user"],
                                   "request": request,
                                    "log":log
    })
    return handler








