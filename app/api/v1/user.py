# app/routes/profile.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form,status
from sqlalchemy.orm import Session
from typing import Optional
import os
from PIL import Image
import uuid
from app.db.database import get_db
from app.models.user import CustomUser
from app.utils.headers_accessing import validate_and_send_user
from app.schema.user import UserData
from app.utils.validate_data import validate_email,validate_username


router = APIRouter()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024 

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_profile_picture(file: UploadFile) -> str:
    # Create uploads directory if it doesn't exist
    upload_dir = "uploads/profile_pictures"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = file.filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save and optimize image
    with Image.open(file.file) as img:
        # Convert to RGB if image is in RGBA mode
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        # Resize image if too large
        if img.size[0] > 800 or img.size[1] > 800:
            img.thumbnail((800, 800))
        # Save with optimization
        img.save(file_path, optimize=True, quality=85)
    
    return file_path

@router.get("/user",response_model=UserData, status_code=status.HTTP_200_OK)
def user_details(requested_user:dict=Depends(validate_and_send_user)):
    # print(requested_user)
    if not requested_user:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong")
    else:
        if requested_user:
            return requested_user
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token is invalid")




@router.put("/update")
async def update_profile(
    username: str = Form(...),
    email: str = Form(...),
    profile_picture: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    requested_user: dict = Depends(validate_and_send_user)
):
    # Get user from database
    if not requested_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate username and email
    validate_username(username)  # Validate the username
    validate_email(email)  # Validate the email

    # Check if username is taken
    if username != requested_user.username:
        existing_user = db.query(CustomUser).filter(CustomUser.username == username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail={"username": "Username already taken"})
    
    # Check if email is taken
    if email != requested_user.email:
        existing_user = db.query(CustomUser).filter(CustomUser.email == email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail={"email": "Email already taken"})
    
    # Handle profile picture upload
    if profile_picture:
        if not allowed_file(profile_picture.filename):
            raise HTTPException(
                status_code=400,
                detail={"profile_picture": "Invalid file format. Allowed formats: jpg, jpeg, png, webp"}
            )
        
        # Check file size
        await profile_picture.seek(0)
        content = await profile_picture.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail={"profile_picture": "File size too large. Maximum size is 5MB"}
            )
        
        # Reset file pointer
        await profile_picture.seek(0)
        
        # Delete old profile picture if exists
        if requested_user.profile_picture and os.path.exists(requested_user.profile_picture):
            try:
                os.remove(requested_user.profile_picture)
            except:
                pass
        
        # Save new profile picture
        file_path = save_profile_picture(profile_picture)
        requested_user.profile_picture = file_path
    
    # Update user information
    requested_user.username = username
    requested_user.email = email
    
    try:
        db.commit()
        db.refresh(requested_user)
        
        return {
            "message": "Profile updated successfully",
            "user": {
                "username": requested_user.username,
                "email": requested_user.email,
                "profile_picture": requested_user.profile_picture,
                "role": requested_user.role,
                "is_active": requested_user.is_active
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while updating profile")