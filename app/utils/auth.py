# from datetime import datetime, timedelta
# import jwt
# from passlib.context import CryptContext
# from typing import Optional

# from app.models import CustomUser  # Adjust import based on your project structure

# # Configuration
# # from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


# SECRET_KEY = "0bb247d0b71602ee3c098eda34ea7b6bf7cb036f5f6948d64917a64421a3584f"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# # Password hashing
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)

# def hash_password(password):
#     return pwd_context.hash(password)

# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt

# def get_user(db, username: str):
#     return db.query(CustomUser).filter(CustomUser.username == username).first()
