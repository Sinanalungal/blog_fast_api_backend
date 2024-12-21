from fastapi import Depends,Cookie,HTTPException,status
from app.models.user import CustomUser
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.auth.auth import verify_access_token

def validate_and_send_user(access_token:str=Cookie(None),db:Session=Depends(get_db)):
    user = verify_access_token(access_token=access_token)
    user = db.query(CustomUser).filter(CustomUser.username == user.get('sub')).first()
    if user and not user.is_active:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is Blocked")
    return user