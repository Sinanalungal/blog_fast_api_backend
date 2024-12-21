from fastapi import APIRouter, Depends, HTTPException, status,responses
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.auth.auth import (
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_access_token,
    verify_refresh_token,
    authenticate_user,
)
from app.models.user import CustomUser
from app.schema.user import UserLogin,UserCreate

router = APIRouter()

# @router.post("/register")
# async def register(
#     form_data: UserCreate,
#     db: Session = Depends(get_db)
# ):
#     if not form_data.username:
#         return HTTPException(status_code=400,detail="Username is required")
#     elif not form_data.email:
#         return HTTPException(status_code=400,detail="Email is required")
#     elif not form_data.password:
#         return HTTPException(status_code=400, detail="Password is required")
#     else:
#         pass
    
#     userdata =  authenticate_user(form_data.username, form_data.password,db)
#     if userdata:
#         access_token = create_access_token(
#             data={"username": userdata.username,"role": userdata.role}
#         )
#         refresh_token = create_refresh_token(
#             data={"username": userdata.username,"role": userdata.role}
#         )
        
#         response = responses.JSONResponse({
#             "access_token": access_token,
#             "refresh_token": refresh_token,
#             "token_type": "bearer"
#         },status_code=status.HTTP_200_OK)
#         response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True)
#         response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True)
#         return response
#     else:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")


# Login or Access Route
@router.post("/login")
async def login(
    form_data: UserLogin,
    db: Session = Depends(get_db)
):
    if not form_data.username or not form_data.password:
        return HTTPException(status_code=400,detail="Username and password are required")
    
    userdata =  authenticate_user(form_data.username, form_data.password,db)
    if userdata:
        access_token = create_access_token(
            data={"username": userdata.username,"role": userdata.role}
        )
        refresh_token = create_refresh_token(
            data={"username": userdata.username,"role": userdata.role}
        )
        
        response = responses.JSONResponse({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        },status_code=status.HTTP_200_OK)
        response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True)
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True)
        return response
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")


# Refresh Route (It works like rotate token)
@router.post("/refresh")
async def refresh(
    token: str,
    db: Session = Depends(get_db)
):
    if not token:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Refresh token missing..")
    
    userdata =  verify_refresh_token(token)
    if userdata and userdata.get('sub'): 
        user = db.query(CustomUser).filter(CustomUser.username == userdata.get('username')).first()

        if not user.is_active:
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is Blocked")
        
        access_token = create_access_token(
            data={"username": user.username,"role": user.role}
        )
        refresh_token = create_refresh_token(
            data={"username": user.username,"role": user.role}
        )
        
        response = responses.JSONResponse({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        },status_code=status.HTTP_200_OK)
        response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True)
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True)
        return response
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is invalid")