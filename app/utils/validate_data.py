from fastapi import HTTPException
import re

EMAIL_REGEX = r"(^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$)"

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 20


def validate_username(username: str) -> bool:
    """
    Validate that the username has a minimum length and allows special characters.
    """
    if len(username) < 3:
        raise HTTPException(
            status_code=400, detail="Username must be at least 3 characters long."
        )
    

    if not re.match(r"^[A-Za-z0-9_@.#&!$%^*()\-+=<>?]*$", username):
        raise HTTPException(
            status_code=400, detail="Username contains invalid characters."
        )
    
    return True



def validate_email(email: str) -> bool:
    """
    Validate email format using regex.
    """
    if not re.match(EMAIL_REGEX, email):
        raise HTTPException(status_code=400, detail="Invalid email format.")
    return True


def validate_password(password: str) -> bool:
    """
    Validate that the password meets strength requirements.
    """
    if len(password) < MIN_PASSWORD_LENGTH or len(password) > MAX_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=400, detail=f"Password must be between {MIN_PASSWORD_LENGTH} and {MAX_PASSWORD_LENGTH} characters long.")
    if not any(char.isupper() for char in password):
        raise HTTPException(
            status_code=400, detail="Password must contain at least one uppercase letter.")
    if not any(char.isdigit() for char in password):
        raise HTTPException(
            status_code=400, detail="Password must contain at least one digit.")
    if not any(char in "!@#$%^&*()-_=+" for char in password):
        raise HTTPException(
            status_code=400, detail="Password must contain at least one special character.")
    return True
