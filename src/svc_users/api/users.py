from fastapi import FastAPI, status, HTTPException, Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
import jwt
from src.svc_users.models.users import User
from src.svc_users.utils.create_db import get_db
from src.svc_users.models.user_pydantic_models import PyUser
from src.svc_users.utils.logging_setup import log
from dotenv import load_dotenv
import uvicorn

load_dotenv()
from src.utils.api_utils import JWT_SECRET, ALGORITHM, get_auth_dependencies

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/login')
app = FastAPI()


@app.get("/about")
def root():
    """
    Root endpoint function
    """
    return {"service": "users"}


@app.post("/sign_up")
def create_new_user(user: PyUser, db: Session = Depends(get_db)):
    """
    Function used for registering new user.
    Input: allowed only alphanumeric characters
    and special characters (_ and -).
    Output: funtions returns json with new user's token
    """

    # search user table for existing username
    existing_user = db.query(User).filter_by(
        username=user.username).one_or_none()

    if existing_user:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail="USER_ALREADY_EXISTS")

    try:
        # create new user
        new_user = User(username=user.username,
                        password=bcrypt.hash(user.password))
        db.add(new_user)
        db.commit()

        log.info(f"New user created. Username {user.username}")

        # create a new user token
        user_dict = {"username": new_user.username,
                     "password": new_user.password}

        token = jwt.encode(user_dict, key=JWT_SECRET, algorithm=ALGORITHM)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="ERROR_WHILE_CREATING_USER")

    return {"access_token": token, "token_type": "bearer"}


@app.post("/login")
def login(user: PyUser, db: Session = Depends(get_db)):
    """
    Function used for user login.
    Input: user provides username and password
    Output: if user exists, function returns json with user's token
    """

    # find user based on input username value
    db_user = db.query(User).filter_by(
        username=user.username).one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="USER_NOT_FOUND")

    # Verify input password
    try:
        bcrypt.verify(user.password, db_user.password)
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="password doesn't match")

    # create a new user token
    user_dict = {"username": db_user.username,
                 "password": db_user.password}
    token = jwt.encode(payload=user_dict, key=JWT_SECRET, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}


@app.get("/protected")
async def protected_route(handler: object = Depends(get_auth_dependencies)):
    db = handler.db

    return {"success": "yeah"}


if __name__ == "__main__":
    uvicorn.run("users:app", host="0.0.0.0", port=8001, reload=True)
    ...
