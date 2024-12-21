from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import CustomUser


SECRET_KEY = ""
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_HOURS = 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str, db: Session):
    user = db.query(CustomUser).filter(CustomUser.username == username).first()
    # print(user.hashed_password, verify_password(password, user.hashed_password))
    if not user.is_active:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is Blocked")
    if user and verify_password(password, user.hashed_password):
        print(user)
        return user
    
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED ,detail='Unauthenticated User')


def create_access_token(data: dict) -> str:
    expire = datetime.now(timezone.utc) + \
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    human_readable_exp = expire.strftime("%Y-%m-%d %H:%M:%S")
    print(f"Token expiration time: {human_readable_exp}")

    to_encode = {
        "sub": data["username"],
        "type": 'access',
        "role": data["role"],
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now().timestamp()),
    }

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict):
    expire = datetime.now(timezone.utc) + \
        timedelta(hours=REFRESH_TOKEN_EXPIRE_HOURS)
    to_encode = {
        "sub": data["username"],
        "type": 'refresh',
        "role": data["role"],
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now().timestamp()),
    }

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(access_token: str, required_role: str):
    try:
        decoded_token = jwt.decode(
            access_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        print(decoded_token, 'this si the decoded token')

        exp_timestamp = decoded_token.get("exp")
        print(exp_timestamp, datetime.now(
            timezone.utc).timestamp(), 'this is two times')
        print(exp_timestamp < datetime.now(
            timezone.utc).timestamp(), 'this is boolean')

        if exp_timestamp and exp_timestamp < datetime.now(timezone.utc).timestamp():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access token expired")

        if decoded_token.get("role") != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden for users with role: {decoded_token.get('role')}"
            )
        print("Access token verified")
        return decoded_token
    except JWTError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(error))


def verify_refresh_token(refresh_token: str):
    try:
        decoded_token = jwt.decode(
            refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        print("refresh token verified")
        return decoded_token

    except JWTError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(error))
