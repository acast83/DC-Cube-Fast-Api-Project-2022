from fastapi import FastAPI, Query, status, HTTPException, Depends,Header
from sqlalchemy.orm import Session
import jwt
from models import User
from db_utils import get_db
import os
JWT_SECRET = os.getenv("JWT_KEY")
ALGORITHM = os.getenv("ALGORITHM")

def check_token(token:str, db):
    try:
        print(token)
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])

        db_user = db.query(User).filter_by(
            username=decoded_token["username"], password=decoded_token["password"]).one_or_none()
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="USER_NOT_FOUND")

        return {"id_user":db_user.id, "token":token}

    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")



def get_database_dependency(db: Session = Depends(get_db)):
    return db

def get_token_dependency(token: str = Header(..., name="Authorization", alias="Authorization")):
    if not token:
        raise HTTPException(status_code=401, detail="Invalid token format")
    return token

def get_auth_dependencies(token: str = Depends(get_token_dependency), db: Session = Depends(get_database_dependency)):

    auth_data = check_token(token=token, db=db)
    handler = type("Handler", (), {"token":token, "db":db, "id_user":auth_data["id_user"]})
    # return {"token": token, "db": db}
    return handler