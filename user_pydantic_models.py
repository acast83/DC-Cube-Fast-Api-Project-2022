"""FastApi Pydantic schemas"""

from pydantic import BaseModel


class PyUser(BaseModel):
    """User schema class"""
    username_api: str
    password_api: str

    class Config:
        """Orm config class"""
        orm_mode = True
