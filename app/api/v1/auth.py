from fastapi import APIRouter, Depends, HTTPException, status, responses,Response,Cookie
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.auth.auth import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    get_password_hash,
    authenticate_user
)
from app.models.user import CustomUser
from app.schema.user import UserLogin, UserCreate
from app.utils.validate_data import validate_username,validate_email,validate_password

router = APIRouter()


# Route for user registration
@router.post("/register", status_code=200)
async def register(
    form_data: UserCreate,
    db: Session = Depends(get_db)
):
    if not form_data.username:
        raise HTTPException(status_code=400, detail="Username is required")
    if not form_data.email:
        raise HTTPException(status_code=400, detail="Email is required")
    if not form_data.password:
        raise HTTPException(status_code=400, detail="Password is required")

    # Validate username
    validate_username(form_data.username)

    # Validate email
    validate_email(form_data.email)

    # Validate password
    validate_password(form_data.password)

    # Check if username or email already exists
    user_exist_with_username = db.query(CustomUser).filter(
        CustomUser.username == form_data.username).first()
    if user_exist_with_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User already exists with this username")

    user_exist_with_email = db.query(CustomUser).filter(
        CustomUser.email == form_data.email).first()
    if user_exist_with_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User already exists with this email")

    # Hash the password
    hashed_password = get_password_hash(form_data.password)

    # Create new user
    new_user = CustomUser(
        username=form_data.username,
        email=form_data.email,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return responses.JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "User created successfully"}
    )



# Login or Access Route
@router.post("/login")
async def login(
    form_data: UserLogin,
    db: Session = Depends(get_db)
):
    if not form_data.username or not form_data.password:
        return HTTPException(status_code=400, detail="Username and password are required")

    userdata = authenticate_user(form_data.username, form_data.password, db)
    if userdata:
        access_token = create_access_token(
            data={"username": userdata.username, "role": userdata.role}
        )
        refresh_token = create_refresh_token(
            data={"username": userdata.username, "role": userdata.role}
        )

        response = responses.JSONResponse({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }, status_code=status.HTTP_200_OK)
        response.set_cookie(key="access_token",
                            value=access_token, httponly=True, secure=True)
        response.set_cookie(key="refresh_token",
                            value=refresh_token, httponly=True, secure=True)
        return response
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")


# Refresh Route (It works like rotate token)
@router.post("/refresh",status_code=status.HTTP_200_OK)
async def refresh(
    refresh_token:str = Cookie(None),
    # token_request: TokenRequest,
    db: Session = Depends(get_db)
):
    if not refresh_token:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Refresh token missing..")

    userdata = verify_refresh_token(refresh_token)
    if userdata and userdata.get('sub'):
        user = db.query(CustomUser).filter(
            CustomUser.username == userdata.get('sub')).first()

        if user:
            if not user.is_active:
                return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is Blocked")

            access_token = create_access_token(
                data={"username": user.username, "role": user.role}
            )
            refresh_token = create_refresh_token(
                data={"username": user.username, "role": user.role}
            )

            response = responses.JSONResponse({
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer"
            }, status_code=status.HTTP_200_OK)
            response.set_cookie(key="access_token",
                                value=access_token, httponly=True, secure=True)
            response.set_cookie(key="refresh_token",
                                value=refresh_token, httponly=True, secure=True)
            return response
        else:
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is invalid")




@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response):
    # Clear the cookies
    response.delete_cookie(key="access_token", path="/", secure=True, httponly=True)
    response.delete_cookie(key="refresh_token", path="/", secure=True, httponly=True)

    return {"message": "Successfully logged out"}

