from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username : str
    email : str
    password : str

class UserData(BaseModel):
    username: str
    email: str
    is_active: bool
    role:str
    profile_picture:Optional[str]


class UserLogin(BaseModel):
    username : str
    password : str


