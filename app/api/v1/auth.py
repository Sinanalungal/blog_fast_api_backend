# from fastapi import APIRouter
# from datetime import timedelta
# from typing import Annotated

# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordRequestForm
# from app.utils.auth import *


# router = APIRouter()

# from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from sqlalchemy.orm import Session

# from app.db.database import get_db
# from app.models import CustomUser
# from app.utils import verify_password, create_access_token  

# router = APIRouter()

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# @router.post("/token", response_model=dict)
# def login_for_access_token(
#     form_data: OAuth2PasswordRequestForm = Depends(),
#     db: Session = Depends(get_db),
# ):
#     user = get_user(db, form_data.username)
#     if not user or not verify_password(form_data.password, user.hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token = create_access_token(data={"sub": user.username})
#     return {"access_token": access_token, "token_type": "bearer"}


# # @router.post("/token")
# # async def login_for_access_token(
# #     form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
# # ) -> Token:
# #     user = authenticate_user(fake_users_db, form_data.username, form_data.password)
# #     if not user:
# #         raise HTTPException(
# #             status_code=status.HTTP_401_UNAUTHORIZED,
# #             detail="Incorrect username or password",
# #             headers={"WWW-Authenticate": "Bearer"},
# #         )
# #     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
# #     access_token = create_access_token(
# #         data={"sub": user.username}, expires_delta=access_token_expires
# #     )
# #     return Token(access_token=access_token, token_type="bearer")


# # @router.get("/users/me/", response_model=User)
# # async def read_users_me(
# #     current_user: Annotated[User, Depends(get_current_active_user)],
# # ):
# #     return current_user


# # @router.get("/users/me/items/")
# # async def read_own_items(
# #     current_user: Annotated[User, Depends(get_current_active_user)],
# # ):
# #     return [{"item_id": "Foo", "owner": current_user.username}]