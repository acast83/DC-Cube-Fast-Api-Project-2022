"""FastApi Pydantic schemas"""

from pydantic import BaseModel


class PyUser(BaseModel):
    """User schema class"""
    username: str
    password: str

    class Config:
        """Orm config class"""
        orm_mode = True
