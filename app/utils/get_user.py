# # from jose import JWTError, jwt
# from fastapi import Depends, HTTPException, status
# from sqlalchemy.orm import Session

# from app.db.database import get_db
# from app.models import CustomUser
# from app.utils import oauth2_scheme, SECRET_KEY, ALGORITHM

# def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#     except JWTError:
#         raise credentials_exception

#     user = get_user(db, username=username)
#     if user is None:
#         raise credentials_exception
#     return user
